#define _POSIX_C_SOURCE 200809L
#define _XOPEN_SOURCE 700
#include "mef_product_paths.h"
#include <ctype.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <time.h>
#include <unistd.h>

static int fail(char *message, size_t size, const char *text)
{
    if (message != NULL && size) snprintf(message, size, "%s", text);
    return -1;
}
static int timestamp(const char *s)
{
    size_t i;
    int year, month, day, hour, minute, second, days;
    static const int limits[] = {31,28,31,30,31,30,31,31,30,31,30,31};
    if (s == NULL || strlen(s) != 24) return 0;
    for (i = 0; i < 24; ++i) {
        if (i == 4 || i == 7) { if (s[i] != '-') return 0; }
        else if (i == 10) { if (s[i] != 'T') return 0; }
        else if (i == 13 || i == 16) { if (s[i] != ':') return 0; }
        else if (i == 19) { if (s[i] != '.') return 0; }
        else if (i == 23) { if (s[i] != 'Z') return 0; }
        else if (!isdigit((unsigned char)s[i])) return 0;
    }
    year = (s[0]-'0')*1000+(s[1]-'0')*100+(s[2]-'0')*10+s[3]-'0';
    month = (s[5]-'0')*10+s[6]-'0'; day = (s[8]-'0')*10+s[9]-'0';
    hour = (s[11]-'0')*10+s[12]-'0'; minute = (s[14]-'0')*10+s[15]-'0';
    second = (s[17]-'0')*10+s[18]-'0';
    if (year < 1 || month < 1 || month > 12 || day < 1 || hour > 23 || minute > 59 || second > 60) return 0;
    days = limits[month-1];
    if (month == 2 && year%4 == 0 && (year%100 != 0 || year%400 == 0)) ++days;
    return day <= days;
}
int mef_recipe_time_format(time_t instant, long microseconds, char *out, size_t size,
    char *message, size_t message_size)
{
    struct tm utc;
    char base[24];
    int n;
    if (out == NULL || size == 0) return fail(message, message_size, "Missing recipe timestamp buffer");
    out[0] = '\0';
    if (microseconds < 0 || microseconds > 999999 || gmtime_r(&instant, &utc) == NULL ||
        strftime(base, sizeof(base), "%Y-%m-%dT%H:%M:%S", &utc) != 19)
        return fail(message, message_size, "Cannot format UTC recipe start time");
    n = snprintf(out, size, "%s.%03ldZ", base, microseconds/1000);
    if (n < 0 || (size_t)n >= size || !timestamp(out)) {
        out[0] = '\0'; return fail(message, message_size, "Recipe timestamp buffer too small or unsupported date");
    }
    if (message != NULL && message_size) message[0] = '\0';
    return 0;
}
int mef_recipe_start_time(char *out, size_t size, char *message, size_t message_size)
{
    struct timeval now;
    if (gettimeofday(&now, NULL) != 0)
        return fail(message, message_size, "Cannot capture UTC recipe start time");
    return mef_recipe_time_format(now.tv_sec, (long)now.tv_usec, out, size, message, message_size);
}
static int absent(const char *path)
{
    struct stat st;
    if (lstat(path, &st) == 0) return 0;
    return errno == ENOENT;
}
int mef_product_paths_resolve(const char *invocation, const char *output_dir,
    const char *output, const char *product_class, const char *start,
    unsigned long sequence, mef_product_paths *out, char *message, size_t message_size)
{
    mef_product_paths pending;
    struct stat st;
    char joined[MEF_PRODUCT_PATH_SIZE], parent[MEF_PRODUCT_PATH_SIZE];
    char canonical[MEF_PRODUCT_PATH_SIZE], leaf[MEF_PRODUCT_PATH_SIZE];
    const char *selected;
    char *slash;
    size_t i, stem;
    int n;
    if (out == NULL) return fail(message, message_size, "Missing product path result");
    if (output_dir != NULL && output != NULL)
        return fail(message, message_size, "Use either --output-dir or --output, not both");
    if (output_dir == NULL && output == NULL)
        return fail(message, message_size, "Supply --output-dir or complete --output");
    if (invocation == NULL || invocation[0] != '/' || !timestamp(start) || sequence == 0 ||
        product_class == NULL || (strcmp(product_class,"CMDP") && strcmp(product_class,"SMDP")))
        return fail(message, message_size, "Invalid invocation, product class, recipe timestamp or sequence");
    selected = output != NULL ? output : output_dir;
    if (!*selected) return fail(message, message_size, "Empty output option");
    for (i = 0; selected[i]; ++i)
        if ((unsigned char)selected[i] < 32 || (unsigned char)selected[i] == 127)
            return fail(message, message_size, "Control character in output path");
    n = selected[0] == '/' ? snprintf(joined,sizeof(joined),"%s",selected) :
        snprintf(joined,sizeof(joined),"%s/%s",invocation,selected);
    if (n < 0 || (size_t)n >= sizeof(joined)) return fail(message,message_size,"Output path too long");
    if (output != NULL) {
        strcpy(parent, joined); slash = strrchr(parent, '/');
        if (slash == NULL || !slash[1]) return fail(message,message_size,"--output requires a FITS filename");
        strcpy(leaf,slash+1);
        if (slash == parent) slash[1] = '\0'; else *slash = '\0';
    } else {
        strcpy(parent,joined);
        n = snprintf(leaf,sizeof(leaf),"%s.%s.%03lu.fits",product_class,start,sequence);
        if (n < 0 || (size_t)n >= sizeof(leaf)) return fail(message,message_size,"Product filename too long");
    }
    stem = strlen(leaf);
    if (stem <= 5 || strcmp(leaf+stem-5,".fits"))
        return fail(message,message_size,"Product filename must end in .fits");
    if (realpath(parent,canonical) == NULL || stat(canonical,&st) != 0 || !S_ISDIR(st.st_mode) ||
        (st.st_mode & 0222) == 0 || access(canonical,W_OK|X_OK) != 0)
        return fail(message,message_size,"Output directory must already exist and be writable");
    memset(&pending,0,sizeof(pending)); strcpy(pending.directory,canonical);
    n = snprintf(pending.fits,sizeof(pending.fits),"%s%s%s",canonical,
        strcmp(canonical,"/") ? "/" : "",leaf);
    if (n < 0 || (size_t)n >= sizeof(pending.fits)) return fail(message,message_size,"Product path too long");
    stem = strlen(pending.fits)-5;
    n = snprintf(pending.asdf,sizeof(pending.asdf),"%.*s.asdf",(int)stem,pending.fits);
    if (n < 0 || (size_t)n >= sizeof(pending.asdf)) return fail(message,message_size,"ASDF path too long");
    n = snprintf(pending.log,sizeof(pending.log),"%.*s.log",(int)stem,pending.fits);
    if (n < 0 || (size_t)n >= sizeof(pending.log)) return fail(message,message_size,"Log path too long");
    if (!absent(pending.fits) || !absent(pending.asdf) || !absent(pending.log))
        return fail(message,message_size,"Product FITS, ASDF or log destination already exists or is inaccessible");
    *out = pending;
    if (message != NULL && message_size) message[0] = '\0';
    return 0;
}
