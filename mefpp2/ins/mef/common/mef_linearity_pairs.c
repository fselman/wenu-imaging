#include "mef_linearity_pairs.h"
#include "mefp_lib.h"
#include <stdint.h>
static void *allocate_default(void *u,size_t n){(void)u;return (malloc)(n);}
static void release_default(void *u,void *p){(void)u;(free)(p);}
static void release(const mef_allocator *a,void *p){if(p)a->release(a->user,p);}
void mef_linearity_pairs_destroy(mef_linearity_pairs_result *r)
{
    if(!r)return;
    mef_allocator a=r->allocator;
    mef_config_destroy(r->configuration);release(&a,r->frame);release(&a,r->bias);release(&a,r->row);release(&a,r);
}
static int text(const char *s,size_t n){return s&&s[0]&&memchr(s,0,n);}
static int interval(const int *v,int n){return v[0]>=1&&v[1]>=v[0]&&v[1]<=n;}
static int good(const mef_linearity_pairs_input *p,size_t k)
{return p->bpm_flags?!(p->bpm_flags[k]&p->reject_bits):!p->bpm_binary||p->bpm_binary->data[k]==1;}
/* Build a RAW-coordinate mask without changing any image. Nonfinite values are
 * left selected for the qualified statistics to reject/count themselves. */
static void selection(const mef_linearity_pairs_input *p,const mef_bias_settings *g,
    const image_t *const *im,int planes,pixelmap *map)
{
    int aw=g->trim[1]-g->trim[0]+1,ah=g->trim[3]-g->trim[2]+1;
    memset(map->data,0,(size_t)map->lx*(size_t)map->ly);
    for(int y=0;y<ah;++y)for(int x=0;x<aw;++x){size_t a=(size_t)y*aw+x;
        size_t k=(size_t)(y+g->trim[2]-1)*map->lx+x+g->trim[0]-1;
        if(!good(p,a))continue;
        int finite=1,sat=0;
        for(int j=0;j<planes;++j){if(!isfinite(im[j]->data[k]))finite=0;if(im[j]->data[k]>=p->saturation_raw)sat=1;}
        map->data[k]=(binpix)(!finite||!sat);
    }
    pixelmap_updatecount(map);
}
static size_t exclusions(const mef_linearity_pairs_input *p,const mef_bias_settings *g,
    const image_t *const *im,int planes,const int *active,size_t *bpm,size_t *sat)
{
    int aw=g->trim[1]-g->trim[0]+1;size_t nonfinite=0;*bpm=*sat=0;
    for(int y=active[2]-1;y<active[3];++y)for(int x=active[0]-1;x<active[1];++x){
        if(!good(p,(size_t)y*aw+x)){++*bpm;continue;}
        size_t k=(size_t)(y+g->trim[2]-1)*im[0]->lx+x+g->trim[0]-1;int finite=1,hit=0;
        for(int j=0;j<planes;++j){if(!isfinite(im[j]->data[k]))finite=0;if(im[j]->data[k]>=p->saturation_raw)hit=1;}
        if(!finite)++nonfinite;else if(hit)++*sat;
    }
    return nonfinite;
}
mef_status mef_linearity_measure_pairs(const mef_linearity_pairs_input *p,
    const mef_allocator *allocator,mef_linearity_pairs_result **out)
{
    mef_allocator a={NULL,allocate_default,release_default};mef_status status=MEF_ERR_INPUT;
    mef_linearity_pairs_result *r=NULL;mef_bias_settings g;pixelmap *map=NULL;
    int *first=NULL,*second=NULL,rois=0,pairs=0,w,h,aw,ah;const char *detail=NULL;
    if(!p||!out||*out||!p->configuration||!p->raw||!p->frame||!p->raw[0]||!p->roi||p->rois<1||
       p->frames<2||p->frames>MAX_IMAGE_NUMBER||p->frames%2||p->amplifier_index<0||
       !text(p->identity.detector_id,64)||!text(p->identity.amplifier_id,64)||
       (p->with_mad!=0&&p->with_mad!=1)||p->reject_bits>255||!isfinite(p->saturation_raw)||p->saturation_raw<=0||
       !isfinite(p->pair_time_tolerance)||p->pair_time_tolerance<0||!p->max_rows||
       (p->bpm_flags&&p->bpm_binary)||(!p->bpm_flags&&p->bpm_count)||
       (allocator&&(!allocator->allocate||!allocator->release)))return status;
    if(allocator)a=*allocator;
    if(mef_config_bias_settings(p->configuration,p->configuration_detector,&g)!=MEF_OK)return MEF_ERR_CONFIG;
    w=p->raw[0]->lx;h=p->raw[0]->ly;
    if(w<1||h<1||w>MAX_COLUMN_NUMBER||h>MAX_LINE_NUMBER||w>INT_MAX/h||
       !interval(g.trim,w)||!interval(g.trim+2,h))return status;
    aw=g.trim[1]-g.trim[0]+1;ah=g.trim[3]-g.trim[2]+1;
    if(p->bpm_flags&&p->bpm_count!=(size_t)aw*ah)return status;
    if(p->bpm_binary){const pixelmap *b=p->bpm_binary;
        if(!b->data||b->lx!=aw||b->ly!=ah)return status;
        for(size_t k=0;k<(size_t)aw*ah;++k)if(b->data[k]!=0&&b->data[k]!=1)return status;}
    int has_bias=p->raw_bias[0]!=NULL;
    if ((p->raw_bias[1]!=NULL)!=has_bias || (!has_bias &&
        (p->raw_bias_asset[0] || p->raw_bias_asset[1] || p->raw_bias_hdu[0] || p->raw_bias_hdu[1]))) return status;
    for(int j=0;j<(has_bias?2:0);++j){if(!p->raw_bias[j]||!p->raw_bias[j]->data||p->raw_bias[j]->lx!=w||p->raw_bias[j]->ly!=h||
       !text(p->raw_bias_asset[j],128)||p->raw_bias_hdu[j]<0)return status;}
    if(has_bias && (p->raw_bias[0]==p->raw_bias[1]||!strcmp(p->raw_bias_asset[0],p->raw_bias_asset[1])))return status;
    for(int i=0;i<p->frames;++i){const mef_linearity_frame *f=p->frame+i;
        if(!p->raw[i]||!p->raw[i]->data||p->raw[i]->lx!=w||p->raw[i]->ly!=h||
           !text(f->asset_id,128)||!text(f->pair_id,64)||f->input_index<0||f->hdu<0||!isfinite(f->seconds)||f->seconds<=0)return status;
        for(int j=0;j<(has_bias?2:0);++j)if(p->raw[i]==p->raw_bias[j]||!strcmp(f->asset_id,p->raw_bias_asset[j]))return status;
        int members=0;
        for(int j=0;j<p->frames;++j){if(!text(p->frame[j].pair_id,64))return status;
            if(!strcmp(f->pair_id,p->frame[j].pair_id)){
                ++members;if(!isfinite(p->frame[j].seconds)||fabs(f->seconds-p->frame[j].seconds)>p->pair_time_tolerance)return status;}}
        if(members!=2)return status;
        for(int j=0;j<i;++j)if(f->input_index==p->frame[j].input_index||!strcmp(f->asset_id,p->frame[j].asset_id)||p->raw[i]==p->raw[j])return status;
    }
    for(int i=0;i<p->rois;++i){const detector_roi *q=p->roi+i;
        if(!text(q->roi_id,64)||q->amplifier<0)return status;
        for(int j=0;j<i;++j)if(!strcmp(q->roi_id,p->roi[j].roi_id))return status;
        if(q->amplifier==p->amplifier_index){int zone[]={q->xmin,q->xmax,q->ymin,q->ymax};
            if(!interval(zone,aw)||!interval(zone+2,ah))return status;
            ++rois;}}
    if(!rois||(size_t)rois>SIZE_MAX/(size_t)(p->frames/2))return status;
    size_t rows=(size_t)rois*(size_t)(p->frames/2);
    if(rows>p->max_rows||rows>SIZE_MAX/sizeof(mef_linearity_pair_row))return status;
    status=MEF_ERR_MEMORY;r=a.allocate(a.user,sizeof *r);if(!r)goto done;
    memset(r,0,sizeof *r);r->allocator=a;r->identity=p->identity;r->frames=p->frames;r->rois=rois;r->pairs=p->frames/2;r->rows=rows;
    r->configuration_detector=p->configuration_detector;r->max_rows=p->max_rows;
    r->amplifier_index=p->amplifier_index;r->with_mad=p->with_mad;r->reject_bits=p->reject_bits;r->saturation_raw=p->saturation_raw;
    r->pair_time_tolerance=p->pair_time_tolerance;r->bpm_supplied=p->bpm_flags||p->bpm_binary;r->bpm_binary_supplied=p->bpm_binary!=NULL;
    if(mef_config_clone(p->configuration,&a,&r->configuration,&detail)!=MEF_OK)goto done;
    r->frame=a.allocate(a.user,(size_t)p->frames*sizeof *r->frame);r->bias=a.allocate(a.user,(size_t)rois*sizeof *r->bias);
    r->row=a.allocate(a.user,rows*sizeof *r->row);first=a.allocate(a.user,(size_t)r->pairs*sizeof(int));second=a.allocate(a.user,(size_t)r->pairs*sizeof(int));
    if(!r->frame||!r->bias||!r->row||!first||!second)goto done;
    memcpy(r->frame,p->frame,(size_t)p->frames*sizeof *r->frame);memset(r->bias,0,(size_t)rois*sizeof *r->bias);memset(r->row,0,rows*sizeof *r->row);
    for(int j=0;j<(has_bias?2:0);++j){strcpy(r->raw_bias_asset[j],p->raw_bias_asset[j]);r->raw_bias_hdu[j]=p->raw_bias_hdu[j];}
    for(int i=0;i<p->frames;++i){int seen=0;for(int j=0;j<i;++j)if(!strcmp(p->frame[i].pair_id,p->frame[j].pair_id))seen=1;
        if(!seen){first[pairs]=i;for(int j=i+1;j<p->frames;++j)if(!strcmp(p->frame[i].pair_id,p->frame[j].pair_id))second[pairs]=j;++pairs;}}
    map=pixelmap_new(w,h);if(!map)goto done;
    if(has_bias) selection(p,&g,p->raw_bias,2,map);
    int qindex=0;
    for(int i=0;i<p->rois;++i)if(p->roi[i].amplifier==p->amplifier_index){
        mef_linearity_bias_roi *b=r->bias+qindex++;b->roi=p->roi[i];
        int active[]={b->roi.xmin,b->roi.xmax,b->roi.ymin,b->roi.ymax};
        b->raw_zone[0]=g.trim[0]+active[0]-1;b->raw_zone[1]=g.trim[0]+active[1]-1;
        b->raw_zone[2]=g.trim[2]+active[2]-1;b->raw_zone[3]=g.trim[2]+active[3]-1;
        if(!has_bias) continue;
        size_t nonfinite=exclusions(p,&g,p->raw_bias,2,active,&b->bpm_excluded,&b->saturated);
        if(image_pair_stats_checked(p->raw_bias[0],p->raw_bias[1],map,map,b->raw_zone,p->with_mad,&b->difference)){status=MEF_ERR_COMPUTATION;goto done;}
        if(b->difference.nonfinite_excluded!=nonfinite){status=MEF_ERR_COMPUTATION;goto done;}
        if(b->difference.stdev_available){b->ron_available=1;b->ron_adu=b->difference.stdev/sqrt(2.0);}
        if(b->difference.mad_available){b->ron_mad_available=1;b->ron_mad_adu=1.4826*b->difference.mad/sqrt(2.0);}
    }
    for(int pair=0;pair<pairs;++pair){const image_t *planes[]={p->raw[first[pair]],p->raw[second[pair]],p->raw_bias[0],p->raw_bias[1]};
        selection(p,&g,planes,has_bias?4:2,map);
        for(int q=0;q<rois;++q){mef_linearity_pair_row *row=r->row+(size_t)pair*rois+q;const mef_linearity_bias_roi *b=r->bias+q;
            row->roi=q;row->first=first[pair];row->second=second[pair];
            int active[]={b->roi.xmin,b->roi.xmax,b->roi.ymin,b->roi.ymax};
            exclusions(p,&g,planes,has_bias?4:2,active,&row->bpm_excluded,&row->saturated);
            if(!has_bias) {
                detector_gain_pair_result *m=&row->measurement;
                m->gain_state=DETECTOR_GAIN_PAIR_MISSING_BIAS;
                image_sample_stats difference;
                if(image_getstats_masked_checked(planes[0],map,b->raw_zone,p->with_mad,&m->levels[0]) ||
                   image_getstats_masked_checked(planes[1],map,b->raw_zone,p->with_mad,&m->levels[1]) ||
                   image_pair_stats_checked(planes[0],planes[1],map,map,b->raw_zone,p->with_mad,&difference)) {
                    status=MEF_ERR_COMPUTATION; goto done;
                }
                m->region_pixels=difference.region_pixels; m->valid_pixels=difference.valid_pixels;
                m->nonfinite_excluded=difference.nonfinite_excluded;
                continue;
            }
            if(detector_gain_pair_checked(planes[0],planes[1],planes[2],planes[3],map,b->raw_zone,p->with_mad,&row->measurement)){status=MEF_ERR_COMPUTATION;goto done;}
            const detector_gain_pair_result *v=&row->measurement;
            if(v->signals_available){row->signal_available=1;row->mean_signal=.5*v->signal_first+.5*v->signal_second;}
            if(v->ron_available){row->variance_available=1;row->single_flat_variance=.5*v->flat_variance;row->single_bias_variance=.5*v->bias_variance;}
        }
    }
    *out=r;r=NULL;status=MEF_OK;
done:
    pixelmap_del(map);release(&a,first);release(&a,second);mef_linearity_pairs_destroy(r);return status;
}
