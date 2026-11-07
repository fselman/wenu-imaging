
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
#include "optimization.h"
typedef struct {
    double center[2],lo[2],hi[2],trace[64];
    int calls,mode,fail_at,invalid;
} cost_context;
static optimization_evaluation cost(const double *x,int n,void *data,double *y)
{
    cost_context *c=data;int j;++c->calls;
    if(c->calls<=64)c->trace[c->calls-1]=x[0];
    for(j=0;j<n;++j) assert(isfinite(x[j])&&x[j]>=c->lo[j]&&x[j]<=c->hi[j]);
    if(c->fail_at==c->calls) return OPTIMIZATION_EVAL_ERROR;
    if(c->mode==4){*y=NAN;return OPTIMIZATION_EVAL_VALID;}
    if(c->mode==5)return (optimization_evaluation)9;
    if(c->mode==6&&c->calls>2){++c->invalid;return OPTIMIZATION_EVAL_INADMISSIBLE;}
    if(c->mode==3&&x[0]<0){++c->invalid;return OPTIMIZATION_EVAL_INADMISSIBLE;}
    if(c->mode==2){*y=7;return OPTIMIZATION_EVAL_VALID;}
    if(c->mode==1){*y=100*pow(x[1]-x[0]*x[0],2)+pow(1-x[0],2);return OPTIMIZATION_EVAL_VALID;}
    *y=0;for(j=0;j<n;++j)*y+=pow((x[j]-c->center[j])/(j?1e-3:1),2);
    return OPTIMIZATION_EVAL_VALID;
}
static void setup(optimization_problem *p,optimization_options *o,cost_context *c,
    int n,double *x,double *scales,double *lo,double *hi)
{
    int j;memset(c,0,sizeof(*c));
    for(j=0;j<n;++j){c->lo[j]=lo[j];c->hi[j]=hi[j];}
    p->dimensions=n;p->initial_simplex=x;p->scales=scales;p->lower=lo;p->upper=hi;
    p->cost=cost;p->context=c;
    o->max_evaluations=3000;o->parameter_tolerance=1e-8;
    o->objective_tolerance=1e-12;o->initial_rank_tolerance=1e-12;
}
static double legacy_cost(double *x,double3 *unused)
{(void)unused;return (x[0]-1)*(x[0]-1);}
int main(void)
{
    double x[]={0,0,2,0,0,.002},s[]={1,.001},lo[]={-10,-10},hi[]={10,10};
    double saved[6];cost_context c;optimization_problem p;optimization_options o;
    optimization_result *out=NULL,*occupied;int i;
    memcpy(saved,x,sizeof x);setup(&p,&o,&c,2,x,s,lo,hi);c.center[0]=1.25;c.center[1]=-.0007;
    assert(minimize_checked(&p,&o,&out)==0&&out->status==OPTIMIZATION_CONVERGED);
    assert(fabs(out->parameters[0]-1.25)<1e-7&&fabs(out->parameters[1]+.0007)<1e-10);
    assert(out->parameter_spread<=o.parameter_tolerance&&out->objective_spread<=o.objective_tolerance);
    assert(out->callback_calls==(size_t)c.calls&&out->evaluations==out->callback_calls);
    occupied=out;assert(minimize_checked(&p,&o,&out)==-1&&out==occupied);
    optimization_result_del(out);out=NULL;assert(!memcmp(saved,x,sizeof x));
    {double xx[]={-1.2,1,-1,1,-1.2,1.2},ss[]={1,1};
     setup(&p,&o,&c,2,xx,ss,lo,hi);c.mode=1;
     assert(minimize_checked(&p,&o,&out)==0&&out->status==OPTIMIZATION_CONVERGED);
     assert(fabs(out->parameters[0]-1)<1e-6&&fabs(out->parameters[1]-1)<1e-6);
     optimization_result_del(out);out=NULL;}
    /* Independent 1D first-step oracles for expansion and both contractions. */
    for(i=0;i<3;++i){double xx[]={0,i==0?1:2},ss[]={1};
     setup(&p,&o,&c,1,xx,ss,lo,hi);c.center[0]=i==0?3:(i==1?.6:-.6);o.max_evaluations=4;
     assert(minimize_checked(&p,&o,&out)==0&&out->status==OPTIMIZATION_EVALUATION_LIMIT);
     assert(out->evaluations==4&&c.calls==4);
     assert(c.trace[2]==(i==0?2:-2));assert(c.trace[3]==(i==0?3:(i==1?1:-1)));
     assert(out->parameters[0]==c.trace[3]);optimization_result_del(out);out=NULL;}
    {double xx[]={0,2},ss[]={1};setup(&p,&o,&c,1,xx,ss,lo,hi);c.mode=2;o.max_evaluations=5;
     assert(minimize_checked(&p,&o,&out)==0&&out->status==OPTIMIZATION_EVALUATION_LIMIT);
     assert(c.trace[4]==1&&out->parameter_spread==1&&out->objective_spread==0);
     optimization_result_del(out);out=NULL;
     setup(&p,&o,&c,1,xx,ss,lo,hi);c.mode=2;
     assert(minimize_checked(&p,&o,&out)==0&&out->status==OPTIMIZATION_CONVERGED);
     assert(out->evaluations>5&&out->parameter_spread<=o.parameter_tolerance);
     optimization_result_del(out);out=NULL;}
    {double xx[]={.2,.8},ss[]={1},ll[]={0},hh[]={1};
     setup(&p,&o,&c,1,xx,ss,ll,hh);c.center[0]=3;o.max_evaluations=120;
     assert(minimize_checked(&p,&o,&out)==0&&out->bound_rejections>0);
     assert(out->parameters[0]>=.99&&out->parameters[0]<=1);
     assert(out->evaluations==out->callback_calls+out->bound_rejections);
     optimization_result_del(out);out=NULL;
     setup(&p,&o,&c,1,xx,ss,lo,hi);c.mode=3;c.center[0]=.3;
     assert(minimize_checked(&p,&o,&out)==0&&c.invalid>0&&out->status==OPTIMIZATION_CONVERGED);
     assert(fabs(out->parameters[0]-.3)<1e-7&&out->rejected_points==(size_t)c.invalid);
     optimization_result_del(out);out=NULL;
     setup(&p,&o,&c,1,xx,ss,lo,hi);c.mode=6;o.max_evaluations=20;
     assert(minimize_checked(&p,&o,&out)==0&&out->status==OPTIMIZATION_EVALUATION_LIMIT);
     assert(out->evaluations==20&&out->rejected_points==18);optimization_result_del(out);out=NULL;
     setup(&p,&o,&c,1,xx,ss,lo,hi);c.fail_at=3;assert(minimize_checked(&p,&o,&out)==-1&&!out);
     c.fail_at=0;c.calls=0;c.mode=4;assert(minimize_checked(&p,&o,&out)==-1&&!out);
     c.mode=5;assert(minimize_checked(&p,&o,&out)==-1&&!out);
     c.mode=3;xx[0]=-.2;assert(minimize_checked(&p,&o,&out)==-1&&!out);xx[0]=.2;
     c.mode=0;xx[1]=xx[0];assert(minimize_checked(&p,&o,&out)==-1&&!out);xx[1]=.8;
     s[0]=0;p.scales=s;assert(minimize_checked(&p,&o,&out)==-1&&!out);s[0]=1;
     o.max_evaluations=1;assert(minimize_checked(&p,&o,&out)==-1&&!out);
     o.max_evaluations=20;o.parameter_tolerance=NAN;assert(minimize_checked(&p,&o,&out)==-1&&!out);}
    {double xx[]={0,0,1,1,2,2},ss[]={1,1};setup(&p,&o,&c,2,xx,ss,lo,hi);
     assert(minimize_checked(&p,&o,&out)==-1&&!out);}
    {double aa[]={0},bb[]={3},*vertices[]={aa,bb};int neval;
     assert(minimize(vertices,1,1e-8,legacy_cost,NULL,&neval)==0);
     assert(fmin(legacy_cost(aa,NULL),legacy_cost(bb,NULL))<1e-12);}
    optimization_result_del(NULL);
    puts("PASS: checked simplex known minima, branch oracles, scaling, feasibility, budgets and legacy control");
    return 0;
}
