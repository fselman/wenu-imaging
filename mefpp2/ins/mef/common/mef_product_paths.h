/* Shared native product naming. No Python, input reads or output creation. */
#ifndef MEF_PRODUCT_PATHS_H
#define MEF_PRODUCT_PATHS_H
#include <stddef.h>
#include <time.h>
#define MEF_PRODUCT_PATH_SIZE 4096
#define MEF_RECIPE_TIME_SIZE 32
typedef struct {
    char directory[MEF_PRODUCT_PATH_SIZE];
    char fits[MEF_PRODUCT_PATH_SIZE];
    char asdf[MEF_PRODUCT_PATH_SIZE];
    char log[MEF_PRODUCT_PATH_SIZE];
} mef_product_paths;
/* Capture once at recipe entry, then reuse for every product in that execution.
 * The explicit format is UTC YYYY-MM-DDTHH:MM:SS.mmmZ. */
int mef_recipe_start_time(char *, size_t, char *, size_t);
/* Deterministic formatter for an already sampled instant; microseconds 0..999999. */
int mef_recipe_time_format(time_t, long, char *, size_t, char *, size_t);
/* Exactly one destination option; product class is CMDP or SMDP. A complete
 * --output overrides the generated basename and supplies its parent directory.
 * Sequence starts at one, printed with at least three digits (1000 is valid).
 * Paths resolve against invocation cwd once; the caller's cwd never changes.
 * Output parent must exist; no directory or file is created. Existing FITS,
 * ASDF or log destinations, including dangling symlinks, are rejected.
 * This is a preflight, not an atomic reservation against concurrent writers. */
int mef_product_paths_resolve(const char *, const char *, const char *,
    const char *, const char *, unsigned long, mef_product_paths *, char *, size_t);
#endif
