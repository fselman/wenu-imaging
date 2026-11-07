#include "detector_noise.h"
#include "detector_measurements_internal.h"
static matrix *noise_matrix(int rows,int columns,size_t limit)
{
    if(rows<1||columns<1||(size_t)rows>SIZE_MAX/(size_t)columns)return NULL;
    size_t n=(size_t)rows*(size_t)columns;
    if(n>limit||n>SIZE_MAX/sizeof(double))return NULL;
    matrix *v=calloc(1,sizeof *v);if(!v)return NULL;
    v->nr=rows;v->nc=columns;v->m=calloc(n,sizeof(double));
    if(!v->m){free(v);return NULL;}return v;
}
static void noise_matrix_del(matrix *v){if(v){if(v->m)free(v->m);free(v);}}
static int valid_factor(const matrix *v,int rows,size_t limit)
{
    if(!v||!v->m||v->nr!=rows||v->nc<1||(size_t)rows>SIZE_MAX/(size_t)v->nc)return 0;
    size_t n=(size_t)rows*(size_t)v->nc;
    if(n>limit||n>SIZE_MAX/sizeof(double))return 0;
    for(size_t i=0;i<n;++i)if(!isfinite(v->m[i]))return 0;
    return 1;
}
void detector_noise_result_del(detector_noise_result *r)
{
    if(!r)return;
    if(r->amplifier)free(r->amplifier);
    if(r->site)free(r->site);
    if(r->observation)free(r->observation);
    if(r->ordered_observation)free(r->ordered_observation);
    if(r->scan_group)free(r->scan_group);
    if(r->observation_to_scan)free(r->observation_to_scan);
    if(r->factor_to_observation)free(r->factor_to_observation);
    if(r->independent_variance)free(r->independent_variance);
    noise_matrix_del(r->master_factor);noise_matrix_del(r->scan_factor);
    noise_matrix_del(r->latent_factor);noise_matrix_del(r->covariance);noise_matrix_del(r->noise_factor);
    matrix_qr_result_del(r->factor_qr);free(r);
}
int detector_noise_measurements(const detector_noise_result *r,detector_measurements *out)
{
    if(!r||!out||r->status!=DETECTOR_NOISE_READY||!r->noise_factor||!r->ordered_observation)return -1;
    detector_measurements view={r->amplifiers,r->sites,r->observations,r->amplifier,r->site,r->ordered_observation,r->noise_factor};
    if(!joint_measurements_valid(&view))return -1;
    *out=view;return 0;
}
int detector_noise_assemble_checked(const detector_noise_problem *p,detector_noise_result **out)
{
    detector_noise_result *r=NULL;matrix *transpose=NULL;
    double *zeros=NULL,*scales=NULL;size_t m,kb,ks=0,cols;
    if(!p||!out||*out||p->data.noise_factor||!joint_samples_valid(&p->data)||
       !p->independent_variance||p->independent_components!=1||
       !isfinite(p->rank_tolerance)||p->rank_tolerance<=0||p->rank_tolerance>=1||
       !isfinite(p->max_factor_condition)||p->max_factor_condition<1||!p->max_dense_elements||
       (p->scan_applied!=0&&p->scan_applied!=1)||
       !valid_factor(p->master_factor,p->data.sites,p->max_dense_elements))return -1;
    m=(size_t)p->data.observations;kb=(size_t)p->master_factor->nc;
    if(p->scan_applied){
        if(p->scan_groups<1||!p->scan_group||!valid_factor(p->scan_factor,p->scan_groups,p->max_dense_elements)||
           (size_t)p->scan_groups>SIZE_MAX/sizeof(*p->scan_group))return -1;
        ks=(size_t)p->scan_factor->nc;
        for(int g=0;g<p->scan_groups;++g){const detector_noise_scan_group *q=p->scan_group+g;
            if(q->input_index<0||q->amplifier<0||q->amplifier>=p->data.amplifiers||q->y<1)return -1;
            for(int j=0;j<g;++j)if(q->input_index==p->scan_group[j].input_index&&
                q->amplifier==p->scan_group[j].amplifier&&q->y==p->scan_group[j].y)return -1;
        }
    }else if(p->scan_groups||p->scan_group||p->scan_factor)return -1;
    if(m>INT_MAX-kb||m+kb>INT_MAX-ks)return -1;
    cols=m+kb+ks;
    if(m>SIZE_MAX/cols||m*cols>p->max_dense_elements||m>SIZE_MAX/m||m*m>p->max_dense_elements)return -1;
    for(size_t i=0;i<m;++i)if(!isfinite(p->independent_variance[i])||p->independent_variance[i]<0)return -1;
    r=calloc(1,sizeof *r);if(!r)goto fail;
    r->amplifiers=p->data.amplifiers;r->sites=p->data.sites;r->observations=p->data.observations;
    r->scan_applied=p->scan_applied;r->scan_groups=p->scan_groups;
    r->rank_tolerance=p->rank_tolerance;r->max_factor_condition=p->max_factor_condition;r->max_dense_elements=p->max_dense_elements;
    r->amplifier=malloc((size_t)r->amplifiers*sizeof *r->amplifier);
    r->site=malloc((size_t)r->sites*sizeof *r->site);r->observation=malloc(m*sizeof *r->observation);
    r->independent_variance=malloc(m*sizeof(double));r->observation_to_scan=malloc(m*sizeof(int));
    r->master_factor=noise_matrix(p->master_factor->nr,p->master_factor->nc,p->max_dense_elements);
    r->latent_factor=noise_matrix((int)m,(int)cols,p->max_dense_elements);
    r->covariance=noise_matrix((int)m,(int)m,p->max_dense_elements);
    if(!r->amplifier||!r->site||!r->observation||!r->independent_variance||!r->observation_to_scan||
       !r->master_factor||!r->latent_factor||!r->covariance)goto fail;
    memcpy(r->amplifier,p->data.amplifier,(size_t)r->amplifiers*sizeof *r->amplifier);
    memcpy(r->site,p->data.site,(size_t)r->sites*sizeof *r->site);memcpy(r->observation,p->data.observation,m*sizeof *r->observation);
    memcpy(r->independent_variance,p->independent_variance,m*sizeof(double));
    memcpy(r->master_factor->m,p->master_factor->m,(size_t)p->master_factor->nr*kb*sizeof(double));
    if(p->scan_applied){
        r->scan_group=malloc((size_t)p->scan_groups*sizeof *r->scan_group);
        r->scan_factor=noise_matrix(p->scan_groups,(int)ks,p->max_dense_elements);
        if(!r->scan_group||!r->scan_factor)goto fail;
        memcpy(r->scan_group,p->scan_group,(size_t)p->scan_groups*sizeof *r->scan_group);
        memcpy(r->scan_factor->m,p->scan_factor->m,(size_t)p->scan_groups*ks*sizeof(double));
    }
    for(size_t i=0;i<m;++i){
        const detector_joint_observation *ob=r->observation+i;const detector_joint_site *site=r->site+ob->site;
        int group=-1;
        if(p->scan_applied){
            for(int g=0;g<p->scan_groups;++g)if(p->scan_group[g].input_index==ob->input_index&&
                p->scan_group[g].amplifier==site->amplifier&&p->scan_group[g].y==site->y)group=g;
            if(group<0)goto fail;
        }
        r->observation_to_scan[i]=group;
        double *row=r->latent_factor->m+i*cols;row[i]=sqrt(p->independent_variance[i]);
        for(size_t k=0;k<kb;++k)row[m+k]=-p->master_factor->m[(size_t)ob->site*kb+k];
        if(group>=0)for(size_t k=0;k<ks;++k)row[m+kb+k]=-p->scan_factor->m[(size_t)group*ks+k];
    }
    for(size_t i=0;i<m;++i)for(size_t j=0;j<m;++j){
        double value=0;for(size_t k=0;k<cols;++k)value+=r->latent_factor->m[i*cols+k]*r->latent_factor->m[j*cols+k];
        if(!isfinite(value))goto fail;
        r->covariance->m[i*m+j]=value;
    }
    transpose=noise_matrix((int)cols,(int)m,p->max_dense_elements);
    zeros=calloc(cols,sizeof(double));scales=malloc(m*sizeof(double));if(!transpose||!zeros||!scales)goto fail;
    for(size_t i=0;i<cols;++i)for(size_t j=0;j<m;++j)transpose->m[i*m+j]=r->latent_factor->m[j*cols+i];
    for(size_t i=0;i<m;++i)scales[i]=1;
    matrix rhs={zeros,(int)cols,1};
    if(matrix_leastsq_qr_checked(transpose,&rhs,scales,p->rank_tolerance,&r->factor_qr))goto fail;
    r->status=DETECTOR_NOISE_RANK_UNAVAILABLE;
    if(r->factor_qr->rank<(int)m)goto done;
    r->status=DETECTOR_NOISE_CONDITION_UNAVAILABLE;
    if(!r->factor_qr->condition_available||r->factor_qr->scaled_condition_1>p->max_factor_condition)goto done;
    r->noise_factor=noise_matrix((int)m,(int)m,p->max_dense_elements);
    r->ordered_observation=malloc(m*sizeof *r->ordered_observation);r->factor_to_observation=malloc(m*sizeof(int));
    if(!r->noise_factor||!r->ordered_observation||!r->factor_to_observation)goto fail;
    for(size_t i=0;i<m;++i){
        r->factor_to_observation[i]=r->factor_qr->pivots[i];
        r->ordered_observation[i]=r->observation[r->factor_to_observation[i]];
        for(size_t j=0;j<=i;++j){double diagonal=r->factor_qr->r->m[j*m+j];
            r->noise_factor->m[i*m+j]=r->factor_qr->r->m[j*m+i]*(diagonal<0?-1:1);}
    }
    r->status=DETECTOR_NOISE_READY;
done:
    noise_matrix_del(transpose);if(zeros)free(zeros);if(scales)free(scales);*out=r;return 0;
fail:
    noise_matrix_del(transpose);if(zeros)free(zeros);if(scales)free(scales);detector_noise_result_del(r);return -1;
}
