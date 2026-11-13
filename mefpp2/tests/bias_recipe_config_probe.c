#include "mef_bias_config.h"
#include <stdio.h>
int main(int argc,char **argv)
{
    int count=argc;char **args=argv,message[512]="";mef_bias_config *owner=NULL;
    if(!mef_bias_expand(argc,argv,&count,&args,&owner,message,sizeof(message))) {
        fprintf(stderr,"%s\n",message);return 1;
    }
    for(int i=1;i<count;++i)puts(args[i]);
    if(owner) {
        size_t n;const char *mode=mef_bias_median_even_handling(owner);
        printf("MEDIAN_EVEN=%s\n",mode?mode:"default");
        const char *const *keys=mef_bias_primary_keys(owner,&n);
        printf("PRIMARY_COUNT=%lu\n",(unsigned long)n);
        for(size_t i=0;i<n;++i)puts(keys[i]);
        keys=mef_bias_detector_keys(owner,&n);
        printf("DETECTOR_COUNT=%lu\n",(unsigned long)n);
        for(size_t i=0;i<n;++i)puts(keys[i]);
    }
    mef_bias_config_destroy(owner);return 0;
}
