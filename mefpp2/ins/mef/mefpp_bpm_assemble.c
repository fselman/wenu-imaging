/* Join completed detector artifacts. No raw input discovery or processing. */
#define _POSIX_C_SOURCE 200809L
#include "mef_bpm_assembly_qc.h"
#include "qfits.h"
#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#undef malloc
#undef calloc
#undef strdup
#undef free
#ifndef MEFPP_CANDIDATE_REVISION
#define MEFPP_CANDIDATE_REVISION "unknown"
#endif
#define MAX_DETECTORS 4096

static char *read_recipe(const char *path)
{
    FILE *f=fopen(path,"rb");
    struct stat st;
    char *text=NULL;
    if(!f) return NULL;
    if(fstat(fileno(f),&st) || !S_ISREG(st.st_mode) || st.st_size<=0 || st.st_size>1024*1024) goto done;
    text=calloc((size_t)st.st_size+1,1);
    if(text && (fread(text,1,(size_t)st.st_size,f)!=(size_t)st.st_size || memchr(text,0,(size_t)st.st_size))) {
        free(text);text=NULL;
    }
done:
    if(fclose(f)){free(text);text=NULL;}
    return text;
}
static int load_manifest(FILE *f,mef_bpm_assembly_detector *d,const char **qc,size_t *count)
{
    char *line=NULL;size_t capacity=0;
    ssize_t length;int okay=0;
    while((length=getline(&line,&capacity,f))>=0) {
        char *fields[4],*cursor=line,*end;
        unsigned long slot;
        size_t k;
        if(*count==MAX_DETECTORS || length>16384 || line[length-1]!='\n' || memchr(line,0,(size_t)length)) goto done;
        line[length-1]=0;
        for(k=0;k<4;++k) {
            fields[k]=cursor;
            if(cursor) {char *tab=strchr(cursor,'\t');if(tab){*tab=0;cursor=tab+1;}else cursor=NULL;}
            if(!fields[k] || !*fields[k] || strchr(fields[k],'\r')) goto done;
        }
        if(cursor)goto done;
        errno=0;slot=strtoul(fields[1],&end,10);
        if(errno || *end || fields[1][0]<'0' || fields[1][0]>'9' || slot>INT_MAX-1 ||
            fields[2][0]!='/' || fields[3][0]!='/') goto done;
        d[*count]=(mef_bpm_assembly_detector){strdup(fields[2]),strdup(fields[0]),(size_t)slot};
        qc[*count]=strdup(fields[3]);
        ++*count;
        if(!d[*count-1].path || !d[*count-1].detector_id || !qc[*count-1]) goto done;
    }
    okay=*count>0 && !ferror(f);
done:
    free(line);
    return okay;
}
static char *plane_map(const char *path,const mef_bpm_assembly_detector *d,size_t n)
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
int main(int argc,char **argv)
{
    mef_bpm_assembly_detector *detectors=NULL;
    const char **sidecars=NULL;
    char *recipe=NULL,*planes=NULL,*asdf=NULL,message[512]="Invalid BPM assembly command";
    FILE *manifest=NULL,*log=NULL;
    size_t count=0,i,n;
    struct stat st;
    int status=1;
    /* MANIFEST FINAL.fits REFERENCE-ID LOG START CHILD-REVISION RECIPE.toml */
    if(argc!=8 || argv[2][0]!='/' || argv[4][0]!='/' || argv[7][0]!='/' ||
        strlen(argv[5])!=24 || strlen(argv[6])!=40 || strspn(argv[6],"0123456789abcdef")!=40) goto done;
    n=strlen(argv[2]);
    if(n<6 || strcmp(argv[2]+n-5,".fits"))goto done;
    asdf=malloc(n+1);if(!asdf)goto done;
    snprintf(asdf,n+1,"%.*s.asdf",(int)(n-5),argv[2]);
    if(lstat(argv[2],&st)==0 || errno!=ENOENT || lstat(asdf,&st)==0 || errno!=ENOENT)goto done;
    detectors=calloc(MAX_DETECTORS,sizeof(*detectors));sidecars=calloc(MAX_DETECTORS,sizeof(*sidecars));
    manifest=fopen(argv[1],"rb");recipe=read_recipe(argv[7]);
    if(!detectors || !sidecars || !manifest || !recipe || !load_manifest(manifest,detectors,sidecars,&count))goto done;
    if(fclose(manifest)){manifest=NULL;goto done;}manifest=NULL;
    log=fopen(argv[4],"wx");if(!log)goto done;
    if(fprintf(log,"BPM_MEF_ASSEMBLY_START %lu\n",(unsigned long)count)<0 || fflush(log))goto done;
    if(mef_bpm_mef_assemble(argv[2],argv[3],detectors,count,message,sizeof(message)))goto done;
    planes=plane_map(argv[2],detectors,count);
    if(!planes){snprintf(message,sizeof(message),"Cannot inspect final BPM image-plane map");goto done;}
    {
        mef_bpm_assembly_qc request={.fits_path=argv[2],.asdf_path=asdf,.log_path=argv[4],
            .created_at=argv[5],.source_revision=MEFPP_CANDIDATE_REVISION,.detector_source_revision=argv[6],
            .recipe_path=argv[7],.recipe_snapshot=recipe,.detectors=detectors,.sidecars=sidecars,
            .detector_count=count,.plane_map=planes};
        if(mef_bpm_assembly_qc_write(&request,message,sizeof(message)))goto done;
    }
    if(fprintf(log,"BPM_MEF_ASSEMBLY_COMPLETE\n")<0 || fflush(log) || fsync(fileno(log)))goto done;
    if(fclose(log)){log=NULL;goto done;}log=NULL;
    puts("BPM_MEF_ASSEMBLY_COMPLETE");status=0;
done:
    if(status)fprintf(stderr,"%s; retain completed artifacts and logs\n",message);
    if(log)fclose(log);
    if(manifest)fclose(manifest);
    for(i=0;i<count;++i){free((void *)detectors[i].path);free((void *)detectors[i].detector_id);free((void *)sidecars[i]);}
    free(detectors);free(sidecars);free(recipe);free(planes);free(asdf);
    qfits_cache_purge();
    return status;
}
