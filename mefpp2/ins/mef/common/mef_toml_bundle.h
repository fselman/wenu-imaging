/* Internal C90 composition boundary. Values borrow the bundle's parser owners. */
#ifndef MEF_TOML_BUNDLE_H
#define MEF_TOML_BUNDLE_H
#include "mef_toml_bridge.h"
typedef struct mef_toml_bundle mef_toml_bundle;
typedef int (*mef_toml_check)(const char *, const mef_toml_value *, int);
mef_status mef_toml_bundle_open(const char *path, const mef_allocator *allocator,
    mef_toml_check check, mef_toml_bundle **out, char *diagnostic, size_t capacity);
void mef_toml_bundle_close(mef_toml_bundle *bundle);
size_t mef_toml_bundle_count(const mef_toml_bundle *bundle);
mef_status mef_toml_bundle_get(const mef_toml_bundle *bundle, const char *key,
    mef_toml_value *out);
#endif
