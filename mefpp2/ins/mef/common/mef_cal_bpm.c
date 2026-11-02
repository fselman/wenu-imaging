#include "mef_cal_bpm.h"
#include "mef_bpm_settings.h"
#include "mef_operation_template.h"
#include "mefp_lib.h"
#include "pixelmap_flags8.h"
#include <float.h>

struct mef_bpm_result {
    mef_allocator allocator;
    mef_request *request;
    detector_response_result *response;
    unsigned char *prior_flags, *combined;
    size_t *fit_indices;
    pixelmap *prior_selection, *selection;
    mef_bpm_qc qc;
};
typedef struct {
    mef_context *context;
    const mef_bpm_input *input;
    const mef_bpm_options *options;
    const mef_allocator *allocator;
    const mef_resolved_request_spec *resolved;
    mef_bpm_settings settings;
    mef_bpm_result *pending;
    cube_t *cube;
    pixelmap **samples;
} operation;
static void release(const mef_allocator *a, const void *p) {
    if (p) a->release(a->user,(void *)p);
}
void mef_bpm_result_destroy(mef_bpm_result *r) {
    mef_allocator a;
    if (!r) return;
    a=r->allocator;
    mef_request_destroy(r->request); detector_response_result_del(r->response);
    pixelmap_del(r->prior_selection); pixelmap_del(r->selection);
    release(&a,r->prior_flags); release(&a,r->combined); release(&a,r->qc.frames);
    release(&a,r->fit_indices);
    release(&a,r);
}
const detector_response_result *mef_bpm_result_response(const mef_bpm_result *r) { return r?r->response:NULL; }
const unsigned char *mef_bpm_result_prior_flags(const mef_bpm_result *r) { return r?r->prior_flags:NULL; }
const unsigned char *mef_bpm_result_combined_flags(const mef_bpm_result *r) { return r?r->combined:NULL; }
const pixelmap *mef_bpm_result_selection(const mef_bpm_result *r) { return r?r->selection:NULL; }
const mef_bpm_qc *mef_bpm_result_qc(const mef_bpm_result *r) { return r?&r->qc:NULL; }
const mef_request *mef_bpm_result_request(const mef_bpm_result *r) { return r?r->request:NULL; }
const size_t *mef_bpm_result_fit_indices(const mef_bpm_result *r) { return r?r->fit_indices:NULL; }
static int finite_number(double x) { return x==x && x>=-DBL_MAX && x<=DBL_MAX; }
static int interval(const int *p, int maximum) { return p[0]>=1 && p[1]>=p[0] && p[1]<=maximum; }
static int map_valid(const pixelmap *p, int width, int height) {
    int i;
    if (!p) return 1;
    if (!p->data || p->lx!=width || p->ly!=height) return 0;
    for (i=0;i<width*height;++i) if (p->data[i]!=0 && p->data[i]!=1) return 0;
    return 1;
}
static mef_status validate(void *opaque, mef_error **error) {
    operation *s=opaque;
    const mef_bpm_input *in=s->input;
    const mef_bpm_options *o=s->options;
    const mef_request_spec *rq;
    const mef_bias_settings *g;
    size_t i,j, pixels;
    int width,height,aw,ah,scan,has_bias=0,has_bpm=0;
    (void)error;
    if (!s->context || !in || !o || !in->frames || in->count<2 || in->count>MAX_IMAGE_NUMBER ||
        !in->frames[0] || !in->master_bias || !in->master_bias->data ||
        o->reject_bits>255 || (o->with_mad!=0 && o->with_mad!=1) ||
        (o->saturation_set!=0 && o->saturation_set!=1) ||
        (o->saturation_set && (!finite_number(o->saturation_raw) || o->saturation_raw<=0 ||
         !finite_number(o->upper_fraction) || o->upper_fraction<=0 || o->upper_fraction>1)) ||
        ((o->roi_count!=0)!=(o->rois!=NULL)) || (o->prior_flags && o->prior_binary) ||
        (!o->prior_flags && o->prior_count)) return MEF_ERR_INPUT;
    s->allocator=mef_context_allocator(s->context);
    s->resolved=mef_request_resolved_view(mef_context_request(s->context));
    if (!s->resolved) return MEF_ERR_INPUT;
    rq=&s->resolved->request;
    if (rq->operation!=MEF_OP_CAL_BPM || rq->operation_version!=1 || rq->input_count!=in->count)
        return MEF_ERR_INPUT;
    if (s->resolved->bpm_selection_count!=1) return MEF_ERR_UNSUPPORTED;
    for (i=0;i<in->count;++i)
        if (strcmp(rq->inputs[i].detector_id,rq->inputs[0].detector_id)) return MEF_ERR_UNSUPPORTED;
    for (i=0;i<rq->calibration_count;++i) {
        if (strcmp(rq->calibrations[i].detector_id,rq->inputs[0].detector_id)) return MEF_ERR_UNSUPPORTED;
        if (s->resolved->calibration_roles[i]==MEF_CAL_BIAS) ++has_bias;
        else if (s->resolved->calibration_roles[i]==MEF_CAL_BPM) ++has_bpm;
        else return MEF_ERR_UNSUPPORTED;
    }
    if (has_bias!=1 || has_bpm>1) return MEF_ERR_UNSUPPORTED;
    if ((has_bpm!=0)!=(o->prior_flags!=NULL || o->prior_binary!=NULL)) return MEF_ERR_INPUT;
    if (mef_config_bpm_settings(mef_context_config(s->context),in->configuration_detector,&s->settings)!=MEF_OK)
        return MEF_ERR_CONFIG;
    g=&s->settings.scan;
    if ((s->settings.proportional!=0 && s->settings.proportional!=1) ||
        !finite_number(s->settings.low) || !finite_number(s->settings.high) ||
        s->settings.low>=s->settings.high) return MEF_ERR_CONFIG;
    width=in->frames[0]->lx; height=in->frames[0]->ly;
    if (width<=0 || height<=0 || width>MAX_COLUMN_NUMBER || height>MAX_LINE_NUMBER ||
        width>INT_MAX/height) return MEF_ERR_INPUT;
    if (!interval(g->trim,width) || !interval(g->trim+2,height) ||
        g->trim[0]==g->trim[1] || g->trim[2]==g->trim[3] ||
        (g->use_prescan && !interval(g->prescan,width)) ||
        (g->use_overscan && !interval(g->overscan,width))) return MEF_ERR_CONFIG;
    scan=(g->use_prescan?g->prescan[1]-g->prescan[0]+1:0)+
        (g->use_overscan?g->overscan[1]-g->overscan[0]+1:0);
    if (g->rejection[0]<0 || g->rejection[1]<0 ||
        (scan==0 && (g->rejection[0] || g->rejection[1])) ||
        (scan>0 && (g->rejection[0]>=scan || g->rejection[1]>=scan-g->rejection[0]))) return MEF_ERR_CONFIG;
    aw=g->trim[1]-g->trim[0]+1; ah=g->trim[3]-g->trim[2]+1;
    pixels=(size_t)aw*(size_t)ah;
    if (in->master_bias->lx!=aw || in->master_bias->ly!=ah ||
        (o->prior_flags && o->prior_count!=pixels) || !map_valid(o->prior_binary,aw,ah)) return MEF_ERR_INPUT;
    for (i=0;i<pixels;++i) if (!finite_number(in->master_bias->data[i])) return MEF_ERR_INPUT;
    for (i=0;i<o->roi_count;++i) if (!interval(o->rois[i],aw) || !interval(o->rois[i]+2,ah)) return MEF_ERR_INPUT;
    for (i=0;i<in->count;++i) {
        const image_t *im=in->frames[i];
        if (!im || !im->data || im->lx!=width || im->ly!=height ||
            (o->samples && !map_valid(o->samples[i],aw,ah))) return MEF_ERR_INPUT;
        /* Finite electronic reads are mandatory. Nonfinite active samples
         * remain visible as missing coverage in the qualified response core. */
        for (j=0;j<(size_t)width*(size_t)height;++j) {
            int x=(int)(j%(size_t)width)+1;
            if (!finite_number(im->data[j]) &&
                ((g->use_prescan && x>=g->prescan[0] && x<=g->prescan[1]) ||
                 (g->use_overscan && x>=g->overscan[0] && x<=g->overscan[1]))) return MEF_ERR_INPUT;
        }
    }
    return MEF_OK;
}
static mef_status load(void *opaque, mef_error **error) {
    operation *s=opaque;
    const mef_bpm_input *in=s->input;
    const mef_bpm_options *o=s->options;
    const mef_bias_settings *g=&s->settings.scan;
    mef_bpm_result *r;
    mef_bb work;
    mef_ccd detector;
    image_t *copy,*cropped;
    mef_bpm_frame_qc *q;
    mef_status status;
    size_t i,pixels=(size_t)in->master_bias->lx*(size_t)in->master_bias->ly;
    int zone[4];
    r=s->allocator->allocate(s->allocator->user,sizeof(*r));
    if (!r) return MEF_ERR_MEMORY;
    memset(r,0,sizeof(*r)); r->allocator=*s->allocator; s->pending=r;
    status=mef_request_create_resolved(s->resolved,s->allocator,&r->request,error);
    if (status!=MEF_OK) return status;
    q=s->allocator->allocate(s->allocator->user,in->count*sizeof(*q));
    if (!q) return MEF_ERR_MEMORY;
    memset(q,0,in->count*sizeof(*q)); r->qc.frames=q;
    r->qc.input_count=in->count; r->qc.reject_bits=o->reject_bits;
    r->qc.bias_applied=1; r->qc.provisional_numerical_only=1;
    r->qc.saturation_set=o->saturation_set;
    r->qc.saturation_raw=o->saturation_set?o->saturation_raw:0;
    r->qc.upper_fraction=o->saturation_set?o->upper_fraction:0;
    r->qc.prior=o->prior_flags?MEF_BPM_PRIOR_FLAGS8:o->prior_binary?MEF_BPM_PRIOR_BINARY:MEF_BPM_PRIOR_OMITTED;
    if (o->prior_flags) {
        r->prior_flags=s->allocator->allocate(s->allocator->user,pixels);
        if (!r->prior_flags) return MEF_ERR_MEMORY;
        memcpy(r->prior_flags,o->prior_flags,pixels);
        if (pixelmap_flags8_selection_checked(r->prior_flags,in->master_bias->lx,
            in->master_bias->ly,o->reject_bits,&r->prior_selection)!=0) return MEF_ERR_COMPUTATION;
    } else if (o->prior_binary) {
        r->prior_selection=pixelmap_copy((pixelmap *)o->prior_binary);
        if (!r->prior_selection) return MEF_ERR_COMPUTATION;
        pixelmap_updatecount(r->prior_selection);
    }
    memset(&work,0,sizeof(work)); memset(&detector,0,sizeof(detector));
    memcpy(detector.prescan_x,g->prescan,sizeof(g->prescan));
    memcpy(detector.overscan_x,g->overscan,sizeof(g->overscan));
    memcpy(detector.trimreg,g->trim,sizeof(g->trim));
    work.ccd=&detector; work.xtnum=1; work.nxts=1;
    work.use_prescan=g->use_prescan; work.use_overscan=g->use_overscan;
    memcpy(work.scanrej,g->rejection,sizeof(g->rejection));
    s->cube=cube_new(in->frames[0]->lx,in->frames[0]->ly,(int)in->count);
    if (!s->cube) return MEF_ERR_COMPUTATION;
    for (i=0;i<in->count;++i) {
        zone[2]=g->trim[2]; zone[3]=g->trim[3];
        if (g->use_prescan) {
            zone[0]=g->prescan[0]; zone[1]=g->prescan[1];
            if (image_getstats_masked_checked(in->frames[i],NULL,zone,o->with_mad,&q[i].prescan)!=0) return MEF_ERR_COMPUTATION;
        }
        if (g->use_overscan) {
            zone[0]=g->overscan[0]; zone[1]=g->overscan[1];
            if (image_getstats_masked_checked(in->frames[i],NULL,zone,o->with_mad,&q[i].overscan)!=0) return MEF_ERR_COMPUTATION;
        }
        copy=image_copy((image_t *)in->frames[i]);
        if (!copy) return MEF_ERR_COMPUTATION;
        if (g->use_prescan || g->use_overscan)
            cropped=mef_overscan_correction(copy,&work,(int)i,"bpm");
        else cropped=image_getvig(copy,g->trim[0],g->trim[2],g->trim[1],g->trim[3]);
        image_del(copy);
        if (!cropped) return MEF_ERR_COMPUTATION;
        s->cube->plane[i]=cropped;
    }
    s->cube->lx=in->master_bias->lx; s->cube->ly=in->master_bias->ly;
    if (cube_sub_im(s->cube,(image_t *)in->master_bias)!=0) return MEF_ERR_COMPUTATION;
    for (i=0;i<in->count;++i)
        if (image_getstats_masked_checked(s->cube->plane[i],r->prior_selection,NULL,o->with_mad,&q[i].active_corrected)!=0)
            return MEF_ERR_COMPUTATION;
    return MEF_OK;
}
static mef_status calculate(void *opaque, mef_error **error) {
    operation *s=opaque;
    mef_bpm_result *r=s->pending;
    detector_response_options o;
    size_t i,j,k,n=(size_t)s->cube->lx*(size_t)s->cube->ly;
    int used=0,x,y,eligible;
    cube_t view;
    image_t **planes=NULL;
    const pixelmap **maps=NULL;
    pixelvalue *fractions=NULL;
    mef_bpm_frame_qc *q=(mef_bpm_frame_qc *)r->qc.frames;
    const mef_bias_settings *g=&s->settings.scan;
    mef_status status=MEF_ERR_MEMORY;
    (void)error;
    memset(&o,0,sizeof(o)); o.proportional=s->settings.proportional;
    o.low=s->settings.low; o.high=s->settings.high;
    o.reference=r->prior_selection;
    o.rois=s->options->rois; o.roi_count=s->options->roi_count;
    r->fit_indices=s->allocator->allocate(s->allocator->user,s->input->count*sizeof(size_t));
    planes=calloc(s->input->count,sizeof(*planes));
    maps=calloc(s->input->count,sizeof(*maps));
    fractions=malloc(n*sizeof(*fractions));
    s->samples=calloc(s->input->count,sizeof(*s->samples));
    if (!r->fit_indices || !planes || !maps || !fractions || !s->samples) goto done;
    for (i=0;i<s->input->count;++i) {
        s->samples[i]=pixelmap_new(s->cube->lx,s->cube->ly);
        if (!s->samples[i]) goto done;
        for (j=0;j<n;++j) {
            double value=s->cube->plane[i]->data[j],fraction=0;
            x=(int)(j%(size_t)s->cube->lx); y=(int)(j/(size_t)s->cube->lx);
            eligible=1;
            if (s->options->samples && s->options->samples[i] && !s->options->samples[i]->data[j]) {
                eligible=0; ++q[i].sample_excluded;
            } else if (!finite_number(value)) { eligible=0; ++q[i].nonfinite; }
            else if (s->options->saturation_set) {
                size_t raw=(size_t)(y+g->trim[2]-1)*(size_t)s->input->frames[i]->lx+(size_t)(x+g->trim[0]-1);
                double original=s->input->frames[i]->data[raw];
                double usable=s->options->saturation_raw-original+value;
                if (original>=s->options->saturation_raw) { eligible=0; ++q[i].saturated; }
                else if (!(usable>0) || !finite_number(usable) ||
                    value>=s->options->upper_fraction*usable) { eligible=0; ++q[i].margin_excluded; }
                else fraction=value/usable;
            }
            s->samples[i]->data[j]=(binpix)eligible;
            if (!eligible || (r->prior_selection && !r->prior_selection->data[j])) continue;
            eligible=o.roi_count==0;
            for (k=0;k<o.roi_count && !eligible;++k) {
                const int *z=o.rois[k];
                eligible=x+1>=z[0] && x+1<=z[1] && y+1>=z[2] && y+1<=z[3];
            }
            if (eligible) fractions[q[i].reference_samples++]=(pixelvalue)fraction;
        }
        pixelmap_updatecount(s->samples[i]);
        if (!q[i].reference_samples) continue;
        if (s->options->saturation_set)
            q[i].reference_fraction_median=median_pixelvalue(fractions,(int)q[i].reference_samples);
        q[i].included_in_fit=1;
        r->fit_indices[used]=i; planes[used]=s->cube->plane[i]; maps[used]=s->samples[i]; ++used;
    }
    status=MEF_ERR_COMPUTATION;
    if (used<2) goto done;
    memset(&view,0,sizeof(view)); view.lx=s->cube->lx; view.ly=s->cube->ly; view.np=used; view.plane=planes;
    o.samples=maps;
    if (cube_response_checked(&view,&o,&r->response)!=0) goto done;
    free(planes); free(maps); free(fractions); planes=NULL; maps=NULL; fractions=NULL;
    if (r->qc.prior!=MEF_BPM_PRIOR_BINARY) {
        r->combined=s->allocator->allocate(s->allocator->user,n);
        if (!r->combined) return MEF_ERR_MEMORY;
        for (i=0;i<n;++i) r->combined[i]=(unsigned char)(r->response->reasons[i] |
            (r->prior_flags?r->prior_flags[i]:0));
    }
    if (pixelmap_flags8_selection_checked(r->combined?r->combined:r->response->reasons,
        s->cube->lx,s->cube->ly,s->options->reject_bits,&r->selection)!=0) return MEF_ERR_COMPUTATION;
    for (i=0;i<n;++i) if (!r->response->valid->data[i] ||
        (r->prior_selection && !r->prior_selection->data[i])) r->selection->data[i]=0;
    pixelmap_updatecount(r->selection);
    return MEF_OK;
done:
    free(planes); free(maps); free(fractions); return status;
}
static void cleanup(void *opaque) {
    operation *s=opaque;
    size_t i;
    if (s->samples) for (i=0;i<s->input->count;++i) pixelmap_del(s->samples[i]);
    free(s->samples); s->samples=NULL;
    cube_del(s->cube); s->cube=NULL;
}
mef_status mef_cal_bpm(mef_context *context, const mef_bpm_input *input,
    const mef_bpm_options *options, mef_bpm_result **out, mef_error **error) {
    operation s;
    mef_status status;
    static const mef_operation_steps steps={validate,load,calculate,NULL,cleanup};
    if (!out || *out || (error && *error)) return MEF_ERR_INPUT;
    memset(&s,0,sizeof(s)); s.context=context; s.input=input; s.options=options;
    status=mef_operation_run(&steps,&s,error);
    if (status==MEF_OK) { *out=s.pending; return MEF_OK; }
    mef_bpm_result_destroy(s.pending);
    if (error && !*error) (void)mef_error_create(status,"BPM numerical service: invalid/unsupported request, geometry or computation",s.allocator,error);
    return status;
}
