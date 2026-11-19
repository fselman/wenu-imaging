#include "mef_linearity_prepare.h"
#include "mefp_lib.h"
#include <math.h>
#include <stdint.h>
static void *allocate_default(void *u,size_t n){(void)u;return (malloc)(n);}
static void release_default(void *u,void *p){(void)u;(free)(p);}
static void release(const mef_allocator *a,void *p){if(p)a->release(a->user,p);}
static int interval(const int *r,int n){return 1<=r[0]&&r[0]<r[1]&&r[1]<=n;}
static int band(const int *r,int n){return 1<=r[0]&&r[0]<=r[1]&&r[1]<=n;}
void mef_linearity_prepare_frame_destroy(mef_linearity_prepare_frame_result *r)
{
    if(!r)return;
    mef_allocator a=r->allocator;image_del(r->active);
    release(&a,r->row_correction);release(&a,r);
}
mef_status mef_linearity_prepare_frame(const mef_linearity_prepare_frame_input *p,
    const mef_allocator *allocator,mef_linearity_prepare_frame_result **out)
{
    mef_allocator a={NULL,allocate_default,release_default};
    mef_linearity_prepare_frame_result *r=NULL;image_t *copy=NULL;
    mef_status status=MEF_ERR_INPUT;size_t raw_pixels,active_pixels,need;
    if(!p||!out||*out||!p->raw||!p->raw->data||
       (p->role!=MEF_PREPARE_BIAS&&p->role!=MEF_PREPARE_FLAT)||
       (p->role==MEF_PREPARE_FLAT)!=(p->master!=NULL)||
       (allocator&&(!allocator->allocate||!allocator->release)))return status;
    if(allocator)a=*allocator;
    int w=p->raw->lx,h=p->raw->ly;const mef_bias_settings *g=&p->settings;
    if(w<1||h<1||w>MAX_COLUMN_NUMBER||h>MAX_LINE_NUMBER||w>INT_MAX/h||
       !interval(g->trim,w)||!interval(g->trim+2,h)||
       (g->use_prescan!=0&&g->use_prescan!=1)||(g->use_overscan!=0&&g->use_overscan!=1)||
       (g->use_prescan&&!band(g->prescan,w))||(g->use_overscan&&!band(g->overscan,w)))return MEF_ERR_CONFIG;
    int n=(g->use_prescan?g->prescan[1]-g->prescan[0]+1:0)+
          (g->use_overscan?g->overscan[1]-g->overscan[0]+1:0);
    if(g->rejection[0]<0||g->rejection[1]<0||
       (n?(g->rejection[0]>=n||g->rejection[1]>=n-g->rejection[0]):
          (g->rejection[0]||g->rejection[1])))return MEF_ERR_CONFIG;
    int aw=g->trim[1]-g->trim[0]+1,ah=g->trim[3]-g->trim[2]+1;
    raw_pixels=(size_t)w*h;active_pixels=(size_t)aw*ah;
    if(raw_pixels>SIZE_MAX/2||active_pixels>SIZE_MAX/2||
       raw_pixels*2>SIZE_MAX-active_pixels*2)return MEF_ERR_INPUT;
    need=2*raw_pixels+active_pixels*(p->master?2:1);
    if(!p->max_working_pixels||need>p->max_working_pixels)return MEF_ERR_INPUT;
    if(p->master){
        if(!p->master->data||p->master->lx!=aw||p->master->ly!=ah)return status;
        for(size_t k=0;k<active_pixels;++k)if(!isfinite(p->master->data[k]))return status;
    }
    /* Validate every enabled electronic sample, including first/last raw rows. */
    for(int y=0;y<h;++y)for(int x=1;x<=w;++x)
        if(((g->use_prescan&&x>=g->prescan[0]&&x<=g->prescan[1])||
            (g->use_overscan&&x>=g->overscan[0]&&x<=g->overscan[1]))&&
            !isfinite(p->raw->data[y*w+x-1]))return status;
    status=MEF_ERR_MEMORY;r=a.allocate(a.user,sizeof *r);if(!r)goto done;
    memset(r,0,sizeof *r);r->allocator=a;r->settings=*g;r->role=p->role;
    r->rows=n?(size_t)h:0;
    if(n){r->row_correction=a.allocate(a.user,(size_t)h*sizeof(pixelvalue));if(!r->row_correction)goto done;}
    copy=image_copy((image_t *)p->raw);if(!copy)goto done;
    if(n){
        mef_bb work;mef_ccd detector;memset(&work,0,sizeof work);memset(&detector,0,sizeof detector);
        memcpy(detector.prescan_x,g->prescan,sizeof g->prescan);
        memcpy(detector.overscan_x,g->overscan,sizeof g->overscan);
        memcpy(detector.trimreg,g->trim,sizeof g->trim);
        work.ccd=&detector;work.xtnum=work.nxts=1;
        work.use_prescan=g->use_prescan;work.use_overscan=g->use_overscan;
        memcpy(work.scanrej,g->rejection,sizeof g->rejection);
        r->active=mef_overscan_correction_traced(copy,&work,0,"linearity",NULL,r->row_correction,(size_t)h);
    }else r->active=image_getvig(copy,g->trim[0],g->trim[2],g->trim[1],g->trim[3]);
    image_del(copy);copy=NULL;if(!r->active)goto done;
    if(p->master&&image_sub_local(r->active,(image_t *)p->master)){status=MEF_ERR_COMPUTATION;goto done;}
    *out=r;r=NULL;status=MEF_OK;
done:
    image_del(copy);mef_linearity_prepare_frame_destroy(r);return status;
}
void mef_linearity_prepared_destroy(mef_linearity_prepared_result *r)
{
    if(!r)return;
    mef_allocator a=r->allocator;mef_linearity_pairs_destroy(r->raw);
    release(&a,r->row);release(&a,r->row_correction);release(&a,r);
}
mef_status mef_linearity_prepare_pairs(const mef_linearity_pairs_input *p,
    const image_t *master,size_t max_working_pixels,const mef_allocator *allocator,
    mef_linearity_prepared_result **out)
{
    mef_allocator a={NULL,allocate_default,release_default};mef_status status=MEF_ERR_INPUT;
    mef_linearity_prepared_result *r=NULL;mef_linearity_prepare_frame_result *f[2]={NULL,NULL};
    pixelmap *mask=NULL;mef_bias_settings settings;
    if(!p||!master||!out||*out||!p->configuration||!p->raw||!p->raw[0]||
       p->frames<2||p->frames>MAX_IMAGE_NUMBER||
       (allocator&&(!allocator->allocate||!allocator->release)))return status;
    status=mef_config_bias_settings(p->configuration,p->configuration_detector,&settings);
    if(status!=MEF_OK)return status;
    int w=p->raw[0]->lx,h=p->raw[0]->ly;const mef_bias_settings *g=&settings;
    if(w<1||h<1||w>MAX_COLUMN_NUMBER||h>MAX_LINE_NUMBER||w>INT_MAX/h||
       !interval(g->trim,w)||!interval(g->trim+2,h))return MEF_ERR_CONFIG;
    int aw=g->trim[1]-g->trim[0]+1,ah=g->trim[3]-g->trim[2]+1;
    /* Conservative logical-pixel ceiling, before owner allocations: all raw
     * inputs, one raw copy, master, two corrected flats, selection, difference,
     * combined selection and borrowed BPM. Statistics scratch is dependency
     * storage, not a claim about total process bytes. Traces are row bounded. */
    size_t raw_pixels=(size_t)w*h,active_pixels=(size_t)aw*ah;
    size_t planes=(size_t)p->frames+3;
    if(raw_pixels>SIZE_MAX/planes||active_pixels>SIZE_MAX/7||
       raw_pixels*planes>SIZE_MAX-active_pixels*7||
       raw_pixels*planes+active_pixels*7>max_working_pixels||
       (size_t)h>SIZE_MAX/((size_t)p->frames+2)/sizeof(pixelvalue))return MEF_ERR_INPUT;
    if(allocator)a=*allocator;
    r=a.allocate(a.user,sizeof *r);if(!r)return MEF_ERR_MEMORY;
    memset(r,0,sizeof *r);r->allocator=a;r->settings=settings;
    status=mef_linearity_measure_pairs(p,&a,&r->raw);if(status!=MEF_OK)goto done;
    status=MEF_ERR_MEMORY;
    r->row=a.allocate(a.user,r->raw->rows*sizeof *r->row);
    r->row_correction=a.allocate(a.user,((size_t)p->frames+2)*(size_t)h*sizeof(pixelvalue));
    if(!r->row||!r->row_correction)goto done;
    memset(r->row,0,r->raw->rows*sizeof *r->row);
    mask=pixelmap_new(aw,ah);if(!mask)goto done;
    mef_linearity_prepare_frame_input in;
    memset(&in,0,sizeof in);in.settings=*g;in.max_working_pixels=max_working_pixels;
    for(int b=0;b<(p->raw_bias[0]?2:0);++b){
        if(p->processed) {
            if(!p->bias_traces[b]) {status=MEF_ERR_INPUT;goto done;}
            memcpy(r->row_correction+((size_t)p->frames+b)*h,p->bias_traces[b],(size_t)h*sizeof(pixelvalue));
            continue;
        }
        in.role=MEF_PREPARE_BIAS;in.raw=p->raw_bias[b];
        status=mef_linearity_prepare_frame(&in,&a,&f[0]);if(status!=MEF_OK)goto done;
        if(!f[0]->rows){status=MEF_ERR_CONFIG;goto done;} /* this corrected-stage API requires scans */
        memcpy(r->row_correction+((size_t)p->frames+b)*h,f[0]->row_correction,(size_t)h*sizeof(pixelvalue));
        mef_linearity_prepare_frame_destroy(f[0]);f[0]=NULL;
    }
    in.role=MEF_PREPARE_FLAT;in.master=master;r->trace_rows=(size_t)h;
    for(int pair=0;pair<r->raw->pairs;++pair){
        const mef_linearity_pair_row *first=r->raw->row+(size_t)pair*r->raw->rois;
        int members[2]={first->first,first->second};
        const image_t *active[2];
        for(int j=0;j<2;++j){
            if(p->processed) {
                active[j]=p->processed[members[j]];
                if(!active[j] || !active[j]->data || active[j]->lx!=aw || active[j]->ly!=ah ||
                   !p->processed_traces || !p->processed_traces[members[j]]) {status=MEF_ERR_INPUT;goto done;}
                memcpy(r->row_correction+(size_t)members[j]*h,p->processed_traces[members[j]],(size_t)h*sizeof(pixelvalue));
                continue;
            }
            in.raw=p->raw[members[j]];
            status=mef_linearity_prepare_frame(&in,&a,&f[j]);if(status!=MEF_OK)goto done;
            active[j]=f[j]->active;
            memcpy(r->row_correction+(size_t)members[j]*h,f[j]->row_correction,(size_t)h*sizeof(pixelvalue));}
        /* Exact common RAW four-plane population. Corrected nonfinite values on
         * this population are errors, never an opportunity to change membership. */
        for(int y=0;y<ah;++y)for(int x=0;x<aw;++x){
            size_t k=(size_t)y*aw+x,raw=(size_t)(y+g->trim[2]-1)*w+x+g->trim[0]-1;
            int good=p->bpm_flags?!(p->bpm_flags[k]&p->reject_bits):!p->bpm_binary||p->bpm_binary->data[k]==1;
            const image_t *planes4[]={p->raw[members[0]],p->raw[members[1]],p->raw_bias[0],p->raw_bias[1]};
            for(int j=0;j<(p->raw_bias[0]?4:2);++j)if(!isfinite(planes4[j]->data[raw])||planes4[j]->data[raw]>=p->saturation_raw)good=0;
            mask->data[k]=(binpix)good;
            /* Per-ROI count equality below rejects any corrected nonfinite on
             * an admitted measured site without imposing a new outside-ROI cut. */
        }
        for(int q=0;q<r->raw->rois;++q){size_t k=(size_t)pair*r->raw->rois+q;
            const detector_roi *roi=&r->raw->bias[q].roi;int zone[]={roi->xmin,roi->xmax,roi->ymin,roi->ymax};
            mef_linearity_prepared_roi *row=r->row+k;
            if(image_getstats_masked_checked(active[0],mask,zone,p->with_mad,&row->first)||
               image_getstats_masked_checked(active[1],mask,zone,p->with_mad,&row->second)||
               image_pair_stats_checked(active[0],active[1],mask,mask,zone,p->with_mad,&row->difference)||
               row->first.valid_pixels!=r->raw->row[k].measurement.valid_pixels||
               row->second.valid_pixels!=row->first.valid_pixels||row->difference.valid_pixels!=row->first.valid_pixels){status=MEF_ERR_COMPUTATION;goto done;}
        }
        for(int j=0;j<2;++j){mef_linearity_prepare_frame_destroy(f[j]);f[j]=NULL;}
    }
    *out=r;r=NULL;status=MEF_OK;
done:
    mef_linearity_prepare_frame_destroy(f[0]);mef_linearity_prepare_frame_destroy(f[1]);
    pixelmap_del(mask);mef_linearity_prepared_destroy(r);return status;
}
