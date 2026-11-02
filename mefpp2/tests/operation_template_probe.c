/* Check phase ordering, early stop and cleanup of every partial operation. */
#include "mef_operation_template.h"
#include <assert.h>
#include <string.h>
typedef struct { int next, fail, cleaned; } state;
static mef_status step(state *s, int phase)
{
    assert(s->next == phase); ++s->next;
    return s->fail == phase ? MEF_ERR_COMPUTATION : MEF_OK;
}
static mef_status validate(void *s, mef_error **e) { (void)e; return step(s, 0); }
static mef_status load(void *s, mef_error **e) { (void)e; return step(s, 1); }
static mef_status calculate(void *s, mef_error **e) { (void)e; return step(s, 2); }
static mef_status publish(void *s, mef_error **e) { (void)e; return step(s, 3); }
static void cleanup(void *p) { state *s; s = p; assert(!s->cleaned); s->cleaned = 1; }
int main(void)
{
    mef_operation_steps steps;
    state s;
    int failure;
    steps.validate = validate; steps.load = load; steps.calculate = calculate;
    steps.publish = publish; steps.cleanup = cleanup;
    for (failure = -1; failure <= 3; ++failure) {
        memset(&s, 0, sizeof(s)); s.fail = failure;
        assert(mef_operation_run(&steps, &s, NULL) ==
            (failure == -1 ? MEF_OK : MEF_ERR_COMPUTATION));
        assert(s.cleaned && s.next == (failure == -1 ? 4 : failure + 1));
    }
    steps.publish = NULL; memset(&s, 0, sizeof(s)); s.fail = -1;
    assert(mef_operation_run(&steps, &s, NULL) == MEF_OK && s.next == 3 && s.cleaned);
    return 0;
}
