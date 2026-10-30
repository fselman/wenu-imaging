/* Internal opt-in M2 compatibility reader. Not installed/stable ABI. C90. */
#ifndef MEF_CONFIG_TOML_H
#define MEF_CONFIG_TOML_H
#include "mef_config.h"
/* Serial process initialization, once before any reader/worker activity. */
void mef_config_toml_initialize(void);
/* Explicit path; no defaults, cwd changes or CLI overrides. Version 1
 * is a complete native compatibility snapshot, not the final domain schema.
 * Version 2 composes compatibility subsets; version 3 adds typed domains/units; final mapped fields required. Integer/real/string types are exact, not coerced.
 * Fields use existing native units/storage, not unit conversion or new cuts.
 * The parser tree and temporary data die before return; *out owns its settings.
 * Allocator covers C90 composition and returned M1 snapshot owners, not parser
 * allocations or the existing temporary detector map.
 * Outputs must start NULL; diagnostics are copied into caller storage when
 * non-NULL/capacity>0. No ordinary failure exits, installs or writes products. */
mef_status mef_config_from_toml(const char *path, const mef_allocator *allocator,
    mef_config **out, char *diagnostic, size_t capacity);
/* Owned settings + frozen per-field domain/unit/source records. Borrow the
 * const settings only while this document lives. Clone owns both components.
 * Source records describe winning file/line and explicit/inherited selection;
 * source content hashes and complete override histories are not recorded here.
 * No file is reopened when inspecting/cloning a successfully loaded document.
 * Allocator covers these new C90 owners, not parser/shim/temp detector storage. */
typedef struct mef_config_document mef_config_document;
mef_status mef_config_document_from_toml(const char *path, const mef_allocator *allocator,
    mef_config_document **out, char *diagnostic, size_t capacity);
mef_status mef_config_document_clone(const mef_config_document *source, const mef_allocator *allocator,
    mef_config_document **out, char *diagnostic, size_t capacity);
const mef_config *mef_config_document_settings(const mef_config_document *doc);
mef_status mef_config_document_dump_sources(const mef_config_document *doc, FILE *stream);
void mef_config_document_destroy(mef_config_document *doc);
#endif
