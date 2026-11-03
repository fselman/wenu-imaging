#include "mef_linearity_pairs_export.h"
#include <locale.h>
#include <math.h>
#include <string.h>

typedef struct { FILE *stream; int first, bad_value; } writer;
static void separator(writer *w)
{ if(!w->first)fputc('\t',w->stream);w->first=0; }
static void text(writer *w,const char *s)
{
    separator(w);
    for(const unsigned char *p=(const unsigned char *)s;*p;++p){
        switch(*p){
        case '\\':fputs("\\\\",w->stream);break;
        case '\t':fputs("\\t",w->stream);break;
        case '\n':fputs("\\n",w->stream);break;
        case '\r':fputs("\\r",w->stream);break;
        default:if(*p<32||*p==127)fprintf(w->stream,"\\x%02X",(unsigned int)*p);
                else fputc(*p,w->stream);
        }
    }
}
static void integer(writer *w,int value){separator(w);fprintf(w->stream,"%d",value);}
static void count(writer *w,size_t value){separator(w);fprintf(w->stream,"%zu",value);}
static void number(writer *w,int available,double value)
{
    separator(w);if(!available)return;
    if(!isfinite(value)){w->bad_value=1;return;}
    fprintf(w->stream,"%.17g",value);
}
static void end(writer *w){fputc('\n',w->stream);w->first=1;}
static int valid(const mef_linearity_pairs_result *r)
{
    struct lconv *locale=localeconv();
    if(!r||!r->frame||!r->bias||!r->row||r->frames<2||r->rois<1||!r->rows||
       !locale||strcmp(locale->decimal_point,"."))return 0;
    for(size_t i=0;i<r->rows;++i){const mef_linearity_pair_row *row=r->row+i;
        if(row->roi<0||row->roi>=r->rois||row->first<0||row->first>=r->frames||
           row->second<0||row->second>=r->frames)return 0;}
    return 1;
}
static void common(writer *w,const mef_linearity_pairs_result *r,int roi)
{
    integer(w,1);text(w,r->identity.detector_id);text(w,r->identity.amplifier_id);
    count(w,r->configuration_detector);text(w,r->bias[roi].roi.roi_id);
    const detector_roi *a=&r->bias[roi].roi;
    integer(w,a->xmin);integer(w,a->xmax);integer(w,a->ymin);integer(w,a->ymax);
    for(int j=0;j<4;++j)integer(w,r->bias[roi].raw_zone[j]);
    for(int j=0;j<2;++j){text(w,r->raw_bias_asset[j]);integer(w,r->raw_bias_hdu[j]);}
    integer(w,r->bpm_supplied);integer(w,r->bpm_binary_supplied);count(w,r->reject_bits);
    number(w,1,r->saturation_raw);number(w,1,r->pair_time_tolerance);
}
#define COMMON "schema_version\tdetector\tamplifier\tconfiguration_detector\troi\tactive_xmin\tactive_xmax\tactive_ymin\tactive_ymax\traw_xmin\traw_xmax\traw_ymin\traw_ymax\tbias1_asset\tbias1_hdu\tbias2_asset\tbias2_hdu\tbpm_supplied\tbpm_binary_supplied\treject_bits\tsaturation_raw_adu\tpair_time_tolerance_s"
static mef_status finish(writer *w)
{
    int failed=fflush(w->stream);
    if(failed||ferror(w->stream))return MEF_ERR_IO;
    return w->bad_value?MEF_ERR_COMPUTATION:MEF_OK;
}
mef_status mef_linearity_pairs_write_tsv(FILE *stream,const mef_linearity_pairs_result *r)
{
    if(!stream||!valid(r))return MEF_ERR_INPUT;
    writer w={stream,1,0};
    fputs(COMMON "\tpair_id\tfirst_asset\tfirst_input_index\tfirst_hdu\tfirst_seconds\tsecond_asset\tsecond_input_index\tsecond_hdu\tsecond_seconds\tregion_pixels\tbpm_excluded\tnonfinite_excluded\tsaturated\tvalid_pixels\tlevels_available\tflat1_mean_adu\tflat2_mean_adu\tbias1_mean_adu\tbias2_mean_adu\tsignal_available\tsignal1_adu\tsignal2_adu\tmean_signal_adu\tvariance_available\tflat_difference_variance_adu2\tbias_difference_variance_adu2\tsingle_flat_variance_adu2\tsingle_bias_variance_adu2\tmismatch_available\tfractional_mismatch\tmatched_ron_available\tmatched_ron_adu\tmatched_ron_mad_available\tmatched_ron_mad_adu\tgain_state\tpoint_gain_e_per_adu\n",stream);
    static const char *states[]={"arithmetic_available","too_few_pixels","nonpositive_signal","nonpositive_variance"};
    for(size_t i=0;i<r->rows;++i){const mef_linearity_pair_row *row=r->row+i;
        const detector_gain_pair_result *m=&row->measurement;
        common(&w,r,row->roi);text(&w,r->frame[row->first].pair_id);
        const int indices[]={row->first,row->second};
        for(int j=0;j<2;++j){const mef_linearity_frame *f=r->frame+indices[j];
            text(&w,f->asset_id);integer(&w,f->input_index);integer(&w,f->hdu);number(&w,1,f->seconds);}
        count(&w,m->region_pixels);count(&w,row->bpm_excluded);count(&w,m->nonfinite_excluded);
        count(&w,row->saturated);count(&w,m->valid_pixels);
        integer(&w,m->levels[0].level_available);
        for(int j=0;j<4;++j)number(&w,m->levels[j].level_available,m->levels[j].mean);
        integer(&w,row->signal_available);number(&w,m->signals_available,m->signal_first);
        number(&w,m->signals_available,m->signal_second);number(&w,row->signal_available,row->mean_signal);
        integer(&w,row->variance_available);number(&w,row->variance_available,m->flat_variance);
        number(&w,row->variance_available,m->bias_variance);number(&w,row->variance_available,row->single_flat_variance);
        number(&w,row->variance_available,row->single_bias_variance);
        integer(&w,m->mismatch_available);number(&w,m->mismatch_available,m->fractional_mismatch);
        integer(&w,m->ron_available);number(&w,m->ron_available,m->ron_adu);
        integer(&w,m->ron_mad_available);number(&w,m->ron_mad_available,m->ron_mad_adu);
        int state=(int)m->gain_state;
        text(&w,state>=0&&state<4?states[state]:"invalid_state");
        if(state<0||state>=4)w.bad_value=1;
        number(&w,m->gain_state==DETECTOR_GAIN_PAIR_AVAILABLE,m->gain_e_per_adu);end(&w);
    }
    return finish(&w);
}
mef_status mef_linearity_bias_write_tsv(FILE *stream,const mef_linearity_pairs_result *r)
{
    if(!stream||!valid(r))return MEF_ERR_INPUT;
    writer w={stream,1,0};
    fputs(COMMON "\tregion_pixels\tbpm_excluded\tnonfinite_excluded\tsaturated\tvalid_pixels\tlevel_available\tdifference_mean_adu\tdifference_median_adu\tstdev_available\tdifference_stdev_adu\tmad_available\tdifference_mad_adu\tron_available\tron_adu\tron_mad_available\tron_mad_adu\n",stream);
    for(int i=0;i<r->rois;++i){const mef_linearity_bias_roi *b=r->bias+i;const image_sample_stats *s=&b->difference;
        common(&w,r,i);count(&w,s->region_pixels);count(&w,b->bpm_excluded);count(&w,s->nonfinite_excluded);
        count(&w,b->saturated);count(&w,s->valid_pixels);integer(&w,s->level_available);
        number(&w,s->level_available,s->mean);number(&w,s->level_available,s->median);
        integer(&w,s->stdev_available);number(&w,s->stdev_available,s->stdev);
        integer(&w,s->mad_available);number(&w,s->mad_available,s->mad);
        integer(&w,b->ron_available);number(&w,b->ron_available,b->ron_adu);
        integer(&w,b->ron_mad_available);number(&w,b->ron_mad_available,b->ron_mad_adu);end(&w);
    }
    return finish(&w);
}
