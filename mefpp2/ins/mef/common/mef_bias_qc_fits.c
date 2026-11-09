/* Serialize stored bias QC measurements into additive FITS cards.
 * Values, availability and population definitions come from the shared archive;
 * the versioned mapping registry supplies names/codes. No statistics are rerun.
 */

#include "mef_bias_qc_fits.h"
#include "qfits.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <locale.h>
#undef malloc
#undef free

#define G(s, a, f) {s, a, f},
#define M(a, f)
#define Q(s, a, f)
#define C(k, a, f)

static const struct group {
    int scope;
    const char *asdf, *fits;
} groups[] = {

#include "mef_bias_qc_fits.def"
};
#undef G
#undef M
#define G(s, a, f)
#define M(a, f) {a, f},

static const struct metric {
    const char *asdf, *fits;
} metrics[] = {

#include "mef_bias_qc_fits.def"
};
#undef M
#undef Q
#define M(a, f)
#define Q(s, a, f) {s, a, f},

static const struct scalar {
    int scope;
    const char *asdf, *fits;
} scalars[] = {

#include "mef_bias_qc_fits.def"
};
#undef Q
#undef C
#define Q(s, a, f)
#define C(k, a, f) {k, a, f},

static const struct lookup_context_code {
    const char *kind, *text, *value;
} codes[] = {

#include "mef_bias_qc_fits.def"
};
#undef G
#undef M
#undef Q
#undef C
#define LENGTH(a) (sizeof(a) / sizeof((a)[0]))

static const char *lookup_context_code(const char *kind, const char *text)
{
    size_t i;
    if (text == NULL) {
        return NULL;
    }
    for (i = 0; i < LENGTH(codes); ++i) {
        if (!strcmp(kind, codes[i].kind) && !strcmp(text, codes[i].text)) {
            return codes[i].value;
        }
    }
    return NULL;
}

static const mef_qc_measurement *find_measurement(
    const mef_qc_measurement *measurement, size_t measurement_count, const char *name)
{
    size_t i;
    const mef_qc_measurement *found = NULL;
    if (!measurement || !name) {
        return NULL;
    }
    for (i = 0; i < measurement_count; ++i) {
        if (measurement[i].name && !strcmp(measurement[i].name, name)) {
            if (found) {
                return NULL;
            }
            found = measurement + i;
        }
    }
    return found;
}

/* Preflight the exact 80-byte HIERARCH layout. No supplied comments or CONTINUE cards.
 * qfits must never silently truncate a keyword, value or quoted string. */

static int append_fits_card(qfits_header *header, const char *name, const char *value, int string)
{
    char key[81], quoted[81];
    size_t i, measurement_count = 0, limit;
    if (name == NULL || value == NULL || strlen(name) + 9 >= sizeof(key)) {
        return 0;
    }
    snprintf(key, sizeof(key), "HIERARCH %s", name);
    if (qfits_header_getstr(header, key) != NULL) {
        return 0;
    }
    limit = (strlen(key) < 29 ? 29 : strlen(key)) + 2;
    if (string) {
        quoted[measurement_count++] = '\'';
        for (i = 0; value[i]; ++i) {
            unsigned char c = (unsigned char)value[i];
            if (c < 32 || c > 126 || measurement_count + 3 >= sizeof(quoted)) {
                return 0;
            }
            quoted[measurement_count++] = (char)c;
            if (c == '\'') {
                quoted[measurement_count++] = '\'';
            }
        }
        quoted[measurement_count++] = '\'';
        quoted[measurement_count] = '\0';
        value = quoted;
    }
    if (limit + strlen(value) > 80) {
        return 0;
    }
    qfits_header_append(header, key, value, NULL, NULL);
    return qfits_header_getstr(header, key) != NULL;
}

static int append_context_field(
    qfits_header *header, const char *base, const char *suffix, const char *value, int string)
{
    char key[128];
    int measurement_count =
        snprintf(key, sizeof(key), "ESO MPP QC %s%s%s", base, *suffix ? " " : "", suffix);
    return measurement_count > 0 && (size_t)measurement_count < sizeof(key) &&
           append_fits_card(header, key, value, string);
}

static int append_integer_field(
    qfits_header *header, const char *base, const char *suffix, uint64_t value)
{
    char number[32];
    snprintf(number, sizeof(number), "%llu", (unsigned long long)value);
    return append_context_field(header, base, suffix, number, 0);
}

static int append_measurement_context(
    qfits_header *header, const char *key, const mef_qc_measurement *measurement)
{
    static const char *bounds[] = {"X1", "X2", "Y1", "Y2"};
    size_t i;
    if (!append_context_field(
            header, key, "STG", lookup_context_code("stage", measurement->stage), 1) ||
        !append_context_field(
            header, key, "MASK", lookup_context_code("mask", measurement->mask_policy), 1) ||
        !append_context_field(
            header, key, "COORD", lookup_context_code("coord", measurement->coordinates), 1) ||
        !measurement->clipping ||
        (strcmp(measurement->clipping, "none") &&
            strcmp(measurement->clipping, "median_centered_monotone_sigma")) ||
        !measurement->nonfinite_policy || strcmp(measurement->nonfinite_policy, "excluded")) {
        return 0;
    }
    if (strcmp(measurement->clipping, "none") &&
        !append_context_field(header, key, "CLIP", "MEDSIG", 1)) {
        return 0;
    }
    if (measurement->mask_id &&
        !append_context_field(header, key, "BPMID", measurement->mask_id, 1)) {
        return 0;
    }
    for (i = 0; i < 4; ++i) {
        if (measurement->bounds[i] < 0 ||
            !append_integer_field(header, key, bounds[i], (uint64_t)measurement->bounds[i])) {
            return 0;
        }
    }
    for (i = 0; i < measurement->source_count; ++i) {
        char suffix[32];
        snprintf(suffix, sizeof(suffix), "SRC%lu", (unsigned long)i + 1);

        /* Product identities are absolute paths in ASDF. FITS uses basename. */

        if (!measurement->source_ids || !measurement->source_ids[i]) {
            return 0;
        }
        const char *s = strrchr(measurement->source_ids[i], '/');
        s = s ? s + 1 : measurement->source_ids[i];
        if (!append_context_field(header, key, suffix, s, 1)) {
            return 0;
        }
    }
    return 1;
}

static int append_measurement(
    qfits_header *header, const char *key, const mef_qc_measurement *measurement, int own_context)
{
    char number[64];
    const char *method;
    if (!measurement || measurement->vector || !measurement->unit ||
        !append_integer_field(header, key, "NSAMP", measurement->sample_count)) {
        return 0;
    }
    if (own_context && !append_measurement_context(header, key, measurement)) {
        return 0;
    }
    if (measurement->method) {
        method = lookup_context_code("method", measurement->method);
        if (!append_context_field(header, key, "METHOD", method, 1)) {
            return 0;
        }
    }
    if (!append_context_field(header, key, "UNIT", measurement->unit, 1)) {
        return 0;
    }
    if (measurement->state == MEF_QC_MEASURED) {
        if (!measurement->method || !measurement->values || measurement->value_count != 1 ||
            !isfinite(measurement->values[0]) || measurement->reason) {
            return 0;
        }
        if (!strcmp(measurement->unit, "count")) {
            if (measurement->values[0] < 0 ||
                floor(measurement->values[0]) != measurement->values[0]) {
                return 0;
            }
            snprintf(number, sizeof(number), "%.0f", measurement->values[0]);
        } else {
            char *product_qc;
            snprintf(number, sizeof(number), "%.17g", measurement->values[0]);
            for (product_qc = number; *product_qc; ++product_qc) {
                if (*product_qc == 'e') {
                    *product_qc = 'E';
                }
            }

            /* A float-looking card preserves type for integral-valued ADU. */

            if (!strchr(number, '.') && !strchr(number, 'E')) {
                strcat(number, ".0");
            }
        }
        return append_context_field(header, key, "S", "measured", 1) &&
               append_context_field(header, key, "", number, 0);
    }
    return measurement->state == MEF_QC_UNAVAILABLE && !measurement->values &&
           !measurement->value_count && append_context_field(header, key, "S", "unavailable", 1) &&
           append_context_field(
               header, key, "R", lookup_context_code("reason", measurement->reason), 1);
}

static int append_sample_group(qfits_header *header, int scope, const char *prefix,
    const mef_qc_measurement *measurement, size_t measurement_count)
{
    size_t i, j;
    char key[96], name[96], group[80];
    for (i = 0; i < LENGTH(groups); ++i) {
        if (groups[i].scope == scope) {
            snprintf(group, sizeof(group), "%s%s%s", prefix, *prefix ? " " : "", groups[i].fits);
            snprintf(name, sizeof(name), "%s.mean", groups[i].asdf);
            const mef_qc_measurement *first =
                find_measurement(measurement, measurement_count, name);
            if (!first || !append_measurement_context(header, group, first)) {
                return 0;
            }
            for (j = 0; j < LENGTH(metrics); ++j) {
                snprintf(name, sizeof(name), "%s.%s", groups[i].asdf, metrics[j].asdf);
                snprintf(key, sizeof(key), "%s %s", group, metrics[j].fits);
                const mef_qc_measurement *m =
                    find_measurement(measurement, measurement_count, name);

                /* The registry groups only definitions whose context is identical. */

                if (!m || !m->stage || !m->mask_policy || !m->coordinates || !m->clipping ||
                    !m->nonfinite_policy || strcmp(m->clipping, "none") ||
                    strcmp(m->nonfinite_policy, "excluded") || strcmp(first->stage, m->stage) ||
                    strcmp(first->mask_policy, m->mask_policy) ||
                    strcmp(first->coordinates, m->coordinates) ||
                    memcmp(first->bounds, m->bounds, sizeof(m->bounds)) ||
                    first->source_count != m->source_count ||
                    ((first->mask_id == NULL) != (m->mask_id == NULL)) ||
                    (first->mask_id && strcmp(first->mask_id, m->mask_id))) {
                    return 0;
                }
                for (size_t k = 0; k < m->source_count; ++k) {
                    if (strcmp(first->source_ids[k], m->source_ids[k])) {
                        return 0;
                    }
                }
                if (!append_measurement(header, key, m, 0)) {
                    return 0;
                }
            }
        }
    }
    for (i = 0; i < LENGTH(scalars); ++i) {
        if (scalars[i].scope == scope) {
            const mef_qc_measurement *m =
                find_measurement(measurement, measurement_count, scalars[i].asdf);

            /* BPM parameter measurements exist only when a BPM was supplied. */

            if (!m && (!strncmp(scalars[i].asdf, "bpm.", 4) ||
                          !strncmp(scalars[i].asdf, "ron_clip.", 9) ||
                          !strcmp(scalars[i].asdf, "read_noise.clipped"))) {
                continue;
            }
            snprintf(key, sizeof(key), "%s%s%s", prefix, *prefix ? " " : "", scalars[i].fits);
            if (!append_measurement(header, key, m, 1)) {
                return 0;
            }
        }
    }
    return 1;
}

int mef_bias_qc_fits_header(
    const mef_product_qc *product_qc, size_t index, qfits_header **out, char *message, size_t size)
{
    qfits_header *header = NULL;
    const mef_qc_detector_record *d;
    size_t i;
    if (!product_qc || !product_qc->detectors || !product_qc->inputs || !out || *out ||
        index >= product_qc->detector_count || !product_qc->fits_path) {
        goto failed;
    }

    /* Numeric formatting is locale sensitive. Refuse rather than mutate global
     * locale or emit a decimal comma in scientific metadata. */

    if (strcmp(localeconv()->decimal_point, ".")) {
        goto failed;
    }
    d = product_qc->detectors + index;
    if (!d->id || !d->inputs || d->bin_x < 1 || d->bin_y < 1 ||
        d->input_count != product_qc->input_count) {
        goto failed;
    }
    header = qfits_header_new();
    if (!header) {
        goto failed;
    }
    const char *fits = strrchr(product_qc->fits_path, '/');
    fits = fits ? fits + 1 : product_qc->fits_path;
    char asdf[128];
    size_t length = strlen(fits);
    if (length < 5 || length + 1 >= sizeof(asdf) || strcmp(fits + length - 5, ".fits")) {
        goto failed;
    }
    memcpy(asdf, fits, length - 5);
    strcpy(asdf + length - 5, ".asdf");
    if (!append_context_field(header, "MAPVER", "", "bias-scalar/1", 1) ||
        !append_context_field(header, "ASDF", "", asdf, 1) ||
        !append_context_field(header, "PROD", "", fits, 1) ||
        !append_integer_field(header, "CONFIG", "", d->configuration_detector) ||
        !append_integer_field(header, "BINX", "", (uint64_t)d->bin_x) ||
        !append_integer_field(header, "BINY", "", (uint64_t)d->bin_y) ||
        !append_context_field(header, "READID", "", d->readout_id, 1) ||
        !append_context_field(header, "AMP", "", d->amplifier, 1) ||
        !append_sample_group(header, 0, "", d->measurements, d->measurement_count)) {
        goto failed;
    }
    if (d->median_even_handling &&
        ((strcmp(d->median_even_handling, "average") && strcmp(d->median_even_handling, "lower")) ||
            !append_context_field(header, "MED EVEN", "", d->median_even_handling, 1))) {
        goto failed;
    }
    if (product_qc->qc_profile &&
        !append_context_field(header, "PROFILE", "", product_qc->qc_profile, 1)) {
        goto failed;
    }
    const mef_qc_measurement *pair =
        find_measurement(d->measurements, d->measurement_count, "read_noise");
    if (!pair) {
        goto failed;
    }
    for (i = 0; i < pair->source_count; ++i) {
        size_t j;
        char key[32];

        /* Unrequested RON uses the product as its source, not a raw pair. */

        if (!strncmp(pair->source_ids[i], "raw-", 4)) {
            for (j = 0; j < product_qc->input_count; ++j) {
                if (!strcmp(pair->source_ids[i], product_qc->inputs[j].id)) {
                    break;
                }
            }
            if (j == product_qc->input_count) {
                goto failed;
            }
            snprintf(key, sizeof(key), "RON I%lu", (unsigned long)i + 1);
            if (!append_integer_field(header, key, "", product_qc->inputs[j].original_index)) {
                goto failed;
            }
        }
    }
    for (i = 0; i < d->input_count; ++i) {
        char prefix[48];
        const mef_qc_input_binding *b = d->inputs + i;
        if (!b->input_id || strcmp(b->input_id, product_qc->inputs[i].id) || b->source_hdu < 0 ||
            product_qc->inputs[i].original_index > 99999999) {
            goto failed;
        }
        snprintf(prefix, sizeof(prefix), "FRAME%03llu",
            (unsigned long long)product_qc->inputs[i].original_index + 1);
        if (!append_context_field(header, prefix, "ID", b->input_id, 1) ||
            !append_integer_field(header, prefix, "HDU", (uint64_t)b->source_hdu) ||
            !append_context_field(header, prefix, "USE", b->accepted ? "used" : "rejected", 1) ||
            (!b->accepted && !append_context_field(header, prefix, "WHY",
                                 lookup_context_code("reason", b->rejection_reason), 1)) ||
            !append_sample_group(header, 1, prefix, b->measurements, b->measurement_count)) {
            goto failed;
        }
    }
    if (product_qc->bpm_registry &&
        !append_context_field(header, "BPM REG", "", product_qc->bpm_registry, 1)) {
        goto failed;
    }
    *out = header;
    return 0;
failed:
    qfits_header_destroy(header);
    if (message && size) {
        snprintf(message, size,
            "bias-scalar/1 header refused: invalid metadata, unknown code, collision or "
            "80-byte card limit");
    }
    return -1;
}
