/* Shared private file metadata checks, extracted unchanged from BPM files. */
#ifndef MEF_FILE_METADATA_INTERNAL_H
#define MEF_FILE_METADATA_INTERNAL_H
#include "mef_layout.h"
#include "qfits.h"
#include <ctype.h>
#include <float.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>
static int finite_number(double v) { return v==v && v>=-DBL_MAX && v<=DBL_MAX; }
static int binding_matches(const mef_layout_map *map,const char *detector,const mef_image_ref *ref,
    const char *unit,size_t slot) {
    const mef_bound_detector *d;
    size_t entries=0;
    if(!map || !ref || !detector) return 0;
    d=mef_layout_find(map,detector);
    (void)mef_layout_map_view(map,&entries);
    return d && entries==1 && d->selection==MEF_OUTPUT_SELECTED &&
        !strcmp(ref->detector_id,detector) && !strcmp(d->unit,unit) && d->configuration_detector==slot &&
        d->image.hdu_index==ref->hdu_index && !strcmp(mef_layout_map_path(map),ref->resolved_path) &&
        (!ref->extname || (d->image.has_extname && d->image.has_extver &&
         !strcmp(ref->extname,d->image.extname) && ref->extver==d->image.extver));
}
static int exposure(const char *path,int hdu,const char *key,double *out) {
    qfits_header *h=qfits_header_readext((char *)path,hdu);
    char *text,*end,buffer[81],name[81],value[81],comment[81],line[81];
    double number;
    int i,occurrences=0;
    if(!h) return 0;
    /* Reject ambiguous metadata instead of taking the first duplicate card. */
    for(i=0;i<h->n;++i) {
        if(qfits_header_getitem(h,i,name,value,comment,line)!=0) { qfits_header_destroy(h); return 0; }
        if(!strcmp(name,key)) ++occurrences;
    }
    text=qfits_header_getstr(h,key);
    if(occurrences!=1 || !text || strlen(text)>80) { qfits_header_destroy(h); return 0; }
    strcpy(buffer,text); qfits_header_destroy(h);
    for(i=0;buffer[i];++i) if(buffer[i]=='D' || buffer[i]=='d') buffer[i]='E';
    errno=0; number=strtod(buffer,&end);
    if(end==buffer || errno || !finite_number(number) || number<=0) return 0;
    while(isspace((unsigned char)*end)) ++end;
    if(*end) return 0;
    *out=number; return 1;
}
#endif
