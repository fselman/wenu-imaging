/* Internal opt-in M2 compatibility reader. Not installed/stable ABI. C90. */
#ifndef MEF_CONFIG_TOML_H
#define MEF_CONFIG_TOML_H
#include "mef_config.h"
/* Serial process initialization, once before any reader/worker activity. */
void mef_config_toml_initialize(void);
/* Explicit path; no defaults, cwd changes or CLI overrides. Version 1
 * is a complete native compatibility snapshot, not the final domain schema.
 * Version 2 composes explicit reusable subsets; final mapped fields required. Integer/real/string types are exact, not coerced.
 * Fields use existing native units/storage, not unit conversion or new cuts.
 * The parser tree and temporary data die before return; *out owns its settings.
 * Allocator covers C90 composition and returned M1 snapshot owners, not parser
 * allocations or the existing temporary detector map.
 * Outputs must start NULL; diagnostics are copied into caller storage when
 * non-NULL/capacity>0. No ordinary failure exits, installs or writes products. */
mef_status mef_config_from_toml(const char *path, const mef_allocator *allocator,
    mef_config **out, char *diagnostic, size_t capacity);
#endif
