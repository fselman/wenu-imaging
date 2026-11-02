/* Purpose: independent response/coverage controls and exact byte-mask I/O.
 * Synthetic active planes only. No production inputs, installations or science
 * qualification. Legacy constructors are independent arithmetic references. */
#include "eclipse.h"
#include <assert.h>
#include <math.h>
#include <string.h>

static void destroy_legacy(image_t **r, int mode) {
    int j;
    for (j=0;j<(mode?2:3);++j) image_del(r[j]);
    free(r);
}
static void numerical(void) {
    cube_t *c=cube_new(8,1,5);
    detector_response_options o;
    detector_response_result *r=NULL;
    image_t **legacy, *norm;
    pixelmap *reference=pixelmap_new(8,1), *samples[5];
    pixelvalue saved[5][8];
    int rois[2][4]={{1,5,1,1},{3,8,1,1}};
    int mode,i,j;
    assert(c && reference);
    for (j=0;j<5;++j) {
        c->plane[j]=image_new(8,1); samples[j]=pixelmap_new(8,1);
        assert(c->plane[j] && samples[j]);
        for (i=0;i<8;++i) c->plane[j]->data[i]=(pixelvalue)((j+1)*16*(i+1));
        memcpy(saved[j],c->plane[j]->data,sizeof(saved[j]));
    }
    memset(&o,0,sizeof(o)); o.low=.5; o.high=1.5;
    /* All-good/omitted maps and overlapping ROI union preserve exact legacy
     * medians, float slope/intercept/residual stores and normalization. */
    for (mode=0;mode<2;++mode) {
        o.proportional=mode;
        legacy=mode?cube_create_gainmap_proportional(c):cube_create_gainmap_robust(c);
        assert(legacy);
        norm=image_normalize(legacy[0],NORM_MEAN); assert(norm);
        assert(cube_response_checked(c,&o,&r)==0);
        /* Existing even image median is lower-central for eight samples. */
        assert(r->reference_levels[0]==64);
        assert(!memcmp(r->slope->data,legacy[0]->data,8*sizeof(pixelvalue)));
        assert(!memcmp(r->normalized->data,norm->data,8*sizeof(pixelvalue)));
        assert(!memcmp(r->residual->data,legacy[mode?1:2]->data,8*sizeof(pixelvalue)));
        if (!mode) assert(!memcmp(r->intercept->data,legacy[1]->data,8*sizeof(pixelvalue)));
        assert(r->reasons[0]==4 && r->reasons[7]==8);
        for (i=0;i<8;++i) assert(r->valid->data[i] && r->sample_count[i]==5);
        detector_response_result_del(r); r=NULL;
        o.reference=reference; o.rois=(const int (*)[4])rois; o.roi_count=2;
        assert(cube_response_checked(c,&o,&r)==0);
        assert(!memcmp(r->normalized->data,norm->data,8*sizeof(pixelvalue)));
        detector_response_result_del(r); r=NULL; o.reference=NULL; o.rois=NULL; o.roi_count=0;
        image_del(norm); destroy_legacy(legacy,mode);
    }
    /* Reference excludes known defects; every pixel still measured. Known
     * response 0.25/1/2 and zero robust residual are checked independently. */
    for (j=0;j<5;++j) {
        for (i=0;i<8;++i) c->plane[j]->data[i]=(pixelvalue)((j+1)*16*(i==0?.25:i==7?2:1));
        memcpy(saved[j],c->plane[j]->data,sizeof(saved[j]));
    }
    reference->data[0]=reference->data[7]=0; o.reference=reference; o.proportional=0;
    assert(cube_response_checked(c,&o,&r)==0);
    assert(r->normalization==1 && r->normalized->data[0]==.25 && r->normalized->data[7]==2);
    assert(r->reasons[0]==4 && r->reasons[7]==8 && r->sample_count[0]==5);
    for (i=0;i<8;++i) assert(r->residual->data[i]==0);
    detector_response_result_del(r); r=NULL;
    /* The provisional two-flat case remains a slope test, not linearity. */
    c->np=2;
    assert(cube_response_checked(c,&o,&r)==0 && r->sample_count[0]==2 && r->normalized->data[0]==.25);
    detector_response_result_del(r); r=NULL; c->np=5;
    /* Missing measurements yield explicit coverage, not a bad-pixel reason.
     * One finite/saturation selection excludes a sample from a pixel only. */
    for (j=0;j<5;++j) samples[j]->data[2]=0;
    for (j=1;j<5;++j) samples[j]->data[5]=0;
    samples[0]->data[3]=0; o.samples=(const pixelmap *const *)samples;
    assert(cube_response_checked(c,&o,&r)==0);
    assert(r->sample_count[2]==0 && !r->valid->data[2] && !r->fit_state[2] && !r->reasons[2]);
    assert(r->sample_count[3]==4 && r->valid->data[3]);
    assert(r->sample_count[5]==1 && !r->valid->data[5] && !r->reasons[5]);
    detector_response_result_del(r); r=NULL;
    /* Strict equality endpoints are rejected. Nonfinite samples are excluded.
     * Invalid ROI/polarity/occupied output fail without input mutation. */
    o.low=.25; o.high=2;
    assert(cube_response_checked(c,&o,&r)==0 && r->reasons[0]==4 && r->reasons[7]==8);
    assert(cube_response_checked(c,&o,&r)==-1); detector_response_result_del(r); r=NULL;
    c->plane[0]->data[4]=NAN;
    assert(cube_response_checked(c,&o,&r)==0 && r->sample_count[4]==4);
    detector_response_result_del(r); r=NULL; c->plane[0]->data[4]=saved[0][4];
    reference->data[0]=2; assert(cube_response_checked(c,&o,&r)==-1 && !r); reference->data[0]=0;
    for (i=0;i<8;++i) samples[0]->data[i]=0;
    assert(cube_response_checked(c,&o,&r)==-1 && !r);
    for (i=0;i<8;++i) samples[0]->data[i]=1;
    o.rois=(const int (*)[4])rois; o.roi_count=2; rois[0][0]=0;
    assert(cube_response_checked(c,&o,&r)==-1 && !r); rois[0][0]=1; o.rois=NULL; o.roi_count=0;
    for (j=0;j<5;++j) assert(!memcmp(saved[j],c->plane[j]->data,sizeof(saved[j])));
    /* Degenerate x or zero normalization cannot manufacture a result. */
    for (j=0;j<5;++j) for (i=0;i<8;++i) c->plane[j]->data[i]=0;
    o.samples=NULL;
    assert(cube_response_checked(c,&o,&r)==-1 && !r);
    for (j=0;j<5;++j) pixelmap_del(samples[j]);
    pixelmap_del(reference); cube_del(c);
}
static void flags(void) {
    unsigned char raw[256], *copy=NULL;
    pixelmap *m=NULL;
    image_t *im=image_new(256,1);
    int i;
    FILE *stream;
    assert(im);
    for (i=0;i<256;++i) { raw[i]=(unsigned char)i; im->data[i]=(pixelvalue)i; }
    assert(pixelmap_flags8_from_image_checked(im,&copy)==0 && !memcmp(raw,copy,256));
    free(copy); copy=NULL;
    assert(pixelmap_flags8_selection_checked(raw,256,1,255,&m)==0 && m->ngoodpix==1);
    pixelmap_del(m); m=NULL;
    assert(pixelmap_flags8_selection_checked(raw,256,1,4,&m)==0 && m->ngoodpix==128);
    assert(m->data[8]==1 && m->data[4]==0); pixelmap_del(m); m=NULL;
    assert(pixelmap_flags8_selection_checked(raw,256,1,0,&m)==0 && m->ngoodpix==256);
    pixelmap_del(m); m=NULL;
    assert(pixelmap_flags8_selection_checked(raw,256,1,256,&m)==-1 && !m);
    im->data[100]=1.5; assert(pixelmap_flags8_from_image_checked(im,&copy)==-1 && !copy);
    im->data[100]=256; assert(pixelmap_flags8_from_image_checked(im,&copy)==-1 && !copy);
    im->data[100]=NAN; assert(pixelmap_flags8_from_image_checked(im,&copy)==-1 && !copy);
    /* Invalid registry writes nothing. Failed byte/header/flush never reports
     * success (Linux /dev/full when present; portable checks always above). */
    stream=tmpfile(); assert(stream);
    assert(pixelmap_flags8_write_checked(stream,raw,256,1,"invalid registry")==-1);
    assert(ftell(stream)==0); assert(fclose(stream)==0);
#ifdef __linux__
    stream=fopen("/dev/full","wb");
    if (stream) { assert(pixelmap_flags8_write_checked(stream,raw,256,1,"WENU_BPM_V1")==-1); fclose(stream); }
#endif
    image_del(im);
}
int main(int argc,char **argv) {
    unsigned char data[256], *readback=NULL;
    FILE *f;
    int i,x=-1,y=-1,hdu;
    if (argc==1) { numerical(); flags(); puts("PASS: legacy equality, masked references, ROI union, coverage, strict bounds, errors, byte flags"); return 0; }
    if (argc==3 && !strcmp(argv[1],"write")) {
        for (i=0;i<256;++i) data[i]=(unsigned char)i;
        f=fopen(argv[2],"wbx"); assert(f);
        assert(pixelmap_flags8_write_checked(f,data,256,1,"WENU_BPM_V1")==0);
        assert(fclose(f)==0);
        return 0;
    }
    assert(argc==4 && (!strcmp(argv[1],"read") || !strcmp(argv[1],"reject")));
    hdu=atoi(argv[3]);
    i=pixelmap_flags8_load_checked(argv[2],hdu,"WENU_BPM_V1",&readback,&x,&y);
    if (!strcmp(argv[1],"reject")) { assert(i==-1 && !readback && x==-1 && y==-1); return 0; }
    assert(i==0 && x==256 && y==1);
    for (i=0;i<256;++i) assert(readback[i]==(unsigned char)i);
    free(readback); return 0;
}
