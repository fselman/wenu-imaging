/* Known-answer numerical controls, using synthetic pixels only. */
#include "eclipse.h"
#include <assert.h>
#include <math.h>
#include <string.h>
static void close_to(double actual, double expected) {
    assert(fabs(actual-expected) < 1e-9 * (1+fabs(expected)));
}
/* Every request must preserve the selected results of the full estimator. */
static void check_selected(const image_t *image, const pixelmap *map, const int *zone)
{
    image_sample_stats full, actual, expected, sentinel;
    assert(image_getstats_masked_checked(image, map, zone, 1, &full) == 0);
    for (unsigned int fields = 1; fields < 16; ++fields) {
        assert(image_getstats_masked_selected_checked(image, map, zone, fields, &actual) == 0);
        expected = full;
        if (!(fields & IMAGE_SAMPLE_MEAN)) expected.mean = 0.0;
        if (!(fields & IMAGE_SAMPLE_STDEV)) {
            expected.stdev = 0.0; expected.stdev_available = 0;
        }
        if (!(fields & IMAGE_SAMPLE_MEDIAN)) expected.median = 0.0;
        if (!(fields & IMAGE_SAMPLE_MAD)) {
            expected.mad = 0.0; expected.mad_available = 0;
        }
        if (!(fields & (IMAGE_SAMPLE_MEAN | IMAGE_SAMPLE_MEDIAN)))
            expected.level_available = 0;
        assert(!memcmp(&actual, &expected, sizeof(actual)));
    }
    memset(&sentinel, 0x5a, sizeof(sentinel)); actual = sentinel;
    assert(image_getstats_masked_selected_checked(image, map, zone, 0, &actual) == -1);
    assert(!memcmp(&actual, &sentinel, sizeof(actual)));
    assert(image_getstats_masked_selected_checked(image, map, zone, 16, &actual) == -1);
    assert(!memcmp(&actual, &sentinel, sizeof(actual)));
}
int main(void) {
    image_t *a, *b;
    pixelmap *m, *n;
    image_sample_stats s, sentinel;
    pixelvalue saved[8];
    double values[4] = {1, 2, 3, 100}, median, mad;
    int roi[4] = {1,3,1,1}, invalid[4] = {0,2,1,1};
    int i;
    /* Maths scaffold: conventional even median, raw MAD, unchanged inputs. */
    assert(double_median_mad_checked(values, 4, 1, &median, &mad) == 0);
    close_to(median,2.5); close_to(mad,1); assert(values[3] == 100);
    median=17; mad=19; values[1]=NAN;
    assert(double_median_mad_checked(values,4,1,&median,&mad) == -1);
    assert(median==17 && mad==19);
    a=image_new(4,2); b=image_new(4,2); m=pixelmap_new(4,2); n=pixelmap_new(4,2);
    assert(a && b && m && n);
    for(i=0;i<8;++i) { a->data[i]=(pixelvalue)(i+1); b->data[i]=0; }
    a->data[7]=1000; m->data[7]=0; memcpy(saved,a->data,sizeof(saved));
    check_selected(a, m, NULL); check_selected(a, NULL, roi);
    /* Masked outlier: independent integers 1..7, sample variance 28/6. */
    assert(image_getstats_masked_checked(a,m,NULL,1,&s)==0);
    assert(s.valid_pixels==7 && s.bpm_excluded==1 && s.nonfinite_excluded==0);
    close_to(s.mean,4); close_to(s.median,4); close_to(s.stdev,sqrt(28.0/6)); close_to(s.mad,2);
    assert(image_getstats_masked_checked(a,NULL,NULL,0,&s)==0 && s.mean>100 && !s.mad_available);
    assert(image_getstats_masked_checked(a,m,roi,1,&s)==0);
    close_to(s.mean,2); close_to(s.stdev,1); close_to(s.mad,1);
    memset(&sentinel,0x5a,sizeof(sentinel)); s=sentinel;
    assert(image_getstats_masked_checked(a,m,invalid,1,&s)==-1);
    assert(!memcmp(&s,&sentinel,sizeof(s)));
    m->data[0]=2;
    assert(image_getstats_masked_checked(a,m,NULL,1,&s)==-1 && !memcmp(&s,&sentinel,sizeof(s)));
    m->data[0]=1;
    check_selected(a, m, NULL);
    assert(!memcmp(a->data,saved,sizeof(saved)));
    /* Pair mask intersection excludes different bad pixels; inputs untouched. */
    n->data[0]=0;
    assert(image_pair_stats_checked(a,b,m,n,NULL,1,&s)==0);
    assert(s.valid_pixels==6 && s.bpm_excluded==2); close_to(s.mean,4.5);
    assert(!memcmp(a->data,saved,sizeof(saved)) && n->data[0]==0 && m->data[7]==0);
    /* Nonfinite partition, no good samples, one sample, valid zero MAD. */
    a->data[1]=NAN; a->data[2]=INFINITY; m->data[2]=0;
    assert(image_getstats_masked_checked(a,m,NULL,1,&s)==0);
    assert(s.nonfinite_excluded==1 && s.bpm_excluded==2 && s.valid_pixels==5);
    check_selected(a, m, NULL);
    memset(m->data,0,8);
    check_selected(a, m, NULL);
    assert(image_getstats_masked_checked(a,m,NULL,1,&s)==0 && !s.level_available && !s.stdev_available);
    m->data[0]=1;
    assert(image_getstats_masked_checked(a,m,NULL,1,&s)==0 && s.level_available && !s.stdev_available);
    close_to(s.mad,0);
    m->lx=3;
    assert(image_getstats_masked_checked(a,m,NULL,1,&s)==-1); m->lx=4;
    image_del(a); image_del(b); pixelmap_del(m); pixelmap_del(n);
    puts("PASS: BPM/ROI/counts, sample stdev, conventional median/MAD, raw pair intersection, errors and immutability");
    return 0;
}
