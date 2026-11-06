/* Exercise the real path helper without processing images or creating outputs. */
#include "mef_product_paths.h"
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc, char **argv)
{
    mef_product_paths paths, original;
    char message[256], start[MEF_RECIPE_TIME_SIZE], *end;
    unsigned long number;
    if (argc == 2 && !strcmp(argv[1],"--capture")) {
        if (mef_recipe_start_time(start,sizeof(start),message,sizeof(message))) {
            fprintf(stderr,"%s\n",message); return 1;
        }
        puts(start); return 0;
    }
    if (argc == 4 && !strcmp(argv[1],"--format")) {
        long long seconds;
        long microseconds;
        errno = 0; seconds = strtoll(argv[2],&end,10);
        if (errno || end == argv[2] || *end || (long long)(time_t)seconds != seconds) return 2;
        errno = 0; microseconds = strtol(argv[3],&end,10);
        if (errno || end == argv[3] || *end) return 2;
        if (mef_recipe_time_format((time_t)seconds,microseconds,start,sizeof(start),message,sizeof(message))) {
            fprintf(stderr,"%s\n",message); return 1;
        }
        puts(start); return 0;
    }
    if (argc != 7) return 2;
    errno = 0; number = strtoul(argv[6],&end,10);
    if (errno || end == argv[6] || *end || argv[6][0] == '-') return 2;
    memset(&paths,0x5a,sizeof(paths)); original = paths;
    if (mef_product_paths_resolve(argv[1],strcmp(argv[2],"-")?argv[2]:NULL,
        strcmp(argv[3],"-")?argv[3]:NULL,argv[4],argv[5],number,&paths,message,sizeof(message))) {
        if (memcmp(&paths,&original,sizeof(paths))) return 3;
        fprintf(stderr,"%s\n",message); return 1;
    }
    printf("%s\n%s\n%s\n%s\n",paths.directory,paths.fits,paths.asdf,paths.log);
    return 0;
}
