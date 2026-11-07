/* Independent sorted-array oracle; production selection does not sort. */
#include "pixelmap_flags8.h"
#include <time.h>
static int clip_compare(const void *a,const void *b)
{ double x=*(const double *)a,y=*(const double *)b; return (x>y)-(x<y); }
static image_clipped_stats clip_oracle(const image_t *a,const image_t *b,
    const pixelmap *m,const image_clip_options *o)
{
    image_clipped_stats c; double v[257]; size_t n=0;
    memset(&c,0,sizeof(c));
    for(int i=0;i<a->lx;++i) {
        ++c.sample.region_pixels;
        if(m && !m->data[i]) {++c.sample.bpm_excluded;continue;}
        pixelvalue d=(pixelvalue)(a->data[i]-b->data[i]);
        if(!isfinite(a->data[i])||!isfinite(b->data[i])||!isfinite(d)) {++c.sample.nonfinite_excluded;continue;}
        v[n++]=d;
    }
    for(;;) {
        double sum=0,ss=0;
        qsort(v,n,sizeof(*v),clip_compare);
        c.sample.valid_pixels=n;
        c.sample.level_available=n!=0;c.sample.stdev_available=n>1;
        c.sample.mean=c.sample.median=c.sample.stdev=0;
        if(n) {
            for(size_t i=0;i<n;++i)sum+=v[i];
            c.sample.mean=sum/n;
            c.sample.median=(v[(n-1)/2]+v[n/2])/2;
            for(size_t i=0;i<n;++i)ss+=(v[i]-sum/n)*(v[i]-sum/n);
            if(n>1)c.sample.stdev=sqrt(ss/(n-1));
        }
        if(n<2||c.iterations==o->max_iterations)break;
        ++c.iterations;
        size_t k=0;
        for(size_t i=0;i<n;++i) {
            if(v[i]<c.sample.median-o->sigma_low*c.sample.stdev)++c.rejected_low;
            else if(v[i]>c.sample.median+o->sigma_high*c.sample.stdev)++c.rejected_high;
            else v[k++]=v[i];
        }
        if(k==n) {c.converged=1;break;}
        n=k;
    }
    return c;
}
static void clipping_contract(void)
{
    unsigned int state=113;
    for(int trial=0;trial<300;++trial) {
        int n=1+trial%257;
        image_t *a=image_new(n,1),*b=image_new(n,1);
        pixelmap *m=pixelmap_new(n,1);
        image_clip_options o={trial%2?1.5:3.0,trial%3?2.0:4.0,trial%4?10:1};
        image_clipped_stats c,ref,saved;
        pixelvalue before[257];
        assert(a&&b&&m);
        for(int i=0;i<n;++i) {
            state=state*1664525u+1013904223u;
            a->data[i]=(pixelvalue)((int)(state%19)-9);b->data[i]=0;
            if(i%29==0)a->data[i]=120;
            if(i%13==0)m->data[i]=0;
        }
        if(trial%5==0)a->data[n-1]=NAN;
        if(trial%7==0)b->data[n/2]=INFINITY;
        memcpy(before,a->data,(size_t)n*sizeof(*before));
        assert(image_pair_stats_clipped_checked(a,b,m,NULL,NULL,&o,&c)==0);
        ref=clip_oracle(a,b,m,&o);
        assert(c.sample.valid_pixels==ref.sample.valid_pixels && c.rejected_low==ref.rejected_low &&
            c.rejected_high==ref.rejected_high && c.iterations==ref.iterations && c.converged==ref.converged);
        assert(c.sample.bpm_excluded==ref.sample.bpm_excluded && c.sample.nonfinite_excluded==ref.sample.nonfinite_excluded);
        assert(fabs(c.sample.mean-ref.sample.mean)<1e-10 && c.sample.median==ref.sample.median &&
            fabs(c.sample.stdev-ref.sample.stdev)<1e-10);
        assert(c.sample.region_pixels==c.sample.valid_pixels+c.sample.bpm_excluded+
            c.sample.nonfinite_excluded+c.rejected_low+c.rejected_high);
        assert(!memcmp(before,a->data,(size_t)n*sizeof(*before)));
        saved=c;o.sigma_low=0;
        assert(image_pair_stats_clipped_checked(a,b,m,NULL,NULL,&o,&c)==-1 && !memcmp(&saved,&c,sizeof(c)));
        image_del(a);image_del(b);pixelmap_del(m);
    }
    {
        image_t *a=image_new(4,1); image_clipped_stats c;
        image_clip_options o={5,5,10}; int zone[4]={2,3,1,1};
        a->data[0]=1;a->data[1]=2;a->data[2]=3;a->data[3]=4;
        assert(!image_getstats_clipped_checked(a,NULL,NULL,&o,&c) && c.sample.median==2.5 && c.converged);
        assert(!image_getstats_clipped_checked(a,NULL,zone,&o,&c) && c.sample.median==2.5 && c.sample.valid_pixels==2);
        for(int i=0;i<4;++i)a->data[i]=7;
        assert(!image_getstats_clipped_checked(a,NULL,NULL,&o,&c) && c.sample.stdev==0 && c.converged);
        zone[0]=0; assert(image_getstats_clipped_checked(a,NULL,zone,&o,&c)==-1);
        image_del(a);
    }
    {
        const unsigned char flags[]={0,1,2,128,255,0}; unsigned char saved[6];
        pixelmap *m=NULL;memcpy(saved,flags,6);
        assert(!pixelmap_flags8_selection_checked(flags,6,1,255,&m));
        assert(m->ngoodpix==2 && m->data[0] && m->data[5]);pixelmap_del(m);m=NULL;
        assert(!pixelmap_flags8_selection_checked(flags,6,1,1,&m));
        assert(m->ngoodpix==4 && m->data[2] && m->data[3]);pixelmap_del(m);
        assert(!memcmp(saved,flags,6));
    }
    puts("PASS: 300 independent sorted clipping oracles, finite/mask partitions, ties, even medians, limits and immutable reason bytes");
}
static void clipping_benchmark(void)
{
    image_t *a=image_new(2048,4100),*b=image_new(2048,4100);
    image_clip_options o={5,5,10}; image_clipped_stats c; clock_t start;
    size_t n=2048u*4100u;
    assert(a&&b);
    for(size_t i=0;i<n;++i) {a->data[i]=(pixelvalue)((int)(i%17)-8);b->data[i]=0;}
    a->data[111]=1000;
    start=clock(); assert(!image_pair_stats_clipped_checked(a,b,NULL,NULL,NULL,&o,&c));
    assert(c.converged && c.rejected_high==1 && c.sample.valid_pixels==n-1);
    printf("BENCHMARK pixels=%lu iterations=%d scratch_bytes=%lu cpu_seconds=%.6f\n",
        (unsigned long)n,c.iterations,(unsigned long)(n*sizeof(double)),(double)(clock()-start)/CLOCKS_PER_SEC);
    image_del(a);image_del(b);
}
static void mask_policy_contract(const char *directory)
{
    const unsigned char flags[6]={0,1,2,128,255,0};
    unsigned char binary[2][6]={{1,0,0,0,0,1},{0,1,1,1,1,0}};
    mef_bpm_policy p;pixelmap *expected=NULL;
    assert(!pixelmap_flags8_selection_checked(flags,6,1,255,&expected));
    for(int kind=0;kind<3;++kind) {
        char path[4096];FILE *f;mef_layout *layout=NULL;mef_layout_map *map=NULL;
        mef_layout_options o;mef_detector_binding b;pixelmap *selected=NULL;
        snprintf(path,sizeof(path),"%s/mask-%d.fits",directory,kind);
        f=fopen(path,"wx");assert(f);
        assert(!pixelmap_flags8_write_checked(f,kind==2?flags:binary[kind],6,1,"WENU_BPM_V1"));assert(!fclose(f));
        memset(&o,0,sizeof(o));o.max_hdus=4;o.max_header_bytes=65536;
        memset(&b,0,sizeof(b));b.detector_id="D";b.unit="mask";b.readout_id="explicit";
        b.bin_x=b.bin_y=b.active_x=b.active_y=1;b.active_width=6;b.active_height=1;
        b.health=MEF_HEALTH_UNKNOWN;b.selection=MEF_OUTPUT_SELECTED;
        assert(mef_layout_read(path,&o,NULL,&layout,NULL)==MEF_OK);
        assert(mef_layout_bind(layout,&b,1,NULL,&map,NULL)==MEF_OK);mef_layout_destroy(layout);
        memset(&p,0,sizeof(p));p.supplied=1;p.encoding=kind==2?MEF_BPM_REASON8:MEF_BPM_BINARY;
        p.bad_when_nonzero=kind!=0;p.reject_bits=255;strcpy(p.registry,"WENU_BPM_V1");
        assert(mef_layout_load_bpm_policy(map,"D",&p,&selected,NULL)==MEF_OK);
        assert(!memcmp(selected->data,expected->data,6));pixelmap_del(selected);selected=NULL;
        if(kind==2) {
            assert(mef_layout_load_bpm(map,"D",0,&selected,NULL)!=MEF_OK && !selected);
            strcpy(p.registry,"WRONG");assert(mef_layout_load_bpm_policy(map,"D",&p,&selected,NULL)!=MEF_OK && !selected);
        }
        assert(mef_bpm_policy_matches(&p,p.encoding,p.bad_when_nonzero?0:1,p.reject_bits,p.registry));
        if(kind<2)assert(!mef_bpm_policy_matches(&p,p.encoding,p.bad_when_nonzero?1:0,p.reject_bits,p.registry));
        mef_layout_map_destroy(map);
    }
    pixelmap_del(expected);
    puts("PASS: identical native FITS selections for both binary polarities and reason bytes 0/1/2/128/255; wrong registry and binary reinterpretation refused");
}
