#include "mef_roi_config.h"
#include "mef_config_toml.h"
#include <assert.h>
#include <stdlib.h>
#include <string.h>
typedef struct {int calls,fail,live;} fault;
static void *allocate(void *u,size_t n){fault *f=u;if(++f->calls==f->fail)return NULL;void *p=(malloc)(n);if(p)++f->live;return p;}
static void release(void *u,void *p){fault *f=u;assert(p&&f->live>0);--f->live;(free)(p);}
int main(int argc,char **argv)
{
    mef_roi_config *c=NULL,*occupied;char diagnostic[256];
    detector_joint_amplifier amp[3];int dim[3][2]={{100,80},{100,80},{60,50}};
    detector_roi out[3],saved[3];size_t count=999;
    assert(argc==4);mef_config_toml_initialize();
    mef_status status=mef_roi_config_read(argv[2],argv[1],NULL,&c,diagnostic,sizeof diagnostic);
    if(!strcmp(argv[3],"reject")){assert(status!=MEF_OK&&!c);return 0;}
    if(!strcmp(argv[3],"eso")){
        assert(status==MEF_OK&&c&&mef_roi_config_count(c)==3);
        memset(amp,0,sizeof amp);strcpy(amp[0].detector_id,"ESO_CCD_#96");strcpy(amp[0].amplifier_id,"R");
        strcpy(amp[1].detector_id,"ESO_CCD_#65");strcpy(amp[1].amplifier_id,"L");
        strcpy(amp[2].detector_id,"ESO_CCD_#65");strcpy(amp[2].amplifier_id,"R");
        assert(mef_roi_config_bind(c,3,amp,(const int (*)[2])dim,out,3,&count,NULL,0)==MEF_OK);
        assert(count==3&&out[0].amplifier==1&&out[1].amplifier==1&&out[2].amplifier==0);
        assert(!strcmp(amp[out[0].amplifier].detector_id,"ESO_CCD_#65"));
        assert(!strcmp(amp[out[2].amplifier].detector_id,"ESO_CCD_#96"));
        assert(remove(argv[2])==0);mef_roi_config_destroy(c);puts("ESO # identities preserved and bound");return 0;
    }
    assert(status==MEF_OK&&c&&mef_roi_config_count(c)==3);
    assert(strstr(mef_roi_config_source(c),"center"));
    /* Guard occupied owners and custom allocator cleanup at every allocation. */
    occupied=c;assert(mef_roi_config_read(argv[2],argv[1],NULL,&c,NULL,0)!=MEF_OK&&c==occupied);
    for(int i=1;i<=4;++i){fault f={0,i,0};mef_allocator a={&f,allocate,release};mef_roi_config *q=NULL;
        status=mef_roi_config_read(argv[2],argv[1],&a,&q,NULL,0);
        assert((i<=3&&status==MEF_ERR_MEMORY&&!q)||(i==4&&status==MEF_OK&&q));
        mef_roi_config_destroy(q);assert(!f.live);
    }
    /* Source removal must not affect frozen metadata or binding. */
    assert(remove(argv[2])==0);
    memset(amp,0,sizeof amp);strcpy(amp[0].detector_id,"CHIP8");strcpy(amp[0].amplifier_id,"OUT1");
    strcpy(amp[1].detector_id,"CHIP1");strcpy(amp[1].amplifier_id,"OUT1");
    strcpy(amp[2].detector_id,"CHIP1");strcpy(amp[2].amplifier_id,"OUT2");
    memset(out,0x5a,sizeof out);memcpy(saved,out,sizeof out);
    assert(mef_roi_config_bind(c,3,amp,(const int (*)[2])dim,out,2,&count,NULL,0)!=MEF_OK);
    assert(count==999&&!memcmp(out,saved,sizeof out));
    dim[1][0]=10;
    assert(mef_roi_config_bind(c,3,amp,(const int (*)[2])dim,out,3,&count,NULL,0)!=MEF_OK);
    assert(count==999&&!memcmp(out,saved,sizeof out));dim[1][0]=100;
    strcpy(amp[0].detector_id,"UNKNOWN");
    assert(mef_roi_config_bind(c,3,amp,(const int (*)[2])dim,out,3,&count,NULL,0)!=MEF_OK);
    assert(count==999&&!memcmp(out,saved,sizeof out));strcpy(amp[0].detector_id,"CHIP8");
    strcpy(amp[0].amplifier_id,"UNKNOWN");
    assert(mef_roi_config_bind(c,3,amp,(const int (*)[2])dim,out,3,&count,NULL,0)!=MEF_OK);
    assert(count==999&&!memcmp(out,saved,sizeof out));strcpy(amp[0].amplifier_id,"OUT1");
    amp[2]=amp[1];
    assert(mef_roi_config_bind(c,3,amp,(const int (*)[2])dim,out,3,&count,NULL,0)!=MEF_OK);
    assert(count==999&&!memcmp(out,saved,sizeof out));strcpy(amp[2].amplifier_id,"OUT2");
    assert(mef_roi_config_bind(c,3,amp,(const int (*)[2])dim,out,3,&count,NULL,0)==MEF_OK);
    assert(count==3&&out[0].amplifier==1&&out[1].amplifier==1&&out[2].amplifier==0);
    assert(out[0].xmin==1&&out[0].xmax==40&&out[1].xmin==30&&out[2].ymax==80);
    detector_joint_amplifier tmp=amp[0];amp[0]=amp[1];amp[1]=tmp;
    assert(mef_roi_config_bind(c,3,amp,(const int (*)[2])dim,out,3,&count,NULL,0)==MEF_OK);
    assert(out[0].amplifier==0&&out[2].amplifier==1);
    for(int i=0;i<3;++i)printf("%s %s %s %d %d %d %d\n",out[i].roi_id,
        amp[out[i].amplifier].detector_id,amp[out[i].amplifier].amplifier_id,
        out[i].xmin,out[i].xmax,out[i].ymin,out[i].ymax);
    mef_roi_config_destroy(c);return 0;
}
