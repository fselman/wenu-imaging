/* Shared project processing policy. No process-global mutable mask state. */
#ifndef MEF_PROCESSING_H
#define MEF_PROCESSING_H
#include "mef_config.h"
typedef enum { MEF_BPM_BINARY = 1, MEF_BPM_REASON8 = 2 } mef_bpm_encoding;
typedef struct {
    int supplied;
    mef_bpm_encoding encoding;
    int bad_when_nonzero;
    unsigned int reject_bits;
    char registry[69];
} mef_bpm_policy;
typedef struct {
    mef_bpm_policy bpm;
    int ron_clip_supplied, ron_clip_enabled, ron_clip_max_iterations;
    double ron_clip_low, ron_clip_high;
} mef_processing_policy;
const mef_processing_policy *mef_config_processing(const mef_config *);
/* True for an unspecified project policy or an identical explicit caller policy. */
int mef_bpm_policy_matches(const mef_bpm_policy *, mef_bpm_encoding, int good_value,
    unsigned int reject_bits, const char *registry);
/* Reader-internal construction hook; call only before publishing a snapshot. */
void mef_config_initialize_processing(mef_config *, const mef_processing_policy *);
#endif
