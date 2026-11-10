/* Read only the explicit transport bindings before numerical services run.
 * The service parsers retain their own complete grammar/geometry validation.
 */
#define _POSIX_C_SOURCE 200809L
#include "mef_bpm_linearity_recipe.h"
#include <stdio.h>
#include <string.h>

typedef struct { char *path, *hdu; } flat_binding;

static int fields(char *line, char **values, int capacity)
{
    int count=0;
    char *next=line;
    while (next && count<capacity) {
        char *tab=strchr(next,'\t');
        values[count++]=next;
        if (tab) { *tab=0; next=tab+1; } else next=NULL;
    }
    return next?-1:count;
}

static int source_path(const mef_bpm_linearity_recipe *recipe, const char *path, int calibration)
{
    return mef_bpm_linearity_has_dependency(recipe,path) &&
        mef_bpm_linearity_below(path,calibration?recipe->calibration:recipe->raw);
}

static int header_matches(const mef_bpm_linearity_detector *detector, const char *key, const char *value)
{
    static const char *keys[]={"detector","slot","readout","bin_x","bin_y","mask_encoding","good_value","mask_registry","reject_bits"};
    static const char *options[]={"--detector-id","--config-detector","--readout-id","--bin-x","--bin-y","--bpm-encoding","--bpm-good-value","--bpm-registry","--reject-bits"};
    size_t i;
    if (!strcmp(key,"with_mad")) {
        const char *mad=mef_bpm_linearity_option(detector,"--mad");
        return mad && !strcmp(value,!strcmp(mad,"yes")?"1":"0");
    }
    for (i=0; i<sizeof(keys)/sizeof(*keys); ++i) {
        if (!strcmp(key,keys[i])) {
            const char *bound=mef_bpm_linearity_option(detector,options[i]);
            return !bound || !strcmp(value,bound);
        }
    }
    return 1;
}

int mef_bpm_linearity_bindings_admit(mef_bpm_linearity_recipe *recipe,
    const mef_bpm_linearity_detector *detector)
{
    flat_binding flats[64]={{0}};
    char *line=NULL, *values[8];
    size_t capacity=0, count=0, index=0;
    ssize_t length;
    FILE *stream=NULL;
    int okay=0, n;
    const char *control_keys[3]={"--config","--flats","--roi-file"};
    const int preparation_files[6]={1,2,3,4,8,15};
    const char *prior=mef_bpm_linearity_option(detector,"--input-bpm");
    const char *prior_hdu=mef_bpm_linearity_option(detector,"--bpm-hdu");
    const char *bias_hdu=mef_bpm_linearity_option(detector,"--bias-hdu");
    size_t i;
    const char *preparation_hash=NULL, *bpm_hash=NULL;
    for (i=0; i<recipe->dependency_count; ++i) {
        if (!strcmp(recipe->dependencies[i].path,detector->preparation_argv[1])) preparation_hash=recipe->dependencies[i].sha256;
        if (mef_bpm_linearity_option(detector,"--config") &&
            !strcmp(recipe->dependencies[i].path,mef_bpm_linearity_option(detector,"--config"))) bpm_hash=recipe->dependencies[i].sha256;
    }
    if (!preparation_hash || !bpm_hash || strcmp(preparation_hash,bpm_hash)) goto done;
    if (!prior || !prior_hdu || !bias_hdu || strcmp(bias_hdu,detector->preparation_argv[6])) goto done;
    for (i=0; i<6; ++i) {
        if (!mef_bpm_linearity_has_dependency(recipe,detector->preparation_argv[preparation_files[i]])) goto done;
    }
    for (i=0; i<3; ++i) {
        const char *path=mef_bpm_linearity_option(detector,control_keys[i]);
        if (!path || !mef_bpm_linearity_has_dependency(recipe,path)) goto done;
    }
    stream=fopen(detector->preparation_argv[4],"rb");
    if (!stream) goto done;
    while ((length=getline(&line,&capacity,stream))>=0) {
        if (length<1 || length>32768 || line[length-1]!='\n' || memchr(line,0,(size_t)length)) goto done;
        line[length-1]=0; n=fields(line,values,8);
        if (n<2 || (n==2 && !header_matches(detector,values[0],values[1]))) goto done;
        if (!strcmp(values[0],"flat") || !strcmp(values[0],"bias")) {
            if (!source_path(recipe,values[1],0)) goto done;
            if (!strcmp(values[0],"flat")) {
                if (n!=6 || count==64) goto done;
                flats[count].path=strdup(values[1]); flats[count].hdu=strdup(values[2]);
                ++count;
                if (!flats[count-1].path || !flats[count-1].hdu) goto done;
            }
        } else if (!strcmp(values[0],"bpm")) {
            if (n!=4 || !source_path(recipe,values[1],1) || strcmp(values[1],prior) ||
                strcmp(values[2],prior_hdu)) goto done;
        }
    }
    if (ferror(stream) || !count) goto done;
    if (fclose(stream)) { stream=NULL; goto done; } stream=NULL;
    stream=fopen(mef_bpm_linearity_option(detector,"--flats"),"rb");
    if (!stream) goto done;
    while ((length=getline(&line,&capacity,stream))>=0) {
        if (length<1 || length>32768 || line[length-1]!='\n' || memchr(line,0,(size_t)length)) goto done;
        line[length-1]=0; n=fields(line,values,8);
        if (n!=3 || index>=count || strcmp(values[0],flats[index].path) ||
            strcmp(values[1],flats[index].hdu)) goto done;
        ++index;
    }
    if (ferror(stream) || index!=count) goto done;
    if (fclose(stream)) { stream=NULL; goto done; } stream=NULL;
    stream=fopen(detector->preparation_argv[8],"rb");
    if (!stream || getline(&line,&capacity,stream)<0 ||
        strcmp(line,"input_index\thdu\tasset\tpath\taccepted\n")) goto done;
    while ((length=getline(&line,&capacity,stream))>=0) {
        if (length<1 || length>32768 || line[length-1]!='\n' || memchr(line,0,(size_t)length)) goto done;
        line[length-1]=0; n=fields(line,values,8);
        if (n!=5 || !source_path(recipe,values[3],0)) goto done;
    }
    okay=!ferror(stream);
done:
    if (stream && fclose(stream)) okay=0;
    for (i=0; i<count; ++i) { free(flats[i].path); free(flats[i].hdu); }
    free(line);
    return okay;
}
