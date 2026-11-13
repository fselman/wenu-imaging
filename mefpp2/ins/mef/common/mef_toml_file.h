#ifndef MEF_TOML_FILE_H
#define MEF_TOML_FILE_H

#include <stddef.h>
#include "tomlc17.h"

/* Owns the supplied path, source bytes, and typed values. A reader that
 * transfers a member clears it before destroying the file owner.
 */
typedef struct mef_toml_file {
    char *path;
    char *source;
    size_t length;
    toml_result_t parsed;
} mef_toml_file;

/* A zero size limit selects the parser's default limit. The returned owner
 * must be destroyed even on failure. Parse errors are in parsed.errmsg.
 */
mef_toml_file mef_toml_file_read(const char *path, size_t max_bytes);
void mef_toml_file_destroy(mef_toml_file *file);

#endif
