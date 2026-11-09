/* Exercise only the native byte-copy boundary; no QC fixture serialization. */
#include "mef_mef_assemble.h"
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
int main(int argc,char **argv)
{
    mef_bpm_assembly_detector *d;
    size_t n,i;
    char message[512];int status;
    if(argc<6 || (argc-3)%3)return 2;
    n=(size_t)(argc-3)/3;d=calloc(n,sizeof(*d));if(!d)return 2;
    for(i=0;i<n;++i){
        char *end;unsigned long slot;
        errno=0;slot=strtoul(argv[5+3*i],&end,10);
        if(errno || *end || slot>4096){free(d);return 2;}
        d[i]=(mef_bpm_assembly_detector){argv[3+3*i],argv[4+3*i],(size_t)slot};
    }
    status=mef_bpm_mef_assemble(argv[1],argv[2],d,n,message,sizeof(message));
    if(*message)fprintf(stderr,"%s\n",message);
    free(d);return status?1:0;
}
