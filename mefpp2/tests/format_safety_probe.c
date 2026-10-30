/* Test copies expose private formatter state without a production test API. */
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>
#include <limits.h>
static int fail_copy;
static char *message_copy(const char *text) { return fail_copy ? NULL : strdup(text); }
#define strdup message_copy
#include "../src/unix/comm.c"
#undef strdup

static time_t fixed_seconds = 946684800;
static time_t fixed_time(time_t *out) { if (out) *out = fixed_seconds; return fixed_seconds; }
static int fixed_timeofday(struct timeval *out, void *zone)
{ (void)zone; out->tv_sec = fixed_seconds; out->tv_usec = 120000; return 0; }
#define time fixed_time
#define gettimeofday fixed_timeofday
#include "../src/unix/t_iso8601.c"
#undef time
#undef gettimeofday

#include "../qfits5/src/xmemory.c"
#include "qfits.h"
#include "mefp_lib.h"
static int fail_item;
static int test_getitem(qfits_header *, int, char *, char *, char *, char *);
#define qfits_header_getitem test_getitem
#include "../ins/mef/common/mefp_lib.c"
#undef qfits_header_getitem
#include "../src/iproc/image_rtd.c"
static int test_getitem(qfits_header *h, int i, char *k, char *v, char *c, char *l)
{ return fail_item ? -1 : qfits_header_getitem(h, i, k, v, c, l); }
static char captured[2048];
static void capture(char *text)
{ assert(strlen(text) < sizeof(captured)); strcpy(captured, text); }
static char *read_stream(FILE *stream)
{
    static char bytes[20000];
    size_t n;
    rewind(stream); n = fread(bytes, 1, sizeof(bytes) - 1, stream);
    assert(!ferror(stream)); bytes[n] = '\0'; return bytes;
}
int main(int argc, char **argv)
{
    char large[6000], name[1100], key[80], boundary[80];
    qfits_header *header, *update, *merged;
    FILE *stream;
    char *text;
    size_t before_bytes;
    int before_cells;
    memset(large, 'x', sizeof(large) - 1); large[sizeof(large) - 1] = '\0';
    if (argc == 2 && !strcmp(argv[1], "--swap-overflow")) {
        memset(xmemory_tmpdirname, 'x', sizeof(xmemory_tmpdirname) - 1);
        xmemory_tmpdirname[sizeof(xmemory_tmpdirname) - 1] = '\0';
        (void)xmemory_tmpfilename(INT_MAX); assert(0); return 90;
    }
    if (argc == 2 && !strcmp(argv[1], "--rtd-cwd-overflow")) {
        assert(rtd_swapfilename() == NULL);
        puts("PASS: RTD cwd overflow rejected offline"); return 0;
    }
    assert(argc == 1);
    /* Short/percent-containing diagnostics retain exact bytes; oversized
     * callbacks remain bounded and explicitly marked. */
    qfits_err_statset(1); assert(qfits_err_register(capture) == 0);
    qfits_warning("%s %d", "100% literal %n", 7);
    assert(!strcmp(captured, "*** 100% literal %n 7"));
    qfits_error("%s", "100% literal %n");
    assert(!strcmp(captured, "error: 100% literal %n"));
    qfits_warning("%s", large); assert(strlen(captured) == 1023);
    assert(!strcmp(captured + strlen(captured) - 14, "...[truncated]"));
    qfits_error("%s", large); assert(strlen(captured) == 1023);
    assert(strstr(captured, "...[truncated]") != NULL);
    puts("PASS: qfits exact and bounded diagnostic callbacks");
    /* Real Eclipse terminal/log paths; long logs mark truncation. Newline-only
     * formats must reach empty safely; local copy failure must return. */
    comm_config.ansiterm = 0; set_verbose(1);
    set_logfilename("messages.log"); set_logfile(1);
    e_warning("%s", "100% literal %n"); e_error("%s", "short error");
    e_comment(0, "%s", "short comment");
    e_warning("%s", large); e_error("%s", large); e_comment(0, "%s", large);
    compute_status(large, 0, 1, 0);
    e_error("\n\n"); e_warning("\n\n"); e_comment(0, "\n\n");
    fail_copy = 1; e_error("ignored"); e_warning("ignored"); e_comment(0, "ignored"); fail_copy = 0;
    stream = fopen("messages.log", "rb"); assert(stream != NULL); text = read_stream(stream);
    assert(strstr(text, "100% literal %n") && strstr(text, "short error") && strstr(text, "short comment"));
    { int markers = 0; char *at = text; while ((at = strstr(at, "...[truncated]")) != NULL) { ++markers; ++at; } assert(markers == 4); }
    assert(fclose(stream) == 0);
    memset(name, 'a', sizeof(name) - 1); name[sizeof(name) - 1] = '\0';
    set_logfilename(name); assert(get_logfilename()[0] == '\0' && !logfile_active());
    puts("PASS: Eclipse log bounds, percent text, newline stripping and copy failure");
    /* Checked keyword formatter rejects overlong values rather than truncating
     * metadata, including an exact-fit boundary and one character beyond it. */
    assert(mef_bpm_frame_key(key, sizeof(key), "HIERARCH ESO P%N", 7) == 0);
    assert(!strcmp(key, "HIERARCH ESO P%N FRAME007"));
    memset(boundary, 'K', 70); boundary[70] = '\0';
    assert(mef_bpm_frame_key(key, sizeof(key), boundary, 1) == 0 && strlen(key) == 79);
    boundary[70] = 'K'; boundary[71] = '\0';
    assert(mef_bpm_frame_key(key, sizeof(key), boundary, 1) == -1 && key[0] == '\0');
    puts("PASS: BPM keyword percent text, exact fit and explicit overflow rejection");
    /* Header text dump uses data output; no CONTINUE/serialization redesign. */
    header = qfits_header_default(); update = qfits_header_default(); assert(header && update);
    qfits_header_add(header, "OBJECT", "100% literal %n", "percent %s", NULL);
    stream = tmpfile(); assert(stream);
    assert(qfits_header_dump_hdr(header, stream) == 0);
    assert(strstr(read_stream(stream), "100% literal %n") != NULL); assert(fclose(stream) == 0);
    before_bytes = xmemory_table.alloc_total; before_cells = xmemory_table.ncells;
    fail_item = 1; merged = fits_header_merge(header, update); fail_item = 0;
    assert(merged == NULL && xmemory_table.alloc_total == before_bytes && xmemory_table.ncells == before_cells);
    qfits_header_destroy(header); qfits_header_destroy(update);
    puts("PASS: literal header dump and failed merge owner cleanup");
    /* Fixed clock preserves historical local-time/centisecond arithmetic.
     * A five-digit year exercises the former fixed-size timestamp overflow. */
    assert(!strcmp(get_date_iso8601(), "2000-01-01"));
    assert(!strcmp(get_datetime_iso8601(), "2000-01-01T00:00:00"));
    assert(!strcmp(get_datetimemili_iso8601(), "2000-01-01T00:00:00.012"));
    fixed_seconds = (time_t)253402300800.0;
    assert(!strcmp(get_datetime_iso8601(), "10000-01-01T00:00:00"));
    assert(!strcmp(get_datetimemili_iso8601(), "10000-01-01T00:00:00.012"));
    puts("PASS: exact ordinary and extended-year timestamp formatting");
    /* Existing tmpdir guard reserves suffix room; defend formatter as well. */
    name[0] = '/'; memset(name + 1, 'a', 958); name[959] = '\0';
    assert(xmemory_set_tmpdir(name) == 0); assert(strlen(xmemory_tmpfilename(INT_MAX)) < 1024);
    name[959] = 'a'; name[960] = '\0'; assert(xmemory_set_tmpdir(name) == -1);
    assert(xmemory_set_tmpdir("/tmp") == 0);
    puts("PASS: swap filename accepted/rejected boundaries");
    assert(rtd_swapfilename() != NULL);
    assert(rtd_file_command(name, sizeof(name), "percent%file") == 0);
    assert(!strcmp(name, "config -file percent%file"));
    assert(rtd_file_command(name, sizeof(name), large) == -1);
    puts("PASS: RTD command bounds and ordinary exchange name offline");
    puts("PASS: format safety contract"); return 0;
}
