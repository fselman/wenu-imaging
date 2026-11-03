#include "mef_linearity_files.h"
#include "mef_file_metadata_internal.h"
#include "pixelmap_flags8.h"
#include "cube_defs.h"
#include <math.h>
#include <stdint.h>
static void *allocate_default(void *u,size_t n){(void)u;return (malloc)(n);}
static void release_default(void *u,void *p){(void)u;(free)(p);}
static void release(const mef_allocator *a,void *p){if(p)a->release(a->user,p);}
void mef_linearity_files_destroy(mef_linearity_files_result *r)
{
    if(!r)return;
    mef_allocator a=r->allocator;
    mef_linearity_samples_destroy(r->samples);
    if(r->input_paths)for(int i=0;i<r->frames;++i)release(&a,r->input_paths[i]);
    release(&a,r->input_paths);release(&a,r->input_binding);release(&a,r->bias_path);release(&a,r->bpm_path);
    release(&a,r->bias_asset_id);release(&a,r->bpm_asset_id);release(&a,r);
}
static char *copy_text(const mef_allocator *a,const char *s)
{size_t n=strlen(s)+1;char *p=a->allocate(a->user,n);if(p)memcpy(p,s,n);return p;}
static int ref_valid(const mef_image_ref *r)
{
    return r&&r->resolved_path&&r->resolved_path[0]=='/'&&strlen(r->resolved_path)<4096&&
        r->asset_record_id&&r->asset_record_id[0]&&strlen(r->asset_record_id)<128&&
        r->detector_id&&r->hdu_index>=0;
}
static int active_calibration(const mef_bound_detector *d,int width,int height)
{
    return d&&d->active_x==1&&d->active_y==1&&d->active_width==width&&d->active_height==height&&
        d->image.axes[0]==(size_t)width&&d->image.axes[1]==(size_t)height;
}
static int add_pixels(const mef_bound_detector *d,size_t *total,size_t limit)
{
    if(d->image.axes[0]>SIZE_MAX/d->image.axes[1])return 0;
    size_t n=d->image.axes[0]*d->image.axes[1];
    if(n>limit||*total>limit-n)return 0;
    *total+=n;return 1;
}
mef_status mef_linearity_from_files(const mef_linearity_files_input *p,
    const mef_allocator *allocator,mef_linearity_files_result **out)
{
    mef_allocator a={NULL,allocate_default,release_default};mef_status status=MEF_ERR_INPUT;
    mef_linearity_files_result *r=NULL;image_t **raw=NULL,*bias=NULL;pixelmap *binary=NULL;
    unsigned char *flags=NULL;mef_linearity_frame *frames=NULL;mef_bias_settings g;
    const mef_bound_detector *first,*cal,*d;size_t total=0;int count,width,height;
    if(!p||!out||*out||(allocator&&(!allocator->allocate||!allocator->release)))return status;
    if(allocator)a=*allocator;
    const mef_linearity_sample_input *s=&p->sample;
    if(s->frames<2||s->frames>MAX_IMAGE_NUMBER||s->frames%2||s->raw||s->frame||s->master_bias||s->bpm_flags||
       s->bpm_binary||s->bpm_count||s->samples||!s->configuration||!p->input||!p->bias_map||!ref_valid(p->bias_reference)||
       !memchr(s->identity.detector_id,0,64)||!s->identity.detector_id[0]||
       !memchr(s->identity.amplifier_id,0,64)||!s->identity.amplifier_id[0]||
       !p->exposure_key||!p->exposure_key[0]||strlen(p->exposure_key)>80||p->exposure_hdu<0||
       !isfinite(p->pair_time_tolerance)||p->pair_time_tolerance<0||!p->max_loaded_pixels||
       (p->mask_encoding!=MEF_LINEARITY_MASK_OMITTED&&p->mask_encoding!=MEF_LINEARITY_MASK_REASON8&&p->mask_encoding!=MEF_LINEARITY_MASK_BINARY)||
       (p->mask_encoding==MEF_LINEARITY_MASK_OMITTED)!=(p->bpm_map==NULL)||
       (p->bpm_map?!ref_valid(p->bpm_reference):p->bpm_reference!=NULL)||
       (p->mask_encoding==MEF_LINEARITY_MASK_BINARY&&p->binary_good_value!=0&&p->binary_good_value!=1)||
       (p->mask_encoding==MEF_LINEARITY_MASK_REASON8&&(!p->mask_registry||!p->mask_registry[0]||strlen(p->mask_registry)>32)))return status;
    if(!s->roi||s->rois<1||!s->max_sites||!s->max_observations||s->amplifier_index<0||s->reject_bits>255||
       !isfinite(s->saturation_raw)||s->saturation_raw<=0||!isfinite(s->identity.signal_min)||
       !isfinite(s->identity.signal_max)||s->identity.signal_min>=s->identity.signal_max)return status;
    const char *detector=s->identity.detector_id;count=s->frames;
    if(mef_config_bias_settings(s->configuration,s->configuration_detector,&g)!=MEF_OK)return MEF_ERR_CONFIG;
    if(g.trim[0]<1||g.trim[2]<1||g.trim[1]<g.trim[0]||g.trim[3]<g.trim[2]||
       g.trim[1]>MAX_COLUMN_NUMBER||g.trim[3]>MAX_LINE_NUMBER)return MEF_ERR_CONFIG;
    width=g.trim[1]-g.trim[0]+1;height=g.trim[3]-g.trim[2]+1;
    if(width<=1||height<=1)return MEF_ERR_CONFIG;
    first=mef_layout_find(p->input[0].map,detector);if(!first)return status;
    int selected_rois=0;
    for(int i=0;i<s->rois;++i)if(s->roi[i].amplifier==s->amplifier_index){
        const detector_roi *q=s->roi+i;
        if(!memchr(q->roi_id,0,64)||!q->roi_id[0]||q->xmin<1||q->ymin<1||q->xmax<q->xmin||q->ymax<q->ymin||q->xmax>width||q->ymax>height)return status;
        ++selected_rois;
    }
    if(!selected_rois)return status;
    for(int i=0;i<count;++i){const mef_linearity_file_frame *f=p->input+i;
        if(!ref_valid(&f->reference)||!f->pair_id||!f->pair_id[0]||strlen(f->pair_id)>63||f->input_index<0||
           !binding_matches(f->map,detector,&f->reference,"ADU",s->configuration_detector)||
           mef_layout_compatible(p->input[0].map,f->map,"ADU","ADU",NULL,NULL)!=MEF_OK)return status;
        d=mef_layout_find(f->map,detector);
        if(d->active_x!=g.trim[0]||d->active_y!=g.trim[2]||d->active_width!=width||d->active_height!=height||
           (d->image.amplifier[0]&&strcmp(d->image.amplifier,s->identity.amplifier_id))||
           !add_pixels(d,&total,p->max_loaded_pixels))return status;
        for(int j=0;j<i;++j)if(f->input_index==p->input[j].input_index||
           !strcmp(f->reference.asset_record_id,p->input[j].reference.asset_record_id)||
           (!strcmp(f->reference.resolved_path,p->input[j].reference.resolved_path)&&f->reference.hdu_index==p->input[j].reference.hdu_index))return status;
    }
    const mef_layout_map *maps[2]={p->bias_map,p->bpm_map};const mef_image_ref *refs[2]={p->bias_reference,p->bpm_reference};
    for(int i=0;i<(p->bpm_map?2:1);++i){
        if(!binding_matches(maps[i],detector,refs[i],i?"mask":"ADU",s->configuration_detector)||
           mef_layout_compatible(p->input[0].map,maps[i],"ADU",i?"mask":"ADU",NULL,NULL)!=MEF_OK)return status;
        cal=mef_layout_find(maps[i],detector);
        if(!active_calibration(cal,width,height)||!add_pixels(cal,&total,p->max_loaded_pixels))return status;
        if(cal->image.amplifier[0]&&strcmp(cal->image.amplifier,s->identity.amplifier_id))return status;
        for(int j=0;j<count;++j)if(!strcmp(refs[i]->asset_record_id,p->input[j].reference.asset_record_id)||
           (!strcmp(refs[i]->resolved_path,p->input[j].reference.resolved_path)&&refs[i]->hdu_index==p->input[j].reference.hdu_index))return status;
    }
    if(p->bpm_map&&(!strcmp(p->bias_reference->asset_record_id,p->bpm_reference->asset_record_id)||
       (!strcmp(p->bias_reference->resolved_path,p->bpm_reference->resolved_path)&&p->bias_reference->hdu_index==p->bpm_reference->hdu_index)))return status;
    status=MEF_ERR_MEMORY;r=a.allocate(a.user,sizeof *r);if(!r)goto done;
    memset(r,0,sizeof *r);r->allocator=a;r->frames=count;r->bpm_supplied=p->bpm_map!=NULL;r->mask_encoding=p->mask_encoding;
    r->exposure_hdu=p->exposure_hdu;r->pair_time_tolerance=p->pair_time_tolerance;r->max_loaded_pixels=p->max_loaded_pixels;
    r->binary_good_value=p->mask_encoding==MEF_LINEARITY_MASK_BINARY?p->binary_good_value:0;
    strcpy(r->exposure_key,p->exposure_key);if(p->mask_encoding==MEF_LINEARITY_MASK_REASON8)strcpy(r->mask_registry,p->mask_registry);
    r->input_paths=a.allocate(a.user,(size_t)count*sizeof *r->input_paths);
    r->input_binding=a.allocate(a.user,(size_t)count*sizeof *r->input_binding);
    raw=a.allocate(a.user,(size_t)count*sizeof *raw);frames=a.allocate(a.user,(size_t)count*sizeof *frames);
    if(r->input_paths)for(int i=0;i<count;++i)r->input_paths[i]=NULL;
    if(raw)for(int i=0;i<count;++i)raw[i]=NULL;
    if(!r->input_paths||!r->input_binding||!raw||!frames)goto done;
    memset(frames,0,(size_t)count*sizeof *frames);
    for(int i=0;i<count;++i){const mef_linearity_file_frame *f=p->input+i;
        r->input_paths[i]=copy_text(&a,f->reference.resolved_path);if(!r->input_paths[i])goto done;
        r->input_binding[i]=*mef_layout_find(f->map,detector);frames[i].input_index=f->input_index;frames[i].hdu=f->reference.hdu_index;
        strcpy(frames[i].asset_id,f->reference.asset_record_id);strcpy(frames[i].pair_id,f->pair_id);
        if(!exposure(r->input_paths[i],p->exposure_hdu,p->exposure_key,&frames[i].seconds)){status=MEF_ERR_INPUT;goto done;}
    }
    for(int i=0;i<count;++i){int members=0;
        for(int j=0;j<count;++j)if(!strcmp(frames[i].pair_id,frames[j].pair_id)){
            ++members;if(fabs(frames[i].seconds-frames[j].seconds)>p->pair_time_tolerance){status=MEF_ERR_INPUT;goto done;}}
        if(members!=2){status=MEF_ERR_INPUT;goto done;}
    }
    r->bias_path=copy_text(&a,p->bias_reference->resolved_path);r->bias_asset_id=copy_text(&a,p->bias_reference->asset_record_id);
    r->bias_binding=*mef_layout_find(p->bias_map,detector);
    if(!r->bias_path||!r->bias_asset_id)goto done;
    if(p->bpm_map){r->bpm_path=copy_text(&a,p->bpm_reference->resolved_path);r->bpm_asset_id=copy_text(&a,p->bpm_reference->asset_record_id);
        r->bpm_binding=*mef_layout_find(p->bpm_map,detector);if(!r->bpm_path||!r->bpm_asset_id)goto done;}
    for(int i=0;i<count;++i){status=mef_layout_load(p->input[i].map,detector,raw+i,NULL);if(status!=MEF_OK)goto done;}
    status=mef_layout_load(p->bias_map,detector,&bias,NULL);if(status!=MEF_OK)goto done;
    if(p->mask_encoding==MEF_LINEARITY_MASK_BINARY){status=mef_layout_load_bpm(p->bpm_map,detector,p->binary_good_value,&binary,NULL);if(status!=MEF_OK)goto done;}
    if(p->mask_encoding==MEF_LINEARITY_MASK_REASON8){int w,h;
        if(pixelmap_flags8_load_checked(r->bpm_path,r->bpm_binding.image.hdu_index,p->mask_registry,&flags,&w,&h)||w!=width||h!=height){status=MEF_ERR_INPUT;goto done;}}
    mef_linearity_sample_input input=*s;input.raw=(const image_t *const *)raw;input.frame=frames;input.master_bias=bias;
    input.bpm_flags=flags;input.bpm_count=flags?(size_t)width*(size_t)height:0;input.bpm_binary=binary;
    status=mef_linearity_samples(&input,&a,&r->samples);if(status!=MEF_OK)goto done;
    *out=r;r=NULL;
done:
    if(raw){for(int i=0;i<count;++i)image_del(raw[i]);release(&a,raw);}
    image_del(bias);pixelmap_del(binary);if(flags)free(flags);release(&a,frames);mef_linearity_files_destroy(r);return status;
}
