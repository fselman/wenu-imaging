/* Configuration only: no FITS I/O, recipe or Pycavi processing. */
#include "mef_config_toml.h"
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
static void release(void *user, void *pointer)
{
    tracker *t;
    t = user; assert(t->live > 0); --t->live; free(pointer);
}
int main(int argc, char **argv)
{
    mef_config *config, *copy, *failed;
    mef_allocator allocator;
    mef_status status;
    char diagnostic[1024], tiny;
    const char *clone_detail;
    tracker t;
    size_t total, index;
    FILE *output;
    int close_error;
    if (argc != 3 && argc != 4) return 2;
    config = NULL;
    /* Initialization/argument guard; no file is parsed before initialization. */
    assert(mef_config_from_toml(argv[1], NULL, &config, diagnostic, sizeof(diagnostic)) == MEF_ERR_CONFIG);
    assert(config == NULL && diagnostic[0] != '\0');
    mef_config_toml_initialize(); mef_config_toml_initialize();
    /* Failed read followed by valid read within the same process. */
    if (argc == 4) {
        assert(mef_config_from_toml(argv[3], NULL, &config, diagnostic, sizeof(diagnostic)) != MEF_OK);
        assert(config == NULL);
        printf("REJECTED: %s\n", diagnostic);
    }
    /* Normal parse/copy: parser tree is already freed when this call returns. */
    status = mef_config_from_toml(argv[1], NULL, &config, diagnostic, sizeof(diagnostic));
    if (status != MEF_OK) {
        fprintf(stderr, "TOML status %d: %s\n", (int)status, diagnostic); return 1;
    }
    copy = NULL;
    assert(mef_config_clone(config, NULL, &copy, &clone_detail) == MEF_OK);
    mef_config_destroy(config); config = copy;
    /* Occupied output and truncated diagnostic remain safe. */
    tiny = 'x'; copy = config;
    assert(mef_config_from_toml(argv[1], NULL, &config, &tiny, 1) == MEF_ERR_CONFIG);
    assert(config == copy && tiny == '\0');
    assert(mef_config_from_toml(NULL, NULL, &copy, NULL, 0) == MEF_ERR_CONFIG);
    /* Inject each composition/snapshot owner allocation, not parser allocations. */
    if (argc == 3) {
    memset(&t, 0, sizeof(t)); allocator.user = &t;
    allocator.allocate = allocate; allocator.release = release;
    failed = NULL;
    assert(mef_config_from_toml(argv[1], &allocator, &failed, diagnostic, sizeof(diagnostic)) == MEF_OK);
    total = t.calls; assert(total > 0 && total < 1024);
    mef_config_destroy(failed); assert(t.live == 0);
    for (index = 1; index <= total; ++index) {
        t.calls = 0; t.fail_at = index; failed = NULL;
        assert(mef_config_from_toml(argv[1], &allocator, &failed, diagnostic, sizeof(diagnostic)) == MEF_ERR_MEMORY);
        assert(failed == NULL && t.live == 0 && diagnostic[0] != '\0');
    }
    } else total = 0;
    /* Dump surviving immutable config after parser/temp/source destruction. */
    output = fopen(argv[2], "w"); assert(output != NULL);
    status = mef_config_dump(config, output); close_error = fclose(output);
    mef_config_destroy(config);
    assert(status == MEF_OK && close_error == 0);
    printf("PASS: TOML snapshot, clone/lifetime/occupied output, %lu composition/snapshot allocation failures\n", (unsigned long)total);
    return 0;
}
