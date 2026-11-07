/* Shared private measurement contract; no optimizer or numerical defaults. */
#ifndef ECLIPSE_DETECTOR_MEASUREMENTS_INTERNAL_H
#define ECLIPSE_DETECTOR_MEASUREMENTS_INTERNAL_H
#include <stdint.h>
#include <limits.h>
#include <math.h>
#include <string.h>
#include "detector_joint.h"
static int joint_samples_valid(const detector_measurements *p)
{
    size_t m,a,j;int i;
    if(!p||p->amplifiers<1||p->sites<1||p->observations<1||!p->amplifier||
       !p->site||!p->observation)return 0;
    m=(size_t)p->observations;
    if((size_t)p->amplifiers>SIZE_MAX/sizeof(*p->amplifier)||
       (size_t)p->sites>SIZE_MAX/sizeof(*p->site)||m>SIZE_MAX/sizeof(*p->observation))return 0;
    for(a=0;a<(size_t)p->amplifiers;++a) {
        const detector_joint_amplifier *amp=p->amplifier+a;
        if(!memchr(amp->detector_id,0,64)||!memchr(amp->amplifier_id,0,64)||
           !amp->detector_id[0]||!amp->amplifier_id[0]||
           !isfinite(amp->signal_min)||!isfinite(amp->signal_max)||
           amp->signal_min<0||amp->signal_min>=amp->signal_max)return 0;
        for(j=0;j<a;++j) if(!strcmp(amp->detector_id,p->amplifier[j].detector_id)&&
            !strcmp(amp->amplifier_id,p->amplifier[j].amplifier_id))return 0;
    }
    for(i=0;i<p->sites;++i) {
        const detector_joint_site *s=p->site+i;
        if(s->amplifier<0||s->amplifier>=p->amplifiers||s->x<1||s->y<1)return 0;
        for(j=0;j<(size_t)i;++j)if(s->amplifier==p->site[j].amplifier&&
            s->x==p->site[j].x&&s->y==p->site[j].y)return 0;
    }
    for(i=0;i<p->observations;++i) {
        const detector_joint_observation *ob=p->observation+i;
        if(ob->site<0||ob->site>=p->sites||ob->input_index<0||!isfinite(ob->seconds)||
           ob->seconds<=0||!isfinite(ob->signal))return 0;
        a=(size_t)p->site[ob->site].amplifier;
        if(ob->signal<p->amplifier[a].signal_min||ob->signal>p->amplifier[a].signal_max)return 0;
        for(j=0;j<(size_t)i;++j)if(ob->input_index==p->observation[j].input_index) {
            if(ob->site==p->observation[j].site||ob->seconds!=p->observation[j].seconds)return 0;
        }
    }
    return 1;
}
static int joint_measurements_valid(const detector_measurements *p)
{
    size_t a,j,m;
    if(!joint_samples_valid(p)||!p->noise_factor||!p->noise_factor->m)return 0;
    m=(size_t)p->observations;
    if(p->noise_factor->nr!=p->observations||
       (p->noise_factor->nc!=1&&p->noise_factor->nc!=p->observations))return 0;
    if(p->noise_factor->nc!=1&&(m>SIZE_MAX/m||m*m>SIZE_MAX/sizeof(double)))return 0;
    for(a=0;a<m;++a) {
        if(p->noise_factor->nc==1) {
            if(!isfinite(p->noise_factor->m[a])||p->noise_factor->m[a]<=0)return 0;
        }else for(j=0;j<m;++j) {
            double v=p->noise_factor->m[a*m+j];
            if(!isfinite(v)||(a==j&&v<=0)||(j>a&&v!=0))return 0;
        }
    }
    return 1;
}

#endif
