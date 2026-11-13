/* Command selection/help only; no configuration or numerical initialization. */
#ifndef MEF_RECIPE_HELP_H
#define MEF_RECIPE_HELP_H
#include <stdio.h>
void mef_recipe_top_help(FILE *, const char *);
int mef_recipe_category_help(FILE *, const char *);
void mef_recipe_operation_help(FILE *, const char *, const char *);
#endif
