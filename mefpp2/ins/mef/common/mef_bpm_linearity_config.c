#define _POSIX_C_SOURCE 200809L
#define _XOPEN_SOURCE 700
#include "mef_bpm_linearity.h"
#include "qfits.h"
#include <dirent.h>
#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

const char *mef_bpm_linearity_string(toml_datum_t table, const char *key)
{
    toml_datum_t value=toml_get(table,key);
    return value.type==TOML_STRING && value.u.str.len>0 &&
        strlen(value.u.s)==(size_t)value.u.str.len ? value.u.s : NULL;
}

static int keys(toml_datum_t table, const char *allowed)
{
    int i;
    if (table.type!=TOML_TABLE) return 0;
    for (i=0; i<table.u.tab.size; ++i) {
        char key[128];
        if (strlen(table.u.tab.key[i])!=(size_t)table.u.tab.len[i] ||
            snprintf(key,sizeof(key),"|%s|",table.u.tab.key[i])>=(int)sizeof(key) ||
            !strstr(allowed,key)) return 0;
    }
    return 1;
}

static int clean_path(const char *path)
{
    size_t n=path?strlen(path):0;
    return n>1 && path[0]=='/' && path[n-1]!='/' && !strstr(path,"//") &&
        !strstr(path,"/../") && !strstr(path,"/./") &&
        !(n>=3 && !strcmp(path+n-3,"/..")) && !(n>=2 && !strcmp(path+n-2,"/.")) &&
        !strchr(path,'\n') && !strchr(path,'\r') && !strchr(path,'\t');
}

int mef_bpm_linearity_below(const char *path, const char *root)
{
    size_t n=strlen(root);
    return clean_path(path) && !strncmp(path,root,n) && path[n]=='/';
}

int mef_bpm_linearity_directory(const char *path)
{
    struct stat st;
    return path && !stat(path,&st) && S_ISDIR(st.st_mode);
}

static char *resolved(const char *base, const char *path)
{
    char joined[MEF_PRODUCT_PATH_SIZE], canonical[MEF_PRODUCT_PATH_SIZE];
    if (!path || snprintf(joined,sizeof(joined),"%s%s%s",path[0]=='/'?"":base,
            path[0]=='/'?"":"/",path)>=(int)sizeof(joined) || !realpath(joined,canonical)) return NULL;
    return strdup(canonical);
}

char *mef_bpm_linearity_expand(const mef_bpm_linearity *recipe, const char *text)
{
    char buffer[MEF_PRODUCT_PATH_SIZE], seconds[21];
    size_t used=0;
    if (!text) return NULL;
    snprintf(seconds,sizeof(seconds),"%.19sZ",recipe->run->recipe_start);
    while (*text) {
        const char *value=NULL;
        size_t token=0, n;
        if (!strncmp(text,"${START}",8)) { value=recipe->run->recipe_start; token=8; }
        if (!strncmp(text,"${START_SECONDS}",16)) { value=seconds; token=16; }
        if (value) {
            n=strlen(value);
            if (used+n>=sizeof(buffer)) return NULL;
            memcpy(buffer+used,value,n); used+=n; text+=token;
        } else {
            if (used+1>=sizeof(buffer)) return NULL;
            buffer[used++]=*text++;
        }
    }
    buffer[used]=0;
    return strdup(buffer);
}

static char **arguments(mef_bpm_linearity *recipe, toml_datum_t table,
    const char *key, int *count)
{
    toml_datum_t values=toml_get(table,key);
    char **argv;
    int i;
    if (values.type!=TOML_ARRAY || values.u.arr.size<1 || values.u.arr.size>128) return NULL;
    *count=values.u.arr.size;
    argv=calloc((size_t)*count+1,sizeof(*argv));
    if (!argv) return NULL;
    for (i=0; i<*count; ++i) {
        toml_datum_t item=values.u.arr.elem[i];
        if (item.type!=TOML_STRING || item.u.str.len<=0 ||
            strlen(item.u.s)!=(size_t)item.u.str.len ||
            !(argv[i]=mef_bpm_linearity_expand(recipe,item.u.s))) {
            while (i) free(argv[--i]);
            free(argv); return NULL;
        }
    }
    return argv;
}

static int project_roots(mef_bpm_linearity *recipe)
{
    char *project_path=resolved(recipe->orchestration,
        mef_bpm_linearity_string(recipe->document.toptab,"project"));
    toml_datum_t project, roots;
    int okay=0;
    if (!project_path) return 0;
    recipe->project_path=project_path;
    recipe->project=toml_parse_file_ex(project_path);
    free(recipe->orchestration);
    recipe->orchestration=strdup(project_path);
    if (!recipe->orchestration) return 0;
    *strrchr(recipe->orchestration,'/')=0;
    if (!recipe->project.ok) return 0;
    project=toml_get(recipe->project.toptab,"project");
    roots=toml_get(project,"roots");
    recipe->raw=resolved(recipe->orchestration,mef_bpm_linearity_string(roots,"raw"));
    recipe->reduced=resolved(recipe->orchestration,mef_bpm_linearity_string(roots,"output"));
    recipe->calibration=resolved(recipe->orchestration,mef_bpm_linearity_string(roots,"calibration"));
    recipe->work=resolved(recipe->orchestration,mef_bpm_linearity_string(roots,"work"));
    recipe->logs=resolved(recipe->orchestration,mef_bpm_linearity_string(roots,"logs"));
    if (recipe->raw && recipe->reduced && recipe->calibration && recipe->work && recipe->logs) {
        okay=mef_bpm_linearity_below(recipe->calibration,recipe->reduced) &&
            mef_bpm_linearity_below(recipe->work,recipe->reduced) &&
            mef_bpm_linearity_below(recipe->logs,recipe->reduced) &&
            strcmp(recipe->raw,recipe->reduced) && strcmp(recipe->raw,recipe->orchestration) &&
            !mef_bpm_linearity_below(recipe->raw,recipe->reduced) &&
            !mef_bpm_linearity_below(recipe->reduced,recipe->raw) &&
            !mef_bpm_linearity_below(recipe->orchestration,recipe->raw) &&
            !mef_bpm_linearity_below(recipe->orchestration,recipe->reduced);
    }
    return okay;
}

void mef_bpm_linearity_initialize(mef_bpm_linearity *recipe, mef_recipe_run *run)
{
    memset(recipe,0,sizeof(*recipe));
    recipe->run=run;recipe->qc=1;
}

int mef_bpm_linearity_prepare(mef_bpm_linearity *recipe, int argc, char **argv)
{
    char *slash, *binding_recipe;
    toml_datum_t version, rows, dependencies;
    const char *revision, *relative, *author_revision;
    FILE *f;
    struct stat binding_info;
    long length;
    size_t i;
    recipe->diagnostic="Invalid native BPM/linearity recipe or bindings";
    if ((argc!=7 && argc!=9) || strcmp(argv[1],"cal") || strcmp(argv[2],"bpm-linearity") ||
        strcmp(argv[3],"--config") || strcmp(argv[5],"--bindings")) {
        recipe->show_usage=1; return 0;
    }
    if(argc==9 && (strcmp(argv[7],"--qc") ||
        (strcmp(argv[8],"true") && strcmp(argv[8],"false")))) {recipe->show_usage=1;return 0;}
    recipe->recipe_path=resolved(recipe->run->invocation_directory,argv[4]);
    recipe->bindings_path=resolved(recipe->run->invocation_directory,argv[6]);
    if (!recipe->recipe_path || !recipe->bindings_path) return 0;
    recipe->orchestration=strdup(recipe->recipe_path);
    if (!recipe->orchestration) return 0;
    slash=strrchr(recipe->orchestration,'/'); *slash=0;
    if (stat(recipe->bindings_path,&binding_info) || !S_ISREG(binding_info.st_mode) ||
        binding_info.st_size<1 || binding_info.st_size>16*1024*1024) return 0;
    recipe->document=toml_parse_file_ex(recipe->recipe_path);
    recipe->bindings=toml_parse_file_ex(recipe->bindings_path);
    if (!recipe->document.ok || !recipe->bindings.ok ||
        !keys(recipe->document.toptab,"|bpm_linearity_recipe_schema_version||project||run||assembly||preparation||bpm||detectors||calibration_bindings||native_recipe||qc|") ||
        !project_roots(recipe) ||
        !mef_bpm_linearity_below(recipe->recipe_path,recipe->orchestration) ||
        !mef_bpm_linearity_below(recipe->bindings_path,recipe->orchestration) ||
        strcmp(recipe->orchestration,recipe->run->invocation_directory)) return 0;
    version=toml_get(recipe->document.toptab,"qc");
    if(version.type!=TOML_UNKNOWN) {
        if(version.type!=TOML_BOOLEAN) return 0;
        recipe->qc=version.u.boolean;
    }
    if(argc==9) recipe->qc=!strcmp(argv[8],"true");
    version=toml_get(recipe->bindings.toptab,"bpm_linearity_bindings_schema_version");
    revision=mef_bpm_linearity_string(recipe->bindings.toptab,"source_revision");
    author_revision=mef_bpm_linearity_string(toml_get(recipe->document.toptab,"native_recipe"),"source_revision");
    binding_recipe=resolved(recipe->orchestration,
        mef_bpm_linearity_string(recipe->bindings.toptab,"recipe"));
    i=binding_recipe && !strcmp(binding_recipe,recipe->recipe_path);
    free(binding_recipe);
    if (!author_revision || strcmp(author_revision,recipe->run->revision) ||
        !i || version.type!=TOML_INT64 || version.u.int64!=1 || !revision ||
        strcmp(revision,recipe->run->revision) || !keys(recipe->bindings.toptab,
            "|bpm_linearity_bindings_schema_version||source_revision||recipe||dependencies||directories||copies||detectors|")) return 0;
    version=toml_get(recipe->document.toptab,"bpm_linearity_recipe_schema_version");
    relative=mef_bpm_linearity_string(recipe->document.toptab,"run");
    if (version.type!=TOML_INT64 || version.u.int64!=1 || !relative || relative[0]=='/' ||
        !(recipe->output=resolved(recipe->reduced,relative)) ||
        !mef_bpm_linearity_below(recipe->output,recipe->reduced)) return 0;
    recipe->reference_detector=mef_bpm_linearity_string(toml_get(recipe->document.toptab,"assembly"),"reference_detector");
    if (!recipe->reference_detector || !mef_recipe_run_paths(recipe->run,recipe->output,NULL,"CMDP")) return 0;
    f=fopen(recipe->recipe_path,"rb");
    if (!f) return 0;
    if (fseek(f,0,SEEK_END) || (length=ftell(f))<1 || length>1024*1024 || fseek(f,0,SEEK_SET)) {
        fclose(f); return 0;
    }
    recipe->recipe_source=calloc((size_t)length+1,1);
    i=recipe->recipe_source && fread(recipe->recipe_source,1,(size_t)length,f)==(size_t)length;
    if (fclose(f) || !i || memchr(recipe->recipe_source,0,(size_t)length)) return 0;
    rows=toml_get(recipe->bindings.toptab,"detectors");
    dependencies=toml_get(recipe->bindings.toptab,"dependencies");
    if (rows.type!=TOML_ARRAY || rows.u.arr.size<1 || rows.u.arr.size>4095 ||
        dependencies.type!=TOML_ARRAY || dependencies.u.arr.size<1 || dependencies.u.arr.size>65536) return 0;
    recipe->detector_count=(size_t)rows.u.arr.size;
    recipe->dependency_count=(size_t)dependencies.u.arr.size+1;
    recipe->detectors=calloc(recipe->detector_count,sizeof(*recipe->detectors));
    recipe->dependencies=calloc(recipe->dependency_count,sizeof(*recipe->dependencies));
    if (!recipe->detectors || !recipe->dependencies) return 0;
    for (i=0; i<recipe->detector_count; ++i) {
        mef_bpm_linearity_detector *detector=recipe->detectors+i;
        toml_datum_t row=rows.u.arr.elem[i], slot=toml_get(row,"configuration_detector");
        if (!keys(row,"|detector_id||configuration_detector||preparation||bpm||fits||asdf||prepared|")) return 0;
        detector->detector_id=mef_bpm_linearity_string(row,"detector_id");
        if (!detector->detector_id || slot.type!=TOML_INT64 || slot.u.int64<0 || slot.u.int64>INT_MAX-1) return 0;
        detector->configuration_detector=(size_t)slot.u.int64;
        detector->preparation_argv=arguments(recipe,row,"preparation",&detector->preparation_argc);
        detector->bpm_argv=arguments(recipe,row,"bpm",&detector->bpm_argc);
        detector->fits=mef_bpm_linearity_expand(recipe,mef_bpm_linearity_string(row,"fits"));
        detector->asdf=mef_bpm_linearity_expand(recipe,mef_bpm_linearity_string(row,"asdf"));
        detector->prepared=mef_bpm_linearity_expand(recipe,mef_bpm_linearity_string(row,"prepared"));
        if (!detector->preparation_argv || !detector->bpm_argv || !detector->fits || !detector->asdf || !detector->prepared) return 0;
    }
    for (i=0; i<(size_t)dependencies.u.arr.size; ++i) {
        toml_datum_t row=dependencies.u.arr.elem[i];
        const char *path=mef_bpm_linearity_string(row,"path");
        mef_bpm_linearity_dependency *dependency=recipe->dependencies+i;
        if (!keys(row,"|path||sha256|")) return 0;
        dependency->path=resolved(recipe->orchestration,path);
        dependency->sha256=mef_bpm_linearity_string(row,"sha256");
        if (!dependency->path || !dependency->sha256 || strlen(dependency->sha256)!=64 ||
            strspn(dependency->sha256,"0123456789abcdef")!=64) return 0;
    }
    recipe->dependencies[recipe->dependency_count-1].path=strdup(recipe->bindings_path);
    recipe->dependencies[recipe->dependency_count-1].sha256=recipe->bindings_sha256;
    if (!recipe->dependencies[recipe->dependency_count-1].path) return 0;
    recipe->receipt=malloc(strlen(recipe->output)+32);
    if (!recipe->receipt) return 0;
    sprintf(recipe->receipt,"%s/native-recipe.toml",recipe->output);
    return 1;
}

void mef_bpm_linearity_usage(void)
{
    fputs("Usage: mefpp_bpm_linearity_recipe cal bpm-linearity --config RECIPE.toml --bindings NATIVE.toml [--qc true|false]\n"
        "  --config     Required authoring recipe; references project.toml.\n"
        "  --bindings   Required frozen native control file (current limitation).\n"
        "  --qc         Override recipe qc; default true when both are omitted.\n"
        "  --help       Show this message without processing.\n"
        "Run from orchestration with niceness >=10 and a fresh empty reduced run.\n"
        "Recipe [preparation] input_bpm: archived (default) or omitted.\n"
        "Recipe [bpm] response_low=0.5, response_high=1.5; require 0 < low < high.\n"
        "Response at either limit is flagged; supplied BPM skips candidate creation.\n"
        "QC false skips optional full-frame QC and MAD; ROI measurements remain.\n",stderr);
}

void mef_bpm_linearity_destroy(mef_bpm_linearity *recipe)
{
    size_t i;
    if (recipe->detectors) for (i=0; i<recipe->detector_count; ++i) {
        mef_bpm_linearity_detector *d=recipe->detectors+i;
        int j;
        if (d->preparation_argv) for (j=0; j<d->preparation_argc; ++j) free(d->preparation_argv[j]);
        if (d->bpm_argv) for (j=0; j<d->bpm_argc; ++j) free(d->bpm_argv[j]);
        free(d->preparation_argv); free(d->bpm_argv); free(d->fits); free(d->asdf); free(d->prepared);
    }
    if (recipe->dependencies) for (i=0; i<recipe->dependency_count; ++i) free(recipe->dependencies[i].path);
    free(recipe->detectors); free(recipe->dependencies);
    free(recipe->recipe_path); free(recipe->recipe_source); free(recipe->bindings_path); free(recipe->project_path);
    free(recipe->raw); free(recipe->orchestration); free(recipe->reduced);
    free(recipe->calibration); free(recipe->work); free(recipe->logs); free(recipe->output); free(recipe->receipt);
    toml_free(recipe->document); toml_free(recipe->bindings); toml_free(recipe->project);
    qfits_cache_purge();
}
