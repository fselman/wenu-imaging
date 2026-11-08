#include "mef_product_qc.h"
#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

static int fail(char *message, size_t size, const char *text)
{ if (message != NULL && size) snprintf(message,size,"%s",text); return -1; }
static int text(const char *s)
{
    size_t i;
    if (s == NULL || !*s || strlen(s) > 1048576) return 0;
    for (i=0;s[i];++i) if ((unsigned char)s[i] < 32 && s[i] != '\n' && s[i] != '\t') return 0;
    return 1;
}
static int digest(const char *s, size_t n)
{
    size_t i;
    if (s == NULL || strlen(s) != n) return 0;
    for (i=0;i<n;++i) if (!((s[i]>='0' && s[i]<='9') || (s[i]>='a' && s[i]<='f'))) return 0;
    return 1;
}
static int timestamp(const char *s)
{
    size_t i; int year,month,day,hour,minute,second,days;
    static const int length[]={31,28,31,30,31,30,31,31,30,31,30,31};
    if (s == NULL || strlen(s) != 24) return 0;
    for(i=0;i<24;++i) {
        if(i==4||i==7) { if(s[i]!='-') return 0; }
        else if(i==10) { if(s[i]!='T') return 0; }
        else if(i==13||i==16) { if(s[i]!=':') return 0; }
        else if(i==19) { if(s[i]!='.') return 0; }
        else if(i==23) { if(s[i]!='Z') return 0; }
        else if(!isdigit((unsigned char)s[i])) return 0;
    }
    year=(s[0]-'0')*1000+(s[1]-'0')*100+(s[2]-'0')*10+s[3]-'0';
    month=(s[5]-'0')*10+s[6]-'0'; day=(s[8]-'0')*10+s[9]-'0';
    hour=(s[11]-'0')*10+s[12]-'0'; minute=(s[14]-'0')*10+s[15]-'0'; second=(s[17]-'0')*10+s[18]-'0';
    if(year<1||month<1||month>12||day<1||hour>23||minute>59||second>60) return 0;
    days=length[month-1]; if(month==2 && year%4==0 && (year%100!=0 || year%400==0)) ++days;
    return day<=days;
}
static int known(const mef_product_qc *p,const char *id)
{
    size_t i;
    if(!text(id)) return 0;
    if(!strcmp(id,p->id)) return 1;
    for(i=0;i<p->input_count;++i) if(!strcmp(id,p->inputs[i].id)) return 1;
    for(i=0;i<p->calibration_count;++i) if(!strcmp(id,p->calibrations[i].id)) return 1;
    return 0;
}
static int measurements(const mef_product_qc *p,const mef_qc_measurement *m,size_t n,const char *detector_id)
{
    size_t i,j;
    if(m==NULL||n==0||n>100000) return 0;
    for(i=0;i<n;++i) {
        if(!text(m[i].name)||!text(m[i].unit)||!text(m[i].stage)||!text(m[i].coordinates)||!text(m[i].mask_policy)||!text(m[i].clipping)||!text(m[i].nonfinite_policy)||
            (m[i].vector!=0 && m[i].vector!=1)||m[i].source_count==0||m[i].source_count>p->input_count+p->calibration_count+1||
            m[i].source_ids==NULL) return 0;
        for(j=0;j<i;++j) if(!strcmp(m[i].name,m[j].name)) return 0;
        for(j=0;j<m[i].source_count;++j) {
            size_t k;
            if(!known(p,m[i].source_ids[j])) return 0;
            for(k=0;k<j;++k) if(!strcmp(m[i].source_ids[j],m[i].source_ids[k])) return 0;
        }
        if(strcmp(m[i].mask_policy,"omitted") && strcmp(m[i].mask_policy,"applied") &&
            strcmp(m[i].mask_policy,"not_applicable") && strcmp(m[i].mask_policy,"unmasked_diagnostic")) return 0;
        if(!strcmp(m[i].mask_policy,"applied") && m[i].mask_id==NULL) return 0;
        if((!strcmp(m[i].mask_policy,"omitted") || !strcmp(m[i].mask_policy,"not_applicable")) && m[i].mask_id!=NULL) return 0;
        if(m[i].mask_id!=NULL) {
            int found=0;
            for(j=0;j<p->calibration_count;++j) if(!strcmp(m[i].mask_id,p->calibrations[j].id) && !strcmp(p->calibrations[j].role,"bpm")) {
                size_t k;
                for(k=0;k<p->calibrations[j].binding_count;++k)
                    if(!strcmp(detector_id,p->calibrations[j].bindings[k].detector_id)) found=1;
            }
            if(!found) return 0;
        }
        if(m[i].bounds[0]||m[i].bounds[1]||m[i].bounds[2]||m[i].bounds[3]) {
            if(m[i].bounds[0]<1||m[i].bounds[1]<m[i].bounds[0]||m[i].bounds[2]<1||m[i].bounds[3]<m[i].bounds[2]) return 0;
        }
        if(m[i].state==MEF_QC_MEASURED) {
            if(!text(m[i].method)||m[i].reason!=NULL||m[i].sample_count==0||m[i].values==NULL||
                m[i].value_count==0||m[i].value_count>10000000||(!m[i].vector && m[i].value_count!=1)) return 0;
            for(j=0;j<m[i].value_count;++j) {
                if(!isfinite(m[i].values[j])) return 0;
                if(!strcmp(m[i].unit,"count") && (m[i].values[j]<0||m[i].values[j]>9007199254740991.0||floor(m[i].values[j])!=m[i].values[j])) return 0;
            }
        } else if(m[i].state==MEF_QC_UNAVAILABLE||m[i].state==MEF_QC_INVALID) {
            if(!text(m[i].reason)||m[i].values!=NULL||m[i].value_count!=0) return 0;
        } else return 0;
    }
    return 1;
}
static int header_metadata(const mef_product_qc *p)
{
    size_t i,j;
    if((p->recipe_config_path==NULL)!=(p->recipe_config_snapshot==NULL))return 0;
    if(p->recipe_config_path&&(!text(p->recipe_config_path)||p->recipe_config_path[0]!='/'||
        !text(p->recipe_config_snapshot)))return 0;
    if(p->header_card_count>16*(p->detector_count+1)||
        (p->header_card_count&&(!p->header_cards||!p->recipe_config_path)))return 0;
    for(i=0;i<p->header_card_count;++i) {
        const mef_qc_fits_card *c=p->header_cards+i;int found=0;
        if(!memchr(c->keyword,0,81)||!*c->keyword||!memchr(c->fits_value,0,81)||
            !memchr(c->value,0,81)||!memchr(c->comment,0,81)||!memchr(c->card,0,81)||
            !c->type||(c->present!=0&&c->present!=1))return 0;
        if(c->detector_id) {
            for(j=0;j<p->detector_count;++j)
                if(p->detectors[j].id&&!strcmp(c->detector_id,p->detectors[j].id)&&c->hdu==p->detectors[j].output_hdu)found=1;
            if(!found)return 0;
        } else if(c->hdu!=0)return 0;
        if(!c->present) {
            if(strcmp(c->type,"missing")||*c->card||*c->fits_value)return 0;
        } else {
            if(strlen(c->card)!=80||(!strcmp(c->type,"real")&&!isfinite(c->real))||
                (!strcmp(c->type,"boolean")&&c->boolean!=0&&c->boolean!=1))return 0;
            if(strcmp(c->type,"undefined")&&strcmp(c->type,"string")&&strcmp(c->type,"integer")&&
                strcmp(c->type,"real")&&strcmp(c->type,"boolean")&&strcmp(c->type,"fits_literal"))return 0;
        }
        for(j=0;j<i;++j)if(c->hdu==p->header_cards[j].hdu&&
            !strcmp(c->keyword,p->header_cards[j].keyword))return 0;
    }
    return 1;
}
int mef_product_qc_validate(const mef_product_qc *p,char *message,size_t size)
{
    size_t i,j,k,n;
    if(p==NULL||!text(p->id)||!text(p->fits_path)||p->fits_path[0]!='/'||
        !text(p->log_path)||p->log_path[0]!='/'||!text(p->assessment_id)||!text(p->recipe_name)||
        !timestamp(p->recipe_start)||p->recipe_version==0||p->product_sequence==0||
        !text(p->producer_name)||!text(p->producer_version)||!digest(p->source_revision,40)||
        !text(p->configuration_id)||!text(p->configuration_snapshot)||
        p->inputs==NULL||p->input_count==0||p->input_count>100000||
        p->detectors==NULL||p->detector_count==0||p->detector_count>4096||
        (p->sha256!=NULL && !digest(p->sha256,64))||p->calibration_count>4096||
        (p->calibration_count && p->calibrations==NULL)) return fail(message,size,"Invalid product identity, execution or configuration");
    if (p->bpm_registry) {
        if (!*p->bpm_registry || strlen(p->bpm_registry)>32) return fail(message,size,"Invalid BPM registry");
        for (i=0;p->bpm_registry[i];++i)
            if (!isalnum((unsigned char)p->bpm_registry[i]) && p->bpm_registry[i]!='_' && p->bpm_registry[i]!='-')
                return fail(message,size,"Invalid BPM registry");
    }
    if(!header_metadata(p))return fail(message,size,"Invalid selected FITS provenance");
    n=strlen(p->fits_path);
    if(n<=5||strcmp(p->fits_path+n-5,".fits")) return fail(message,size,"Product must retain a .fits basename");
    {
        const char *a=strrchr(p->fits_path,'/'), *b=strrchr(p->log_path,'/');
        if(a==NULL||b==NULL||a-p->fits_path!=b-p->log_path||
            strncmp(p->fits_path,p->log_path,(size_t)(a-p->fits_path)))
            return fail(message,size,"Product log must use the selected product directory");
    }
    for(i=0;i<p->input_count;++i) {
        if(!text(p->inputs[i].id)||!text(p->inputs[i].path)||p->inputs[i].path[0]!='/'||
            !strcmp(p->inputs[i].id,p->id)||(p->inputs[i].sha256!=NULL && !digest(p->inputs[i].sha256,64)))
            return fail(message,size,"Invalid embedded input identity");
        for(j=0;j<i;++j) if(!strcmp(p->inputs[i].id,p->inputs[j].id)||
            p->inputs[i].original_index==p->inputs[j].original_index)
            return fail(message,size,"Duplicate embedded input identity or original index");
    }
    for(i=0;i<p->calibration_count;++i) {
        const mef_qc_calibration_record *c=p->calibrations+i;
        if(!text(c->id)||!text(c->path)||c->path[0]!='/'||!text(c->role)||!strcmp(c->id,p->id)||
            (c->sha256!=NULL && !digest(c->sha256,64))||(c->qc_path!=NULL && !text(c->qc_path))||c->bindings==NULL||c->binding_count==0||
            c->binding_count>p->detector_count) return fail(message,size,"Invalid calibration identity or bindings");
        for(j=0;j<p->input_count;++j) if(!strcmp(c->id,p->inputs[j].id)) return fail(message,size,"Calibration/input ID collision");
        for(j=0;j<i;++j) if(!strcmp(c->id,p->calibrations[j].id)) return fail(message,size,"Duplicate calibration ID");
        for(j=0;j<c->binding_count;++j) {
            int found=0;
            if(!text(c->bindings[j].detector_id)||c->bindings[j].source_hdu<0) return fail(message,size,"Invalid calibration selector");
            for(k=0;k<j;++k) if(!strcmp(c->bindings[j].detector_id,c->bindings[k].detector_id)) return fail(message,size,"Duplicate calibration detector");
            for(k=0;k<p->detector_count;++k)
                if(p->detectors[k].id!=NULL && !strcmp(c->bindings[j].detector_id,p->detectors[k].id)) found=1;
            if(!found) return fail(message,size,"Unknown calibration detector");
        }
    }
    for(i=0;i<p->detector_count;++i) {
        const mef_qc_detector_record *d=p->detectors+i;
        if(d->median_even_handling && strcmp(d->median_even_handling,"average") && strcmp(d->median_even_handling,"lower"))
            return fail(message,size,"Invalid bias median even handling");
        if(!text(d->id)||!text(d->amplifier)||!text(d->readout_id)||d->output_hdu<1||(size_t)d->output_hdu>p->detector_count||d->bin_x<1||d->bin_y<1||
            d->inputs==NULL||d->input_count!=p->input_count||!measurements(p,d->measurements,d->measurement_count,d->id))
            return fail(message,size,"Invalid product detector coverage or QC");
        for(j=0;j<i;++j) if(!strcmp(d->id,p->detectors[j].id)||d->output_hdu==p->detectors[j].output_hdu)
            return fail(message,size,"Duplicate detector identity or output HDU");
        for(j=0;j<p->input_count;++j) {
            const mef_qc_input_binding *b=d->inputs+j;
            if(!text(b->input_id)||strcmp(b->input_id,p->inputs[j].id)||b->source_hdu<0||
                (b->accepted!=0 && b->accepted!=1)||(b->accepted && b->rejection_reason!=NULL)||
                (!b->accepted && !text(b->rejection_reason))||!measurements(p,b->measurements,b->measurement_count,d->id))
                return fail(message,size,"Invalid ordered input binding, participation or QC");
            for(k=0;k<b->measurement_count;++k) {
                size_t q;
                for(q=0;q<b->measurements[k].source_count;++q)
                    if(strcmp(b->measurements[k].source_ids[q],b->input_id))
                        return fail(message,size,"Input QC must identify its own embedded input");
            }
        }
    }
    if(message!=NULL && size) message[0]='\0';
    return 0;
}
