/* Private parser boundary; no tomlc17/C99 types cross this C90 header. */
#ifndef MEF_TOML_BRIDGE_H
#define MEF_TOML_BRIDGE_H
#include "mef_config.h"
typedef struct mef_toml_document mef_toml_document;
typedef enum { MEF_TOML_INTEGER, MEF_TOML_REAL, MEF_TOML_TEXT } mef_toml_kind;
typedef struct {
    mef_toml_kind kind;
    int integer;
    double real;
    const char *text;
} mef_toml_value;
/* Call once in a serial initialization phase before any parsing. No concurrent
 * option changes or concurrent parsing are qualified. Idempotent, not atomic. */
void mef_config_toml_initialize(void);
mef_status mef_toml_open(const char *path, mef_toml_document **out,
    char *diagnostic, size_t capacity);
void mef_toml_close(mef_toml_document *document);
size_t mef_toml_count(const mef_toml_document *document);
mef_status mef_toml_get(const mef_toml_document *document, const char *key,
    mef_toml_value *out);
#endif
