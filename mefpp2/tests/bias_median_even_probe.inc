/* Sorted oracle is test-only; production uses in-place Wirth selection. */
#include "mef_bias_kernel.h"
#include <float.h>
#include <time.h>
static int median_compare(const void *a,const void *b)
{ pixelvalue x=*(const pixelvalue *)a,y=*(const pixelvalue *)b;return (x>y)-(x<y); }
static void median_even_contract(void)
{
    unsigned int state=29;
    for(int n=1;n<=32;++n)for(int trial=0;trial<100;++trial) {
        pixelvalue a[32],b[32],sorted[32],legacy[32];
        for(int i=0;i<n;++i){state=state*1664525u+1013904223u;a[i]=(pixelvalue)((int)(state%101)-50)/4;}
        memcpy(b,a,(size_t)n*sizeof(*a));memcpy(sorted,a,(size_t)n*sizeof(*a));memcpy(legacy,a,(size_t)n*sizeof(*a));
        qsort(sorted,(size_t)n,sizeof(*a),median_compare);
        pixelvalue expected=(pixelvalue)(0.5*(double)sorted[(n-1)/2]+0.5*(double)sorted[n/2]);
        assert(median_pixelvalue_opts(a,n,MEDIAN_EVEN_AVERAGE)==expected);
        assert(median_pixelvalue_opts(b,n,MEDIAN_EVEN_LOWER)==sorted[(n-1)/2]);
        /* The generic historical helper retains its special two-value average. */
        assert(median_pixelvalue(legacy,n)==(n==2?expected:sorted[(n-1)/2]));
    }
    {
        pixelvalue extreme[4]={FLT_MAX,FLT_MAX,FLT_MAX,FLT_MAX};
        assert(median_pixelvalue_opts(extreme,4,MEDIAN_EVEN_AVERAGE)==FLT_MAX);
    }
    for(int n=3;n<=10;++n) {
        cube_t *cube=cube_new(2,3,n);assert(cube);
        for(int j=0;j<n;++j){cube->plane[j]=image_new(2,3);assert(cube->plane[j]);for(int k=0;k<6;++k)cube->plane[j]->data[k]=(pixelvalue)(j-5+k);}
        image_t *avg=cube_avg_median_opts(cube,MEDIAN_EVEN_AVERAGE),*low=cube_avg_median(cube);
        assert(avg&&low);
        for(int k=0;k<6;++k) {
            assert(avg->data[k]==(pixelvalue)(0.5*(n-1)-5+k));
            assert(low->data[k]==(pixelvalue)((n-1)/2-5+k));
            for(int j=0;j<n;++j)assert(cube->plane[j]->data[k]==(pixelvalue)(j-5+k));
        }
        assert(!cube_avg_median_opts(cube,(median_even_handling)9));
        image_del(avg);image_del(low);cube_del(cube);
    }
    for(int mode=0;mode<2;++mode) {
        cube_t *cube=cube_new(1,1,10);mef_bias_statistics s;int used[10];
        for(int i=0;i<10;++i){cube->plane[i]=image_new(1,1);cube->plane[i]->data[0]=(pixelvalue)(i<5?i-5:i-4);}
        image_t *master=mode?mef_bias_stack_masked_opts(cube,3,100,&s,used,NULL,MEDIAN_EVEN_LOWER):mef_bias_stack(cube,3,100,&s,used);
        assert(master && master->data[0]==(mode?-1:0) && s.accepted==10);
        for(int i=0;i<10;++i)assert(used[i]);
        image_del(master);
    }
    puts("PASS: 3200 sorted median oracles, odd/even cubes, input preservation, legacy wrapper, finite midpoint and default-average/lower bias kernels");
}
static void median_even_benchmark(void)
{
    cube_t *cube=cube_new(2048,4100,10);size_t n=2048u*4100u;assert(cube);
    for(int j=0;j<10;++j){cube->plane[j]=image_new(2048,4100);assert(cube->plane[j]);for(size_t i=0;i<n;++i)cube->plane[j]->data[i]=(pixelvalue)((int)(i%17)+j);}
    for(int mode=0;mode<2;++mode) {
        clock_t start=clock();image_t *out=cube_avg_median_opts(cube,(median_even_handling)mode);assert(out);
        for(size_t i=0;i<n;++i)assert(out->data[i]==(pixelvalue)((int)(i%17)+(mode?4:4.5)));
        printf("BENCHMARK mode=%s pixels=%lu frames=10 timeline_bytes=%lu cpu_seconds=%.6f\n",mode?"lower":"average",(unsigned long)n,(unsigned long)(10*sizeof(pixelvalue)),(double)(clock()-start)/CLOCKS_PER_SEC);
        image_del(out);
    }
    cube_del(cube);
}
