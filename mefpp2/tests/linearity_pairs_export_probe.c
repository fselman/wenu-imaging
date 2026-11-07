#include "mef_linearity_pairs_export.h"
#include "mefp_lib.h"
#include <assert.h>
int main(int argc,char **argv)
{
    assert(argc==5);int missing=atoi(argv[4]);
    mef_bb *bb=mef_bb_new_from_paf(argv[1]);assert(bb);
    int trim[]={2,5,2,2};memcpy(bb->ccd[0].trimreg,trim,sizeof trim);
    mef_config *config=NULL;assert(mef_config_from_legacy(bb,NULL,&config,NULL)==MEF_OK);mef_bb_del(bb);
    image_t *images[4],*bias[2];const image_t *raw[4];
    for(int i=0;i<4;++i){images[i]=image_new(6,3);assert(images[i]);raw[i]=images[i];
        for(int k=0;k<18;++k)images[i]->data[k]=100+(i==1||i==2?100:0);}
    for(int i=0;i<2;++i){bias[i]=image_new(6,3);assert(bias[i]);for(int k=0;k<18;++k)bias[i]->data[k]=10;}
    for(int x=0;x<4;++x){int pattern=x==0?1:x==1?-1:0;
        images[0]->data[7+x]+=pattern;images[3]->data[7+x]-=pattern;
        images[1]->data[7+x]+=2*pattern;images[2]->data[7+x]-=2*pattern;bias[0]->data[7+x]+=pattern;}
    unsigned char flags[]={0,1,1,1};
    mef_linearity_frame frames[4];memset(frames,0,sizeof frames);
    for(int i=0;i<4;++i){snprintf(frames[i].asset_id,128,"F%d\\tab\tline\n",i);
        strcpy(frames[i].pair_id,i==0||i==3?"P0":"P1");frames[i].input_index=10+i;
        frames[i].hdu=1;frames[i].seconds=i==0||i==3?2:5;}
    detector_roi roi;memset(&roi,0,sizeof roi);strcpy(roi.roi_id,"center");roi.xmin=roi.ymin=roi.ymax=1;roi.xmax=4;
    mef_linearity_pairs_input p;memset(&p,0,sizeof p);p.configuration=config;p.frames=4;p.raw=raw;p.frame=frames;
    strcpy(p.identity.detector_id,"ESO_CCD_#65");strcpy(p.identity.amplifier_id,"L");
    p.raw_bias[0]=bias[0];p.raw_bias[1]=bias[1];p.raw_bias_asset[0]="B0";p.raw_bias_asset[1]="B1";
    p.raw_bias_hdu[0]=p.raw_bias_hdu[1]=1;p.rois=1;p.roi=&roi;p.saturation_raw=1000;p.max_rows=2;p.with_mad=1;
    if(missing){p.bpm_flags=flags;p.bpm_count=4;p.reject_bits=255;}
    mef_linearity_pairs_result *r=NULL;assert(mef_linearity_measure_pairs(&p,NULL,&r)==MEF_OK);
    FILE *out=fopen(argv[2],"w");assert(out);assert(mef_linearity_pairs_write_tsv(out,r)==MEF_OK);assert(!fclose(out));
    out=fopen(argv[3],"w");assert(out);assert(mef_linearity_bias_write_tsv(out,r)==MEF_OK);assert(!fclose(out));
    assert(mef_linearity_pairs_write_tsv(NULL,r)==MEF_ERR_INPUT);
    out=fopen(argv[1],"r");assert(out);assert(mef_linearity_bias_write_tsv(out,r)==MEF_ERR_IO);fclose(out);
    mef_linearity_pairs_destroy(r);mef_config_destroy(config);
    for(int i=0;i<4;++i)image_del(images[i]);
    for(int i=0;i<2;++i)image_del(bias[i]);
    puts("PASS: measured pair/bias tables and stream failure");return 0;
}
