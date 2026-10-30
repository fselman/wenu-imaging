/* Opt-in configuration bridge; never call a recipe, read FITS or install. */
#include "mef_config_toml.h"
#include "mefp_lib.h"
#include <stdio.h>
#include <string.h>

int main(int argc, char **argv)
{
    mef_config_document *document;
    mef_config *snapshot;
    mef_bb *legacy;
    const mef_config *settings;
    const char *detail;
    char diagnostic[1024];
    mef_status status;
    int failed;
    document = NULL; snapshot = NULL;
    if (argc != 3 || (strcmp(argv[1], "paf") && strcmp(argv[1], "toml"))) {
        fprintf(stderr, "usage: mef_config_read paf|toml explicit-path\n");
        return 2;
    }
    if (!strcmp(argv[1], "toml")) {
        mef_config_toml_initialize();
        status = mef_config_document_from_toml(argv[2], NULL, &document,
            diagnostic, sizeof(diagnostic));
        if (status != MEF_OK) {
            fprintf(stderr, "configuration status %d: %s\n", (int)status, diagnostic);
            return 1;
        }
        settings = mef_config_document_settings(document);
    } else {
        legacy = mef_bb_new_from_paf(argv[2]);
        if (legacy == NULL) return 1;
        status = mef_config_from_legacy(legacy, NULL, &snapshot, &detail);
        mef_bb_del(legacy);
        if (status != MEF_OK) {
            fprintf(stderr, "configuration status %d: %s\n", (int)status,
                detail == NULL ? "no detail" : detail);
            return 1;
        }
        settings = snapshot;
    }
    failed = fputs("{\"settings\":", stdout) == EOF;
    if (mef_config_dump(settings, stdout) != MEF_OK) failed = 1;
    if (fputs(",\"sources\":", stdout) == EOF) failed = 1;
    if (document != NULL) {
        if (mef_config_document_dump_sources(document, stdout) != MEF_OK) failed = 1;
    } else if (fputs("null", stdout) == EOF) failed = 1;
    if (fputs("}\n", stdout) == EOF || fflush(stdout) != 0) failed = 1;
    mef_config_document_destroy(document);
    mef_config_destroy(snapshot);
    return failed ? 1 : 0;
}
