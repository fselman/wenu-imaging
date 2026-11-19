/* Typed metadata fixture only. Calls the real validator/writer, no image recipe. */
#include "mef_product_qc.h"
#include <math.h>
#include <stdio.h>
#include <string.h>
#ifndef MEF_QC_VALIDATE_ONLY
#define MEF_QC_VALIDATE_ONLY 0
#endif
int main(int argc,char **argv)
{
    mef_product_qc p,original;
    mef_qc_input_record inputs[3];mef_qc_detector_record detectors[2];
    mef_qc_input_binding bindings[2][3];mef_qc_measurement raw[2][3],product[2][4];
    double raw_values[2][3]={{125.5,126.25,127.125},{225.5,226.25,227.125}};
    double master[2]={12.5,23.75},ron[2]={3.141592653589793,2.718281828459045};
    double profile[3]={-0.0,0.33333333333333331,123456.78901234567},sample_count=12.0;
    const char *ids[3]={"raw-0000","raw-0001","raw-0002"};
    const char *one[3][1]={{"raw-0000"},{"raw-0001"},{"raw-0002"}};
    const char *pair[2]={"raw-0000","raw-0002"},*output[1]={"product-0001"},*wrong[1]={"missing"};
    mef_qc_calibration_binding cb[2]={{"CCD-A",5},{"CCD-B",3}};
    mef_qc_calibration_record calibration;
    char bpm[4096];
    char paths[3][4096],fits[4096],log[4096],message[256];const char *mode,*base;int i,j,code;
    if(argc!=4 && argc!=5)return 2;
    mode=argv[2];base=argv[3];
    memset(&p,0,sizeof(p));memset(inputs,0,sizeof(inputs));memset(detectors,0,sizeof(detectors));
    memset(bindings,0,sizeof(bindings));memset(raw,0,sizeof(raw));memset(product,0,sizeof(product));
    snprintf(fits,sizeof(fits),"%s/CMDP.2026-11-06T15:00:00.123Z.001.fits",base);
    snprintf(log,sizeof(log),"%s/CMDP.2026-11-06T15:00:00.123Z.001.log",base);
    for(j=0;j<3;++j){
        snprintf(paths[j],sizeof(paths[j]),"%s/raw-%d.fits",base,j);
        inputs[j].id=ids[j];inputs[j].path=paths[j];inputs[j].original_index=(uint64_t)(10+j*10);
    }
    for(i=0;i<2;++i){
        detectors[i].id=i?"CCD-B":"CCD-A";detectors[i].amplifier=i?"R":"L";
        detectors[i].readout_id="fixture:normal";detectors[i].configuration_detector=i?2:7;
        detectors[i].output_hdu=i+1;detectors[i].bin_x=detectors[i].bin_y=1;
        detectors[i].inputs=bindings[i];detectors[i].input_count=3;
        detectors[i].measurements=product[i];detectors[i].measurement_count=4;
        for(j=0;j<3;++j){
            raw[i][j].name="raw_active.mean";raw[i][j].unit="ADU";
            raw[i][j].stage="raw_before_correction";raw[i][j].method="arithmetic_mean";
            raw[i][j].state=MEF_QC_MEASURED;raw[i][j].values=&raw_values[i][j];
            raw[i][j].value_count=1;raw[i][j].sample_count=12;
            raw[i][j].coordinates="FITS-1-based-inclusive";
            raw[i][j].mask_policy="omitted";raw[i][j].clipping="none";raw[i][j].nonfinite_policy="excluded";
            raw[i][j].bounds[0]=1;raw[i][j].bounds[1]=4;raw[i][j].bounds[2]=1;raw[i][j].bounds[3]=3;
            raw[i][j].source_ids=one[j];raw[i][j].source_count=1;
            bindings[i][j].input_id=ids[j];bindings[i][j].source_hdu=(j%2)?i+1:2-i;
            bindings[i][j].accepted=!(i==0 && j==1);
            bindings[i][j].rejection_reason=bindings[i][j].accepted?NULL:"existing_frame_mean_rejection";
            bindings[i][j].measurements=&raw[i][j];bindings[i][j].measurement_count=1;
        }
        for(j=0;j<4;++j){
            product[i][j]=raw[i][0];product[i][j].stage="median_stacked_master";
            product[i][j].source_ids=output;product[i][j].source_count=1;
        }
        product[i][0].name="master.mean";product[i][0].values=&master[i];
        product[i][1].name="ron.stdev_adu";product[i][1].values=&ron[i];
        product[i][1].stage="raw_pair_difference_before_any_correction";
        product[i][1].method="existing_raw_pair_stdev_div_sqrt_2";
        product[i][1].source_ids=pair;product[i][1].source_count=2;
        product[i][2].name="variance";product[i][2].unit="ADU2";product[i][2].state=MEF_QC_UNAVAILABLE;
        product[i][2].values=NULL;product[i][2].value_count=0;product[i][2].method=NULL;
        product[i][2].reason="legacy_variance_unavailable";
        product[i][3].name="synthetic_profile";product[i][3].values=profile;
        product[i][3].vector=1;product[i][3].value_count=3;
    }
    p.id="product-0001";p.fits_path=fits;p.log_path=log;
    p.assessment_id="fixture-bias-0001";p.recipe_name="cal.bias";p.recipe_version=1;
    p.recipe_start="2026-11-06T15:00:00.123Z";p.product_sequence=1;
    p.producer_name="native-product-qc-fixture";p.producer_version="1";
    p.source_revision="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
    p.configuration_id="fixture-effective-settings";
    p.configuration_snapshot="{\"MEF.NCHIPS\":{\"type\":\"int\",\"value\":2}}";
    p.inputs=inputs;p.input_count=3;p.detectors=detectors;p.detector_count=2;
    mef_qc_text_evidence evidence[2]={{"plan.tsv","plan/1","source\tA\n"},{"traces.tsv","trace/1","1\t2.5\n"}};
    if(!strcmp(mode,"table") || !strcmp(mode,"table-hdu") || !strcmp(mode,"duplicate-evidence") || !strcmp(mode,"missing-evidence")) {
        strcpy(fits+strlen(fits)-5,".tsv");p.table_name="roi_measurements";p.detector_count=1;
        detectors[0].output_hdu=!strcmp(mode,"table-hdu")?1:0;
        p.evidence=evidence;p.evidence_count=2;
        if(!strcmp(mode,"duplicate-evidence")) evidence[1].name=evidence[0].name;
        if(!strcmp(mode,"missing-evidence")) evidence[1].text=NULL;
    }
    if(!strcmp(mode,"with-bpm")) {
        memset(&calibration,0,sizeof(calibration));snprintf(bpm,sizeof(bpm),"%s/bpm.fits",base);
        calibration.id="bpm-0000";calibration.path=bpm;calibration.role="bpm";calibration.bindings=cb;calibration.binding_count=2;
        p.calibrations=&calibration;p.calibration_count=1;
        for(i=0;i<2;++i){
            for(j=0;j<3;++j){raw[i][j].mask_policy="applied";raw[i][j].mask_id=calibration.id;}
            product[i][0].mask_policy="applied";product[i][0].mask_id=calibration.id;
        }
    }
    else if(!strcmp(mode,"applied-without-bpm"))raw[0][0].mask_policy="applied";
    else if(!strcmp(mode,"unknown-mask")){raw[0][0].mask_policy="applied";raw[0][0].mask_id="missing-bpm";}
    else if(!strcmp(mode,"duplicate-input"))inputs[1].id=inputs[0].id;
    else if(!strcmp(mode,"duplicate-index"))inputs[1].original_index=inputs[0].original_index;
    else if(!strcmp(mode,"duplicate-detector"))detectors[1].id=detectors[0].id;
    else if(!strcmp(mode,"duplicate-output-hdu"))detectors[1].output_hdu=detectors[0].output_hdu;
    else if(!strcmp(mode,"missing-binding"))detectors[1].input_count=2;
    else if(!strcmp(mode,"reordered-binding"))bindings[0][0].input_id=ids[2];
    else if(!strcmp(mode,"negative-source-hdu"))bindings[0][0].source_hdu=-1;
    else if(!strcmp(mode,"bad-acceptance"))bindings[0][0].accepted=2;
    else if(!strcmp(mode,"missing-rejection-reason"))bindings[0][1].rejection_reason=NULL;
    else if(!strcmp(mode,"nonfinite-value"))master[0]=NAN;
    else if(!strcmp(mode,"unknown-source"))product[0][0].source_ids=wrong;
    else if(!strcmp(mode,"wrong-input-origin"))raw[0][0].source_ids=output;
    else if(!strcmp(mode,"unavailable-has-value"))product[0][2].values=master;
    else if(!strcmp(mode,"measured-no-samples"))product[0][0].sample_count=0;
    else if(!strcmp(mode,"invalid-time"))p.recipe_start="2026-02-30T15:00:00.123Z";
    else if(!strcmp(mode,"duplicate-measurement"))product[0][1].name=product[0][0].name;
    else if(!strcmp(mode,"fractional-count")){product[0][0].unit="count";master[0]=1.5;}
    else if(!strcmp(mode,"integer-count")){product[0][0].unit="count";product[0][0].values=&sample_count;}
    else if(!strcmp(mode,"outside-log"))p.log_path="/elsewhere/log";
    else if(!strcmp(mode,"bad-sha"))inputs[0].sha256="not-a-sha256";
    else if(!strcmp(mode,"invalid-region"))product[0][0].bounds[0]=0;
    else if(strcmp(mode,"good") && strcmp(mode,"table") && strcmp(mode,"table-hdu") &&
            strcmp(mode,"duplicate-evidence") && strcmp(mode,"missing-evidence"))return 2;
    original=p;
    if(!strcmp(argv[1],"validate"))code=mef_product_qc_validate(&p,message,sizeof(message));
    else if(!strcmp(argv[1],"write") && argc==5){
#if MEF_QC_VALIDATE_ONLY
        return 2;
#else
        code=mef_product_qc_write(argv[4],&p,message,sizeof(message));
#endif
    } else return 2;
    if(memcmp(&p,&original,sizeof(p)))return 3;
    if(code)fprintf(stderr,"%s\n",message);
    return code?1:0;
}
