#include "mef_linearity_samples.h"
#include "mefp_lib.h"
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
static void *allocate_default(void *u,size_t n){(void)u;return (malloc)(n);}
static void release_default(void *u,void *p){(void)u;(free)(p);}
static void release(const mef_allocator *a,void *p){if(p)a->release(a->user,p);}
void mef_linearity_samples_destroy(mef_linearity_sample_result *r)
{
    if(!r)return;
    mef_allocator a=r->allocator;
    mef_config_destroy(r->configuration);release(&a,r->frame);release(&a,r->population);
    release(&a,r->roi);release(&a,r->site);release(&a,r->observation);release(&a,r);
}
static int interval(const int *v,int n){return v[0]>=1&&v[1]>=v[0]&&v[1]<=n;}
static int text(const char *s,size_t n){return memchr(s,0,n)&&s[0];}
static int selected(const mef_linearity_sample_input *p,int x,int y)
{
    for(int i=0;i<p->rois;++i){const detector_roi *q=p->roi+i;
        if(q->amplifier==p->amplifier_index&&x>=q->xmin&&x<=q->xmax&&y>=q->ymin&&y<=q->ymax)return 1;}
    return 0;
}
mef_status mef_linearity_samples(const mef_linearity_sample_input *p,
    const mef_allocator *allocator,mef_linearity_sample_result **out)
{
    mef_allocator a={NULL,allocate_default,release_default};
    mef_linearity_sample_result *r=NULL;mef_bias_settings g;
    image_t *copy=NULL,*active=NULL;int *site_map=NULL,*remap=NULL;
    mef_status status=MEF_ERR_INPUT;const char *diagnostic=NULL;
    size_t pixels,union_pixels=0,capacity;int width,height,aw,ah,scan=0,nroi=0;
    if(!p||!out||*out||!p->configuration||p->frames<1||p->frames>MAX_IMAGE_NUMBER||
       !p->raw||!p->frame||!p->raw[0]||!p->raw[0]->data||!p->master_bias||!p->master_bias->data||
       !p->roi||p->rois<1||p->amplifier_index<0||!p->max_sites||!p->max_observations||
       p->reject_bits>255||!isfinite(p->saturation_raw)||p->saturation_raw<=0||
       !text(p->identity.detector_id,64)||!text(p->identity.amplifier_id,64)||
       !isfinite(p->identity.signal_min)||!isfinite(p->identity.signal_max)||
       p->identity.signal_min>=p->identity.signal_max||
       (allocator&&(!allocator->allocate||!allocator->release)))return status;
    if(allocator)a=*allocator;
    status=mef_config_bias_settings(p->configuration,p->configuration_detector,&g);
    if(status!=MEF_OK)return status;
    width=p->raw[0]->lx;height=p->raw[0]->ly;
    if(width<1||height<1||width>MAX_COLUMN_NUMBER||height>MAX_LINE_NUMBER||width>INT_MAX/height)return MEF_ERR_INPUT;
    if((g.use_prescan!=0&&g.use_prescan!=1)||(g.use_overscan!=0&&g.use_overscan!=1)||
       !interval(g.trim,width)||!interval(g.trim+2,height)||g.trim[0]==g.trim[1]||g.trim[2]==g.trim[3]||
       (g.use_prescan&&!interval(g.prescan,width))||(g.use_overscan&&!interval(g.overscan,width)))return MEF_ERR_CONFIG;
    if(g.use_prescan)scan+=g.prescan[1]-g.prescan[0]+1;
    if(g.use_overscan)scan+=g.overscan[1]-g.overscan[0]+1;
    if(g.rejection[0]<0||g.rejection[1]<0||(!scan&&(g.rejection[0]||g.rejection[1]))||
       (scan&&(g.rejection[0]>=scan||g.rejection[1]>=scan-g.rejection[0])))return MEF_ERR_CONFIG;
    aw=g.trim[1]-g.trim[0]+1;ah=g.trim[3]-g.trim[2]+1;pixels=(size_t)aw*(size_t)ah;
    if(p->master_bias->lx!=aw||p->master_bias->ly!=ah||
       (p->bpm_flags?p->bpm_count!=pixels:p->bpm_count!=0))return MEF_ERR_INPUT;
    for(size_t k=0;k<pixels;++k)if(!isfinite(p->master_bias->data[k]))return MEF_ERR_INPUT;
    for(int i=0;i<p->rois;++i){const detector_roi *q=p->roi+i;
        if(!text(q->roi_id,64)||q->amplifier<0||q->xmin<1||q->ymin<1||q->xmax<q->xmin||q->ymax<q->ymin)return MEF_ERR_INPUT;
        for(int j=0;j<i;++j)if(!strcmp(q->roi_id,p->roi[j].roi_id))return MEF_ERR_INPUT;
        if(q->amplifier==p->amplifier_index){if(q->xmax>aw||q->ymax>ah)return MEF_ERR_INPUT;++nroi;}}
    if(!nroi)return MEF_ERR_INPUT;
    for(int f=0;f<p->frames;++f){const image_t *im=p->raw[f];const mef_linearity_frame *v=p->frame+f;
        if(!im||!im->data||im->lx!=width||im->ly!=height||!text(v->asset_id,128)||!text(v->pair_id,64)||
           v->input_index<0||v->hdu<0||!isfinite(v->seconds)||v->seconds<=0)return MEF_ERR_INPUT;
        for(int j=0;j<f;++j)if(v->input_index==p->frame[j].input_index||!strcmp(v->asset_id,p->frame[j].asset_id))return MEF_ERR_INPUT;
        if(p->samples&&p->samples[f]){const pixelmap *m=p->samples[f];
            if(!m->data||m->lx!=aw||m->ly!=ah)return MEF_ERR_INPUT;
            for(size_t k=0;k<pixels;++k)if(m->data[k]!=0&&m->data[k]!=1)return MEF_ERR_INPUT;}
        for(int y=0;y<height;++y)for(int x=1;x<=width;++x)
            if(((g.use_prescan&&x>=g.prescan[0]&&x<=g.prescan[1])||
                (g.use_overscan&&x>=g.overscan[0]&&x<=g.overscan[1]))&&
               !isfinite(im->data[y*width+x-1]))return MEF_ERR_INPUT;
    }
    for(int y=1;y<=ah;++y)for(int x=1;x<=aw;++x)
        if(selected(p,x,y)&&(!p->bpm_flags||!(p->bpm_flags[(y-1)*aw+x-1]&p->reject_bits)))++union_pixels;
    if(union_pixels>p->max_sites||union_pixels>INT_MAX||pixels>SIZE_MAX/sizeof(int))return MEF_ERR_INPUT;
    if(union_pixels&&((size_t)p->frames>SIZE_MAX/union_pixels))return MEF_ERR_INPUT;
    capacity=union_pixels*(size_t)p->frames;if(capacity>p->max_observations)capacity=p->max_observations;
    if(capacity>INT_MAX||capacity>SIZE_MAX/sizeof(detector_joint_observation)||
       union_pixels>SIZE_MAX/sizeof(detector_joint_site))return MEF_ERR_INPUT;
    status=MEF_ERR_MEMORY;r=a.allocate(a.user,sizeof *r);if(!r)goto done;
    memset(r,0,sizeof *r);r->allocator=a;r->scan=g;r->identity=p->identity;r->amplifier_index=p->amplifier_index;
    r->width=aw;r->height=ah;r->frames=p->frames;r->rois=nroi;r->noise_state=MEF_LINEARITY_NOISE_UNAVAILABLE;
    r->bpm_supplied=p->bpm_flags!=NULL;r->reject_bits=p->reject_bits;r->saturation_raw=p->saturation_raw;
    if(mef_config_clone(p->configuration,&a,&r->configuration,&diagnostic)!=MEF_OK)goto done;
    r->frame=a.allocate(a.user,(size_t)p->frames*sizeof *r->frame);
    r->population=a.allocate(a.user,(size_t)p->frames*sizeof *r->population);
    r->roi=a.allocate(a.user,(size_t)nroi*sizeof *r->roi);
    site_map=a.allocate(a.user,pixels*sizeof *site_map);
    if(union_pixels){r->site=a.allocate(a.user,union_pixels*sizeof *r->site);remap=a.allocate(a.user,union_pixels*sizeof *remap);}
    if(capacity)r->observation=a.allocate(a.user,capacity*sizeof *r->observation);
    if(!r->frame||!r->population||!r->roi||!site_map||(union_pixels&&(!r->site||!remap))||(capacity&&!r->observation))goto done;
    memcpy(r->frame,p->frame,(size_t)p->frames*sizeof *r->frame);memset(r->population,0,(size_t)p->frames*sizeof *r->population);
    nroi=0;for(int i=0;i<p->rois;++i)if(p->roi[i].amplifier==p->amplifier_index){r->roi[nroi]=p->roi[i];r->roi[nroi++].amplifier=0;}
    int sites=0;
    for(int y=1;y<=ah;++y)for(int x=1;x<=aw;++x){size_t k=(size_t)(y-1)*aw+x-1;site_map[k]=selected(p,x,y)?-1:-2;
        if(site_map[k]==-1&&(!p->bpm_flags||!(p->bpm_flags[k]&p->reject_bits))){
            r->site[sites].amplifier=0;r->site[sites].x=x;r->site[sites].y=y;remap[sites]=-1;site_map[k]=sites++;}}
    for(int f=0;f<p->frames;++f){
        mef_bb work;mef_ccd detector;memset(&work,0,sizeof work);memset(&detector,0,sizeof detector);
        memcpy(detector.prescan_x,g.prescan,sizeof g.prescan);memcpy(detector.overscan_x,g.overscan,sizeof g.overscan);
        memcpy(detector.trimreg,g.trim,sizeof g.trim);work.ccd=&detector;work.xtnum=1;work.nxts=1;
        work.use_prescan=g.use_prescan;work.use_overscan=g.use_overscan;memcpy(work.scanrej,g.rejection,sizeof g.rejection);
        copy=image_copy((image_t *)p->raw[f]);if(!copy)goto done;
        active=scan?mef_overscan_correction(copy,&work,f,"linearity"):
            image_getvig(copy,g.trim[0],g.trim[2],g.trim[1],g.trim[3]);
        image_del(copy);copy=NULL;if(!active)goto done;
        if(image_sub_local(active,(image_t *)p->master_bias)){status=MEF_ERR_COMPUTATION;goto done;}
        mef_linearity_population *q=r->population+f;
        for(int y=1;y<=ah;++y)for(int x=1;x<=aw;++x){size_t k=(size_t)(y-1)*aw+x-1;
            size_t raw=(size_t)(y+g.trim[2]-2)*width+x+g.trim[0]-2;
            double original=p->raw[f]->data[raw],value=active->data[k];
            if(site_map[k]==-2){++q->outside_roi;continue;}
            if(site_map[k]==-1){++q->bpm_excluded;continue;}
            if(p->samples&&p->samples[f]&&!p->samples[f]->data[k]){++q->sample_excluded;continue;}
            if(!isfinite(original)||!isfinite(value)){++q->nonfinite;continue;}
            if(original>=p->saturation_raw){++q->saturated;continue;}
            if((size_t)r->observations>=capacity){status=MEF_ERR_INPUT;goto done;}
            detector_joint_observation *v=r->observation+r->observations++;
            v->site=site_map[k];v->input_index=p->frame[f].input_index;v->seconds=p->frame[f].seconds;v->signal=value;
            remap[v->site]=0;++q->admitted;
        }
        image_del(active);active=NULL;
    }
    for(int i=0;i<sites;++i)if(remap[i]==0){remap[i]=r->sites;r->site[r->sites++]=r->site[i];}
    for(int i=0;i<r->observations;++i)r->observation[i].site=remap[r->observation[i].site];
    *out=r;r=NULL;status=MEF_OK;
done:
    image_del(active);image_del(copy);release(&a,site_map);release(&a,remap);mef_linearity_samples_destroy(r);return status;
}
