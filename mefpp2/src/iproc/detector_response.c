#include "detector_response.h"
#include "median.h"
#include "doubles.h"
#include <float.h>
#include <string.h>

static int finite_number(double x) { return x == x && x >= -DBL_MAX && x <= DBL_MAX; }
static int dimensions(int x, int y) {
    return x > 0 && y > 0 && x <= MAX_COLUMN_NUMBER && y <= MAX_LINE_NUMBER &&
        x <= INT_MAX/y && (size_t)x <= (size_t)-1/(size_t)y/sizeof(pixelvalue) &&
        (size_t)x <= (size_t)-1/(size_t)y/sizeof(int);
}
static int map_valid(const pixelmap *m, int x, int y) {
    int i;
    if (!m) return 1;
    if (!m->data || m->lx != x || m->ly != y) return 0;
    for (i=0; i<x*y; ++i) if (m->data[i] != 0 && m->data[i] != 1) return 0;
    return 1;
}
void detector_response_result_del(detector_response_result *r) {
    if (!r) return;
    image_del(r->slope); image_del(r->intercept); image_del(r->residual);
    image_del(r->normalized); pixelmap_del(r->valid);
    free(r->sample_count); free(r->fit_state); free(r->reasons);
    free(r->reference_levels); free(r);
}
int cube_response_checked(const cube_t *c, const detector_response_options *o,
    detector_response_result **out) {
    detector_response_result *r = NULL;
    pixelvalue *buffer = NULL;
    unsigned char *reference = NULL;
    double3 line;
    double *fit = NULL, minimum, maximum, sum;
    size_t k;
    int i, j, x, y, n, used, normalization_count, npix, status = -1;
    memset(&line, 0, sizeof(line));
    if (!out || *out || !c || !o || !dimensions(c->lx,c->ly) || !c->plane ||
        c->np < 2 || c->np > MAX_IMAGE_NUMBER ||
        (o->proportional != 0 && o->proportional != 1) ||
        !finite_number(o->low) || !finite_number(o->high) || o->low >= o->high ||
        ((o->roi_count != 0) != (o->rois != NULL)) ||
        !map_valid(o->reference,c->lx,c->ly)) return -1;
    npix=c->lx*c->ly;
    for (j=0;j<c->np;++j) {
        if (!c->plane[j] || !c->plane[j]->data || c->plane[j]->lx!=c->lx ||
            c->plane[j]->ly!=c->ly || (o->samples &&
            !map_valid(o->samples[j],c->lx,c->ly))) return -1;
    }
    for (k=0;k<o->roi_count;++k) {
        const int *z=o->rois[k];
        if (z[0]<1 || z[1]<z[0] || z[1]>c->lx ||
            z[2]<1 || z[3]<z[2] || z[3]>c->ly) return -1;
    }
    r=calloc(1,sizeof(*r));
    buffer=malloc((size_t)npix*sizeof(*buffer));
    reference=calloc((size_t)npix,1);
    line.x=malloc((size_t)c->np*sizeof(double));
    line.y=malloc((size_t)c->np*sizeof(double));
    if (!r || !buffer || !reference || !line.x || !line.y) goto done;
    r->plane_count=c->np; r->proportional=o->proportional;
    r->reference_levels=malloc((size_t)c->np*sizeof(double));
    r->sample_count=calloc((size_t)npix,sizeof(int));
    r->fit_state=calloc((size_t)npix,1); r->reasons=calloc((size_t)npix,1);
    r->slope=image_new(c->lx,c->ly); r->residual=image_new(c->lx,c->ly);
    r->intercept=image_new(c->lx,c->ly); r->valid=pixelmap_new(c->lx,c->ly);
    if (!r->reference_levels || !r->sample_count || !r->fit_state || !r->reasons ||
        !r->slope || !r->residual || !r->intercept || !r->valid) goto done;
    memset(r->valid->data,0,(size_t)npix);
    for (i=0;i<npix;++i) {
        x=i%c->lx+1; y=i/c->lx+1;
        used=o->roi_count==0;
        for (k=0;k<o->roi_count && !used;++k) {
            const int *z=o->rois[k];
            used=x>=z[0] && x<=z[1] && y>=z[2] && y<=z[3];
        }
        reference[i]=(unsigned char)(used && (!o->reference || o->reference->data[i]));
    }
    for (j=0;j<c->np;++j) {
        n=0;
        for (i=0;i<npix;++i) if (reference[i] &&
            (!o->samples || !o->samples[j] || o->samples[j]->data[i]) &&
            finite_number(c->plane[j]->data[i])) buffer[n++]=c->plane[j]->data[i];
        if (!n) goto done;
        r->reference_levels[j]=(double)median_pixelvalue(buffer,n);
        if (!finite_number(r->reference_levels[j])) goto done;
    }
    for (i=0;i<npix;++i) {
        n=0; minimum=DBL_MAX; maximum=-DBL_MAX;
        for (j=0;j<c->np;++j) {
            double level=r->reference_levels[j];
            if ((o->samples && o->samples[j] && !o->samples[j]->data[i]) ||
                !finite_number(c->plane[j]->data[i]) ||
                (o->proportional && fabs(level)<=1e-30)) continue;
            line.x[n]=level; line.y[n]=c->plane[j]->data[i]; ++n;
            if (level<minimum) minimum=level;
            if (level>maximum) maximum=level;
        }
        r->sample_count[i]=n;
        if ((!o->proportional && (n<2 || minimum==maximum)) || !n) continue;
        line.n=n;
        fit=o->proportional ? fit_proportional(&line) : fit_slope_robust(&line);
        if (!fit) goto done;
        r->slope->data[i]=(pixelvalue)fit[o->proportional ? 0 : 1];
        r->intercept->data[i]=(pixelvalue)(o->proportional ? 0 : fit[0]);
        r->residual->data[i]=(pixelvalue)fit[o->proportional ? 1 : 2];
        free(fit); fit=NULL;
        if (!finite_number(r->slope->data[i]) || !finite_number(r->intercept->data[i]) ||
            !finite_number(r->residual->data[i])) continue;
        r->valid->data[i]=1;
        r->fit_state[i]=(unsigned char)(!o->proportional && r->residual->data[i]<0 ? 2 : 1);
    }
    sum=0; normalization_count=0;
    for (i=0;i<npix;++i) if (reference[i] && r->valid->data[i]) {
        sum+=(double)r->slope->data[i]; ++normalization_count;
    }
    if (!normalization_count) goto done;
    r->normalization=sum/(double)normalization_count;
    if (!finite_number(r->normalization) || fabs(r->normalization)<1e-10) goto done;
    r->normalized=image_cst_op(r->slope,r->normalization,'/');
    if (!r->normalized) goto done;
    for (i=0;i<npix;++i) if (r->valid->data[i]) {
        double value=r->normalized->data[i];
        if (!finite_number(value)) { r->valid->data[i]=0; r->fit_state[i]=0; continue; }
        if (value<=o->low) r->reasons[i]|=4;
        if (value>=o->high) r->reasons[i]|=8;
    }
    pixelmap_updatecount(r->valid);
    *out=r; r=NULL; status=0;
done:
    free(fit); free(buffer); free(reference); free(line.x); free(line.y);
    detector_response_result_del(r);
    return status;
}
