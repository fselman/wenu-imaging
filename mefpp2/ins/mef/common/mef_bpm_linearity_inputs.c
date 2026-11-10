#define _POSIX_C_SOURCE 200809L
#define _XOPEN_SOURCE 700
#include "mef_bpm_linearity.h"
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
#include <sys/resource.h>
#include <unistd.h>

static int empty_directory(const char *path)
{
    struct dirent *entry;
    DIR *directory=opendir(path);
    int okay=1;
    if (!directory) return 0;
    while ((entry=readdir(directory))!=NULL) {
        if (strcmp(entry->d_name,".") && strcmp(entry->d_name,"..")) okay=0;
    }
    if (closedir(directory)) okay=0;
    return okay;
}

static int absent(const char *path)
{
    struct stat st;
    return lstat(path,&st)<0 && errno==ENOENT;
}

static int output_path(const mef_bpm_linearity *recipe, const char *path)
{
    return mef_bpm_linearity_below(path,recipe->output) ||
        mef_bpm_linearity_below(path,recipe->work) || mef_bpm_linearity_below(path,recipe->logs);
}

const char *mef_bpm_linearity_option(const mef_bpm_linearity_detector *detector, const char *key)
{
    const char *result=NULL;
    int i;
    for (i=3; i+1<detector->bpm_argc; i+=2) {
        if (!strcmp(detector->bpm_argv[i],key)) {
            if (result) return NULL;
            result=detector->bpm_argv[i+1];
        }
    }
    return result;
}

static int policy_matches(const mef_bpm_linearity_detector *detector, toml_datum_t policy)
{
    const char *fields[3]={"upper_fraction","minimum_span_fraction","maximum_pair_difference"};
    const char *options[3]={"--upper-fraction","--minimum-span","--maximum-pair-difference"};
    const char *acquisition=mef_bpm_linearity_string(policy,"acquisition");
    const char *mode=mef_bpm_linearity_string(policy,"output_mode");
    size_t i;
    if (!acquisition || !mode || !mef_bpm_linearity_option(detector,"--acquisition") || !mef_bpm_linearity_option(detector,"--output-mode") ||
        strcmp(acquisition,mef_bpm_linearity_option(detector,"--acquisition")) || strcmp(mode,mef_bpm_linearity_option(detector,"--output-mode"))) return 0;
    for (i=0; i<3; ++i) {
        toml_datum_t value=toml_get(policy,fields[i]);
        const char *text=mef_bpm_linearity_option(detector,options[i]);
        char *end;
        double bound, wanted;
        if (!text || (value.type!=TOML_FP64 && value.type!=TOML_INT64)) return 0;
        wanted=value.type==TOML_FP64?value.u.fp64:(double)value.u.int64;
        errno=0; bound=strtod(text,&end);
        if (errno || end==text || *end || !isfinite(bound) || bound!=wanted) return 0;
    }
    return 1;
}

int mef_bpm_linearity_has_dependency(const mef_bpm_linearity *recipe, const char *path)
{
    size_t i;
    for (i=0; i<recipe->dependency_count; ++i) {
        if (!strcmp(recipe->dependencies[i].path,path)) return 1;
    }
    return 0;
}

int mef_bpm_linearity_admit(mef_bpm_linearity *recipe)
{
    toml_datum_t declared=toml_get(recipe->document.toptab,"detectors");
    toml_datum_t directories=toml_get(recipe->bindings.toptab,"directories");
    toml_datum_t copies=toml_get(recipe->bindings.toptab,"copies");
    size_t i,j;
    int found_reference=0;
    recipe->diagnostic="Native bindings, fresh destinations or input fingerprints differ";
    errno=0;
    if (getpriority(PRIO_PROCESS,0)<10 || errno || !empty_directory(recipe->output) ||
        !absent(recipe->run->paths.fits) || !absent(recipe->run->paths.asdf) ||
        !absent(recipe->run->paths.log) || !absent(recipe->receipt) ||
        declared.type!=TOML_ARRAY || (size_t)declared.u.arr.size!=recipe->detector_count ||
        directories.type!=TOML_ARRAY || directories.u.arr.size>32768 ||
        copies.type!=TOML_ARRAY || copies.u.arr.size>65536 ||
        !mef_bpm_linearity_has_dependency(recipe,recipe->recipe_path) ||
        !mef_bpm_linearity_has_dependency(recipe,recipe->project_path)) return 0;
    if (!mef_bpm_linearity_hash(recipe->bindings_path,recipe->bindings_sha256) ||
        stat(recipe->bindings_path,&recipe->dependencies[recipe->dependency_count-1].identity)) return 0;
    for (i=0; i<recipe->detector_count; ++i) {
        mef_bpm_linearity_detector *d=recipe->detectors+i;
        const char *id=mef_bpm_linearity_string(declared.u.arr.elem[i],"detector_id");
        const char *bias=mef_bpm_linearity_option(d,"--master-bias"), *prior=mef_bpm_linearity_option(d,"--input-bpm");
        const char *fits=mef_bpm_linearity_option(d,"--output"), *asdf=mef_bpm_linearity_option(d,"--native-asdf");
        const char *bound_id=mef_bpm_linearity_option(d,"--detector-id");
        char slot[32];
        snprintf(slot,sizeof(slot),"%lu",(unsigned long)d->configuration_detector);
        if (!policy_matches(d,toml_get(recipe->document.toptab,"bpm")) ||
            !id || strcmp(id,d->detector_id) || !bound_id || strcmp(bound_id,id) ||
            !mef_bpm_linearity_option(d,"--config-detector") || strcmp(mef_bpm_linearity_option(d,"--config-detector"),slot) ||
            d->preparation_argc!=16 || strcmp(d->preparation_argv[10],"--native-asdf") ||
            strcmp(d->preparation_argv[14],"--context") || strcmp(d->preparation_argv[11],d->prepared) ||
            strcmp(d->preparation_argv[13],recipe->run->paths.log) ||
            !bias || !prior || !mef_bpm_linearity_has_dependency(recipe,bias) || !mef_bpm_linearity_has_dependency(recipe,prior) ||
            strcmp(bias,d->preparation_argv[5]) || !fits || strcmp(fits,d->fits) || !asdf || strcmp(asdf,d->asdf) ||
            !mef_bpm_linearity_below(bias,recipe->calibration) ||
            !mef_bpm_linearity_below(prior,recipe->calibration) ||
            !mef_bpm_linearity_below(d->fits,recipe->output) ||
            !mef_bpm_linearity_below(d->asdf,recipe->output) ||
            !mef_bpm_linearity_below(d->prepared,recipe->output) ||
            !absent(d->fits) || !absent(d->asdf) || !absent(d->prepared)) return 0;
        if (!mef_bpm_linearity_bindings_admit(recipe,d)) return 0;
        for (j=0; j<i; ++j) {
            if (!strcmp(d->detector_id,recipe->detectors[j].detector_id) ||
                d->configuration_detector==recipe->detectors[j].configuration_detector) return 0;
        }
        if (!strcmp(d->detector_id,recipe->reference_detector)) found_reference=1;
    }
    if (!found_reference) return 0;
    for (i=0; i<(size_t)directories.u.arr.size; ++i) {
        toml_datum_t value=directories.u.arr.elem[i];
        char *path=value.type==TOML_STRING?mef_bpm_linearity_expand(recipe,value.u.s):NULL;
        int okay=path && output_path(recipe,path) && absent(path);
        free(path);
        if (!okay) return 0;
    }
    for (i=0; i<(size_t)copies.u.arr.size; ++i) {
        toml_datum_t row=copies.u.arr.elem[i];
        const char *source=mef_bpm_linearity_string(row,"source");
        const char *target=mef_bpm_linearity_string(row,"target");
        if (!source || !target || !mef_bpm_linearity_has_dependency(recipe,source) ||
            !(mef_bpm_linearity_below(source,recipe->orchestration) ||
              mef_bpm_linearity_below(source,recipe->work)) ||
            !mef_bpm_linearity_below(target,recipe->output) || !absent(target)) return 0;
    }
    for (i=0; i<recipe->dependency_count; ++i) {
        for (j=0; j<i; ++j) {
            if (!strcmp(recipe->dependencies[i].path,recipe->dependencies[j].path)) return 0;
        }
        if (i+1<recipe->dependency_count && !mef_bpm_linearity_dependency_check(recipe->dependencies+i,1)) {
            snprintf(recipe->run->message,sizeof(recipe->run->message),"Input SHA256 differs: %s",recipe->dependencies[i].path);
            return 0;
        }
    }
    return 1;
}

static int make_directory(const mef_bpm_linearity *recipe, const char *path)
{
    char *prefix=strdup(path), canonical[MEF_PRODUCT_PATH_SIZE];
    size_t i, n=strlen(path);
    int okay=prefix!=NULL;
    if (!prefix) return 0;
    for (i=strlen(recipe->reduced)+1; i<=n && okay; ++i) {
        if (prefix[i]=='/' || prefix[i]==0) {
            char saved=prefix[i]; prefix[i]=0;
            if (mkdir(prefix,0700) && errno!=EEXIST) okay=0;
            if (okay && (!realpath(prefix,canonical) || strcmp(prefix,canonical) ||
                !mef_bpm_linearity_directory(prefix))) okay=0;
            prefix[i]=saved;
        }
    }
    free(prefix);
    return okay;
}

static int copy_metadata(const char *source, const char *target)
{
    unsigned char buffer[65536];
    size_t n;
    FILE *input=fopen(source,"rb"), *output=NULL;
    int okay=0, fd=-1;
    if (!input) return 0;
    fd=open(target,O_WRONLY|O_CREAT|O_EXCL,0600);
    if (fd<0) goto done;
    output=fdopen(fd,"wb");
    if (!output) { close(fd); goto done; }
    while ((n=fread(buffer,1,sizeof(buffer),input))!=0) {
        if (fwrite(buffer,1,n,output)!=n) goto done;
    }
    if (!ferror(input) && !fflush(output) && !fsync(fileno(output)) && !fchmod(fileno(output),0444)) okay=1;
done:
    if (fclose(input)) okay=0;
    if (output && fclose(output)) okay=0;
    return okay;
}

int mef_bpm_linearity_begin(mef_bpm_linearity *recipe)
{
    toml_datum_t directories=toml_get(recipe->bindings.toptab,"directories");
    toml_datum_t copies=toml_get(recipe->bindings.toptab,"copies");
    size_t i;
    recipe->diagnostic="Cannot create native recipe workspace or frozen metadata copies";
    if (!mef_recipe_run_begin(recipe->run,recipe->recipe_path,recipe->bindings_path,NULL,0)) return 0;
    for (i=0; i<(size_t)directories.u.arr.size; ++i) {
        char *path=mef_bpm_linearity_expand(recipe,directories.u.arr.elem[i].u.s);
        int okay=path && make_directory(recipe,path);
        free(path);
        if (!okay) return 0;
    }
    for (i=0; i<(size_t)copies.u.arr.size; ++i) {
        toml_datum_t row=copies.u.arr.elem[i];
        if (!copy_metadata(mef_bpm_linearity_string(row,"source"),
            mef_bpm_linearity_string(row,"target"))) return 0;
    }
    return mef_bpm_linearity_observe(recipe);
}
