#include "mef_recipe_help.h"
#include <string.h>

typedef struct {
    const char *category, *name, *purpose;
    int ready;
} recipe_description;

static const recipe_description catalogue[] = {
#define MEF_RECIPE(category, name, entry, ready, purpose) {category, name, purpose, ready},
#include "mef_recipe_catalogue.def"
#undef MEF_RECIPE
};

void mef_recipe_top_help(FILE *out, const char *program)
{
    size_t i, j;
    if (!strcmp(program, "mefpp")) {
        fputs("Usage: mefpp [legacy options]\n", out);
    }
    fputs("Usage: mefpp_recipe CATEGORY OPERATION --config RECIPE.toml [options]\n", out);
    fputs("       mefpp_recipe project init [options]\n", out);
    for (i = 0; i < sizeof(catalogue) / sizeof(*catalogue); ++i) {
        for (j = 0; j < i; ++j) {
            if (!strcmp(catalogue[j].category, catalogue[i].category)) {
                break;
            }
        }
        if (j == i) {
            fprintf(out, "  mefpp_recipe %s --help     List %s commands\n", catalogue[i].category,
                catalogue[i].category);
        }
    }
    fputs("Legacy reduction options remain available with mefpp -h.\n", out);
}

int mef_recipe_category_help(FILE *out, const char *category)
{
    size_t i;
    int found = 0;
    int project = !strcmp(category, "project");
    for (i = 0; i < sizeof(catalogue) / sizeof(*catalogue); ++i) {
        if (!strcmp(category, catalogue[i].category)) {
            if (!found) {
                fprintf(out,
                    "Usage: mefpp_recipe %s OPERATION%s [options]\nCommands:\n",
                    category, project ? "" : " --config RECIPE.toml");
            }
            fprintf(out, "  %-14s %-8s %s\n", catalogue[i].name,
                catalogue[i].ready ? "native" : "pending", catalogue[i].purpose);
            found = 1;
        }
    }
    if (found) {
        fputs("Operation --help lists inputs, options, defaults and outputs.\n", out);
        if (!project) {
            fputs("Pending entries reserve the command; execution is not implemented.\n", out);
        }
        fputs("Help requires no configuration or observations and performs no processing.\n", out);
    }
    return found;
}

void mef_recipe_operation_help(FILE *out, const char *category, const char *operation)
{
    if (!strcmp(category, "project") && !strcmp(operation, "init")) {
        fputs("Usage: mefpp_recipe project init --name NAME --orchestration DIR --raw DIR --reduced DIR\n"
              "All options are required. The raw directory and destination parents must exist.\n"
              "Creates fresh orchestration and reduced directories, including project.toml\n"
              "and reduced subdirectories cal, work and logs. The roots must be disjoint.\n"
              "Orchestration may have any name. Existing destinations are refused.\n"
              "  --help   Show this help\n", out);
        return;
    }
    fprintf(out, "Usage: mefpp_recipe %s %s --config RECIPE.toml [options]\n", category, operation);
    {
        size_t i;
        for (i = 0; i < sizeof(catalogue) / sizeof(*catalogue); ++i) {
            if (!strcmp(category, catalogue[i].category) && !strcmp(operation, catalogue[i].name) &&
                !catalogue[i].ready) {
                fprintf(out, "Status: pending standalone recipe. %s.\n", catalogue[i].purpose);
                if (!strcmp(category, "cal") && !strcmp(operation, "mff")) {
                    fputs("Prerequisites: both dome and sky components; each explicitly selects\n"
                          "a saved flat product or a nonempty raw-flat list. Validate all\n"
                          "Individual recipes are developed first. A later dependency checker\n"
                          "will announce all missing-product reductions and request permission.\n"
                          "Execution is not implemented; final options/defaults remain pending.\n",
                        out);
                } else {
                    fputs("Inputs, defaults and outputs are not yet defined for this public "
                          "command.\n",
                        out);
                }
                return;
            }
        }
    }
    if (!strcmp(operation, "bias")) {
        fputs("Inputs: recipe, project and detector TOMLs, classified processing list and reduced dependencies.\n"
              "  --input ABS_LIST     Processing list: absolute FITS path and DPR.TYPE (BIAS only)\n"
              "  Recipe inputs.list takes an absolute path; run selects the reduced destination.\n"
              "  --bias FILE          Legacy unclassified-list compatibility\n"
              "  --output-dir DIR     Legacy output override, or --output FITS\n"
              "  --detectors all|IDs  Override recipe detector selection; default all\n"
              "  --qc full|legacy     QC profile; default full\n"
              "Recipe bias.mad defaults to false; explicit true opts in.\n"
              "Outputs: master-bias MEF FITS, matching ASDF QC and log.\n",
            out);
    } else {
        fputs("Inputs: recipe, project and detector TOMLs, absolute inputs.list path with absolute FITS paths and DPR.TYPE,\n"
              "reduced master bias and optional BPM; detector selection and explicit ROI/site definitions.\n"
              "Flat pairs derive from header exposure times; missing/ambiguous pairs fail.\n"
              "Raw BIAS rows are optional diagnostic evidence; dependencies are never reduced.\n"
              "  --qc true|false      Override recipe qc; default true\n"
              "Recipe response_low=0.5, response_high=1.5; boundary values are flagged.\n"
              "QC false skips optional full-frame QC and MAD, retaining ROI measurements.\n",
            out);
        if (!strcmp(operation, "bpm-linearity")) {
            fputs(
                "A supplied BPM skips creation and is logged; otherwise robust response fitting "
                "runs.\n"
                "Outputs: detector measurement ASDF; newly created BPM FITS/ASDF and final MEF.\n",
                out);
        } else {
            fputs("BPM creation is disabled. Outputs: detector measurement ASDF and log.\n", out);
        }
        fputs("Linearity is measurement only; no physical response correction is applied.\n", out);
    }
    fputs("  --help               Show this help; no configuration or processing\n"
          "Run from orchestration. Use fresh output destinations; inputs are read-only.\n",
        out);
}
