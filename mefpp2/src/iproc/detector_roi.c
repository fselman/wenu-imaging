/* Exact recorded ROI operators and covariance propagation. */
#include "detector_roi.h"
#include "detector_measurements_internal.h"
#include "dstats.h"

/* Checked ownership uses qfits accounting, unlike unchecked legacy matrix_new. */
static matrix *roi_matrix_new(int nr,int nc,size_t limit)
{
    matrix *m;size_t count;
    if(nr<1||nc<1||(size_t)nr>SIZE_MAX/(size_t)nc)return NULL;
    count=(size_t)nr*(size_t)nc;
    if(count>limit||count>SIZE_MAX/sizeof(double))return NULL;
    m=calloc(1,sizeof(*m));if(!m)return NULL;
    m->nr=nr;m->nc=nc;m->m=calloc(count,sizeof(double));
    if(!m->m){free(m);return NULL;}return m;
}
static void roi_matrix_del(matrix *m)
{ if(m){if(m->m)free(m->m);free(m);} }
void detector_roi_result_del(detector_roi_result *r)
{
    if(!r)return;
    if(r->roi)free(r->roi);
    if(r->row)free(r->row);
    if(r->offset)free(r->offset);
    if(r->member)free(r->member);
    if(r->active_to_row)free(r->active_to_row);
    if(r->union_index)free(r->union_index);
    if(r->amplifier)free(r->amplifier);
    if(r->site)free(r->site);
    if(r->observation)free(r->observation);
    if(r->dimensions)free(r->dimensions);
    if(r->factor_to_active)free(r->factor_to_active);
    roi_matrix_del(r->source_noise_factor);roi_matrix_del(r->projected);
    roi_matrix_del(r->latent_factor);roi_matrix_del(r->covariance);
    roi_matrix_del(r->noise_factor);matrix_qr_result_del(r->factor_qr);free(r);
}
static int roi_contains(const detector_roi *roi,const detector_joint_site *site)
{
    return roi->amplifier==site->amplifier&&site->x>=roi->xmin&&site->x<=roi->xmax&&
        site->y>=roi->ymin&&site->y<=roi->ymax;
}
int detector_roi_aggregate_checked(const detector_roi_problem *p,detector_roi_result **out)
{
    detector_roi_result *r=NULL;const detector_measurements *d;
    int *frames=NULL,*obs_use=NULL,*site_use=NULL;double *times=NULL,*values=NULL,*rhs_values=NULL,*scales=NULL;
    matrix *transpose=NULL,view,rhs;size_t m,rows,total=0,i,j,k,a,b,frame_count=0,active=0,ncols,nrhs;
    int index;
    if(!out||*out||!p||!joint_measurements_valid(&p->data)||p->rois<1||!p->roi||
       !p->dimensions||!isfinite(p->covariance_rank_tolerance)||p->covariance_rank_tolerance<=0||
       p->covariance_rank_tolerance>=1||!isfinite(p->max_factor_condition)||p->max_factor_condition<1||
       !p->max_dense_elements)return -1;
    d=&p->data;m=(size_t)d->observations;
    for(i=0;i<(size_t)d->amplifiers;++i)if(p->dimensions[i][0]<1||p->dimensions[i][1]<1)return -1;
    for(i=0;i<(size_t)d->sites;++i)if(d->site[i].x>p->dimensions[d->site[i].amplifier][0]||
        d->site[i].y>p->dimensions[d->site[i].amplifier][1])return -1;
    if((size_t)p->rois>SIZE_MAX/sizeof(*p->roi))return -1;
    for(i=0;i<(size_t)p->rois;++i) {
        const detector_roi *q=p->roi+i;
        if(!memchr(q->roi_id,0,64)||!q->roi_id[0]||q->amplifier<0||q->amplifier>=d->amplifiers||
           q->xmin<1||q->ymin<1||q->xmin>q->xmax||q->ymin>q->ymax||
           q->xmax>p->dimensions[q->amplifier][0]||q->ymax>p->dimensions[q->amplifier][1])return -1;
        for(j=0;j<i;++j)if(!strcmp(q->roi_id,p->roi[j].roi_id))return -1;
    }
    if(p->pixel_vectors) {
        if(p->pixel_vectors->nr!=d->observations||p->pixel_vectors->nc<1||!p->pixel_vectors->m||
           m>SIZE_MAX/(size_t)p->pixel_vectors->nc||
           m*(size_t)p->pixel_vectors->nc>SIZE_MAX/sizeof(double))return -1;
        for(i=0;i<m*(size_t)p->pixel_vectors->nc;++i)if(!isfinite(p->pixel_vectors->m[i]))return -1;
    }
    r=calloc(1,sizeof(*r));if(!r)goto fail;
    r->amplifiers=d->amplifiers;r->sites=d->sites;r->observations=d->observations;r->rois=p->rois;
    r->covariance_rank_tolerance=p->covariance_rank_tolerance;r->max_factor_condition=p->max_factor_condition;
    r->max_dense_elements=p->max_dense_elements;
    frames=malloc(m*sizeof(int));times=malloc(m*sizeof(double));values=malloc(m*sizeof(double));
    obs_use=calloc(m,sizeof(int));site_use=calloc((size_t)d->sites,sizeof(int));
    if(!frames||!times||!values||!obs_use||!site_use)goto fail;
    for(i=0;i<m;++i) {
        for(j=0;j<frame_count;++j)if(frames[j]==d->observation[i].input_index)break;
        if(j==frame_count){frames[j]=d->observation[i].input_index;times[j]=d->observation[i].seconds;++frame_count;}
    }
    if((size_t)p->rois>SIZE_MAX/frame_count)goto fail;
    rows=(size_t)p->rois*frame_count;
    if(rows>INT_MAX||rows>SIZE_MAX/sizeof(*r->row)||(rows+1)>SIZE_MAX/sizeof(size_t))goto fail;
    r->frames=(int)frame_count;r->rows=(int)rows;
    r->roi=malloc((size_t)p->rois*sizeof(*r->roi));r->row=calloc(rows,sizeof(*r->row));
    r->offset=calloc(rows+1,sizeof(size_t));r->active_to_row=malloc(rows*sizeof(int));
    r->union_index=malloc(m*sizeof(int));
    r->amplifier=malloc((size_t)d->amplifiers*sizeof(*r->amplifier));
    r->site=malloc((size_t)d->sites*sizeof(*r->site));r->observation=malloc(m*sizeof(*r->observation));
    r->dimensions=malloc((size_t)d->amplifiers*sizeof(*r->dimensions));
    r->source_noise_factor=roi_matrix_new(d->noise_factor->nr,d->noise_factor->nc,p->max_dense_elements);
    if(!r->roi||!r->row||!r->offset||!r->active_to_row||!r->union_index||!r->amplifier||
       !r->site||!r->observation||!r->dimensions||!r->source_noise_factor)goto fail;
    memcpy(r->roi,p->roi,(size_t)p->rois*sizeof(*r->roi));
    memcpy(r->amplifier,d->amplifier,(size_t)d->amplifiers*sizeof(*r->amplifier));
    memcpy(r->site,d->site,(size_t)d->sites*sizeof(*r->site));memcpy(r->observation,d->observation,m*sizeof(*r->observation));
    memcpy(r->dimensions,p->dimensions,(size_t)d->amplifiers*sizeof(*r->dimensions));
    memcpy(r->source_noise_factor->m,d->noise_factor->m,m*(size_t)d->noise_factor->nc*sizeof(double));
    for(i=0;i<(size_t)p->rois;++i)for(j=0;j<i;++j) {
        const detector_roi *x=p->roi+i,*y=p->roi+j;
        if(x->amplifier==y->amplifier&&x->xmin<=y->xmax&&y->xmin<=x->xmax&&
           x->ymin<=y->ymax&&y->ymin<=x->ymax) {
            if(r->geometric_overlap_pairs==SIZE_MAX)goto fail;
            ++r->geometric_overlap_pairs;
        }
    }
    for(i=0;i<(size_t)p->rois;++i)for(j=0;j<frame_count;++j) {
        size_t row=i*frame_count+j;
        r->row[row].roi=(int)i;r->row[row].input_index=frames[j];r->row[row].seconds=times[j];
        r->row[row].mean=NAN;
        for(k=0;k<m;++k)if(d->observation[k].input_index==frames[j]&&
            roi_contains(p->roi+i,d->site+d->observation[k].site))++r->row[row].count;
        if(r->row[row].count>SIZE_MAX-total)goto fail;
        total+=r->row[row].count;r->offset[row+1]=total;
        if(r->row[row].count)r->active_to_row[active++]=(int)row;
    }
    if(total>SIZE_MAX/sizeof(int))goto fail;
    if(total){r->member=malloc(total*sizeof(int));if(!r->member)goto fail;}
    for(i=0;i<rows;++i) {
        size_t used=0;
        for(k=0;k<m;++k)if(d->observation[k].input_index==r->row[i].input_index&&
            roi_contains(p->roi+r->row[i].roi,d->site+d->observation[k].site)) {
            r->member[r->offset[i]+used]=(int)k;values[used++]=d->observation[k].signal;
            ++obs_use[k];site_use[d->observation[k].site]=1;
        }
        if(used){r->row[i].mean=double_avg(values,(int)used);if(!isfinite(r->row[i].mean))goto fail;}
    }
    for(k=0;k<m;++k)if(obs_use[k]) {
        r->union_index[r->union_observations++]=(int)k;
        if(obs_use[k]>1)++r->shared_observations;
    }
    for(k=0;k<(size_t)d->sites;++k)if(site_use[k])++r->union_sites;
    r->active_rows=(int)active;r->status=DETECTOR_ROI_EMPTY;if(!active)goto done;
    r->latent_factor=roi_matrix_new((int)active,(int)m,p->max_dense_elements);
    r->covariance=roi_matrix_new((int)active,(int)active,p->max_dense_elements);
    if(!r->latent_factor||!r->covariance)goto fail;
    if(p->pixel_vectors){r->projected=roi_matrix_new((int)active,p->pixel_vectors->nc,p->max_dense_elements);if(!r->projected)goto fail;}
    for(a=0;a<active;++a) {
        size_t row=(size_t)r->active_to_row[a],count=r->row[row].count;
        for(k=0;k<m;++k) {
            for(j=0;j<count;++j) {
                index=r->member[r->offset[row]+j];
                values[j]=d->noise_factor->nc==1?(k==(size_t)index?d->noise_factor->m[index]:0):
                    d->noise_factor->m[(size_t)index*m+k];
            }
            r->latent_factor->m[a*m+k]=double_avg(values,(int)count);
            if(!isfinite(r->latent_factor->m[a*m+k]))goto fail;
        }
        if(p->pixel_vectors)for(k=0;k<(size_t)p->pixel_vectors->nc;++k) {
            for(j=0;j<count;++j)values[j]=p->pixel_vectors->m[(size_t)r->member[r->offset[row]+j]*(size_t)p->pixel_vectors->nc+k];
            r->projected->m[a*(size_t)p->pixel_vectors->nc+k]=double_avg(values,(int)count);
            if(!isfinite(r->projected->m[a*(size_t)p->pixel_vectors->nc+k]))goto fail;
        }
    }
    for(a=0;a<active;++a)for(b=0;b<active;++b) {
        double q=0;for(k=0;k<m;++k)q+=r->latent_factor->m[a*m+k]*r->latent_factor->m[b*m+k];
        if(!isfinite(q))goto fail;
        r->covariance->m[a*active+b]=q;
    }
    r->factor_qr_transposed=(active<=m);
    if(active<=m) {
        transpose=roi_matrix_new((int)m,(int)active,p->max_dense_elements);if(!transpose)goto fail;
        for(i=0;i<m;++i)for(j=0;j<active;++j)transpose->m[i*active+j]=r->latent_factor->m[j*m+i];
        view=*transpose;ncols=active;nrhs=m;
    }else {view=*r->latent_factor;ncols=m;nrhs=active;}
    rhs_values=calloc(nrhs,sizeof(double));scales=malloc(ncols*sizeof(double));
    if(!rhs_values||!scales)goto fail;
    for(i=0;i<ncols;++i)scales[i]=1;
    rhs.m=rhs_values;rhs.nr=(int)nrhs;rhs.nc=1;
    if(matrix_leastsq_qr_checked(&view,&rhs,scales,p->covariance_rank_tolerance,&r->factor_qr))goto fail;
    r->status=DETECTOR_ROI_COVARIANCE_RANK_UNAVAILABLE;
    if((size_t)r->factor_qr->rank<active)goto done;
    r->status=DETECTOR_ROI_COVARIANCE_CONDITION_UNAVAILABLE;
    if(!r->factor_qr->condition_available||r->factor_qr->scaled_condition_1>p->max_factor_condition)goto done;
    r->noise_factor=roi_matrix_new((int)active,(int)active,p->max_dense_elements);
    r->factor_to_active=malloc(active*sizeof(int));if(!r->noise_factor||!r->factor_to_active)goto fail;
    for(j=0;j<active;++j) {
        double sign=r->factor_qr->r->m[j*active+j]<0?-1:1;
        r->factor_to_active[j]=r->factor_qr->pivots[j];
        for(i=j;i<active;++i)r->noise_factor->m[i*active+j]=sign*r->factor_qr->r->m[j*active+i];
    }
    r->status=DETECTOR_ROI_READY;
done:
    if(frames)free(frames);
    if(times)free(times);
    if(values)free(values);
    if(obs_use)free(obs_use);
    if(site_use)free(site_use);
    if(rhs_values)free(rhs_values);
    if(scales)free(scales);
    roi_matrix_del(transpose);*out=r;return 0;
fail:
    if(frames)free(frames);
    if(times)free(times);
    if(values)free(values);
    if(obs_use)free(obs_use);
    if(site_use)free(site_use);
    if(rhs_values)free(rhs_values);
    if(scales)free(scales);
    roi_matrix_del(transpose);detector_roi_result_del(r);return -1;
}
