#define _POSIX_C_SOURCE 200809L
#include "mef_bpm_linearity.h"
#include <stdio.h>
#include <string.h>
#include <unistd.h>

static int product_exists(const char *path)
{
    struct stat st;
    return !stat(path,&st) && S_ISREG(st.st_mode) && st.st_size>0;
}

int mef_bpm_linearity_verify(mef_bpm_linearity *recipe)
{
    size_t i;
    recipe->diagnostic="Incomplete detector coverage or changed dependencies";
    if (!mef_bpm_linearity_observe(recipe)) return 0;
    for (i=0; i<recipe->detector_count; ++i) {
        const mef_bpm_linearity_detector *detector=recipe->detectors+i;
        if (!product_exists(detector->fits) || !product_exists(detector->asdf) ||
            !product_exists(detector->prepared)) return 0;
    }
    return 1;
}

static void quoted(FILE *stream, const char *text)
{
    const unsigned char *p=(const unsigned char *)text;
    fputc('"',stream);
    for (; *p; ++p) {
        if (*p=='"' || *p=='\\') fputc('\\',stream);
        if (*p<32 || *p==127) fprintf(stream,"\\u%04x",(unsigned)*p);
        else fputc(*p,stream);
    }
    fputc('"',stream);
}

static int receipt_file(FILE *stream, const char *key, const char *path)
{
    char digest[65];
    if (!mef_bpm_linearity_hash(path,digest)) return 0;
    fprintf(stream,"%s = ",key); quoted(stream,path);
    fprintf(stream,"\n%s_sha256 = \"%s\"\n",key,digest);
    return !ferror(stream);
}

static int publish_receipt(mef_bpm_linearity *recipe)
{
    FILE *stream=fopen(recipe->receipt,"wx");
    size_t i;
    int okay=0;
    if (!stream) return 0;
    fputs("native_recipe_receipt_schema_version = 1\nstatus = \"complete\"\n"
        "input_preservation = true\nscientific_acceptance = false\n"
        "linearity_correction = \"not_applied\"\ncreated_at = ",stream);
    quoted(stream,recipe->run->recipe_start);
    fputs("\nsource_revision = ",stream); quoted(stream,recipe->run->revision);
    fputs("\nbindings = ",stream); quoted(stream,recipe->bindings_path);
    fprintf(stream,"\nbindings_sha256 = \"%s\"\n",recipe->bindings_sha256);
    fputs("log = ",stream); quoted(stream,recipe->run->paths.log); fputc('\n',stream);
    if (!receipt_file(stream,"fits",recipe->run->paths.fits) ||
        !receipt_file(stream,"asdf",recipe->run->paths.asdf)) goto done;
    for (i=0; i<recipe->detector_count; ++i) {
        mef_bpm_linearity_detector *detector=recipe->detectors+i;
        fputs("\n[[detectors]]\ndetector_id = ",stream); quoted(stream,detector->detector_id);
        fprintf(stream,"\nconfiguration_detector = %lu\n",(unsigned long)detector->configuration_detector);
        if (!receipt_file(stream,"fits",detector->fits) || !receipt_file(stream,"asdf",detector->asdf) ||
            !receipt_file(stream,"prepared",detector->prepared)) goto done;
    }
    okay=!ferror(stream) && !fflush(stream) && !fsync(fileno(stream));
done:
    if (fclose(stream)) okay=0;
    return okay;
}

int mef_bpm_linearity_publish(mef_bpm_linearity *recipe)
{
    mef_bpm_assembly_detector *detectors=calloc(recipe->detector_count,sizeof(*detectors));
    const char **sidecars=calloc(recipe->detector_count,sizeof(*sidecars));
    char *planes=NULL;
    size_t i;
    int okay=0;
    recipe->diagnostic="Final BPM MEF/ASDF publication or input preservation failed";
    if (!detectors || !sidecars) goto done;
    for (i=0; i<recipe->detector_count; ++i) {
        const mef_bpm_linearity_detector *d=recipe->detectors+i;
        detectors[i]=(mef_bpm_assembly_detector){d->fits,d->detector_id,d->configuration_detector};
        sidecars[i]=d->asdf;
    }
    fprintf(recipe->run->log,"MEF_ASSEMBLY_START\n");
    if (fflush(recipe->run->log) || mef_bpm_mef_assemble(recipe->run->paths.fits,
        recipe->reference_detector,detectors,recipe->detector_count,
        recipe->run->message,sizeof(recipe->run->message))) goto done;
    planes=mef_bpm_assembly_plane_map(recipe->run->paths.fits,detectors,recipe->detector_count);
    if (!planes) goto done;
    {
        mef_bpm_assembly_qc request={.fits_path=recipe->run->paths.fits,.asdf_path=recipe->run->paths.asdf,
            .log_path=recipe->run->paths.log,.created_at=recipe->run->recipe_start,
            .source_revision=recipe->run->revision,.detector_source_revision=recipe->run->revision,
            .recipe_path=recipe->recipe_path,.recipe_snapshot=recipe->recipe_source,
            .detectors=detectors,.sidecars=sidecars,.detector_count=recipe->detector_count,.plane_map=planes};
        fprintf(recipe->run->log,"NATIVE_ASDF_START\n");
        if (fflush(recipe->run->log) || mef_bpm_assembly_qc_write(&request,
            recipe->run->message,sizeof(recipe->run->message))) goto done;
    }

    /* [BPM-LINEARITY-PRESERVATION]
     * One final streaming hash per shared dependency; no image cubes retained.
     * A failed check retains products but publishes no successful receipt.
     */

    for (i=0; i<recipe->dependency_count; ++i) {
        if (!mef_bpm_linearity_dependency_check(recipe->dependencies+i,1)) goto done;
    }
    okay=publish_receipt(recipe);
done:
    free(planes); free(detectors); free(sidecars);
    return okay;
}
