/* Configuration document/catalog test only. No engine, FITS or Pycavi calls. */
#include "mef_config_toml.h"
#include "mef_config_domains.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct { size_t calls, fail_at, live; } tracker;
static void *allocate(void *user, size_t bytes)
{
    tracker *t;
    void *p;
    t = user; ++t->calls;
    if (t->fail_at == t->calls) return NULL;
    p = malloc(bytes); if (p != NULL) ++t->live;
    return p;
}
static void release(void *user, void *p)
{
    tracker *t;
    t = user; assert(t->live > 0); --t->live; free(p);
}
int main(int argc, char **argv)
{
    mef_config_document *doc, *copy, *failed, *alias;
    mef_allocator a, invalid;
    mef_status status;
    char diagnostic[1024], tiny;
    FILE *stream;
    tracker t;
    size_t total, i;
    int cloning;
    if (argc == 3 && !strcmp(argv[1], "--catalog")) {
        stream = fopen(argv[2], "w"); assert(stream != NULL);
        assert(mef_domain_catalog_dump(stream)); assert(fclose(stream) == 0); return 0;
    }
    if (argc != 4 && argc != 5) return 2;
    mef_config_toml_initialize(); doc = NULL;
    /* Reject an invalid source then recover in the same process. */
    if (argc == 5 && strcmp(argv[4], "freeze")) {
        status = mef_config_document_from_toml(argv[4], NULL, &doc, diagnostic, sizeof(diagnostic));
        assert(status != MEF_OK && doc == NULL);
        printf("REJECTED: %s\n", diagnostic);
    }
    /* Load once, then clone after any caller-requested private fixture edit. */
    status = mef_config_document_from_toml(argv[1], NULL, &doc, diagnostic, sizeof(diagnostic));
    if (status != MEF_OK) { fprintf(stderr, "document status %d: %s\n", status, diagnostic); return 1; }
    if (argc == 5 && !strcmp(argv[4], "freeze")) {
        stream = fopen(argv[1], "w"); assert(stream != NULL);
        assert(fputs("changed after loading\n", stream) != EOF && fclose(stream) == 0);
    }
    copy = NULL;
    assert(mef_config_document_clone(doc, NULL, &copy, diagnostic, sizeof(diagnostic)) == MEF_OK);
    mef_config_document_destroy(doc); doc = copy;
    /* Invalid/occupied outputs and small diagnostics preserve owners. */
    alias = doc; tiny = 'x';
    assert(mef_config_document_from_toml(argv[1], NULL, &doc, &tiny, 1) == MEF_ERR_CONFIG);
    assert(doc == alias && tiny == '\0');
    assert(mef_config_document_clone(doc, NULL, &doc, NULL, 0) == MEF_ERR_CONFIG);
    invalid.user = NULL; invalid.allocate = allocate; invalid.release = NULL;
    failed = NULL;
    assert(mef_config_document_from_toml(argv[1], &invalid, &failed, NULL, 0) == MEF_ERR_CONFIG);
    assert(mef_config_document_clone(doc, &invalid, &failed, NULL, 0) == MEF_ERR_CONFIG);
    assert(mef_config_document_settings(NULL) == NULL);
    assert(mef_config_document_dump_sources(NULL, NULL) == MEF_ERR_CONFIG);
    mef_config_document_destroy(NULL);
    /* Inject every C90 document/composition/snapshot/report and clone owner.
     * Parser/shim/temp detector-map allocations are outside this callback. */
    if (argc == 4) {
        a.user = &t; a.allocate = allocate; a.release = release;
        for (cloning = 0; cloning < 2; ++cloning) {
            memset(&t, 0, sizeof(t)); failed = NULL;
            status = cloning ? mef_config_document_clone(doc, &a, &failed, diagnostic, sizeof(diagnostic)) :
                mef_config_document_from_toml(argv[1], &a, &failed, diagnostic, sizeof(diagnostic));
            assert(status == MEF_OK); total = t.calls; assert(total > 0 && total < 1024);
            mef_config_document_destroy(failed); assert(t.live == 0);
            for (i = 1; i <= total; ++i) {
                t.calls = 0; t.fail_at = i; failed = NULL;
                status = cloning ? mef_config_document_clone(doc, &a, &failed, diagnostic, sizeof(diagnostic)) :
                    mef_config_document_from_toml(argv[1], &a, &failed, diagnostic, sizeof(diagnostic));
                assert(status == MEF_ERR_MEMORY && failed == NULL && t.live == 0 && diagnostic[0]);
            }
            printf("PASS: %lu %s allocation positions\n", (unsigned long)total, cloning ? "clone" : "document");
        }
    }
    /* Both dumps survive parser, bundle and original-document destruction. */
    stream = fopen(argv[2], "w"); assert(stream != NULL);
    assert(mef_config_dump(mef_config_document_settings(doc), stream) == MEF_OK && fclose(stream) == 0);
    stream = fopen(argv[3], "w"); assert(stream != NULL);
    assert(mef_config_document_dump_sources(doc, stream) == MEF_OK && fclose(stream) == 0);
    stream = fopen(argv[3], "r"); assert(stream != NULL);
    assert(mef_config_document_dump_sources(doc, stream) == MEF_ERR_IO && fclose(stream) == 0);
    mef_config_document_destroy(doc); puts("PASS: immutable settings and source records"); return 0;
}
