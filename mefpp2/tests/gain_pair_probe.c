/* Synthetic arithmetic/ROI/error/lifecycle controls, no FITS or real data. */
#include "eclipse.h"
#include "mef_operation_template.h"
#include <assert.h>
#include <float.h>
#include <string.h>

static void near_value(double got, double expected)
{
    if (!(fabs(got-expected) < 1e-8*(1+fabs(expected))))
        fprintf(stderr,"comparison got=%.17g expected=%.17g\n",got,expected);
    assert(fabs(got-expected) < 1e-8*(1+fabs(expected)));
}
static void fill_pair(image_t **im)
{
    const double a[4][4]={{101,99,100,100},{99,101,100,100},
                           {11,9,10,10},{10,10,10,10}};
    int k,p;
    for (k=0;k<4;++k) for (p=0;p<4;++p) im[k]->data[p]=(pixelvalue)a[k][p];
}
static int measure(image_t **im, pixelmap *map, const int *roi, int mad,
                   detector_gain_pair_result *r)
{
    return detector_gain_pair_checked(im[0],im[1],im[2],im[3],map,roi,mad,r);
}
typedef struct {
    image_t **sequence; size_t first,second;
    image_t *b1,*b2;
    detector_gain_pair_result value;
    int cleaned,calculated,failed,published;
} lifecycle;
static mef_status validate_pair(void *v,mef_error **e)
{
    lifecycle *s=v; (void)e;
    return s->first!=s->second?MEF_OK:MEF_ERR_INPUT;
}
static mef_status load_pair(void *v,mef_error **e) { (void)v;(void)e;return MEF_OK; }
static mef_status calculate_pair(void *v,mef_error **e)
{
    lifecycle *s=v; (void)e;
    if (s->failed) return MEF_ERR_COMPUTATION;
    if (detector_gain_pair_checked(s->sequence[s->first],s->sequence[s->second],
            s->b1,s->b2,NULL,NULL,0,&s->value)) return MEF_ERR_COMPUTATION;
    s->calculated=1; return MEF_OK;
}
static mef_status publish_pair(void *v,mef_error **e)
{
    lifecycle *s=v; (void)e;
    assert(s->calculated); s->published=1; return MEF_OK;
}
static void cleanup_pair(void *v) { lifecycle *s=v; ++s->cleaned; }
int main(void)
{
    image_t *im[4],*sequence[3];
    pixelmap *m=pixelmap_new(4,1);
    detector_gain_pair_result r,sentinel;
    pixelvalue saved[4][4];
    int k,p,roi[4]={1,2,1,1},bad[4]={0,2,1,1};
    lifecycle state;
    mef_operation_steps steps={validate_pair,load_pair,calculate_pair,publish_pair,cleanup_pair};
    for(k=0;k<4;++k) { im[k]=image_new(4,1); assert(im[k]); }
    assert(m); fill_pair(im);
    for(k=0;k<4;++k) memcpy(saved[k],im[k]->data,sizeof(saved[k]));
    /* Independently derived four-pixel answers: variances 8/3 and 2/3. */
    assert(measure(im,NULL,NULL,1,&r)==0 && r.gain_state==DETECTOR_GAIN_PAIR_AVAILABLE);
    near_value(r.flat_variance,8.0/3); near_value(r.bias_variance,2.0/3);
    near_value(r.gain_e_per_adu,90); near_value(r.ron_adu,sqrt(1.0/3));
    near_value(r.ron_mad_adu,1.4826*.5/sqrt(2.0));
    assert(r.valid_pixels==4 && r.ron_available && r.ron_mad_available);
    near_value(r.signal_first,90); near_value(r.fractional_mismatch,0);
    /* A curved synthetic variance sequence retains three distinct pair gains.
     * Independent analytic values: mean signal=100*k-10,
     * full difference variance=8*k*k/3, raw-bias variance=2/3. */
    for(k=1;k<=3;++k) {
        fill_pair(im);
        for(p=0;p<4;++p) {
            im[0]->data[p]=(pixelvalue)(100*k+(p==0?k:p==1?-k:0));
            im[1]->data[p]=(pixelvalue)(100*k+(p==0?-k:p==1?k:0));
        }
        assert(measure(im,NULL,NULL,0,&r)==0);
        near_value(r.flat_variance,8.0*k*k/3);
        near_value(r.gain_e_per_adu,6.0*(100*k-10)/(8*k*k-2));
        /* Half-difference variance: mu/(V-V0) == full pair gain. */
        near_value(r.gain_e_per_adu,(100.0*k-10)/(.5*r.photon_variance));
    }
    fill_pair(im);
    /* First two pixels: flat variance 8, bias variance 2, gain 180/6=30. */
    assert(measure(im,m,roi,0,&r)==0); near_value(r.gain_e_per_adu,30);
    assert(r.valid_pixels==2 && !r.ron_mad_available);
    /* Explicit BPM and a nonfinite value in B1 affect ALL six populations. */
    m->data[0]=0; im[2]->data[3]=NAN;
    assert(measure(im,m,NULL,1,&r)==0);
    assert(r.region_pixels==4 && r.valid_pixels==2 && r.bpm_excluded==1 &&
           r.nonfinite_excluded==1);
    for(k=0;k<4;++k) assert(r.levels[k].valid_pixels==2);
    assert(r.flat_difference.valid_pixels==2 && r.bias_difference.valid_pixels==2);
    near_value(r.levels[0].mean,99.5); near_value(r.levels[2].mean,9.5);
    /* Mask takes precedence; one/no sample stays explicitly unavailable. */
    m->data[3]=0; assert(measure(im,m,NULL,0,&r)==0 && r.bpm_excluded==2 &&
                            r.nonfinite_excluded==0);
    m->data[2]=0; assert(measure(im,m,NULL,1,&r)==0 &&
        r.gain_state==DETECTOR_GAIN_PAIR_TOO_FEW_PIXELS && !r.ron_available);
    m->data[1]=0; assert(measure(im,m,NULL,0,&r)==0 && !r.signals_available);
    memset(m->data,1,4); fill_pair(im);
    /* Nonzero pair median reverses with order; centering preserves noise. */
    im[0]->data[0]+=4; im[0]->data[1]+=4; im[0]->data[2]+=4; im[0]->data[3]+=4;
    assert(measure(im,NULL,NULL,1,&r)==0);
    near_value(r.flat_difference.median,4); near_value(r.flat_variance,8.0/3);
    near_value(r.flat_difference.mad,1); near_value(r.fractional_mismatch,4.0/92);
    assert(detector_gain_pair_checked(im[1],im[0],im[3],im[2],NULL,NULL,1,&sentinel)==0);
    near_value(sentinel.gain_e_per_adu,r.gain_e_per_adu);
    near_value(sentinel.ron_adu,r.ron_adu); near_value(sentinel.flat_difference.median,-4);
    /* Nonpositive signal/variance never becomes a zero-valued valid gain. */
    fill_pair(im); memcpy(im[1]->data,im[0]->data,sizeof(saved[0]));
    assert(measure(im,NULL,NULL,0,&r)==0 &&
           r.gain_state==DETECTOR_GAIN_PAIR_NONPOSITIVE_VARIANCE && r.ron_available);
    fill_pair(im); for(k=0;k<2;++k) for(p=0;p<4;++p) im[k]->data[p]-=100;
    assert(measure(im,NULL,NULL,0,&r)==0 &&
           r.gain_state==DETECTOR_GAIN_PAIR_NONPOSITIVE_SIGNAL);
    /* Invalid geometry, options, map and output alias fail atomically. */
    fill_pair(im); memset(&sentinel,0x5a,sizeof(sentinel)); r=sentinel;
    assert(measure(im,m,bad,0,&r)==-1 && !memcmp(&r,&sentinel,sizeof(r)));
    assert(measure(im,m,NULL,2,&r)==-1 && !memcmp(&r,&sentinel,sizeof(r)));
    m->data[0]=2; assert(measure(im,m,NULL,0,&r)==-1 && !memcmp(&r,&sentinel,sizeof(r)));
    m->data[0]=1; im[3]->lx=3;
    assert(measure(im,NULL,NULL,0,&r)==-1 && !memcmp(&r,&sentinel,sizeof(r))); im[3]->lx=4;
    assert(measure(im,NULL,NULL,0,(detector_gain_pair_result*)im[0]->data)==-1);
    /* Finite operands whose float difference overflows fail, not silently drop. */
    im[0]->data[0]=FLT_MAX; im[1]->data[0]=-FLT_MAX;
    assert(measure(im,NULL,NULL,0,&r)==-1 && !memcmp(&r,&sentinel,sizeof(r)));
    fill_pair(im);
    /* Existing operation lifecycle with explicitly nonconsecutive indices. */
    sequence[0]=im[0]; sequence[1]=im[2]; sequence[2]=im[1];
    memset(&state,0,sizeof(state)); state.sequence=sequence; state.first=0; state.second=2;
    state.b1=im[2]; state.b2=im[3];
    assert(mef_operation_run(&steps,&state,NULL)==MEF_OK);
    assert(state.cleaned==1 && state.published); near_value(state.value.gain_e_per_adu,90);
    state.failed=1; state.cleaned=state.published=state.calculated=0;
    assert(mef_operation_run(&steps,&state,NULL)==MEF_ERR_COMPUTATION &&
           state.cleaned==1 && !state.published);
    /* No borrowed pixels or masks were changed by successful/failed calls. */
    for(k=0;k<4;++k) { assert(!memcmp(saved[k],im[k]->data,sizeof(saved[k]))); image_del(im[k]); }
    for(p=0;p<4;++p) assert(m->data[p]==1);
    pixelmap_del(m);
    puts("PASS: paired gain/RON arithmetic, common BPM/finite ROI, raw origins, unavailability, alias/overflow and operation lifecycle");
    return 0;
}

