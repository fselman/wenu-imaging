/* Bounded libasdf 0.3.0 interchange probe; no mefpp or FITS processing.
 * Values are synthetic fixtures, not scientific QC estimators. */
#include "asdf_probe_compat.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CHECK(x) do { if (!(x)) { fprintf(stderr, "failed at line %d: %s\n", __LINE__, #x); return 1; } } while (0)

int main(int argc, char **argv)
{
    asdf_file_t *file;
    asdf_ndarray_t *array = NULL;
    double *values = NULL;
    const char *unit = NULL;
    int result;
    if (argc < 3) return 2;
    if (strcmp(argv[1], "write") == 0) {
        uint64_t shape[] = {2, 3};
        asdf_ndarray_t output = {.ndim = 2, .shape = shape,
            .datatype = {.type = ASDF_DATATYPE_FLOAT64},
            .byteorder = ASDF_BYTEORDER_LITTLE};
        file = asdf_open(NULL);
        CHECK(file != NULL);
        /* libasdf 0.3.0 cannot add a second missing child through an
         * existing parent path (#219). Build the mapping directly, using the
         * API verified on the Intel Mac, then transfer it into the root once.
         * Keep the same metadata and Python-side exact-content checks. */
        asdf_mapping_t *measurement = asdf_mapping_create(file);
        CHECK(measurement != NULL);
        CHECK(asdf_mapping_set_string0(measurement, "unit", "ADU") == ASDF_VALUE_OK);
        CHECK(asdf_mapping_set_double(measurement, "value", 12.5) == ASDF_VALUE_OK);
        CHECK(asdf_mapping_set_null(measurement, "unavailable") == ASDF_VALUE_OK);
        CHECK(asdf_set_mapping(file, "measurement", measurement) == ASDF_VALUE_OK);
        /* asdf_set_mapping consumes the wrapper; do not destroy it here. */
        values = asdf_ndarray_data_alloc(&output);
        CHECK(values != NULL);
        for (int i = 0; i < 6; ++i) values[i] = (double)i - 2.5;
        CHECK(asdf_set_ndarray(file, "profile", &output) == ASDF_VALUE_OK);
        /* Assignment transfers ownership of the allocated data to file. */
        result = asdf_write_to(file, argv[2]);
        asdf_close(file);
        CHECK(result == 0);
    } else if (strcmp(argv[1], "read") == 0) {
        double level = 0;
        file = asdf_open(argv[2], "r");
        CHECK(file != NULL);
        CHECK(asdf_get_string0(file, "measurement/unit", &unit) == ASDF_VALUE_OK);
        CHECK(strcmp(unit, "ADU") == 0);
        CHECK(asdf_get_double(file, "measurement/value", &level) == ASDF_VALUE_OK);
        CHECK(level == 12.5 && asdf_is_null(file, "measurement/unavailable"));
        CHECK(asdf_get_ndarray(file, "profile", &array) == ASDF_VALUE_OK);
        CHECK(array->ndim == 2 && array->shape[0] == 2 && array->shape[1] == 3);
        CHECK(asdf_ndarray_read_all(array, ASDF_DATATYPE_FLOAT64, (void **)&values) == ASDF_NDARRAY_OK);
        for (int i = 0; i < 6; ++i) CHECK(values[i] == (double)i - 2.5);
        free(values);
        asdf_ndarray_destroy(array);
        asdf_close(file);
    } else if (strcmp(argv[1], "copy-qc") == 0 && argc == 4) {
        file = asdf_open(argv[2], "r");
        CHECK(file != NULL && asdf_is_mapping(file, "qc"));
        CHECK(asdf_get_string0(file, "qc/record/schema_version", &unit) == ASDF_VALUE_OK);
        CHECK(strcmp(unit, "1.0.0") == 0);
        result = asdf_write_to(file, argv[3]);
        asdf_close(file);
        CHECK(result == 0);
    } else return 2;
    puts("PASS: libasdf interchange fixture");
    return 0;
}
