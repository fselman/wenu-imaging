/* Native catalogue routing; each recipe retains its visible lifecycle. */
#include "mef_recipe_help.h"
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/resource.h>

int mef_bias_command(int, char **);
int mef_bpm_linearity_command(int, char **);
typedef int (*recipe_entry)(int, char **);

typedef struct {
    const char *category, *operation;
    recipe_entry entry;
} command;

static const command commands[] = {
#define MEF_RECIPE(category, name, entry, ready, purpose) {category, name, entry},
#include "mef_recipe_catalogue.def"
#undef MEF_RECIPE
};

int main(int argc, char **argv)
{
    size_t i;
    if (argc == 2 && !strcmp(argv[1], "--help")) {
        mef_recipe_top_help(stdout, "mefpp_recipe");
        return EXIT_SUCCESS;
    }
    if (argc == 3 && !strcmp(argv[2], "--help")) {
        if (mef_recipe_category_help(stdout, argv[1])) {
            return EXIT_SUCCESS;
        }
    }
    if (argc >= 3) {
        for (i = 0; i < sizeof(commands) / sizeof(*commands); ++i) {
            const command *c = commands + i;
            if (strcmp(c->category, argv[1]) || strcmp(c->operation, argv[2])) {
                continue;
            }
            if (argc == 4 && !strcmp(argv[3], "--help")) {
                mef_recipe_operation_help(stdout, c->category, c->operation);
                return EXIT_SUCCESS;
            }
            if (!c->entry) {
                fprintf(stderr, "Recipe %s %s is pending; no processing performed.\n", c->category,
                    c->operation);
                return EXIT_FAILURE;
            }
            errno = 0;
            if (getpriority(PRIO_PROCESS, 0) < 10 && !errno && setpriority(PRIO_PROCESS, 0, 10)) {
                perror("Cannot set recipe scheduling priority");
                return EXIT_FAILURE;
            }
            return c->entry(argc, argv);
        }
    }
    fputs("Unknown or incomplete recipe command.\n", stderr);
    mef_recipe_top_help(stderr, "mefpp_recipe");
    return EXIT_FAILURE;
}
