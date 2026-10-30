/* Native domain-schema v1 descriptors. C90; no defaults/scientific conversion. */
#ifndef MEF_CONFIG_DOMAINS_H
#define MEF_CONFIG_DOMAINS_H
#include <stdio.h>
typedef struct {
    char native_key[96];
    char path[192];
    const char *storage, *unit, *role;
} mef_domain_field;
int mef_domain_from_native(const char *key, mef_domain_field *out);
int mef_domain_from_path(const char *path, mef_domain_field *out);
int mef_domain_container(const char *path);
int mef_domain_catalog_dump(FILE *stream);
#endif
