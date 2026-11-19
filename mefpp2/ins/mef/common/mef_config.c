/* Owned immutable snapshot adapter. Legacy numerical processing is untouched. */
#include "mef_config.h"
#include "mef_processing.h"
#include "mefp_lib.h"
#include <float.h>
#include <limits.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int prescan_x[2], overscan_x[2], trimreg[4];
    float ron, gain, crval1, crval2, crpix1, crpix2;
} mef_detector_config;

struct mef_config {
    mef_allocator allocator;
    mef_processing_policy processing;
    mef_detector_config *detectors;
#include "mef_config_members.h"
};

static void *default_allocate(void *user, size_t bytes)
{
    (void)user;
    /* Parentheses bypass Eclipse's function-like malloc/free macros. */
    return (malloc)(bytes);
}

static void default_release(void *user, void *pointer)
{
    (void)user;
    (free)(pointer);
}

static void release_owned(mef_config *config, void *pointer)
{
    if (pointer != NULL)
        config->allocator.release(config->allocator.user, pointer);
}

void mef_config_destroy(mef_config *config)
{
    mef_allocator allocator;
    if (config == NULL) return;
    allocator = config->allocator;
#define MEF_STRING(member, key) release_owned(config, config->member);
#define MEF_INT(member, key)
#define MEF_FLOAT(member, key)
#define MEF_DOUBLE(member, key)
#include "mef_config_fields.def"
#undef MEF_STRING
#undef MEF_INT
#undef MEF_FLOAT
#undef MEF_DOUBLE
    release_owned(config, config->detectors);
    allocator.release(allocator.user, config);
}

mef_status mef_config_from_legacy(const struct _mef_bb_ *source,
    const mef_allocator *allocator, mef_config **out, const char **diagnostic)
{
    mef_allocator selected;
    mef_config *config;
    size_t bytes;
    int i;
    mef_status status;
    const char *detail;
    if (diagnostic != NULL) *diagnostic = NULL;
    if (out == NULL || *out != NULL || source == NULL ||
        source->nchips <= 0 || source->ccd == NULL ||
        (source->bias_median_even_handling != MEDIAN_EVEN_AVERAGE &&
         source->bias_median_even_handling != MEDIAN_EVEN_LOWER) ||
        (allocator != NULL && (allocator->allocate == NULL ||
                               allocator->release == NULL))) {
        if (diagnostic != NULL) *diagnostic = "Invalid snapshot arguments";
        return MEF_ERR_CONFIG;
    }
    if ((size_t)source->nchips > (size_t)-1 / sizeof(mef_detector_config)) {
        if (diagnostic != NULL) *diagnostic = "Detector allocation size overflow";
        return MEF_ERR_MEMORY;
    }
    selected.user = NULL;
    selected.allocate = default_allocate;
    selected.release = default_release;
    if (allocator != NULL) selected = *allocator;
    config = selected.allocate(selected.user, sizeof(*config));
    if (config == NULL) {
        if (diagnostic != NULL) *diagnostic = "Cannot allocate snapshot";
        return MEF_ERR_MEMORY;
    }
    /* Initialize pointer members explicitly; do not assume all-zero NULL bits. */
    config->allocator = selected;
    memset(&config->processing, 0, sizeof(config->processing));
    config->processing.median_even_handling = source->bias_median_even_handling;
    config->processing.median_even_supplied = source->bias_median_even_handling != MEDIAN_EVEN_AVERAGE;
    config->detectors = NULL;
#define MEF_STRING(member, key) config->member = NULL;
#define MEF_INT(member, key) config->member = source->member;
#define MEF_FLOAT(member, key) config->member = source->member;
#define MEF_DOUBLE(member, key) config->member = source->member;
#include "mef_config_fields.def"
#undef MEF_STRING
#undef MEF_INT
#undef MEF_FLOAT
#undef MEF_DOUBLE
    status = MEF_ERR_MEMORY;
    detail = "Cannot allocate detector settings";
    bytes = (size_t)source->nchips * sizeof(*config->detectors);
    config->detectors = selected.allocate(selected.user, bytes);
    if (config->detectors == NULL) goto fail;
    for (i = 0; i < source->nchips; ++i) {
        memcpy(config->detectors[i].prescan_x, source->ccd[i].prescan_x,
               sizeof(config->detectors[i].prescan_x));
        memcpy(config->detectors[i].overscan_x, source->ccd[i].overscan_x,
               sizeof(config->detectors[i].overscan_x));
        memcpy(config->detectors[i].trimreg, source->ccd[i].trimreg,
               sizeof(config->detectors[i].trimreg));
        config->detectors[i].ron = source->ccd[i].ron;
        config->detectors[i].gain = source->ccd[i].gain;
        config->detectors[i].crval1 = source->ccd[i].crval1;
        config->detectors[i].crval2 = source->ccd[i].crval2;
        config->detectors[i].crpix1 = source->ccd[i].crpix1;
        config->detectors[i].crpix2 = source->ccd[i].crpix2;
    }
#define MEF_STRING(member, key) \
    if (source->member == NULL) { \
        status = MEF_ERR_CONFIG; detail = key; goto fail; \
    } \
    bytes = strlen(source->member); \
    if (bytes == (size_t)-1) { detail = key; goto fail; } \
    config->member = selected.allocate(selected.user, bytes + 1); \
    if (config->member == NULL) { detail = key; goto fail; } \
    memcpy(config->member, source->member, bytes + 1);
#define MEF_INT(member, key)
#define MEF_FLOAT(member, key)
#define MEF_DOUBLE(member, key)
#include "mef_config_fields.def"
#undef MEF_STRING
#undef MEF_INT
#undef MEF_FLOAT
#undef MEF_DOUBLE
    *out = config;
    return MEF_OK;
fail:
    mef_config_destroy(config);
    if (diagnostic != NULL) *diagnostic = detail;
    return status;
}


mef_status mef_config_clone(const mef_config *source, const mef_allocator *allocator,
    mef_config **out, const char **diagnostic)
{
    mef_allocator a;
    mef_config *copy;
    size_t bytes;
    const char *detail;
    if (diagnostic != NULL) *diagnostic = NULL;
    if (source == NULL || out == NULL || *out != NULL ||
        (allocator != NULL && (allocator->allocate == NULL || allocator->release == NULL))) {
        if (diagnostic != NULL) *diagnostic = "Invalid clone arguments";
        return MEF_ERR_CONFIG;
    }
    a.user = NULL;
    a.allocate = default_allocate;
    a.release = default_release;
    if (allocator != NULL) a = *allocator;
    copy = a.allocate(a.user, sizeof(*copy));
    if (copy == NULL) {
        if (diagnostic != NULL) *diagnostic = "Cannot allocate config clone";
        return MEF_ERR_MEMORY;
    }
    copy->allocator = a;
    copy->processing = source->processing;
    copy->detectors = NULL;
#define MEF_STRING(member, key) copy->member = NULL;
#define MEF_INT(member, key) copy->member = source->member;
#define MEF_FLOAT(member, key) copy->member = source->member;
#define MEF_DOUBLE(member, key) copy->member = source->member;
#include "mef_config_fields.def"
#undef MEF_STRING
#undef MEF_INT
#undef MEF_FLOAT
#undef MEF_DOUBLE
    /* The opaque source was constructed with the checked detector count. */
    bytes = (size_t)source->nchips * sizeof(*copy->detectors);
    detail = "Cannot allocate cloned detector settings";
    copy->detectors = a.allocate(a.user, bytes);
    if (copy->detectors == NULL) goto memory_failure;
    memcpy(copy->detectors, source->detectors, bytes);
#define MEF_STRING(member, key) \
    bytes = strlen(source->member); \
    detail = key; \
    if (bytes == (size_t)-1) goto memory_failure; \
    copy->member = a.allocate(a.user, bytes + 1); \
    if (copy->member == NULL) goto memory_failure; \
    memcpy(copy->member, source->member, bytes + 1);
#define MEF_INT(member, key)
#define MEF_FLOAT(member, key)
#define MEF_DOUBLE(member, key)
#include "mef_config_fields.def"
#undef MEF_STRING
#undef MEF_INT
#undef MEF_FLOAT
#undef MEF_DOUBLE
    *out = copy;
    return MEF_OK;
memory_failure:
    mef_config_destroy(copy);
    if (diagnostic != NULL) *diagnostic = detail;
    return MEF_ERR_MEMORY;
}

static void json_string(FILE *stream, const char *text)
{
    const unsigned char *p;
    fputc('"', stream);
    for (p = (const unsigned char *)text; *p != 0; ++p) {
        if (*p == '"' || *p == '\\') {
            fputc('\\', stream); fputc(*p, stream);
        } else if (*p < 32) {
            fprintf(stream, "\\u%04x", (unsigned int)*p);
        } else fputc(*p, stream);
    }
    fputc('"', stream);
}

static void bits(FILE *stream, const void *value, size_t size)
{
    unsigned char bytes[sizeof(double)];
    unsigned int endian;
    size_t i;
    endian = 1;
    memcpy(bytes, value, size);
    fputc('"', stream);
    for (i = 0; i < size; ++i)
        fprintf(stream, "%02x", (unsigned int)
            bytes[*(const unsigned char *)&endian ? size - 1 - i : i]);
    fputc('"', stream);
}

static void entry(FILE *stream, int *first, const char *key, const char *type)
{
    if (!*first) fputs(",\n", stream);
    *first = 0;
    json_string(stream, key);
    fputs(":{\"type\":", stream); json_string(stream, type);
    fputs(",\"value\":", stream);
}

mef_status mef_config_dump(const mef_config *config, FILE *stream)
{
    int first, i, j;
    char key[80];
    const mef_detector_config *d;
    if (config == NULL || stream == NULL) return MEF_ERR_CONFIG;
    if (CHAR_BIT != 8 || sizeof(float) != 4 || sizeof(double) != 8 ||
        FLT_RADIX != 2 || FLT_MANT_DIG != 24 || DBL_MANT_DIG != 53 ||
        FLT_MAX_EXP != 128 || DBL_MAX_EXP != 1024) return MEF_ERR_UNSUPPORTED;
    first = 1;
    fputs("{\n", stream);
#define MEF_STRING(member, key) entry(stream, &first, key, "string"); \
    json_string(stream, config->member); fputc('}', stream);
#define MEF_INT(member, key) entry(stream, &first, key, "int"); \
    fprintf(stream, "%d}", config->member);
#define MEF_FLOAT(member, key) entry(stream, &first, key, "float32-bits"); \
    bits(stream, &config->member, sizeof(float)); fputc('}', stream);
#define MEF_DOUBLE(member, key) entry(stream, &first, key, "float64-bits"); \
    bits(stream, &config->member, sizeof(double)); fputc('}', stream);
#include "mef_config_fields.def"
#undef MEF_STRING
#undef MEF_INT
#undef MEF_FLOAT
#undef MEF_DOUBLE
    for (i = 0; i < config->nchips; ++i) {
        d = config->detectors + i;
        for (j = 0; j < 2; ++j) {
            sprintf(key, "MEF.PRESCAN.X.%s.CHIP%d", j ? "MAX" : "MIN", i + 1);
            entry(stream, &first, key, "int"); fprintf(stream, "%d}", d->prescan_x[j]);
            sprintf(key, "MEF.OVERSCAN.X.%s.CHIP%d", j ? "MAX" : "MIN", i + 1);
            entry(stream, &first, key, "int"); fprintf(stream, "%d}", d->overscan_x[j]);
        }
        for (j = 0; j < 4; ++j) {
            sprintf(key, "MEF.CROP.%s.CHIP%d", j == 0 ? "X.MIN" : j == 1 ? "X.MAX" : j == 2 ? "Y.MIN" : "Y.MAX", i + 1);
            entry(stream, &first, key, "int"); fprintf(stream, "%d}", d->trimreg[j]);
        }
#define DET_FLOAT(member, name) \
        sprintf(key, name ".CHIP%d", i + 1); \
        entry(stream, &first, key, "float32-bits"); \
        bits(stream, &d->member, sizeof(float)); fputc('}', stream);
        DET_FLOAT(ron, "MEF.CCD.RON")
        DET_FLOAT(gain, "MEF.CCD.GAIN")
        DET_FLOAT(crval1, "MEF.CRVAL1")
        DET_FLOAT(crval2, "MEF.CRVAL2")
        DET_FLOAT(crpix1, "MEF.CRPIX1")
        DET_FLOAT(crpix2, "MEF.CRPIX2")
#undef DET_FLOAT
    }
    if (config->processing.median_even_supplied) {
        entry(stream,&first,"MEF.BIAS.MEDIAN.EVEN.HANDLING","string");
        json_string(stream,config->processing.median_even_handling == MEDIAN_EVEN_LOWER ? "lower" : "average");
        fputc('}',stream);
    }
    if (config->processing.bpm.supplied) {
        const mef_bpm_policy *p = &config->processing.bpm;
        entry(stream,&first,"BPM.ENCODING","string");
        json_string(stream,p->encoding == MEF_BPM_REASON8 ? "reason8" : "binary"); fputc('}',stream);
        entry(stream,&first,"BPM.BAD_WHEN","string");
        json_string(stream,p->bad_when_nonzero ? "nonzero" : "zero"); fputc('}',stream);
        if (p->encoding == MEF_BPM_REASON8) {
            entry(stream,&first,"BPM.REJECT_BITS","int"); fprintf(stream,"%u}",p->reject_bits);
            entry(stream,&first,"BPM.REGISTRY","string"); json_string(stream,p->registry); fputc('}',stream);
        }
    }
    if (config->processing.ron_clip_supplied) {
        const mef_processing_policy *p = &config->processing;
        entry(stream,&first,"QC.RON.CLIP.ENABLED","int"); fprintf(stream,"%d}",p->ron_clip_enabled);
        entry(stream,&first,"QC.RON.CLIP.LOW","float64-bits"); bits(stream,&p->ron_clip_low,sizeof(double)); fputc('}',stream);
        entry(stream,&first,"QC.RON.CLIP.HIGH","float64-bits"); bits(stream,&p->ron_clip_high,sizeof(double)); fputc('}',stream);
        entry(stream,&first,"QC.RON.CLIP.MAX_ITERATIONS","int"); fprintf(stream,"%d}",p->ron_clip_max_iterations);
    }
    fputs("\n}\n", stream);
    return ferror(stream) ? MEF_ERR_IO : MEF_OK;
}

mef_status mef_config_response_toml(const mef_config *config,FILE *stream,double low,double high)
{
    int i,j;
    char key[80];
    const mef_detector_config *d;
    const mef_processing_policy *p;
    if(!config || !stream || !(low>0) || !(low<high) || high>FLT_MAX ||
        !((float)low>0) || !((float)low<(float)high)) return MEF_ERR_CONFIG;
    fputs("schema_version = 1\n[native]\n",stream);
#define TOML_KEY(key) json_string(stream,key);fputs(" = ",stream);
#define MEF_STRING(member,key) TOML_KEY(key) json_string(stream,config->member);fputc('\n',stream);
#define MEF_INT(member,key) TOML_KEY(key) fprintf(stream,"%d\n",config->member);
#define MEF_FLOAT(member,key) TOML_KEY(key) fprintf(stream,"%#.17g\n", \
    !strcmp(key,"MEF.BPM.LGAINTHR")?(double)(float)low: \
    !strcmp(key,"MEF.BPM.HGAINTHR")?(double)(float)high:(double)config->member);
#define MEF_DOUBLE(member,key) TOML_KEY(key) fprintf(stream,"%#.17g\n",config->member);
#include "mef_config_fields.def"
#undef MEF_STRING
#undef MEF_INT
#undef MEF_FLOAT
#undef MEF_DOUBLE
    for(i=0;i<config->nchips;++i) {
        d=config->detectors+i;
        for(j=0;j<2;++j) {
            sprintf(key,"MEF.PRESCAN.X.%s.CHIP%d",j?"MAX":"MIN",i+1);
            TOML_KEY(key) fprintf(stream,"%d\n",d->prescan_x[j]);
            sprintf(key,"MEF.OVERSCAN.X.%s.CHIP%d",j?"MAX":"MIN",i+1);
            TOML_KEY(key) fprintf(stream,"%d\n",d->overscan_x[j]);
        }
        for(j=0;j<4;++j) {
            sprintf(key,"MEF.CROP.%s.CHIP%d",j==0?"X.MIN":j==1?"X.MAX":j==2?"Y.MIN":"Y.MAX",i+1);
            TOML_KEY(key) fprintf(stream,"%d\n",d->trimreg[j]);
        }
#define DET_TOML(member,name) sprintf(key,name ".CHIP%d",i+1);TOML_KEY(key) fprintf(stream,"%#.17g\n",(double)d->member);
        DET_TOML(ron,"MEF.CCD.RON") DET_TOML(gain,"MEF.CCD.GAIN")
        DET_TOML(crval1,"MEF.CRVAL1") DET_TOML(crval2,"MEF.CRVAL2")
        DET_TOML(crpix1,"MEF.CRPIX1") DET_TOML(crpix2,"MEF.CRPIX2")
#undef DET_TOML
    }
    p=&config->processing;
    if(p->median_even_supplied) {
        TOML_KEY("MEF.BIAS.MEDIAN.EVEN.HANDLING")
        json_string(stream,p->median_even_handling==MEDIAN_EVEN_LOWER?"lower":"average");fputc('\n',stream);
    }
    if(p->bpm.supplied) {
        TOML_KEY("BPM.ENCODING") json_string(stream,p->bpm.encoding==MEF_BPM_REASON8?"reason8":"binary");fputc('\n',stream);
        TOML_KEY("BPM.BAD_WHEN") json_string(stream,p->bpm.bad_when_nonzero?"nonzero":"zero");fputc('\n',stream);
        if(p->bpm.encoding==MEF_BPM_REASON8) {
            TOML_KEY("BPM.REJECT_BITS") fprintf(stream,"%u\n",p->bpm.reject_bits);
            TOML_KEY("BPM.REGISTRY") json_string(stream,p->bpm.registry);fputc('\n',stream);
        }
    }
    if(p->ron_clip_supplied) {
        TOML_KEY("QC.RON.CLIP.ENABLED") fprintf(stream,"%d\n",p->ron_clip_enabled);
        TOML_KEY("QC.RON.CLIP.LOW") fprintf(stream,"%#.17g\n",p->ron_clip_low);
        TOML_KEY("QC.RON.CLIP.HIGH") fprintf(stream,"%#.17g\n",p->ron_clip_high);
        TOML_KEY("QC.RON.CLIP.MAX_ITERATIONS") fprintf(stream,"%d\n",p->ron_clip_max_iterations);
    }
#undef TOML_KEY
    return ferror(stream)?MEF_ERR_IO:MEF_OK;
}

/* Copy only the settings required by the bias operation. */
/* Selected-detector owned bridge for existing bias header helpers. Do not
 * construct a PAF or reload settings when the source is a TOML snapshot. */
#include "mef_bias_files.h"
mef_status mef_config_bias_header_context(const mef_config *config,
    size_t detector, mef_bb **out)
{
    mef_bb *bb;
    const mef_detector_config *d;
    if (config == NULL || out == NULL || *out != NULL ||
        detector >= (size_t)config->nchips) return MEF_ERR_CONFIG;
    bb = calloc(1, sizeof(*bb));
    if (bb == NULL) return MEF_ERR_MEMORY;
#define MEF_STRING(member, key) \
    bb->member = strdup(config->member); \
    if (bb->member == NULL) goto fail;
#define MEF_INT(member, key) bb->member = config->member;
#define MEF_FLOAT(member, key) bb->member = config->member;
#define MEF_DOUBLE(member, key) bb->member = config->member;
#include "mef_config_fields.def"
#undef MEF_STRING
#undef MEF_INT
#undef MEF_FLOAT
#undef MEF_DOUBLE
    bb->nchips = bb->nxts = bb->xtnum = 1;
    bb->bias_median_even_handling = (median_even_handling)config->processing.median_even_handling;
    bb->ccd = calloc(1, sizeof(*bb->ccd));
    if (bb->ccd == NULL) goto fail;
    d = config->detectors + detector;
    memcpy(bb->ccd->prescan_x, d->prescan_x, sizeof(d->prescan_x));
    memcpy(bb->ccd->overscan_x, d->overscan_x, sizeof(d->overscan_x));
    memcpy(bb->ccd->trimreg, d->trimreg, sizeof(d->trimreg));
    bb->ccd->ron = d->ron; bb->ccd->gain = d->gain;
    bb->ccd->crval1 = d->crval1; bb->ccd->crval2 = d->crval2;
    bb->ccd->crpix1 = d->crpix1; bb->ccd->crpix2 = d->crpix2;
    *out = bb;
    return MEF_OK;
fail:
    mef_bb_del(bb);
    return MEF_ERR_MEMORY;
}

#include "mef_bias_settings.h"
mef_status mef_config_bias_settings(const mef_config *config, size_t detector,
    mef_bias_settings *out)
{
    const mef_detector_config *ccd;
    if (config == NULL || out == NULL || detector >= (size_t)config->nchips)
        return MEF_ERR_CONFIG;
    ccd = &config->detectors[detector];
    memcpy(out->prescan, ccd->prescan_x, sizeof(out->prescan));
    memcpy(out->overscan, ccd->overscan_x, sizeof(out->overscan));
    memcpy(out->trim, ccd->trimreg, sizeof(out->trim));
    memcpy(out->rejection, config->scanrej, sizeof(out->rejection));
    out->use_prescan = config->use_prescan;
    out->use_overscan = config->use_overscan;
    out->minimum_frames = config->bias_minframe;
    out->kappa = config->bias_kappa1;
    out->median_even_handling = config->processing.median_even_handling;
    return MEF_OK;
}

#include "mef_bpm_settings.h"
mef_status mef_config_bpm_settings(const mef_config *config, size_t detector,
    mef_bpm_settings *out)
{
    mef_bpm_settings value;
    if (out == NULL || mef_config_bias_settings(config, detector, &value.scan) != MEF_OK)
        return MEF_ERR_CONFIG;
    value.proportional = config->bpm_proportional_flag;
    value.low = config->bpm_gainthr_lo;
    value.high = config->bpm_gainthr_hi;
    *out = value;
    return MEF_OK;
}

const mef_processing_policy *mef_config_processing(const mef_config *config)
{ return config ? &config->processing : NULL; }
void mef_config_initialize_processing(mef_config *config, const mef_processing_policy *policy)
{ config->processing = *policy; }

int mef_bpm_policy_matches(const mef_bpm_policy *p, mef_bpm_encoding encoding,
    int good, unsigned int reject_bits, const char *registry)
{
    if (!p || !p->supplied) return 1;
    if (p->encoding != encoding) return 0;
    if (encoding == MEF_BPM_BINARY) return good == (p->bad_when_nonzero ? 0 : 1);
    return encoding == MEF_BPM_REASON8 && reject_bits == p->reject_bits && registry &&
        !strcmp(registry,p->registry);
}
