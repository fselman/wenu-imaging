/* Project composition shared by standalone recipes. */
#ifndef MEF_PROJECT_H
#define MEF_PROJECT_H
#include "tomlc17.h"
int mef_project_read(const char *, toml_result_t *, char **, int (*)(void *, const char *), void *);
#endif
