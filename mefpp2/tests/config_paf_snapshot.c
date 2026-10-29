/* Configuration-only probe. Never invoke the mefpp recipe or read FITS data. */
#include "mef_config.h"
#include "mefp_lib.h"
#include <stdio.h>

int main(int argc, char **argv)
{
    mef_bb *legacy;
    mef_config *snapshot;
    const char *diagnostic;
    mef_status status;
    FILE *output;
    int failed;
    if (argc != 3) {
        fprintf(stderr, "usage: config_paf_snapshot input.paf output.json\n");
        return 2;
    }
    legacy = mef_bb_new_from_paf(argv[1]);
    if (legacy == NULL) return 1;
    snapshot = NULL;
    status = mef_config_from_legacy(legacy, NULL, &snapshot, &diagnostic);
    mef_bb_del(legacy);
    if (status != MEF_OK) {
        fprintf(stderr, "snapshot failed (%d): %s\n", (int)status,
                diagnostic == NULL ? "no detail" : diagnostic);
        return 1;
    }
    output = fopen(argv[2], "w");
    if (output == NULL) { mef_config_destroy(snapshot); return 1; }
    status = mef_config_dump(snapshot, output);
    failed = fclose(output) != 0;
    mef_config_destroy(snapshot);
    return status != MEF_OK || failed ? 1 : 0;
}
