/* Focused actual allocator/ownership contract for optional legacy cleanup.
 * Included by the existing QC probe; standalone mode needs no ASDF library. */
#include "mefp_lib.h"
#include <assert.h>
#include <unistd.h>

typedef struct { FILE *stream; int saved; } cleanup_capture;
static cleanup_capture cleanup_capture_start(void)
{
    cleanup_capture c;
    fflush(stderr); c.stream=tmpfile(); assert(c.stream);
    c.saved=dup(STDERR_FILENO); assert(c.saved>=0);
    assert(dup2(fileno(c.stream),STDERR_FILENO)>=0); return c;
}
static void cleanup_capture_end(cleanup_capture c,char *text,size_t size)
{
    size_t n;
    fflush(stderr); assert(dup2(c.saved,STDERR_FILENO)>=0); assert(close(c.saved)==0);
    rewind(c.stream); n=fread(text,1,size-1,c.stream); assert(!ferror(c.stream));
    text[n]='\0'; assert(fclose(c.stream)==0);
}
static int cleanup_pointer_count(void)
{
    cleanup_capture c=cleanup_capture_start(); char text[65536],*line; int n=0;
    xmemory_status(); cleanup_capture_end(c,text,sizeof(text));
    line=strstr(text,"ALL_npointers");
    if(line) assert(sscanf(line,"ALL_npointers %d",&n)==1);
    return n;
}
static void optional_cleanup_contract(const char *paf)
{
    static const char *types[]={"bias","bpm","dome","sky","combined","science"};
    mef_bb *bb; size_t i; int baseline,allocated;
    cleanup_capture capture; char text[65536],path[]="/tmp/mefpp-cleanup-XXXXXX";
    char block[2880]; int fd;
    eclipse_init(); set_logfile(0); set_debug(0); set_verbose(0); qfits_cache_purge();
    baseline=cleanup_pointer_count(); capture=cleanup_capture_start();
    mef_bb_clear_work(NULL); mef_bb_del(NULL);
    bb=calloc(1,sizeof(*bb)); assert(bb);
    mef_bb_clear_work(bb); mef_bb_clear_work(bb); mef_bb_del(bb);
    assert(cleanup_pointer_count()==baseline);

    bb=calloc(1,sizeof(*bb)); assert(bb);
#define WORK(field) bb->field=calloc(1,sizeof(*bb->field)); assert(bb->field)
    WORK(bias_scan_median); WORK(bias_scan_stdev);
    WORK(dome_scan_median); WORK(dome_scan_stdev);
    WORK(sky_scan_median); WORK(sky_scan_stdev);
    WORK(science_scan_median); WORK(science_scan_stdev);
    WORK(individual_frame_avg); WORK(individual_frame_median); WORK(individual_frame_sigma);
    WORK(xtname);
#undef WORK
#define NAMES(field,count) bb->field=calloc(3,sizeof(*bb->field)); assert(bb->field); \
    bb->count=3; bb->field[0]=strdup("first"); bb->field[2]=strdup("third"); \
    assert(bb->field[0] && bb->field[2])
    NAMES(bias_frame_name,bias_nframes); NAMES(dome_frame_name,dome_nframes);
    NAMES(sky_frame_name,sky_nframes); NAMES(science_frame_name,science_nframes);
#undef NAMES
    mef_bb_clear_work(bb);
    assert(!bb->bias_scan_median && !bb->bias_scan_stdev && !bb->dome_scan_median && !bb->dome_scan_stdev);
    assert(!bb->sky_scan_median && !bb->sky_scan_stdev && !bb->science_scan_median && !bb->science_scan_stdev);
    assert(!bb->individual_frame_avg && !bb->individual_frame_median && !bb->individual_frame_sigma && !bb->xtname);
    assert(!bb->bias_frame_name && !bb->dome_frame_name && !bb->sky_frame_name && !bb->science_frame_name);
    assert(!bb->bias_nframes && !bb->dome_nframes && !bb->sky_nframes && !bb->science_nframes);
    assert(cleanup_pointer_count()==baseline+1); /* The owner itself remains. */
    mef_bb_clear_work(bb); assert(cleanup_pointer_count()==baseline+1); mef_bb_del(bb);
    assert(cleanup_pointer_count()==baseline);

    bb=calloc(1,sizeof(*bb)); assert(bb);
    bb->bias_framethr_lo=calloc(1,sizeof(float)); bb->bias_framethr_hi=calloc(1,sizeof(float));
    bb->bias_avg1=calloc(1,sizeof(float)); bb->bias_sig1=calloc(1,sizeof(float));
    assert(bb->bias_framethr_lo && bb->bias_framethr_hi && bb->bias_avg1 && bb->bias_sig1);
    bb->instrument=strdup("TESTCAM"); bb->name_bpm=strdup("synthetic-bpm.fits");
    assert(bb->instrument && bb->name_bpm);
    for(i=0;i<sizeof(types)/sizeof(types[0]);++i) mef_create_orig_filename(bb,(char *)types[i]);
    assert(bb->orig_bias && bb->orig_bpm && bb->orig_dome && bb->orig_sky && bb->orig_mff && bb->orig_science);
    assert(!strncmp(bb->orig_bias,"CMDP.TESTCAM.",13) && !strncmp(bb->orig_science,"SMDP.TESTCAM.",13));
    allocated=cleanup_pointer_count();
    for(i=0;i<sizeof(types)/sizeof(types[0]);++i) mef_create_orig_filename(bb,(char *)types[i]);
    assert(cleanup_pointer_count()==allocated); mef_bb_del(bb);
    assert(cleanup_pointer_count()==baseline);

    bb=mef_bb_new_from_paf((char *)paf); assert(bb);
    mef_bb_clear_work(bb); mef_bb_clear_work(bb); mef_bb_del(bb);
    assert(cleanup_pointer_count()==baseline);
    assert(mef_bb_new_from_paf(NULL)==NULL);
    assert(cleanup_pointer_count()==baseline);
    /* A real malformed-file cache failure must release only owned temporaries. */
    fd=mkstemp(path); assert(fd>=0); memset(block,' ',sizeof(block));
    assert(write(fd,block,sizeof(block))==(ssize_t)sizeof(block)); assert(close(fd)==0);
    assert(qfits_cache_prime_bounded(path,2,sizeof(block))!=0); assert(unlink(path)==0);
    qfits_cache_purge(); assert(cleanup_pointer_count()==baseline);
    cleanup_capture_end(capture,text,sizeof(text));
    if(strstr(text,"xmem:")) fprintf(stderr,"%s",text);
    assert(!strstr(text,"xmem:"));

    /* Deliberate misuse remains diagnostic: do not globally suppress free(NULL). */
    capture=cleanup_capture_start(); xmemory_free(NULL,__FILE__,__LINE__);
    cleanup_capture_end(capture,text,sizeof(text));
    assert(strstr(text,"xmem: free requested on NULL pointer"));
    assert(cleanup_pointer_count()==baseline);
    puts("PASS: empty/partial/repeated cleanup, balanced nonnull releases, all creation-name replacements and cache failure; allocator NULL diagnostic retained");
}
#ifdef MEF_CLEANUP_STANDALONE
int main(int argc,char **argv)
{
    if(argc!=2) return 2;
    optional_cleanup_contract(argv[1]); return 0;
}
#endif
