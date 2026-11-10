/* File-identity boundary, not an image or ASDF test. The optional flag mutates
 * only the disposable fixture supplied by recipe_file_hash_contract.py. */
#define _POSIX_C_SOURCE 200809L
#include "mef_bpm_linearity_recipe.h"
#include <stdio.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char **argv)
{
    char digest[65];
    mef_bpm_linearity_dependency dependency={0};
    FILE *stream;
    struct stat before;
    struct timespec times[2];
    int byte;
    if ((argc!=2 && argc!=3) || !mef_bpm_linearity_hash(argv[1],digest)) return 1;
    if (argc==2) { puts(digest); return 0; }
    if (strcmp(argv[2],"--test-restored-timestamp")) return 1;
    dependency.path=argv[1]; dependency.sha256=digest;
    if (!mef_bpm_linearity_dependency_check(&dependency,1) || stat(argv[1],&before)) return 1;
#ifdef __APPLE__
    times[0]=before.st_atimespec; times[1]=before.st_mtimespec;
#else
    times[0]=before.st_atim; times[1]=before.st_mtim;
#endif
    stream=fopen(argv[1],"r+b");
    if (!stream) return 1;
    byte=fgetc(stream);
    if (byte==EOF || fseek(stream,0,SEEK_SET) || fputc(byte^1,stream)==EOF ||
        fflush(stream) || futimens(fileno(stream),times)) { fclose(stream); return 1; }
    if (fclose(stream) || !mef_bpm_linearity_dependency_check(&dependency,0) ||
        mef_bpm_linearity_dependency_check(&dependency,1)) return 1;
    puts("PASS: stat identity alone cannot detect a restored-timestamp edit; final content hash rejects it");
    return 0;
}
