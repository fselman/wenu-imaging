/* Qualification harness only. No production adapter or numerical routines. */
#include "tomlc17.h"
#include <inttypes.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct block block;
struct block { void *pointer; block *next; };
static block *blocks;
static unsigned long calls, fail_at, failures;
static unsigned long outstanding;
static void fatal(const char *message) { fprintf(stderr,"HARNESS: %s\n",message); exit(90); }
static block *find(void *pointer) {
    block *b;
    for (b=blocks;b;b=b->next) if (b->pointer==pointer) return b;
    return NULL;
}
static void *tracked_realloc(void *pointer, size_t size) {
    void *result;
    block *b = NULL;
    if (!size) fatal("zero-size allocation");
    if (pointer && !(b=find(pointer))) fatal("realloc of unknown pointer");
    calls++;
    if (fail_at && calls==fail_at) { failures++; return NULL; }
    result=realloc(pointer,size);
    if (!result) return NULL;
    if (b) b->pointer=result;
    else {
        b=malloc(sizeof(*b));
        if (!b) fatal("tracker allocation failed");
        b->pointer=result; b->next=blocks; blocks=b; outstanding++;
    }
    return result;
}
static void tracked_free(void *pointer) {
    block **link=&blocks, *b;
    if (!pointer) return;
    while (*link && (*link)->pointer!=pointer) link=&(*link)->next;
    if (!*link) fatal("free of unknown or already-freed pointer");
    b=*link; *link=b->next; outstanding--;
    free(pointer); free(b);
}
static void quoted(const char *text, int length) {
    int i;
    unsigned char c;
    putchar('"');
    for (i=0;i<length;i++) {
        c=(unsigned char)text[i];
        if (c=='"' || c=='\\') { putchar('\\'); putchar(c); }
        else if (c<32) printf("\\u%04x",(unsigned)c);
        else putchar(c);
    }
    putchar('"');
}
static void node(toml_datum_t d) {
    int i, tz;
    const char *type;
    char stamp[100];
    switch(d.type) {
    case TOML_TABLE:
        printf("{\"type\":\"table\",\"value\":{");
        for(i=0;i<d.u.tab.size;i++) {
            if(i) putchar(',');
            quoted(d.u.tab.key[i],d.u.tab.len[i]); putchar(':'); node(d.u.tab.value[i]);
        }
        printf("}}"); return;
    case TOML_ARRAY:
        printf("{\"type\":\"array\",\"value\":[");
        for(i=0;i<d.u.arr.size;i++) { if(i) putchar(','); node(d.u.arr.elem[i]); }
        printf("]}"); return;
    case TOML_STRING:
        printf("{\"type\":\"string\",\"value\":"); quoted(d.u.str.ptr,d.u.str.len); putchar('}'); return;
    case TOML_INT64:
        printf("{\"type\":\"integer\",\"value\":\"%" PRId64 "\"}",d.u.int64); return;
    case TOML_FP64:
        printf("{\"type\":\"float\",\"value\":");
        if(isnan(d.u.fp64)) printf("\"nan\"");
        else if(isinf(d.u.fp64)) printf(d.u.fp64<0 ? "\"-inf\"" : "\"inf\"");
        else if(d.u.fp64==0) printf(signbit(d.u.fp64) ? "-0.0":"0.0");
        else printf("%.17g",d.u.fp64);
        putchar('}'); return;
    case TOML_BOOLEAN:
        printf("{\"type\":\"boolean\",\"value\":%s}",d.u.boolean ? "true":"false"); return;
    case TOML_DATE:
        type="date";
        snprintf(stamp,sizeof(stamp),"%04d-%02d-%02d",d.u.ts.year,d.u.ts.month,d.u.ts.day); break;
    case TOML_TIME:
        type="time";
        snprintf(stamp,sizeof(stamp),"%02d:%02d:%02d.%06d",d.u.ts.hour,d.u.ts.minute,d.u.ts.second,d.u.ts.usec); break;
    case TOML_DATETIME:
    case TOML_DATETIMETZ:
        type=d.type==TOML_DATETIME ? "datetime":"offset-datetime";
        snprintf(stamp,sizeof(stamp),"%04d-%02d-%02dT%02d:%02d:%02d.%06d",d.u.ts.year,d.u.ts.month,d.u.ts.day,d.u.ts.hour,d.u.ts.minute,d.u.ts.second,d.u.ts.usec);
        if(d.type==TOML_DATETIMETZ) {
            tz=abs(d.u.ts.tz);
            snprintf(stamp+strlen(stamp),sizeof(stamp)-strlen(stamp),"%c%02d:%02d",d.u.ts.tz<0 ? '-':'+',tz/60,tz%60);
        }
        break;
    default: fatal("unexpected datum type"); return;
    }
    printf("{\"type\":\"%s\",\"value\":",type); quoted(stamp,(int)strlen(stamp)); putchar('}');
}
static int parse_release(const char *path, int expected) {
    toml_result_t r=toml_parse_file_ex(path);
    int ok=r.ok;
    if(!ok && !r.errmsg[0]) fatal("empty parse diagnostic");
    toml_free(r);
    if(outstanding || blocks) fatal("parser allocations remain after free");
    if(expected>=0 && ok!=expected) fatal("unexpected parse status");
    return ok;
}
int main(int argc,char **argv) {
    toml_option_t options=toml_default_option();
    toml_result_t r;
    unsigned long total, index, rejected=0, recovered=0;
    toml_result_t recovery;
    int cycle, baseline_ok;
    if(argc<3) return 2;
    /* Options installed once, before any parse; no concurrent mutation. */
    options.check_utf8=true;
    options.mem_realloc=tracked_realloc;
    options.mem_free=tracked_free;
    toml_set_option(options);
    if(!strcmp(argv[1],"dump")) {
        r=toml_parse_file_ex(argv[2]);
        printf("{\"ok\":%s,",r.ok ? "true":"false");
        if(r.ok) { printf("\"tree\":"); node(r.toptab); }
        else { if(!r.errmsg[0]) fatal("empty diagnostic"); printf("\"error\":"); quoted(r.errmsg,(int)strlen(r.errmsg)); }
        toml_free(r);
        printf(",\"outstanding\":%lu,\"allocation_calls\":%lu}\n",outstanding,calls);
        return outstanding || blocks ? 3:0;
    }
    if(!strcmp(argv[1],"cycles") && argc==4) {
        for(cycle=0;cycle<20;cycle++) { parse_release(argv[2],1); parse_release(argv[3],0); parse_release(argv[2],1); }
        printf("{\"measured_cycles\":20,\"parse_calls\":60,\"outstanding\":%lu}\n",outstanding); return 0;
    }
    if(!strcmp(argv[1],"failures") && argc==4) {
        baseline_ok=parse_release(argv[2],-1); total=calls;
        if(!total || total>256) fatal("allocation control exceeds fixed bound");
        for(index=1;index<=total;index++) {
            calls=0; fail_at=index;
            r=toml_parse_file_ex(argv[2]);
            if(calls<index) fatal("injection point not reached");
            fail_at=0;
            recovery=toml_parse_file_ex(argv[2]);
            if(recovery.ok!=baseline_ok) fatal("recovery changed baseline status");
            if(r.ok) {
                if(!recovery.ok || !toml_equiv(&r,&recovery)) fatal("successful fallback changed semantics");
                recovered++;
            } else {
                if(!r.errmsg[0]) fatal("empty injected error diagnostic");
                rejected++;
            }
            toml_free(r); toml_free(recovery);
            if(outstanding || blocks) fatal("injected parse/recovery leaked");
            parse_release(argv[3],1); /* A valid parse must succeed after every injected case. */
        }
        printf("{\"injection_points\":%lu,\"injections_consumed\":%lu,\"rejected\":%lu,\"equivalent_fallbacks\":%lu,\"outstanding\":%lu}\n",total,failures,rejected,recovered,outstanding);
        return failures==total ? 0:4;
    }
    return 2;
}
