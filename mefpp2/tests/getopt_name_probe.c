/* #103: bounded matching with the actual bundled parser, without image I/O. */
#include <stdio.h>
#include <string.h>
#include "getopt.h"

static struct option options[] = {
    {"h", NO_ARG, NULL, 'a'},
    {"help", NO_ARG, NULL, 'h'},
    {"version", NO_ARG, NULL, 'v'},
    {"verify", NO_ARG, NULL, 'c'},
    {"satmax", REQUIRED_ARG, NULL, 's'},
    {"bias", REQUIRED_ARG, NULL, 'b'},
    {NULL, 0, NULL, 0}
};

static int check(const char *label, int argc, char **argv,
                 int expected, const char *argument)
{
    int result, index;
    optind = 0;
    opterr = 0;
    optarg = NULL;
    index = -1;
    result = getopt_long(argc, argv, "h", options, &index);
    if (result != expected || (argument != NULL &&
        (optarg == NULL || strcmp(optarg, argument) != 0))) {
        fprintf(stderr, "PARSER FAIL %s code=%d\n", label, result);
        return 1;
    }
    printf("PARSER PASS %s\n", label);
    return 0;
}

int main(void)
{
    int failed;
    char *exact[] = {"parser", "--help", NULL};
    char *exact_short_name[] = {"parser", "--h", NULL};
    char *version[] = {"parser", "--version", NULL};
    char *prefix[] = {"parser", "--vers", NULL};
    char *ambiguous[] = {"parser", "--ver", NULL};
    char *long_unknown[] = {"parser", "--version-extra", NULL};
    char *unknown[] = {"parser", "--unknown", NULL};
    char *equals[] = {"parser", "--satmax=2", NULL};
    char *separate[] = {"parser", "--satmax", "2", NULL};
    char *missing[] = {"parser", "--satmax", NULL};
    char *prefix_value[] = {"parser", "--satm=2", NULL};
    char *short_option[] = {"parser", "-h", NULL};
    char *end_options[] = {"parser", "--", NULL};
    failed = 0;
    failed += check("exact-after-short-name", 2, exact, 'h', NULL);
    failed += check("exact-wins-over-prefix", 2, exact_short_name, 'a', NULL);
    failed += check("exact-version", 2, version, 'v', NULL);
    failed += check("unique-prefix", 2, prefix, 'v', NULL);
    failed += check("ambiguous-prefix", 2, ambiguous, '?', NULL);
    failed += check("longer-unknown", 2, long_unknown, '?', NULL);
    failed += check("unknown", 2, unknown, '?', NULL);
    failed += check("equals-value", 2, equals, 's', "2");
    failed += check("separate-value", 3, separate, 's', "2");
    failed += check("missing-value", 2, missing, '?', NULL);
    failed += check("prefix-with-value", 2, prefix_value, 's', "2");
    failed += check("short-option", 2, short_option, 'h', NULL);
    failed += check("end-options", 2, end_options, EOF, NULL);
    printf("PARSER COMPLETE checks=13 failed=%d\n", failed);
    return failed ? 1 : 0;
}
