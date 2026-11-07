#include "mef_linearity_raw_files.h"
#include "mef_file_metadata_internal.h"
#include "pixelmap_flags8.h"
#include "cube_defs.h"
#include <math.h>
#include <stdint.h>
static void *allocate_default(void *u,size_t n){(void)u;return (malloc)(n);}
static void release_default(void *u,void *p){(void)u;(free)(p);}
static void release(const mef_allocator *a,void *p){if(p)a->release(a->user,p);}
static char *copy_text(const mef_allocator *a,const char *s)
{size_t n=strlen(s)+1;char *p=a->allocate(a->user,n);if(p)memcpy(p,s,n);return p;}
static int text(const char *s,size_t n){return s&&s[0]&&memchr(s,0,n);}
static int ref_valid(const mef_image_ref *r)
{return r&&r->resolved_path&&r->resolved_path[0]=='/'&&strlen(r->resolved_path)<4096&&
    text(r->asset_record_id,128)&&r->detector_id&&r->hdu_index>=0;}
static int alias(const mef_image_ref *a,const mef_image_ref *b)
{return !strcmp(a->asset_record_id,b->asset_record_id)||
    (!strcmp(a->resolved_path,b->resolved_path)&&a->hdu_index==b->hdu_index);}
static int budget(const mef_bound_detector *d,size_t *total,size_t limit)
{
    if(!d||!d->image.axes[1]||d->image.axes[0]>SIZE_MAX/d->image.axes[1])return 0;
    size_t n=d->image.axes[0]*d->image.axes[1];
    if(n>limit||*total>limit-n)return 0;
    *total+=n;return 1;
}
mef_status mef_linearity_raw_from_files(const mef_linearity_raw_files_input *p,
    const mef_allocator *allocator,mef_linearity_files_result **out)
{
    mef_allocator a={NULL,allocate_default,release_default};mef_status status=MEF_ERR_INPUT;
    mef_linearity_files_result *r=NULL;image_t **raw=NULL,*bias[2]={NULL,NULL};
    mef_linearity_frame *frames=NULL;pixelmap *binary=NULL;unsigned char *flags=NULL;
    mef_bias_settings g;size_t total=0;int count=0,width,height;
    if(!p||!out||*out||(allocator&&(!allocator->allocate||!allocator->release)))return status;
    if(allocator)a=*allocator;
    const mef_linearity_pairs_input *s=&p->pairs;
    if(!s->configuration||s->raw||s->frame||s->bpm_flags||s->bpm_binary||s->bpm_count||
       !p->input||s->frames<2||s->frames>MAX_IMAGE_NUMBER||s->frames%2||!s->roi||s->rois<1||
       !text(s->identity.detector_id,64)||!text(s->identity.amplifier_id,64)||s->amplifier_index<0||
       (s->with_mad!=0&&s->with_mad!=1)||s->reject_bits>255||!s->max_rows||
       !isfinite(s->saturation_raw)||s->saturation_raw<=0||!isfinite(s->pair_time_tolerance)||s->pair_time_tolerance<0||
       !p->max_loaded_pixels||!p->exposure_key||!p->exposure_key[0]||strlen(p->exposure_key)>80||p->exposure_hdu<0||
       (p->mask_encoding!=MEF_LINEARITY_MASK_OMITTED&&p->mask_encoding!=MEF_LINEARITY_MASK_REASON8&&p->mask_encoding!=MEF_LINEARITY_MASK_BINARY)||
       (p->mask_encoding==MEF_LINEARITY_MASK_OMITTED)!=(p->bpm_map==NULL)||
       (p->bpm_map?!ref_valid(p->bpm_reference):p->bpm_reference!=NULL)||
       (p->mask_encoding==MEF_LINEARITY_MASK_BINARY&&p->binary_good_value!=0&&p->binary_good_value!=1)||
       (p->mask_encoding==MEF_LINEARITY_MASK_REASON8&&(!text(p->mask_registry,33))))return status;
    for(int j=0;j<2;++j)if(s->raw_bias[j]||s->raw_bias_asset[j]||s->raw_bias_hdu[j]||
       !p->raw_bias_map[j]||!ref_valid(p->raw_bias_reference[j]))return status;
    count=s->frames;const char *detector=s->identity.detector_id;
    if(mef_config_bias_settings(s->configuration,s->configuration_detector,&g)!=MEF_OK)return MEF_ERR_CONFIG;
    if(g.trim[0]<1||g.trim[2]<1||g.trim[1]<g.trim[0]||g.trim[3]<g.trim[2]||
       g.trim[1]>MAX_COLUMN_NUMBER||g.trim[3]>MAX_LINE_NUMBER)return MEF_ERR_CONFIG;
    width=g.trim[1]-g.trim[0]+1;height=g.trim[3]-g.trim[2]+1;
    int selected=0;
    for(int i=0;i<s->rois;++i){const detector_roi *roi=s->roi+i;
        if(!text(roi->roi_id,64)||roi->amplifier<0)return status;
        for(int j=0;j<i;++j)if(!strcmp(roi->roi_id,s->roi[j].roi_id))return status;
        if(roi->amplifier==s->amplifier_index){
            if(roi->xmin<1||roi->xmax<roi->xmin||roi->xmax>width||roi->ymin<1||roi->ymax<roi->ymin||roi->ymax>height)return status;
            ++selected;}}
    if(!selected||(size_t)selected>s->max_rows/(size_t)(count/2))return status;
    const mef_bound_detector *first=mef_layout_find(p->input[0].map,detector);
    if(!first)return status;
    for(int i=0;i<count+2+(p->bpm_map?1:0);++i){
        const mef_layout_map *map=i<count?p->input[i].map:i<count+2?p->raw_bias_map[i-count]:p->bpm_map;
        const mef_image_ref *ref=i<count?&p->input[i].reference:i<count+2?p->raw_bias_reference[i-count]:p->bpm_reference;
        int mask=i==count+2;
        if(!ref_valid(ref)||!binding_matches(map,detector,ref,mask?"mask":"ADU",s->configuration_detector)||
           mef_layout_compatible(p->input[0].map,map,"ADU",mask?"mask":"ADU",NULL,NULL)!=MEF_OK)return status;
        const mef_bound_detector *d=mef_layout_find(map,detector);
        if(d->active_x!=(mask?1:g.trim[0])||d->active_y!=(mask?1:g.trim[2])||
           d->active_width!=width||d->active_height!=height||
           d->image.axes[0]!=(mask?(size_t)width:first->image.axes[0])||
           d->image.axes[1]!=(mask?(size_t)height:first->image.axes[1])||
           (d->image.amplifier[0]&&strcmp(d->image.amplifier,s->identity.amplifier_id))||
           !budget(d,&total,p->max_loaded_pixels))return status;
        for(int j=0;j<i;++j){const mef_image_ref *other=j<count?&p->input[j].reference:p->raw_bias_reference[j-count];
            if(alias(ref,other))return status;}
        if(i<count){const mef_linearity_file_frame *f=p->input+i;
            if(!text(f->pair_id,64)||f->input_index<0)return status;
            for(int j=0;j<i;++j)if(f->input_index==p->input[j].input_index)return status;}
    }
    status=MEF_ERR_MEMORY;r=a.allocate(a.user,sizeof *r);if(!r)goto done;
    memset(r,0,sizeof *r);r->allocator=a;r->frames=count;r->bpm_supplied=p->bpm_map!=NULL;
    r->mask_encoding=p->mask_encoding;r->binary_good_value=p->binary_good_value;r->exposure_hdu=p->exposure_hdu;
    r->pair_time_tolerance=s->pair_time_tolerance;r->max_loaded_pixels=p->max_loaded_pixels;
    strcpy(r->exposure_key,p->exposure_key);if(p->mask_encoding==MEF_LINEARITY_MASK_REASON8)strcpy(r->mask_registry,p->mask_registry);
    r->input_paths=a.allocate(a.user,(size_t)count*sizeof *r->input_paths);
    if(r->input_paths)memset(r->input_paths,0,(size_t)count*sizeof *r->input_paths);
    r->input_binding=a.allocate(a.user,(size_t)count*sizeof *r->input_binding);
    raw=a.allocate(a.user,(size_t)count*sizeof *raw);if(raw)memset(raw,0,(size_t)count*sizeof *raw);
    frames=a.allocate(a.user,(size_t)count*sizeof *frames);
    if(!r->input_paths||!r->input_binding||!raw||!frames)goto done;
    memset(frames,0,(size_t)count*sizeof *frames);
    for(int i=0;i<count;++i){const mef_linearity_file_frame *f=p->input+i;
        r->input_paths[i]=copy_text(&a,f->reference.resolved_path);if(!r->input_paths[i])goto done;
        r->input_binding[i]=*mef_layout_find(f->map,detector);
        strcpy(frames[i].asset_id,f->reference.asset_record_id);strcpy(frames[i].pair_id,f->pair_id);
        frames[i].hdu=f->reference.hdu_index;frames[i].input_index=f->input_index;
        if(!exposure(r->input_paths[i],p->exposure_hdu,p->exposure_key,&frames[i].seconds)){status=MEF_ERR_INPUT;goto done;}}
    for(int i=0;i<count;++i){int members=0;
        for(int j=0;j<count;++j)if(!strcmp(frames[i].pair_id,frames[j].pair_id)){
            ++members;if(fabs(frames[i].seconds-frames[j].seconds)>s->pair_time_tolerance){status=MEF_ERR_INPUT;goto done;}}
        if(members!=2){status=MEF_ERR_INPUT;goto done;}}
    for(int j=0;j<2;++j){r->raw_bias_path[j]=copy_text(&a,p->raw_bias_reference[j]->resolved_path);
        if(!r->raw_bias_path[j])goto done;
        r->raw_bias_binding[j]=*mef_layout_find(p->raw_bias_map[j],detector);}
    if(p->bpm_map){r->bpm_path=copy_text(&a,p->bpm_reference->resolved_path);r->bpm_asset_id=copy_text(&a,p->bpm_reference->asset_record_id);
        r->bpm_binding=*mef_layout_find(p->bpm_map,detector);if(!r->bpm_path||!r->bpm_asset_id)goto done;}
    /* All header/binding/association admission above precedes pixel loads. */
    for(int i=0;i<count;++i){status=mef_layout_load(p->input[i].map,detector,raw+i,NULL);if(status!=MEF_OK)goto done;}
    for(int j=0;j<2;++j){status=mef_layout_load(p->raw_bias_map[j],detector,bias+j,NULL);if(status!=MEF_OK)goto done;}
    if(p->mask_encoding==MEF_LINEARITY_MASK_BINARY){status=mef_layout_load_bpm(p->bpm_map,detector,p->binary_good_value,&binary,NULL);if(status!=MEF_OK)goto done;}
    if(p->mask_encoding==MEF_LINEARITY_MASK_REASON8){int w,h;
        if(pixelmap_flags8_load_checked(r->bpm_path,r->bpm_binding.image.hdu_index,p->mask_registry,&flags,&w,&h)||w!=width||h!=height){status=MEF_ERR_INPUT;goto done;}}
    mef_linearity_pairs_input input=*s;input.raw=(const image_t *const *)raw;input.frame=frames;
    input.bpm_flags=flags;input.bpm_count=flags?(size_t)width*(size_t)height:0;input.bpm_binary=binary;
    for(int j=0;j<2;++j){input.raw_bias[j]=bias[j];input.raw_bias_asset[j]=p->raw_bias_reference[j]->asset_record_id;
        input.raw_bias_hdu[j]=p->raw_bias_reference[j]->hdu_index;}
    status=mef_linearity_measure_pairs(&input,&a,&r->pairs);if(status!=MEF_OK)goto done;
    *out=r;r=NULL;
done:
    if(raw){for(int i=0;i<count;++i)image_del(raw[i]);release(&a,raw);}
    for(int j=0;j<2;++j)image_del(bias[j]);
    pixelmap_del(binary);if(flags)free(flags);release(&a,frames);mef_linearity_files_destroy(r);return status;
}
