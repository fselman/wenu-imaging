/* Shared final BPM plane mapping; reads headers only, never pixel arrays. */
#define _POSIX_C_SOURCE 200809L
#include "mef_mef_assemble.h"
#include "qfits.h"
#include <stdio.h>
#include <stdlib.h>
#undef free

char *mef_bpm_assembly_plane_map(const char *path,const mef_bpm_assembly_detector *d,size_t n)
{
    char *text=NULL;size_t length=0,i,hdu=0;int pass,source,okay=1;
    FILE *f=open_memstream(&text,&length);
    if(!f) return NULL;
    for(pass=0;pass<2 && okay;++pass)for(i=0;i<n && okay;++i) {
        int count=qfits_query_n_ext((char *)d[i].path)+1;
        for(source=pass?1:0;source<(pass?count:1);++source) {
            qfits_header *h=qfits_header_readext((char *)path,(int)++hdu);
            char *name=h?qfits_header_getstr(h,"EXTNAME"):NULL;
            if(!name || fprintf(f,"%s\t%d\t%lu\t%s\n",d[i].detector_id,source,
                (unsigned long)hdu,source?qfits_pretty_string(name):"BPM")<0) okay=0;
            qfits_header_destroy(h);
        }
    }
    if(fclose(f) || !okay){free(text);text=NULL;}
    return text;
}
