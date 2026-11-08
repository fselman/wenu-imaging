/* Focused synthetic admission boundaries and native-service failure ownership. */
#include "mef_bias_kernel.h"
static cube_t *zero_spread_cube(int masked, int bracket, double step)
{
    cube_t *cube=cube_new(masked?3:2,1,3);
    assert(cube);
    for(int j=0;j<3;++j) {
        cube->plane[j]=image_new(masked?3:2,1);assert(cube->plane[j]);
        cube->plane[j]->data[0]=(pixelvalue)(100+j+(bracket?j-1:0)*step);
        cube->plane[j]->data[1]=(pixelvalue)(102-j+(bracket?j-1:0)*step);
        if(masked)cube->plane[j]->data[2]=(pixelvalue)(200+j);
    }
    return cube;
}
static void zero_spread_boundaries(void)
{
    for(int mode=0;mode<2;++mode)for(int masked=0;masked<2;++masked) {
        mef_bias_statistics s;int decisions[3]={-1,-1,-1};pixelmap *map=NULL;
        image_t *out;char *names[3]={"equal-a.fits","equal-b.fits","equal-c.fits"};
        mef_bias_diagnostic diagnostic={"ZERO-TEST",names};
        if(masked){map=pixelmap_new(3,1);assert(map);map->data[0]=map->data[1]=1;map->data[2]=0;pixelmap_updatecount(map);}
        /* Equal means from different pixel arrays fail before median stacking. */
        out=mef_bias_stack_masked_diagnostic(zero_spread_cube(masked,0,0),3,10,&s,decisions,map,(median_even_handling)mode,&diagnostic);
        assert(!out && s.measured && s.zero_spread && s.accepted==0);
        for(int i=0;i<3;++i)assert(decisions[i]==0);
        /* Strict nonzero endpoints: only the central frame is admitted. */
        out=mef_bias_stack_masked_opts(zero_spread_cube(masked,1,1),1,1,&s,decisions,map,(median_even_handling)mode);
        assert(!out && !s.zero_spread && !decisions[0] && decisions[1] && !decisions[2]);
        /* Existing temporal median also requires at least three planes. */
        out=mef_bias_stack_masked_opts(zero_spread_cube(masked,1,1),2,1,&s,decisions,map,(median_even_handling)mode);
        assert(!out && !s.zero_spread); /* Insufficient survivors remains a separate failure. */
        /* Minimum input count fails before measuring the spread. */
        out=mef_bias_stack_masked_opts(zero_spread_cube(masked,0,0),4,10,&s,decisions,map,(median_even_handling)mode);
        assert(!out && !s.measured && !s.zero_spread);
        pixelmap_del(map);
    }
    {
        /* A positive double spread can round to zero in legacy float QC. */
        cube_t *cube=cube_new(2,1,3);mef_bias_statistics s;int used[3];
        pixelvalue tiny=nextafterf(0.0f,1.0f);assert(tiny>0);
        for(int j=0;j<3;++j){cube->plane[j]=image_new(2,1);cube->plane[j]->data[0]=j*tiny;cube->plane[j]->data[1]=0;}
        image_t *out=mef_bias_stack(cube,3,10,&s,used);
        assert(out && !s.zero_spread && s.sigma==0 && s.accepted==3);image_del(out);
    }
    {
        /* Invalid unmasked mean must not be labelled zero-spread. */
        cube_t *cube=zero_spread_cube(0,0,0);mef_bias_statistics s;
        cube->plane[0]->data[0]=NAN;
        assert(!mef_bias_stack(cube,3,10,&s,NULL) && !s.zero_spread);
        pixelmap *map=pixelmap_new(2,1);assert(map);map->data[0]=map->data[1]=0;pixelmap_updatecount(map);
        assert(!mef_bias_stack_masked(zero_spread_cube(0,0,0),3,10,&s,NULL,map) && !s.zero_spread);
        pixelmap_del(map);
    }
    puts("PASS: zero-spread kernel boundaries; exact zero, masked/unmasked, both medians, strict endpoints, minimum inputs/survivors, tiny positive spread and invalid/empty populations");
}
static void zero_spread_service(mef_bb *legacy,int detector_index)
{
    image_t *frames[3];const image_t *borrowed[3];pixelvalue saved[3][60];
    mef_bias_input input;mef_bias_measurement_options options;
    legacy->bias_minframe=3;legacy->bias_kappa1=10;legacy->use_prescan=legacy->use_overscan=1;
    legacy->scanrej[0]=legacy->scanrej[1]=0;
    for(int i=0;i<3;++i){frames[i]=image_new(10,6);borrowed[i]=frames[i];assert(frames[i]);
        for(int j=0;j<60;++j)frames[i]->data[j]=(pixelvalue)(100+(j%2?i:-i));
        memcpy(saved[i],frames[i]->data,sizeof(saved[i]));}
    input.frames=borrowed;input.count=3;input.configuration_detector=(size_t)detector_index;
    for(int masked=0;masked<2;++masked) {
        mef_context *context=context_for(legacy,3,masked,NULL);
        mef_bias_result *result=NULL;mef_error *error=NULL;pixelmap *map=NULL;
        memset(&options,0,sizeof(options));options.high_sigma=5;
        if(masked){map=pixelmap_new(10,6);assert(map);for(int j=0;j<60;++j)map->data[j]=1;pixelmap_updatecount(map);options.bpm=map;}
        assert(mef_cal_bias_measurements(context,&input,&options,&result,&error)==MEF_ERR_COMPUTATION);
        assert(!result && error && strstr(mef_error_message(error),"zero-spread") && strstr(mef_error_message(error),"stopped before stacking"));
        mef_error_destroy(error);mef_context_destroy(context);pixelmap_del(map);
    }
    for(int i=0;i<3;++i){assert(!memcmp(saved[i],frames[i]->data,sizeof(saved[i])));image_del(frames[i]);}
    puts("PASS: zero-spread service; specific error, no output transfer, masked/unmasked and borrowed inputs unchanged");
}
