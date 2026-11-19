/* Test-only writer boundary: inspect the typed native request without libasdf.
 * This does not write ASDF and is never linked into a production executable. */
#include "mef_product_qc.h"
#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <sys/stat.h>
int mef_product_qc_write(const char *path,const mef_product_qc *p,char *message,size_t size)
{
    if(mef_product_qc_validate(p,message,size)) return -1;
    char target[4096];
    if(!p->table_name || p->primary_image || p->detector_count!=1 || p->detectors[0].output_hdu!=0 ||
        snprintf(target,sizeof(target),"%s.metadata.tsv",path)>=(int)sizeof(target)) return -1;
    FILE *f=fopen(target,"wx");
    if(!f) return -1;
    fputs("name\tstate\tvalue\tsource\tcount\tx1\tx2\ty1\ty2\n",f);
    const mef_qc_detector_record *d=p->detectors;
    for(size_t i=0;i<d->measurement_count;++i) {
        const mef_qc_measurement *q=d->measurements+i;
        fprintf(f,"%s\t%d\t",q->name,q->state);
        if(q->state==MEF_QC_MEASURED) fprintf(f,"%.17g",q->values[0]);
        fprintf(f,"\t%s\t%llu\t%d\t%d\t%d\t%d\n",q->source_ids[0],(unsigned long long)q->sample_count,
            q->bounds[0],q->bounds[1],q->bounds[2],q->bounds[3]);
    }
    int okay=!ferror(f);if(fclose(f)) okay=0;
    if(!okay) return -1;
    if(snprintf(target,sizeof(target),"%s.evidence",path)>=(int)sizeof(target) || mkdir(target,0700)) return -1;
    for(size_t i=0;i<p->evidence_count;++i) {
        const mef_qc_text_evidence *e=p->evidence+i;
        char filename[4096];
        if(snprintf(filename,sizeof(filename),"%s/%s",target,e->name)>=(int)sizeof(filename)) return -1;
        char *slash=strrchr(filename,'/');
        if(strchr(e->name,'/')) {
            *slash=0;if(mkdir(filename,0700) && errno!=EEXIST) return -1;*slash='/';
        }
        f=fopen(filename,"wx");if(!f) return -1;
        okay=fputs(e->text,f)>=0;if(fclose(f)) okay=0;
        if(!okay) return -1;
    }
    return 0;
}
