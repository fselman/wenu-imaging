/* Native coordinator owners and phases. Measurement-only scientific contract:
 * docs/developer/linearity-preparation-guide-v1.tex, Native recipe.
 */
#ifndef MEF_BPM_LINEARITY_RECIPE_H
#define MEF_BPM_LINEARITY_RECIPE_H
#include "mef_recipe_run.h"
#include "mef_bpm_assembly_qc.h"
#include "tomlc17.h"
#include <stdlib.h>
#include <sys/stat.h>

typedef struct {
    char *path;
    const char *sha256;
    struct stat identity;
} mef_bpm_linearity_dependency;

typedef struct {
    const char *detector_id;
    size_t configuration_detector;
    char **preparation_argv, **bpm_argv;
    int preparation_argc, bpm_argc;
    char *fits, *asdf, *prepared;
} mef_bpm_linearity_detector;

/* All text/arrays are owned until destroy; initialized owners may be destroyed
 * after any failed phase. No detector image cubes are retained by the recipe.
 */
typedef struct {
    mef_recipe_run *run;
    toml_result_t document, bindings, project;
    char *recipe_path, *recipe_source, *bindings_path, *project_path;
    char bindings_sha256[65];
    char *raw, *orchestration, *reduced, *calibration, *work, *logs, *output;
    char *receipt;
    const char *reference_detector, *diagnostic;
    mef_bpm_linearity_detector *detectors;
    mef_bpm_linearity_dependency *dependencies;
    size_t detector_count, dependency_count;
    int show_usage;
} mef_bpm_linearity_recipe;

void mef_bpm_linearity_recipe_initialize(mef_bpm_linearity_recipe *, mef_recipe_run *);
int mef_bpm_linearity_recipe_prepare(mef_bpm_linearity_recipe *, int, char **);
int mef_bpm_linearity_recipe_admit(mef_bpm_linearity_recipe *);
int mef_bpm_linearity_recipe_begin(mef_bpm_linearity_recipe *);
int mef_bpm_linearity_recipe_process(mef_bpm_linearity_recipe *, size_t);
int mef_bpm_linearity_recipe_verify(mef_bpm_linearity_recipe *);
int mef_bpm_linearity_recipe_publish(mef_bpm_linearity_recipe *);
void mef_bpm_linearity_recipe_usage(void);
void mef_bpm_linearity_recipe_destroy(mef_bpm_linearity_recipe *);

/* Shared mechanics, not science. Paths expand only the captured start token. */
char *mef_bpm_linearity_expand(const mef_bpm_linearity_recipe *, const char *);
int mef_bpm_linearity_below(const char *, const char *);
int mef_bpm_linearity_observe(mef_bpm_linearity_recipe *);
int mef_bpm_linearity_hash(const char *, char [65]);
int mef_bpm_linearity_dependency_check(mef_bpm_linearity_dependency *, int);
const char *mef_bpm_linearity_string(toml_datum_t, const char *);
int mef_bpm_linearity_directory(const char *);
const char *mef_bpm_linearity_option(const mef_bpm_linearity_detector *, const char *);
int mef_bpm_linearity_has_dependency(const mef_bpm_linearity_recipe *, const char *);
int mef_bpm_linearity_bindings_admit(mef_bpm_linearity_recipe *, const mef_bpm_linearity_detector *);
int mef_linearity_prepare_command(int, char **);
int mef_bpm_command(int, char **);
#endif
