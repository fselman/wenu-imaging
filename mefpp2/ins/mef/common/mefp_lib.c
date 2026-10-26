
/*---------------------------------------------------------------------------

File name 	:	mefp_lib.c
Author 		:	F. Selman
Created on	:	18 Feb 2005
Description	:	MEF library utilities, from wfi
			by N. Devillard, mutatis mutandi

 *--------------------------------------------------------------------------*/

/*
   $Id: mefp_lib.c,v 1.21 2003/03/18 15:16:20 fselman Exp $
   $Author: fselman $
   $Date: 2003/03/18 15:16:20 $
   $Revision: 0.5 $
   */

/*---------------------------------------------------------------------------
  Includes
  ---------------------------------------------------------------------------*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <errno.h>
#include <ctype.h>
#include <float.h>
#include <limits.h>
#include <unistd.h>

#include "eclipse.h"
#include "mefp_lib.h"
#include "qfits.h"
#include "xmemory.h"

static char recipe_version[] = "mefpp-2.0.3";

/*---------------------------------------------------------------------------
  Function codes
  ---------------------------------------------------------------------------*/
/* Required values must be checked before conversion; qfits owns the returned
 * static buffer, so callers consume/copy it before the next query (#76). */
static int mef_paf_value(char *path, char *key, int kind, char **value)
{
    char *end;
    double number;
    *value = qfits_paf_query(path, key);
    if (*value == NULL) {
        e_error("missing required PAF key [%s] in [%s]", key, path);
        return -1;
    }
    if (kind == 0) {
        if (strlen(*value) > 80) {
            e_error("PAF string exceeds 80 characters: key [%s] in [%s]", key, path);
            return -1;
        }
        return 0;
    }
    errno = 0;
    number = strtod(*value, &end);
    while (isspace((unsigned char)*end)) end++;
    if (end == *value || *end != '\0' || errno == ERANGE ||
        number != number || number > DBL_MAX || number < -DBL_MAX ||
        (kind == 1 && (number < INT_MIN || number > INT_MAX)) ||
        (kind == 2 && (number < -FLT_MAX || number > FLT_MAX))) {
        e_error("invalid numeric PAF value [%s], key [%s] in [%s]", *value, key, path);
        return -1;
    }
    return 0;
}

/* Retain the historical default entry point for other native callers. */
mef_bb * mef_bb_new(void)
{
    return mef_bb_new_from_paf("mefpp.paf");
}

mef_bb * mef_bb_new_from_paf(char *cfgfile)
{
	mef_bb        *       bb ;
	mef_ccd	      *	      ccd;
	int			i;
	char buffer[81];
	char charval[81];
	int			ivalue;
	float			fvalue;
	double			dvalue;
	char *value;
    char *end;
    long nchips;

	bb = calloc(1, sizeof(mef_bb));
    if (bb == NULL) {
        e_error("cannot allocate processing context");
        return NULL;
    }
    if (cfgfile == NULL || qfits_is_paf_file(cfgfile) != 1) {
        e_error("cannot read valid PAF configuration [%s]", cfgfile ? cfgfile : "(null)");
        goto fail;
    }
    bb->name_paf = strdup(cfgfile);
    if (bb->name_paf == NULL) goto allocation_failure;

	/* testing reading from paf file */
	/* Set default parameters for all */

	

	sprintf(buffer,"MEF.NCHIPS");
	if (mef_paf_value(cfgfile, buffer, 1, &value) != 0) goto fail;
	errno = 0;
    nchips = strtol(value, &end, 10);
    while (isspace((unsigned char)*end)) end++;
    if (end == value || *end != '\0' || errno == ERANGE || nchips <= 0 || nchips > INT_MAX) {
        e_error("invalid detector count in PAF [%s], key MEF.NCHIPS", cfgfile);
        goto fail;
    }
    ivalue = (int)nchips;
	if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %d\n",buffer,ivalue); }

	if (ivalue <= 0 || (size_t)ivalue > (size_t)-1 / sizeof(mef_ccd)) {
        e_error("invalid detector count in PAF [%s], key MEF.NCHIPS", cfgfile);
        goto fail;
    }
    bb->nchips = ivalue;

        ccd = calloc(bb->nchips, sizeof(mef_ccd));
    if (ccd == NULL) goto allocation_failure;
    bb->ccd = ccd;

	if (debug_active() >= 1) { e_comment(1, "mef_bb_new: MEF.NCHIPS: %d\n",bb->nchips); }
	bb->noverify		= 0 ;
	bb->name_split		= NULL ;
	
	for(i=0; i<bb->nchips; i++) {

	    e_comment(1, "mef_bb_new: Processing extnum: %d\n",i);

	    (ccd+i)->extnum = i+1;

	    e_comment(1, "mef_bb_new: Processing extnum: %d\n",(ccd+i)->extnum);

	    sprintf(buffer,"MEF.PRESCAN.X.MIN.CHIP%d",i+1);
	    if (mef_paf_value(cfgfile, buffer, 1, &value) != 0) goto fail;
	    ivalue = atoi(value);
	    if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %d\n",buffer,ivalue); }
	    (ccd+i)->prescan_x[0]       = ivalue;

	    sprintf(buffer,"MEF.PRESCAN.X.MAX.CHIP%d",i+1);
	    if (mef_paf_value(cfgfile, buffer, 1, &value) != 0) goto fail;
	    ivalue = atoi(value);
            if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %d\n",buffer,ivalue); }
	    (ccd+i)->prescan_x[1]   	= ivalue;

	    sprintf(buffer,"MEF.OVERSCAN.X.MIN.CHIP%d",i+1);
            if (mef_paf_value(cfgfile, buffer, 1, &value) != 0) goto fail;
            ivalue = atoi(value);
            if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %d\n",buffer,ivalue); }
	    (ccd+i)->overscan_x[0]  	= ivalue;

	    sprintf(buffer,"MEF.OVERSCAN.X.MAX.CHIP%d",i+1);
            if (mef_paf_value(cfgfile, buffer, 1, &value) != 0) goto fail;
            ivalue = atoi(value);
            if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %d\n",buffer,ivalue); }
	    (ccd+i)->overscan_x[1]  	= ivalue;

	    sprintf(buffer,"MEF.CROP.X.MIN.CHIP%d",i+1);
            if (mef_paf_value(cfgfile, buffer, 1, &value) != 0) goto fail;
            ivalue = atoi(value);
            if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %d\n",buffer,ivalue); }
	    (ccd+i)->trimreg[0]     	= ivalue;

	    sprintf(buffer,"MEF.CROP.X.MAX.CHIP%d",i+1);
            if (mef_paf_value(cfgfile, buffer, 1, &value) != 0) goto fail;
            ivalue = atoi(value);
            if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %d\n",buffer,ivalue); }
	    (ccd+i)->trimreg[1]     	= ivalue;

	    sprintf(buffer,"MEF.CROP.Y.MIN.CHIP%d",i+1);
            if (mef_paf_value(cfgfile, buffer, 1, &value) != 0) goto fail;
            ivalue = atoi(value);
            if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %d\n",buffer,ivalue); }
	    (ccd+i)->trimreg[2]     	= ivalue;

	    sprintf(buffer,"MEF.CROP.Y.MAX.CHIP%d",i+1);
            if (mef_paf_value(cfgfile, buffer, 1, &value) != 0) goto fail;
            ivalue = atoi(value);
            if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %d\n",buffer,ivalue); }
	    (ccd+i)->trimreg[3]     	= ivalue;

	    sprintf(buffer,"MEF.CCD.RON.CHIP%d",i+1);
            if (mef_paf_value(cfgfile, buffer, 2, &value) != 0) goto fail;
            fvalue = atof(value);
            if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %f\n",buffer,fvalue); }
	    (ccd+i)->ron            	= fvalue;

	    sprintf(buffer,"MEF.CCD.GAIN.CHIP%d",i+1);
            if (mef_paf_value(cfgfile, buffer, 2, &value) != 0) goto fail;
            fvalue = atof(value);
            if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %f\n",buffer,fvalue); }
	    (ccd+i)->gain           	= fvalue;

	    sprintf(buffer,"MEF.CRVAL1.CHIP%d",i+1);
            if (mef_paf_value(cfgfile, buffer, 1, &value) != 0) goto fail;
            ivalue = atoi(value);
            if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %d\n",buffer,ivalue); }
	    (ccd+i)->crval1		= ivalue;

	    sprintf(buffer,"MEF.CRVAL2.CHIP%d",i+1);
            if (mef_paf_value(cfgfile, buffer, 1, &value) != 0) goto fail;
            ivalue = atoi(value);
            if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %d\n",buffer,ivalue); }
	    (ccd+i)->crval2		= ivalue;

	    sprintf(buffer,"MEF.CRPIX1.CHIP%d",i+1);
            if (mef_paf_value(cfgfile, buffer, 2, &value) != 0) goto fail;
            fvalue = atof(value);
            if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %f\n",buffer,fvalue); }
	    (ccd+i)->crpix1		= fvalue;

	    sprintf(buffer,"MEF.CRPIX2.CHIP%d",i+1);
            if (mef_paf_value(cfgfile, buffer, 2, &value) != 0) goto fail;
            fvalue = atof(value);
	    (ccd+i)->crpix2		= fvalue;
	    if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %f\n",buffer,(ccd+i)->crpix2); }
	
	}
	
	bb->ccd				= ccd ;

	sprintf(buffer,"MEF.ORIGIN");
	if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
	sprintf(charval,"%s", value);
	bb->origin			= strdup(charval);
    if (bb->origin == NULL) goto allocation_failure;
	if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->origin); }

	sprintf(buffer,"MEF.TELESCOPE");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->telescope			= strdup(charval) ;
    if (bb->telescope == NULL) goto allocation_failure;
	if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->telescope); }

        sprintf(buffer,"MEF.INSTRUMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->instrument			= strdup(charval) ;
    if (bb->instrument == NULL) goto allocation_failure;
	if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->instrument); }

        sprintf(buffer,"MEF.CORRECT.REFPIXELS");
        if (mef_paf_value(cfgfile, buffer, 1, &value) != 0) goto fail;
        ivalue = atoi(value);
        bb->correct_ref_pix             = ivalue;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %d\n",buffer,bb->correct_ref_pix); }

        sprintf(buffer,"MEF.RECIPE.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->recipe_key			= strdup(charval) ;
    if (bb->recipe_key == NULL) goto allocation_failure;
	if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->recipe_key); }

        sprintf(buffer,"MEF.DPR.CATG.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->dpr_catg_key        	= strdup(charval) ;
    if (bb->dpr_catg_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->dpr_catg_key); }

        sprintf(buffer,"MEF.DPR.CATG.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->dpr_catg_comment    	= strdup(charval) ;
    if (bb->dpr_catg_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->dpr_catg_comment); }

        sprintf(buffer,"MEF.DPR.TYPE.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->dpr_type_key		= strdup(charval) ;
    if (bb->dpr_type_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->dpr_type_key); }

        sprintf(buffer,"MEF.DPR.TYPE.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->dpr_type_comment    	= strdup(charval) ;
    if (bb->dpr_type_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->dpr_type_comment); }

        /* ESO PHASE3 variables */

        sprintf(buffer,"PHASE3.PRODCATG.KEY.NAME");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_prodcatg_keyname            = strdup(charval) ;
    if (bb->phase3_prodcatg_keyname == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_prodcatg_keyname); }

        sprintf(buffer,"PHASE3.PRODCATG.VAL.BIAS");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_prodcatg_val_bias            = strdup(charval) ;
    if (bb->phase3_prodcatg_val_bias == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_prodcatg_val_bias); }

        sprintf(buffer,"PHASE3.PRODCATG.VAL.BPM");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_prodcatg_val_bpm            = strdup(charval) ;
    if (bb->phase3_prodcatg_val_bpm == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_prodcatg_val_bpm); }

        sprintf(buffer,"PHASE3.PRODCATG.VAL.DOMEFF");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_prodcatg_val_domeff            = strdup(charval) ;
    if (bb->phase3_prodcatg_val_domeff == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_prodcatg_val_domeff); }

        sprintf(buffer,"PHASE3.PRODCATG.VAL.SKYFF");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_prodcatg_val_skyff            = strdup(charval) ;
    if (bb->phase3_prodcatg_val_skyff == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_prodcatg_val_skyff); }

        sprintf(buffer,"PHASE3.PRODCATG.VAL.MFF");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_prodcatg_val_mff            = strdup(charval) ;
    if (bb->phase3_prodcatg_val_mff == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_prodcatg_val_mff); }

        sprintf(buffer,"PHASE3.PRODCATG.VAL.SCIENCE");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_prodcatg_val_science            = strdup(charval) ;
    if (bb->phase3_prodcatg_val_science == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_prodcatg_val_science); }

        sprintf(buffer,"PHASE3.PRODCATG.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_prodcatg_comment        = strdup(charval) ;
    if (bb->phase3_prodcatg_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_prodcatg_comment); }

        sprintf(buffer,"PHASE3.PROGID.KEY.NAME");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_progid_keyname        = strdup(charval) ;
    if (bb->phase3_progid_keyname == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_progid_keyname); }

        sprintf(buffer,"PHASE3.PROGID.HDRKEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_progid_hdrkey        = strdup(charval) ;
    if (bb->phase3_progid_hdrkey == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_progid_hdrkey); }

        sprintf(buffer,"PHASE3.PROGID.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_progid_comment        = strdup(charval) ;
    if (bb->phase3_progid_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_progid_comment); }

        sprintf(buffer,"PHASE3.OBID.KEY.NAME");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_obid_keyname        = strdup(charval) ;
    if (bb->phase3_obid_keyname == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_obid_keyname); }

        sprintf(buffer,"PHASE3.OBID.HDRKEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_obid_hdrkey        = strdup(charval) ;
    if (bb->phase3_obid_hdrkey == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_obid_hdrkey); }

        sprintf(buffer,"PHASE3.OBID.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_obid_comment        = strdup(charval) ;
    if (bb->phase3_obid_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_obid_comment); }

        sprintf(buffer,"PHASE3.NCOMBINE.KEY.NAME");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_ncombine_keyname        = strdup(charval) ;
    if (bb->phase3_ncombine_keyname == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_ncombine_keyname); }

        sprintf(buffer,"PHASE3.NCOMBINE.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_ncombine_comment        = strdup(charval) ;
    if (bb->phase3_ncombine_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_ncombine_comment); }

        sprintf(buffer,"PHASE3.OBSTECH.KEY.NAME");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_obstech_keyname        = strdup(charval) ;
    if (bb->phase3_obstech_keyname == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_obstech_keyname); }

        sprintf(buffer,"PHASE3.OBSTECH.HDRKEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_obstech_hdrkey        = strdup(charval) ;
    if (bb->phase3_obstech_hdrkey == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_obstech_hdrkey); }

        sprintf(buffer,"PHASE3.OBSTECH.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_obstech_comment        = strdup(charval) ;
    if (bb->phase3_obstech_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_obstech_comment); }

        sprintf(buffer,"PHASE3.MJDEND.KEY.NAME");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_mjdend_keyname        = strdup(charval) ;
    if (bb->phase3_mjdend_keyname == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_mjdend_keyname); }

        sprintf(buffer,"PHASE3.MJDEND.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_mjdend_comment        = strdup(charval) ;
    if (bb->phase3_mjdend_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_mjdend_comment); }

        sprintf(buffer,"PHASE3.PROCSOFT.KEY.NAME");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_procsoft_keyname        = strdup(charval) ;
    if (bb->phase3_procsoft_keyname == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_procsoft_keyname); }

        sprintf(buffer,"PHASE3.PROCSOFT.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_procsoft_comment        = strdup(charval) ;
    if (bb->phase3_procsoft_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_procsoft_comment); }

        sprintf(buffer,"PHASE3.TIMESYS.KEY.NAME");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_timesys_keyname        = strdup(charval) ;
    if (bb->phase3_timesys_keyname == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_timesys_keyname); }

        sprintf(buffer,"PHASE3.TIMESYS.VAL");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_timesys_val        = strdup(charval) ;
    if (bb->phase3_timesys_val == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_timesys_val); }
        
        sprintf(buffer,"PHASE3.TIMESYS.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_timesys_comment        = strdup(charval) ;
    if (bb->phase3_timesys_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_timesys_comment); }

        sprintf(buffer,"PHASE3.FILTER.KEY.NAME");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_filter_keyname        = strdup(charval) ;
    if (bb->phase3_filter_keyname == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_filter_keyname); }

        sprintf(buffer,"PHASE3.FILTER.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_filter_comment        = strdup(charval) ;
    if (bb->phase3_filter_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_filter_comment); }

        sprintf(buffer,"PHASE3.FLUXCAL.KEY.NAME");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_fluxcal_keyname        = strdup(charval) ;
    if (bb->phase3_fluxcal_keyname == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_fluxcal_keyname); }

        sprintf(buffer,"PHASE3.FLUXCAL.VAL");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_fluxcal_val        = strdup(charval) ;
    if (bb->phase3_fluxcal_val == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_fluxcal_val); }

        sprintf(buffer,"PHASE3.FLUXCAL.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_fluxcal_comment        = strdup(charval) ;
    if (bb->phase3_fluxcal_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_fluxcal_comment); }

        sprintf(buffer,"PHASE3.RADESYS.KEY.NAME");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_radesys_keyname        = strdup(charval) ;
    if (bb->phase3_radesys_keyname == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_radesys_keyname); }

        sprintf(buffer,"PHASE3.RADESYS.HDRKEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_radesys_hdrkey        = strdup(charval) ;
    if (bb->phase3_radesys_hdrkey == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_radesys_hdrkey); }

        sprintf(buffer,"PHASE3.RADESYS.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->phase3_radesys_comment        = strdup(charval) ;
    if (bb->phase3_radesys_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->phase3_radesys_comment); }

        sprintf(buffer,"MEF.USE.PRESCAN");
        if (mef_paf_value(cfgfile, buffer, 1, &value) != 0) goto fail;
        ivalue = atoi(value);
	bb->use_prescan			= ivalue;
	if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %d\n",buffer,bb->use_prescan); }

        sprintf(buffer,"MEF.USE.OVERSCAN");
        if (mef_paf_value(cfgfile, buffer, 1, &value) != 0) goto fail;
        ivalue = atoi(value);
	bb->use_overscan		= ivalue;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %d\n",buffer,bb->use_overscan); }

        sprintf(buffer,"MEF.BIAS.FRAME.I.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->bias_frame_i_key   		= strdup(charval) ;
    if (bb->bias_frame_i_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->bias_frame_i_key); }

        sprintf(buffer,"MEF.BIAS.FRAME.I.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
        bb->bias_frame_i_comment   	= strdup(charval) ;
    if (bb->bias_frame_i_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->bias_frame_i_comment); }
	
        /* FITS key to identify bias product used to produce flats and science products. */
        sprintf(buffer,"MEF.MASTER.BIAS.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->master_bias_key		= strdup(charval) ;
    if (bb->master_bias_key == NULL) goto allocation_failure;
	if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->master_bias_key); }

        sprintf(buffer,"MEF.MASTER.BIAS.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->master_bias_comment 	= strdup(charval) ;
    if (bb->master_bias_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->master_bias_comment); }

	sprintf(buffer,"MEF.BIAS.NAME.O");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->name_bias_o			= strdup(charval);
    if (bb->name_bias_o == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->name_bias_o); }

        sprintf(buffer,"MEF.BPM.NAME.O");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->name_bpm_o			= strdup(charval);
    if (bb->name_bpm_o == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->name_bpm_o); }

   /*
    * Keys to process BPMs
         * bb->name_bpm
         * bb->bpm_frame_i_key
         * bb->bpm_frame_i_comment
         * bb->bpm_propflag_key
         * bb->bpm_propflag_comment
         * bb->bpm_lgainthr_key
         * bb->bpm_lgainthr_comment
         * bb->bpm_hgainthr_key
         * bb->bpm_hgainthr_comment
         * bb->bpm_frame_i_key
         * bb->bpm_frame_i_comment
         * bb->master_bpm_key
         * bb->master_bpm_comment
   */

        sprintf(buffer,"MEF.BPM.NAME");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->name_bpm			= strdup(charval);
    if (bb->name_bpm == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->name_bpm); }

        sprintf(buffer,"MEF.BPM.FRAME.I.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->bpm_frame_i_key            = strdup(charval);
    if (bb->bpm_frame_i_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->bpm_frame_i_key); }

        sprintf(buffer,"MEF.BPM.FRAME.I.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->bpm_frame_i_comment            = strdup(charval);
    if (bb->bpm_frame_i_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->bpm_frame_i_comment); }

        sprintf(buffer,"MEF.BPM.PROPFLAG.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->bpm_propflag_key            = strdup(charval);
    if (bb->bpm_propflag_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->bpm_propflag_key); }

        sprintf(buffer,"MEF.BPM.PROPFLAG.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->bpm_propflag_comment            = strdup(charval);
    if (bb->bpm_propflag_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->bpm_propflag_comment); }

        sprintf(buffer,"MEF.BPM.LGAINTHR.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->bpm_lgainthr_key            = strdup(charval);
    if (bb->bpm_lgainthr_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->bpm_lgainthr_key); }

        sprintf(buffer,"MEF.BPM.LGAINTHR.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->bpm_lgainthr_comment            = strdup(charval);
    if (bb->bpm_lgainthr_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->bpm_lgainthr_comment); }

        sprintf(buffer,"MEF.BPM.HGAINTHR.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->bpm_hgainthr_key            = strdup(charval);
    if (bb->bpm_hgainthr_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->bpm_hgainthr_key); }

        sprintf(buffer,"MEF.BPM.HGAINTHR.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->bpm_hgainthr_comment            = strdup(charval);
    if (bb->bpm_hgainthr_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->bpm_hgainthr_comment); }

        sprintf(buffer,"MEF.MASTER.BPM.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->master_bpm_key     = strdup(charval) ;
    if (bb->master_bpm_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->master_bpm_key); }

        sprintf(buffer,"MEF.MASTER.BPM.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->master_bpm_comment     = strdup(charval) ;
    if (bb->master_bpm_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->master_bpm_comment); }


        /* FITS key to identify dome product used to produce combined master flat. */
        sprintf(buffer,"MEF.MASTER.DOME.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->master_dome_key     = strdup(charval) ;
    if (bb->master_dome_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->master_dome_key); }

        sprintf(buffer,"MEF.MASTER.DOME.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->master_dome_comment     = strdup(charval) ;
    if (bb->master_dome_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->master_dome_comment); }

        sprintf(buffer,"MEF.DOMEFF.NAME.O");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->name_dome_o			= strdup(charval) ;
    if (bb->name_dome_o == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->name_dome_o); }

        /* FITS keys to identify sky product used to produce combined master flat. */
        sprintf(buffer,"MEF.MASTER.SKY.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->master_sky_key     = strdup(charval) ;
    if (bb->master_sky_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->master_sky_key); }

        sprintf(buffer,"MEF.MASTER.SKY.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->master_sky_comment     = strdup(charval) ;
    if (bb->master_sky_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->master_sky_comment); }

        sprintf(buffer,"MEF.SKYFF.NAME.O");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->name_sky_o			= strdup(charval) ;
    if (bb->name_sky_o == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->name_sky_o); }

        sprintf(buffer,"MEF.MFF.NAME.O");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->name_mf_o			= strdup(charval) ;
    if (bb->name_mf_o == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->name_mf_o); }


        /* FITS keys to identify master flat product used to reduce the science frames. */
        sprintf(buffer,"MEF.MASTER.FLAT.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->master_flat_key         = strdup(charval) ;
    if (bb->master_flat_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->master_flat_key); }

        sprintf(buffer,"MEF.MASTER.FLAT.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
    bb->master_flat_comment     = strdup(charval) ;
    if (bb->master_flat_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->master_flat_comment); }


        sprintf(buffer,"MEF.REFPIX.X");
        if (mef_paf_value(cfgfile, buffer, 2, &value) != 0) goto fail;
        fvalue = atof(value);
	bb->refpix_x			= fvalue;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %f\n",buffer,bb->refpix_x); }

        sprintf(buffer,"MEF.REFPIX.Y");
        if (mef_paf_value(cfgfile, buffer, 2, &value) != 0) goto fail;
        fvalue = atof(value);
	bb->refpix_y			= fvalue;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %f\n",buffer,bb->refpix_y); }

        sprintf(buffer,"MEF.FILTER.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->filter_key			= strdup(charval) ;
    if (bb->filter_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->filter_key); }

	bb->filter_val			= NULL ;

        sprintf(buffer,"MEF.BINX.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->binx_key			= strdup(charval) ;
    if (bb->binx_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->binx_key); }

	bb->binx_val			= NULL ;

        sprintf(buffer,"MEF.BINY.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->biny_key			= strdup(charval) ;
    if (bb->biny_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->biny_key); }

	bb->biny_val			= NULL ;

        sprintf(buffer,"MEF.BIAS.KAPPA1");
        if (mef_paf_value(cfgfile, buffer, 2, &value) != 0) goto fail;
        fvalue = atof(value);
	bb->bias_kappa1			= fvalue;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %f\n",buffer,bb->bias_kappa1); }

        sprintf(buffer,"MEF.BIAS.FRAMENUM.MIN");
        if (mef_paf_value(cfgfile, buffer, 1, &value) != 0) goto fail;
        ivalue = atoi(value);
	bb->bias_minframe		= ivalue ;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %d\n",buffer,bb->bias_minframe); }

        sprintf(buffer,"MEF.BPM.PROPFLAG");
        if (mef_paf_value(cfgfile, buffer, 1, &value) != 0) goto fail;
        ivalue = atoi(value);
	bb->bpm_proportional_flag	= ivalue ;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %d\n",buffer,bb->bpm_proportional_flag); }

        sprintf(buffer,"MEF.BPM.LGAINTHR");
        if (mef_paf_value(cfgfile, buffer, 2, &value) != 0) goto fail;
        fvalue = atof(value);
	bb->bpm_gainthr_lo		= fvalue ;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %f\n",buffer,bb->bpm_gainthr_lo); }

        sprintf(buffer,"MEF.BPM.HGAINTHR");
        if (mef_paf_value(cfgfile, buffer, 2, &value) != 0) goto fail;
        fvalue = atof(value);
	bb->bpm_gainthr_hi		= fvalue ;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %f\n",buffer,bb->bpm_gainthr_hi); }

        sprintf(buffer,"MEF.DOMEFF.FRAME.I.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->domeff_frame_i_key   	= strdup(charval) ;
    if (bb->domeff_frame_i_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->domeff_frame_i_key); }

        sprintf(buffer,"MEF.DOMEFF.FRAME.I.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->domeff_frame_i_comment   	= strdup(charval) ;
    if (bb->domeff_frame_i_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->domeff_frame_i_comment); }

        sprintf(buffer,"MEF.DOMEFF.FRAMETHR.LO.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->dome_framethr_lo_key 	= strdup(charval) ;
    if (bb->dome_framethr_lo_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->dome_framethr_lo_key); }

        sprintf(buffer,"MEF.DOMEFF.FRAMETHR.LO.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
        bb->dome_framethr_lo_comment 	= strdup(charval) ;
    if (bb->dome_framethr_lo_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->dome_framethr_lo_comment); }

        sprintf(buffer,"MEF.DOMEFF.FRAMETHR.LO");
        if (mef_paf_value(cfgfile, buffer, 2, &value) != 0) goto fail;
        fvalue = atof(value);
	bb->dome_framethr_lo 		= fvalue ;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %f\n",buffer,bb->dome_framethr_lo); }


        sprintf(buffer,"MEF.DOMEFF.FRAMETHR.HI.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->dome_framethr_hi_key 	= strdup(charval) ;
    if (bb->dome_framethr_hi_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->dome_framethr_hi_key); }

        sprintf(buffer,"MEF.DOMEFF.FRAMETHR.HI.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
        bb->dome_framethr_hi_comment 	= strdup(charval) ;
    if (bb->dome_framethr_hi_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->dome_framethr_hi_comment); }

        sprintf(buffer,"MEF.DOMEFF.FRAMETHR.HI");
        if (mef_paf_value(cfgfile, buffer, 2, &value) != 0) goto fail;
        fvalue = atof(value);
	bb->dome_framethr_hi 		= fvalue ;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %f\n",buffer,bb->dome_framethr_hi); }

        sprintf(buffer,"MEF.DOMEFF.FRAMENUM.MIN.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->dome_minframe_key		= strdup(charval) ;
    if (bb->dome_minframe_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->dome_minframe_key); }

        sprintf(buffer,"MEF.DOMEFF.FRAMENUM.MIN.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->dome_minframe_comment   	= strdup(charval) ;
    if (bb->dome_minframe_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->dome_minframe_comment); }

        sprintf(buffer,"MEF.DOMEFF.FRAMENUM.MIN");
        if (mef_paf_value(cfgfile, buffer, 1, &value) != 0) goto fail;
        ivalue = atof(value);
	bb->dome_minframe    		= ivalue ;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %d\n",buffer,bb->dome_minframe); }

        sprintf(buffer,"MEF.SKYFF.FRAME.I.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->skyff_frame_i_key		= strdup(charval) ;
    if (bb->skyff_frame_i_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->skyff_frame_i_key); }

        sprintf(buffer,"MEF.SKYFF.FRAME.I.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->skyff_frame_i_comment   	= strdup(charval) ;
    if (bb->skyff_frame_i_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->skyff_frame_i_comment); }

        sprintf(buffer,"MEF.SKYFF.FRAMETHR.LO.KEY");
	if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
	sprintf(charval,"%s", value);
	bb->sky_framethr_lo_key 	= strdup(charval) ;
    if (bb->sky_framethr_lo_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->sky_framethr_lo_key); }

        sprintf(buffer,"MEF.SKYFF.FRAMETHR.LO.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->sky_framethr_lo_comment 	= strdup(charval) ;
    if (bb->sky_framethr_lo_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->sky_framethr_lo_comment); }

        sprintf(buffer,"MEF.SKYFF.FRAMETHR.LO");
        if (mef_paf_value(cfgfile, buffer, 2, &value) != 0) goto fail;
        fvalue = atof(value);
	bb->sky_framethr_lo  		= fvalue ;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %f\n",buffer,bb->sky_framethr_lo); }

        sprintf(buffer,"MEF.SKYFF.FRAMETHR.HI.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->sky_framethr_hi_key 	= strdup(charval) ;
    if (bb->sky_framethr_hi_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->sky_framethr_hi_key); }

        sprintf(buffer,"MEF.SKYFF.FRAMETHR.HI.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->sky_framethr_hi_comment 	= strdup(charval) ;
    if (bb->sky_framethr_hi_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->sky_framethr_hi_comment); }

        sprintf(buffer,"MEF.SKYFF.FRAMETHR.HI");
        if (mef_paf_value(cfgfile, buffer, 2, &value) != 0) goto fail;
        fvalue = atof(value);
	bb->sky_framethr_hi  		= fvalue ;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %f\n",buffer,bb->sky_framethr_hi); }

        sprintf(buffer,"MEF.SKYFF.FRAMENUM.MIN.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->sky_minframe_key		= strdup(charval) ;
    if (bb->sky_minframe_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->sky_minframe_key); }

        sprintf(buffer,"MEF.SKYFF.FRAMENUM.MIN.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->sky_minframe_comment    	= strdup(charval) ;
    if (bb->sky_minframe_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->sky_minframe_comment); }

        sprintf(buffer,"MEF.SKYFF.FRAMENUM.MIN");
        if (mef_paf_value(cfgfile, buffer, 1, &value) != 0) goto fail;
        ivalue = atof(value);
	bb->sky_minframe     		= ivalue ;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %d\n",buffer,bb->sky_minframe); }

        sprintf(buffer,"MEF.PRESCAN.X.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->prescan_x_key		= strdup(charval) ;
    if (bb->prescan_x_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->prescan_x_key); }

        sprintf(buffer,"MEF.PRESCAN.X.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->prescan_x_comment   	= strdup(charval) ;
    if (bb->prescan_x_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->prescan_x_comment); }

	sprintf(buffer,"MEF.OVERSCAN.X.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->overscan_x_key       	= strdup(charval) ;
    if (bb->overscan_x_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->overscan_x_key); }

	sprintf(buffer,"MEF.OVERSCAN.X.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->overscan_x_comment   	= strdup(charval) ;
    if (bb->overscan_x_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->overscan_x_comment); }

        sprintf(buffer,"MEF.SCANREJ.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->scanrej_key			= strdup(charval) ;
    if (bb->scanrej_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->scanrej_key); }

        sprintf(buffer,"MEF.SCANREJ.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->scanrej_comment		= strdup(charval) ;
    if (bb->scanrej_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->scanrej_comment); }

        sprintf(buffer,"MEF.SCANREJ.MIN");
        if (mef_paf_value(cfgfile, buffer, 1, &value) != 0) goto fail;
        ivalue = atof(value);
	bb->scanrej[0]          	= ivalue ;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %d\n",buffer,bb->scanrej[0]); }

        sprintf(buffer,"MEF.SCANREJ.MAX");
        if (mef_paf_value(cfgfile, buffer, 1, &value) != 0) goto fail;
        ivalue = atof(value);
	bb->scanrej[1]          	= ivalue ;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %d\n",buffer,bb->scanrej[1]); }

        sprintf(buffer,"MEF.TRIMREG.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->trimreg_key			= strdup(charval) ;
    if (bb->trimreg_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->trimreg_key); }

        sprintf(buffer,"MEF.TRIMREG.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->trimreg_comment		= strdup(charval) ;
    if (bb->trimreg_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->trimreg_comment); }

        sprintf(buffer,"MEF.CCD.RON.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->ccd_ron_key			= strdup(charval) ;
    if (bb->ccd_ron_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->ccd_ron_key); }

        sprintf(buffer,"MEF.CCD.RON.I.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->ccd_ron_i_key		= strdup(charval) ;
    if (bb->ccd_ron_i_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->ccd_ron_i_key); }

        sprintf(buffer,"MEF.CCD.RON.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->ccd_ron_comment		= strdup(charval) ;
    if (bb->ccd_ron_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->ccd_ron_comment); }

        sprintf(buffer,"MEF.CCD.GAIN.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->ccd_gain_key		= strdup(charval) ;
    if (bb->ccd_gain_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->ccd_gain_key); }

        sprintf(buffer,"MEF.CCD.GAIN.I.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->ccd_gain_i_key        	= strdup(charval) ;
    if (bb->ccd_gain_i_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->ccd_gain_i_key); }

        sprintf(buffer,"MEF.CCD.GAIN.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->ccd_gain_comment		= strdup(charval) ;
    if (bb->ccd_gain_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->ccd_gain_comment); }

        sprintf(buffer,"MEF.PIXREJ.SIGMA.LO.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->pixrej_lo_key		= strdup(charval) ;
    if (bb->pixrej_lo_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->pixrej_lo_key); }

        sprintf(buffer,"MEF.PIXREJ.SIGMA.LO.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->pixrej_lo_comment		= strdup(charval) ;
    if (bb->pixrej_lo_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->pixrej_lo_comment); }

        sprintf(buffer,"MEF.PIXREJ.SIGMA.LO");
        if (mef_paf_value(cfgfile, buffer, 3, &value) != 0) goto fail;
        dvalue = atof(value);
	bb->pixrej_lo   		= dvalue ;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %f\n",buffer,bb->pixrej_lo); }

        sprintf(buffer,"MEF.PIXREJ.SIGMA.HI.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->pixrej_hi_key		= strdup(charval) ;
    if (bb->pixrej_hi_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->pixrej_hi_key); }

        sprintf(buffer,"MEF.PIXREJ.SIGMA.HI.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->pixrej_hi_comment   	= strdup(charval) ;
    if (bb->pixrej_hi_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->pixrej_hi_comment); }

        sprintf(buffer,"MEF.PIXREJ.SIGMA.HI");
        if (mef_paf_value(cfgfile, buffer, 3, &value) != 0) goto fail;
        dvalue = atof(value);
	bb->pixrej_hi   		= dvalue ;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %f\n",buffer,bb->pixrej_hi); }

        sprintf(buffer,"MEF.MEDIAN.REG.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->median_reg_key		= strdup(charval) ;
    if (bb->median_reg_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->median_reg_key); }

        sprintf(buffer,"MEF.MEDIAN.REG.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->median_reg_comment  	= strdup(charval) ;
    if (bb->median_reg_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->median_reg_comment); }

        sprintf(buffer,"MEF.MEDIAN.REG.X1");
        if (mef_paf_value(cfgfile, buffer, 1, &value) != 0) goto fail;
        ivalue = atof(value);
	bb->median_reg[0] 		= ivalue ;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %d\n",buffer,bb->median_reg[0]); }

        sprintf(buffer,"MEF.MEDIAN.REG.X2");
        if (mef_paf_value(cfgfile, buffer, 1, &value) != 0) goto fail;
        ivalue = atof(value);
	bb->median_reg[1] 		= ivalue ;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %d\n",buffer,bb->median_reg[1]); }

        sprintf(buffer,"MEF.MEDIAN.REG.Y1");
        if (mef_paf_value(cfgfile, buffer, 1, &value) != 0) goto fail;
        ivalue = atof(value);
	bb->median_reg[2] 		= ivalue ;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %d\n",buffer,bb->median_reg[2]); }

        sprintf(buffer,"MEF.MEDIAN.REG.Y2");
        if (mef_paf_value(cfgfile, buffer, 1, &value) != 0) goto fail;
        ivalue = atof(value);
	bb->median_reg[3] 		= ivalue ;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %d\n",buffer,bb->median_reg[3]); }


	bb->median_surf   		= (bb->median_reg[1]-bb->median_reg[0]+1) *
						(bb->median_reg[3]-bb->median_reg[2]+1);

        sprintf(buffer,"MEF.KERN.HSIZE.KEY");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->kern_hsize_key		= strdup(charval) ;
    if (bb->kern_hsize_key == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->kern_hsize_key); }

        sprintf(buffer,"MEF.KERN.HSIZE.COMMENT");
        if (mef_paf_value(cfgfile, buffer, 0, &value) != 0) goto fail;
        sprintf(charval,"%s", value);
	bb->kern_hsize_comment		= strdup(charval) ;
    if (bb->kern_hsize_comment == NULL) goto allocation_failure;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %s\n",buffer,bb->kern_hsize_comment); }

        sprintf(buffer,"MEF.KERN.HSIZE");
        if (mef_paf_value(cfgfile, buffer, 1, &value) != 0) goto fail;
        ivalue = atof(value);
	bb->kern_hsize  		= ivalue ;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %d\n",buffer,bb->kern_hsize); }


	bb->sat_check			= 1;

        sprintf(buffer,"MEF.SATLEVEL");
        if (mef_paf_value(cfgfile, buffer, 3, &value) != 0) goto fail;
        dvalue = atof(value);
	bb->sat_level			= dvalue ;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %f\n",buffer,bb->sat_level); }

        sprintf(buffer,"MEF.SATMAX");
        if (mef_paf_value(cfgfile, buffer, 3, &value) != 0) goto fail;
        dvalue = atof(value);
	bb->sat_max			= dvalue ;
        if (debug_active() >= 1) { e_comment(1, "mef_bb_new: %s:\t\t %f\n",buffer,bb->sat_max); }


    return bb;
allocation_failure:
    e_error("cannot allocate context while reading PAF [%s]", cfgfile);
fail:
    mef_bb_del(bb);
    return NULL;
}

void mef_bb_del(mef_bb * bb)
{
	int	i ;

	if (bb==NULL) return ;
    if (bb->name_paf) free(bb->name_paf);

	if (bb->origin)				free(bb->origin) ;
	if (bb->telescope)			free(bb->telescope) ;
	if (bb->instrument)			free(bb->instrument) ;
	if (bb->name_dome) 			free(bb->name_dome);
	if (bb->name_dome_o) 		free(bb->name_dome_o);
	if (bb->name_sky) 			free(bb->name_sky);
	if (bb->name_sky_o) 		free(bb->name_sky_o);
	if (bb->name_mf)            free(bb->name_mf);
	if (bb->name_mf_o) 			free(bb->name_mf_o);
	if (bb->name_bias) 			free(bb->name_bias);
	if (bb->name_bias_o)        free(bb->name_bias_o);
    if (bb->name_bpm)           free(bb->name_bpm);
    if (bb->name_bpm_o)         free(bb->name_bpm_o);

    /*
     * bb->bpm_frame_i_key
     * bb->bpm_frame_i_comment
     * bb->bpm_propflag_key
     * bb->bpm_propflag_comment
     * bb->bpm_lgainthr_key
     * bb->bpm_lgainthr_comment
     * bb->bpm_hgainthr_key
     * bb->bpm_hgainthr_comment
     * bb->master_bpm_key
     * bb->master_bpm_comment
     */

    if (bb->bpm_frame_i_key)                free(bb->bpm_frame_i_key);
    if (bb->bpm_frame_i_comment)            free(bb->bpm_frame_i_comment);
    if (bb->bpm_propflag_key)               free(bb->bpm_propflag_key);
    if (bb->bpm_propflag_comment)           free(bb->bpm_propflag_comment);
    if (bb->bpm_lgainthr_key)               free(bb->bpm_lgainthr_key);
    if (bb->bpm_lgainthr_comment)           free(bb->bpm_lgainthr_comment);
    if (bb->bpm_hgainthr_key)               free(bb->bpm_hgainthr_key);
    if (bb->bpm_hgainthr_comment)           free(bb->bpm_hgainthr_comment);
    if (bb->master_bpm_key)                 free(bb->master_bpm_key);
    if (bb->master_bpm_comment)             free(bb->master_bpm_comment);

	if (bb->ccd) 				free(bb->ccd);

	if (bb->recipe_key)			free(bb->recipe_key);
	
	if (bb->dpr_catg_key)			free(bb->dpr_catg_key);
	if (bb->dpr_catg_val)			free(bb->dpr_catg_val);
	if (bb->dpr_catg_comment)		free(bb->dpr_catg_comment) ;

	if (bb->dpr_type_key)           	free(bb->dpr_type_key);
    if (bb->dpr_type_val)           	free(bb->dpr_type_val);
    if (bb->dpr_type_comment)       	free(bb->dpr_type_comment) ;

    if (bb->phase3_prodcatg_keyname)               free(bb->phase3_prodcatg_keyname);
    if (bb->phase3_prodcatg_val_bias)               free(bb->phase3_prodcatg_val_bias);
    if (bb->phase3_prodcatg_val_domeff)               free(bb->phase3_prodcatg_val_domeff);
    if (bb->phase3_prodcatg_val_skyff)               free(bb->phase3_prodcatg_val_skyff);
    if (bb->phase3_prodcatg_val_mff)               free(bb->phase3_prodcatg_val_mff);
    if (bb->phase3_prodcatg_val_science)               free(bb->phase3_prodcatg_val_science);
    if (bb->phase3_prodcatg_comment)           free(bb->phase3_prodcatg_comment) ;
	
	if (bb->filter_key) 			    free(bb->filter_key);
	if (bb->filter_val) 			    free(bb->filter_val);
	if (bb->binx_key) 			        free(bb->binx_key);
	if (bb->binx_val) 			        free(bb->binx_val);
	if (bb->biny_key) 			        free(bb->biny_key);
	if (bb->biny_val) 			        free(bb->biny_val);
	if (bb->data_partition) 		    free(bb->data_partition);
	if (bb->flat_partition) 		    free(bb->flat_partition);
	if (bb->bias_partition) 		    free(bb->bias_partition);
    if (bb->bpm_partition)              free(bb->bpm_partition);

    if (bb->master_bias_key)            free(bb->master_bias_key);
    if (bb->master_bias_comment)        free(bb->master_bias_comment);
	if (bb->bias_frame_i_key)		    free(bb->bias_frame_i_key);
	if (bb->bias_frame_i_comment)		free(bb->bias_frame_i_comment);
	if (bb->bias_median)			    free(bb->bias_median);
    if (bb->bias_stdev)                 free(bb->bias_stdev);
	if (bb->bias_nplanes)			    free(bb->bias_nplanes);
    if (bb->bias_scan_median)           free(bb->bias_scan_median);
    if (bb->bias_scan_stdev)            free(bb->bias_scan_stdev);

    if (bb->master_dome_key)            free(bb->master_dome_key);
    if (bb->master_dome_comment)        free(bb->master_dome_comment);
	if (bb->domeff_frame_i_key)		    free(bb->domeff_frame_i_key);
	if (bb->domeff_frame_i_comment)		free(bb->domeff_frame_i_comment);
	if (bb->dome_framethr_lo_key)		free(bb->dome_framethr_lo_key);
	if (bb->dome_framethr_lo_comment)	free(bb->dome_framethr_lo_comment);
	if (bb->dome_framethr_hi_key)       free(bb->dome_framethr_hi_key);
    if (bb->dome_framethr_hi_comment)   free(bb->dome_framethr_hi_comment);
	if (bb->dome_minframe_key)		    free(bb->dome_minframe_key);
	if (bb->dome_minframe_comment)		free(bb->dome_minframe_comment);
	if (bb->dome_median) 			    free(bb->dome_median);
    if (bb->dome_stdev)                 free(bb->dome_stdev);
	if (bb->dome_nplanes) 			    free(bb->dome_nplanes);
	
    if (bb->master_sky_key)             free(bb->master_sky_key);
    if (bb->master_sky_comment)         free(bb->master_sky_comment);
	if (bb->skyff_frame_i_key)		    free(bb->skyff_frame_i_key);
	if (bb->skyff_frame_i_comment)		free(bb->skyff_frame_i_comment);
	if (bb->sky_framethr_lo_key)		free(bb->sky_framethr_lo_key);
	if (bb->sky_framethr_lo_comment)	free(bb->sky_framethr_lo_comment);
	if (bb->sky_framethr_hi_key)        free(bb->sky_framethr_hi_key);
    if (bb->sky_framethr_hi_comment)    free(bb->sky_framethr_hi_comment);
	if (bb->sky_minframe_key)		    free(bb->sky_minframe_key);
	if (bb->sky_minframe_comment)       free(bb->sky_minframe_comment);
	if (bb->sky_median) 			    free(bb->sky_median);
    if (bb->sky_stdev)                  free(bb->sky_stdev);
	if (bb->sky_nplanes) 			    free(bb->sky_nplanes);


	if (bb->flat_median) 			free(bb->flat_median);
    if (bb->flat_stdev)             free(bb->flat_stdev);
    if (bb->combined_flat_median)   free(bb->combined_flat_median);
    if (bb->combined_flat_stdev)    free(bb->combined_flat_stdev);

	if (bb->prescan_x_key)			free(bb->prescan_x_key);
	if (bb->prescan_x_comment)		free(bb->prescan_x_comment);
	if (bb->overscan_x_key)			free(bb->overscan_x_key);
	if (bb->overscan_x_comment)		free(bb->overscan_x_comment);
	if (bb->scanrej_key)			free(bb->scanrej_key);
	if (bb->scanrej_comment)		free(bb->scanrej_comment);
	if (bb->trimreg_key)			free(bb->trimreg_key);
	if (bb->trimreg_comment)		free(bb->trimreg_comment);

	if (bb->ccd_ron_key)			free(bb->ccd_ron_key);
	if (bb->ccd_ron_i_key)			free(bb->ccd_ron_i_key);
	if (bb->ccd_ron_comment)		free(bb->ccd_ron_comment);

	if (bb->ccd_gain_key)                   free(bb->ccd_gain_key);
        if (bb->ccd_gain_i_key)                 free(bb->ccd_gain_i_key);
        if (bb->ccd_gain_comment)               free(bb->ccd_gain_comment);

	if (bb->pixrej_lo_key)			free(bb->pixrej_lo_key);
	if (bb->pixrej_lo_comment)		free(bb->pixrej_lo_comment);
	if (bb->pixrej_hi_key)                  free(bb->pixrej_hi_key);
        if (bb->pixrej_hi_comment)              free(bb->pixrej_hi_comment);
	if (bb->median_reg_key)			free(bb->median_reg_key);
	if (bb->median_reg_comment)		free(bb->median_reg_comment);

	if (bb->kern_hsize_key)			free(bb->kern_hsize_key);
	if (bb->kern_hsize_comment)		free(bb->kern_hsize_comment);

	/* deleting pointers to input science frame names */
	if (bb->science_name_i) free(bb->science_name_i);
	if (bb->science_nframes > 0) {
	    if ( (bb->science_frame_name)!= NULL) {
		for(i=0; i<bb->science_nframes; i++) {
		   if (bb->science_frame_name[i]) free(bb->science_frame_name[i]);
		}
		free(bb->science_frame_name);
	    }
	}
	if (bb->name_split)                     free(bb->name_split);

	free(bb);
}

void mef_bb_dump(mef_bb * bb, FILE * out)
{
	fprintf(out,
			"\n"
			"Parameters for this command:\n"
			"\n"
			"[Extension]\n"
			"xtnum       = %d\n"
			"\n"
			"[Output]\n"
			"Name        = %s\n"
			"\n"
			"[Bias]\n"
			"Name        = %s\n"
			"\n"
			"[Dome]\n"
			"Name        = %s\n\n"
			"Filter	     = %s\n"
			"Binning in X= %s\n"
			"Binning in Y= %s\n"
			"LoThresh    = %g\n"
			"HiThresh    = %g\n"
			"MinFrames   = %d\n"
			"SaveFlat    = %s\n"
			"\n"
			"[Sky]\n"
			"Name        = %s\n"
			"LoThresh    = %g\n"
			"HiThresh    = %g\n"
			"MinFrames   = %d\n"
			"SaveFlat    = %s\n"
			"\n"
			"[Prescan]\n"
			"xmin        = %d\n"
			"xmax        = %d\n"
			"\n"
			"[Overscan]\n"
			"xmin        = %d\n"
			"xmax        = %d\n"
			"\n"
			"[Scan rejection]\n"
			"min         = %d\n"
			"max         = %d\n"
			"\n"
			"[Trimming]\n"
			"xmin        = %d\n"
			"xmax        = %d\n"
			"ymin        = %d\n"
			"ymax        = %d\n"
			"\n"
			"[Pixel]\n"
			"ReadoutNoise  = %g\n"
			"Gain          = %g\n"
			"LoSigmaRej    = %g\n"
			"HiSigmaRej    = %g\n"
			"\n"
			"[Median region]\n"
			"xmin        = %d\n"
			"xmax        = %d\n"
			"ymin        = %d\n"
			"ymax        = %d\n"
			"\n"
			"[Smoothing kernel]\n"
			"HalfSize    = %d\n"
			"\n\n",

		bb->xtnum,
		bb->name_mf_o,
		bb->name_bias ? bb->name_bias : "none",
		bb->name_dome ? bb->name_dome : "unknown",
		bb->filter_val ? bb->filter_val : "unknown",
		bb->binx_val ? bb->binx_val : "unknown",
		bb->biny_val ? bb->biny_val : "unknown",
		bb->dome_framethr_lo,
		bb->dome_framethr_hi,
		bb->dome_minframe,
		bb->dome_save ? "yes" : "no",
		bb->name_sky ? bb->name_sky : "unknown",
		bb->sky_framethr_lo,
		bb->sky_framethr_hi,
		bb->sky_minframe,
		bb->sky_save ? "yes" : "no",
		(((bb->ccd)+0)->prescan_x)[0],
	        (((bb->ccd)+0)->prescan_x)[1],
		(((bb->ccd)+0)->overscan_x)[0],
		(((bb->ccd)+0)->overscan_x)[1],
		bb->scanrej[0],
		bb->scanrej[1],
		(((bb->ccd)+0)->trimreg)[0],
		(((bb->ccd)+0)->trimreg)[1],
		(((bb->ccd)+0)->trimreg)[2],
		(((bb->ccd)+0)->trimreg)[3],
		((bb->ccd)+(bb->xtnum-1))->ron,
		((bb->ccd)+0)->gain,
		bb->pixrej_lo,
		bb->pixrej_hi,
		bb->median_reg[0],
		bb->median_reg[1],
		bb->median_reg[2],
		bb->median_reg[3],
		bb->kern_hsize
			);
}

/*
 * This is the missing merging routine from qfits. Should
 * be replaced by the qfits implementation one once it is out.
 */

qfits_header *fits_header_merge(qfits_header *base, qfits_header *update)
{
	int i;
	qfits_header	*merged_header;
	char		key[FITS_LINESZ+1], val[FITS_LINESZ+1], com[FITS_LINESZ+1], lin[FITS_LINESZ+1];

	merged_header = qfits_header_copy(base);
	for (i=0 ; i<update->n; i++) {
		if (qfits_header_getitem(update,i,key,val,com,lin)) {
			e_error("fits_header_merge: error reading item %i from update header\n");
			return NULL;
		}
		if (strncmp(key,"END",3) != 0) {
			if ( qfits_header_getstr(merged_header,key) != NULL) { /* update value in common card */
				qfits_header_mod(merged_header,key,val,com);
			} else {								/* append new keyword card   */
				qfits_header_add(merged_header,key,val,com,lin);
			}
		}
	}
	return merged_header;
}

/* A completed extension is published only after all writes/close succeed.
 * Earlier completed extensions remain on a later failure; callers receive -1. */
int mef_split(char *name_i, char *name_o, int xtnum)
{
    qfits_header *h_main = NULL;
    qfits_header *h_ext = NULL;
    qfits_header *h_todump = NULL;
    FILE *extension = NULL;
    char *fdata = NULL;
    char output[FILENAMESZ];
    char temporary[FILENAMESZ];
    char zeros[FITS_BLOCK_SIZE];
    int n_ext, first, last, i, fd, data_beg;
    int naxis1, naxis2, bitpix;
    int result = -1;
    int temporary_exists = 0;
    size_t fsize, data_size, bytes_per_pixel, padding;
    long position;

    if (name_i == NULL || name_o == NULL || is_fits_file(name_i) != 1) {
        e_error("cannot find FITS input [%s]", name_i ? name_i : "(null)");
        goto cleanup;
    }
    h_main = qfits_header_read(name_i);
    n_ext = qfits_query_n_ext(name_i);
    if (h_main == NULL || n_ext < 1 || xtnum > n_ext) {
        e_error("cannot read requested extensions of [%s]", name_i);
        goto cleanup;
    }
    if (strlen(name_o) + 40 >= sizeof(output)) {
        e_error("split output name too long [%s]", name_o);
        goto cleanup;
    }
    first = xtnum < 1 ? 1 : xtnum;
    last = xtnum < 1 ? n_ext : xtnum;
    fdata = falloc(name_i, 0, &fsize);
    if (fdata == NULL) {
        e_error("cannot map input [%s]", name_i);
        goto cleanup;
    }
    memset(zeros, 0, sizeof(zeros));
    for (i = first; i <= last; i++) {
        h_ext = qfits_header_readext(name_i, i);
        if (h_ext == NULL) {
            e_error("cannot read extension %d of [%s]", i, name_i);
            goto cleanup;
        }
        naxis1 = qfits_header_getint(h_ext, "NAXIS1", 0);
        naxis2 = qfits_header_getint(h_ext, "NAXIS2", 0);
        bitpix = qfits_header_getint(h_ext, "BITPIX", 0);
        if (naxis1 <= 0 || naxis2 <= 0 ||
            (bitpix != 8 && bitpix != 16 && bitpix != 32 && bitpix != 64 &&
             bitpix != -32 && bitpix != -64)) {
            e_error("invalid image geometry/type in [%s] extension %d", name_i, i);
            goto cleanup;
        }
        bytes_per_pixel = BYTESPERPIXEL(bitpix);
        if ((size_t)naxis1 > (size_t)-1 / (size_t)naxis2 ||
            (size_t)naxis1 * (size_t)naxis2 > (size_t)-1 / bytes_per_pixel) {
            e_error("image byte count overflow in [%s] extension %d", name_i, i);
            goto cleanup;
        }
        data_size = (size_t)naxis1 * (size_t)naxis2 * bytes_per_pixel;
        if (qfits_get_datinfo(name_i, i, &data_beg, NULL) != 0 || data_beg < 0 ||
            (size_t)data_beg > fsize || data_size > fsize - (size_t)data_beg) {
            e_error("invalid/truncated data in [%s] extension %d", name_i, i);
            goto cleanup;
        }
        sprintf(output, "%s_%02d.fits", name_o, i);
        sprintf(temporary, "%s.tmp.XXXXXX", output);
        fd = mkstemp(temporary);
        if (fd < 0) {
            e_error("cannot create temporary output for [%s]", output);
            goto cleanup;
        }
        temporary_exists = 1;
        extension = fdopen(fd, "wb");
        if (extension == NULL) {
            close(fd);
            e_error("cannot open temporary output for [%s]", output);
            goto cleanup;
        }
        h_todump = fits_header_merge(h_main, h_ext);
        if (h_todump == NULL || qfits_header_dump(h_todump, extension) != 0 ||
            fwrite(fdata + data_beg, 1, data_size, extension) != data_size) {
            e_error("cannot write split output [%s]", output);
            goto cleanup;
        }
        position = ftell(extension);
        if (position < 0) {
            e_error("cannot determine output size [%s]", output);
            goto cleanup;
        }
        padding = (FITS_BLOCK_SIZE - (position % FITS_BLOCK_SIZE)) % FITS_BLOCK_SIZE;
        if (fwrite(zeros, 1, padding, extension) != padding || fflush(extension) != 0) {
            e_error("cannot finish split output [%s]", output);
            goto cleanup;
        }
        if (fclose(extension) != 0) {
            extension = NULL;
            e_error("cannot close split output [%s]", output);
            goto cleanup;
        }
        extension = NULL;
        if (rename(temporary, output) != 0) {
            e_error("cannot publish split output [%s]", output);
            goto cleanup;
        }
        temporary_exists = 0;
        qfits_header_destroy(h_todump);
        h_todump = NULL;
        qfits_header_destroy(h_ext);
        h_ext = NULL;
    }
    result = 0;
cleanup:
    if (extension != NULL) fclose(extension);
    if (temporary_exists && unlink(temporary) != 0)
        e_error("cannot remove incomplete output [%s]", temporary);
    if (h_todump != NULL) qfits_header_destroy(h_todump);
    if (h_ext != NULL) qfits_header_destroy(h_ext);
    if (h_main != NULL) qfits_header_destroy(h_main);
    if (fdata != NULL) free(fdata);
    return result;
}


/*
 *  * Loads a WFI framelist into a cube_t structure.
 *   */
cube_t * mef_cube_framelist_load(framelist *flist, int xtnum)
{
	cube_t    *     loaded ;
	image_t  * mef_frame ;
	register pixelvalue *pt;
	int                     i ;
	int               *     exts ;
	int                     err ;
	int                     single_frames ;

	/* Load framelist */
	if (flist==NULL) {
		e_error("mef_cube_framelist_load: cannot load input framelist");
		return NULL ;
	}
	if (debug_active() >= 1) {
	   e_comment(1, "mef_cube_framelist_load: Preparing to load framelist.");
	   }
	/* Get number of extensions contained in each frame */
	if (debug_active() >= 1) {
	   e_comment(1, "mef_cube_framelist_load: Allocating memory for array with list of names");
	   }
	exts = malloc(flist->n * sizeof(int));
	if (debug_active() >= 1) {
	   e_comment(1, "mef_cube_framelist_load: Done");
	   }
	for (i=0 ; i<flist->n ; i++) {
	        if (debug_active() >= 1) {
		    e_comment(1, "mef_cube_framelist_load: Determining number of extensions for image %s",flist->name[i]);
		    }
		exts[i] = qfits_query_n_ext(flist->name[i]);
		if (debug_active() >= 1) {
		   e_comment(1, "%d",exts[i]);
		   }
	}
	if (debug_active() >= 1) {
	    e_comment(1, "mef_cube_framelist_load: Checking consistency");
	    }

	/* Check consistency - FSE 2024-06-29: force to always read from list by setting single_frames=0. original was 1 */
	err=0 ;
	single_frames = 0;
	for (i=1 ; i<flist->n ; i++) {
		/* Check that all files have the same number of extensions */
		if (exts[i]!=exts[0]) {
			e_error("mef_cube_framelist_load: inconsistent input data set");
			err++ ;
		}
		/* Check that the requested extension (if any) is present */
		if (xtnum>0) {
			if (xtnum>exts[i]) {
				e_error("mef_cube_framelist_load: inconsistent input data set");
				err++;
			}
			if (exts[i]>0) {
				single_frames = 0 ;
			}
		}
	}
	if (debug_active() >= 1) {
	   e_comment(1, "mef_cube_framelist_load: Done");
	   }
	/* Process errors */
	if (err) {
		e_error("mef_cube_framelist_load: %d errors occurred during reading", err);
		for (i=0 ; i<flist->n ; i++) {
			e_error("mef_cube_framelist_load: frame [%s] has %d extensions", flist->name[i], exts[i]);
		}
		framelist_del(flist);
		free(exts);
		return NULL ;
	}
	if (debug_active() >= 1) {
	   e_comment(1, "mef_cube_framelist_load: Freeing (number of) exts array");
	   }
	free(exts);
	if (debug_active() >= 1) {
	   e_comment(1, "mef_cube_framelist_load: Done");
	   }

	/* A list of single frames */
	err=0 ;
	if (single_frames) {
		if (debug_active() >= 1) {
		   e_comment(1, "mef_cube_framelist_load: Single frame case");
		   e_comment(1, "mef_cube_framelist_load: Loading image %s into cube...", flist->name[0]);
		   }
		loaded = cube_load_strings(&flist->name[0], flist->n);
		if (loaded == NULL) {
			e_error("mef_cube_framelist_load: loading single file  [%s] from framelist", flist->name[0]);
			err++ ;
		}
	} else {
		/* A list of whole WFI frames */
		/* Load first image */
		i=0;
		if (debug_active() >= 1) {
		   e_comment(1, "mef_cube_framelist_load: Multiple extensions case");
		   e_comment(1, "mef_cube_framelist_load: Loading extension %d of image %s into cube...", xtnum, flist->name[i]);
		   }
		mef_frame = mef_load_ext(flist->name[i], xtnum) ;
		if (mef_frame==NULL) {
			e_error("mef_cube_loadframelist_: cannot load frame [%s][%d]", flist->name[i], xtnum);
			err++ ;
		}
		loaded = cube_new(mef_frame->lx, mef_frame->ly, flist->n);
		loaded->plane[0] = mef_frame ;
		for (i=1 ; i<flist->n ; i++) {
			mef_frame = mef_load_ext(flist->name[i], xtnum);
			if (debug_active() >= 1) {
			   e_comment(1, "mean= %f", (float) image_getmean(mef_frame));
			   }
			if (mef_frame == NULL) {
				e_error("mef_cube_framelist_load: cannot load frame [%s][%d]", flist->name[i], xtnum);
				err++ ;
			}
			loaded->plane[i] = mef_frame ;
		}
	}
	if (debug_active() >= 1) {
	   e_comment(1, "mef_cube_framelist_load:stats");
	   }
	/* Process errors */
	if (err) {
		e_error("mef_cube_framelist_load: an error occurred during loading: aborting");
		if (loaded!=NULL) {
			cube_del(loaded) ;
		}
		loaded = NULL ;
	}
	return loaded ;
}

/*
 *  * Loads a WFI list into a cube_t structure.
 *   */
cube_t * mef_cube_load(char * filename, int xtnum)
{
	cube_t    *     loaded ;
	image_t  * mef_frame ;
	register pixelvalue *pt;
	framelist *     flist ;
	int                     i ;
	int               *     exts ;
	int                     err ;
	int                     single_frames ;

	/* Check entries */
	if (filename==NULL) return NULL ;

	/* Load framelist */
	if (debug_active() >= 1) {
	   e_comment(1, "mef_cube_load: Loading framelist %s...", filename);
	   }
	flist = framelist_load(filename);
	if (flist==NULL) {
		e_error("mef_cube_load: cannot load frame list [%s]", filename);
		return NULL ;
	}
	if (debug_active() >= 1) {
	   e_comment(1, "mef_cube_load: Done.");
	   }
	loaded = mef_cube_framelist_load(flist, xtnum);
	return loaded;
}




image_t * mef_load_ext(char * filename, int xtnum)
{
	qfitsloader		ql ;
	image_t		*	ext_load ;

	ql.filename = filename ;
	ql.xtnum    = xtnum ;
	ql.pnum     = 0 ;
	ql.map      = 1 ;
#ifdef DOUBLEPIX
	ql.ptype    = PTYPE_DOUBLE ;
#else
	ql.ptype    = PTYPE_FLOAT ;
#endif
	if (debug_active() >= 1) {
	   e_comment(1, "mef_load_ext: Init qloader for extension %d of file %s", ql.xtnum, ql.filename);
	   }
	if (qfitsloader_init(&ql)!=0) {
		return NULL ;
	}
	if (debug_active() >= 1) {
	   e_comment(1, "Done.");
	   e_comment(1, "ef_load_ext: Loading pixels...");
	   }
	if (qfits_loadpix(&ql)!=0) {
		return NULL ;
	}
	if (debug_active() >= 1) {
	   e_comment(1, "Done.");
	   }

	ext_load = malloc(sizeof(image_t));
	ext_load->lx = ql.lx ;
	ext_load->ly = ql.ly ;
#ifdef DOUBLEPIX
	ext_load->data = (pixelvalue*)ql.dbuf ;
#else
	ext_load->data = (pixelvalue*)ql.fbuf ;
#endif

	/* for debugging purposes
	   {int i;
	   for (i=0;i<(ext_load->lx)*(ext_load->ly);i++) {
	   printf("%f",(float) ext_load->data[i]);
	   }
	   }
	   --- end debugging ---*/

	return ext_load ;
}


int mef_is_extension(char * filename)
{
	return qfits_query_n_ext(filename) ;
}

image_t * mef_overscan_correction(image_t *   mef_frame, mef_bb *bb, int nplane, char * what)
{
    int *   prescan_x = ((bb->ccd)+(bb->xtnum-1))->prescan_x;
    int *   overscan_x = ((bb->ccd)+(bb->xtnum-1))->overscan_x;
    int *   rej_int = bb->scanrej;
    int *   crop_reg = ((bb->ccd)+(bb->xtnum-1))->trimreg;
    int     use_prescan = bb->use_prescan;
    int     use_overscan = bb->use_overscan;
	image_t	*	cropped_frame ;
	pixelvalue		filtered ;
    pixelvalue      avg_filtered;
    int             nfiltered;
	pixelvalue	*	bias_line ;
    pixelvalue  *   scan_line ;
    double          medval;
    double      *   scan_double;
    double          stdev_val ;
	int				scan_width ;
	int				i, j, k ;
    int             zIndex;
	pixelvalue	*	pix ;
	int		prescan_factor, overscan_factor;

	/* Sanity tests with input parameters */
 	prescan_factor = 0;
	overscan_factor = 0;
	if (use_prescan != 0) prescan_factor = 1;
	if (use_overscan != 0) overscan_factor = 1;

	scan_width = (prescan_x[1]-prescan_x[0]+1)*prescan_factor +
		(overscan_x[1]-overscan_x[0]+1)*overscan_factor ;

	if ((rej_int[0]+rej_int[1])>=scan_width) {
		e_error("in rejection parameters: rejecting too many pixels");
		return NULL ;
	}

	if ((crop_reg[0]>=crop_reg[1])||(crop_reg[2]>=crop_reg[3])) {
		e_error("in crop region definition");
		return NULL ;
	}


	/* Bring coordinates back to C convention */
	prescan_x[0]-- ; prescan_x[1]-- ; overscan_x[0]-- ; overscan_x[1]-- ;

	/* Make out bias column */
	bias_line = malloc(scan_width * sizeof(pixelvalue));
    scan_line = malloc(mef_frame->ly * sizeof(pixelvalue));

	/* Loop on all lines */
    avg_filtered = 0.0;
    nfiltered = 0;
	for (j=0 ; j<mef_frame->ly ; j++) {
		pix = mef_frame->data + j*mef_frame->lx ;
		k=0 ;
		if (use_prescan != 0) {
		   for (i=prescan_x[0] ; i<=prescan_x[1] ; i++) {
			bias_line[k++] = pix[i];
		   }
		}
		if (use_overscan != 0) {
		   for (i=overscan_x[0] ; i<=overscan_x[1] ; i++) {
			bias_line[k++] = pix[i] ;
		   }
		}
		filtered =
			function1d_average_reject(bias_line,
					scan_width,
					rej_int[0],
					rej_int[1]);
        /* e_comment(1,"Subtracting %f from each bias pixel", filtered); */
		for (i=0 ; i<mef_frame->lx ; i++) {
			pix[i] -= filtered ;
		}
        scan_line[j] = filtered;
        avg_filtered += filtered;
        nfiltered += 1;
	}
    medval = (double) median_pixelvalue(scan_line, mef_frame->ly);
    scan_double = pixel2double_array(scan_line, mef_frame->ly);
    for (j=0 ; j<mef_frame->ly ; j++) {
        scan_double[j] -= medval;
    }
    stdev_val = double_rms(scan_double, mef_frame->ly);
    free(bias_line);
    free(scan_line);

    e_comment(1, "********************* overscan medval: %f stdev_val: %f", medval, stdev_val);

    /* We write the bb-> qc keywords for the corresponding frame */
    if (bb->nxts == 1) {    /* if we work in only one extension */
        zIndex = 0;
    } else {                        /* we are working in all the extensions */
        zIndex = bb->xtnum-1;
    }
    if (!strcmp(what, "bias")) {
        bb->bias_scan_median[nplane] = medval ;
        bb->bias_scan_stdev[nplane] = stdev_val ;
        e_comment(1, "%s[%d]  -- nplane: %d  overscan medval: %f stdev_val: %f", get_basename(bb->bias_frame_name[nplane]), bb->xtnum, nplane, medval, stdev_val);
    }

    if (!strcmp(what, "dome")) {
        bb->dome_scan_median[nplane] = medval ;
        bb->dome_scan_stdev[nplane] = stdev_val ;
        e_comment(1, "%s[%d]  -- nplane: %d  overscan medval: %f stdev_val: %f", get_basename(bb->dome_frame_name[nplane]), bb->xtnum, nplane, medval, stdev_val);
    }

    if (!strcmp(what, "sky")) {
        bb->sky_scan_median[nplane] = medval ;
        bb->sky_scan_stdev[nplane] = stdev_val ;
        e_comment(1, "%s[%d]  -- nplane: %d  overscan medval: %f stdev_val: %f", get_basename(bb->sky_frame_name[nplane]), bb->xtnum, nplane, medval, stdev_val);
    }

    if (!strcmp(what, "science")) {
        bb->science_scan_median[nplane] = medval ;
        bb->science_scan_stdev[nplane] = stdev_val ;
        e_comment(1, "%s[%d]  -- nplane: %d  overscan medval: %f stdev_val: %f", get_basename(bb->science_frame_name[nplane]), bb->xtnum, nplane, medval, stdev_val);
    }

	/* Bring coordinates back to FITS convention */
	prescan_x[0]++ ; prescan_x[1]++ ; overscan_x[0]++ ; overscan_x[1]++ ;

	/* Extract cropped region */
	cropped_frame = image_getvig(mef_frame,
			crop_reg[0],
			crop_reg[2],
			crop_reg[1],
			crop_reg[3]);


	return cropped_frame ;
}

int	mef_cube_overscan_correction(cube_t *i_cube,mef_bb *bb, char * what)
{
	int 		i;
	image_t	*	scancorr;

	if (debug_active() >= 1) {
	   e_comment(1, "applying overscan/prescan/trimming correction");
	   e_comment(1,"prescan  = [%d %d]",(((bb->ccd)+(bb->xtnum-1))->prescan_x)[0],
					 (((bb->ccd)+(bb->xtnum-1))->prescan_x)[1]);
	   e_comment(1,"overscan = [%d %d]",(((bb->ccd)+(bb->xtnum-1))->overscan_x)[0],
					 (((bb->ccd)+(bb->xtnum-1))->overscan_x)[1]);
	   e_comment(1,"trimreg  = [%d %d %d %d]",(((bb->ccd)+(bb->xtnum-1))->trimreg)[0],
					 (((bb->ccd)+(bb->xtnum-1))->trimreg)[1],
					 (((bb->ccd)+(bb->xtnum-1))->trimreg)[2],
					 (((bb->ccd)+(bb->xtnum-1))->trimreg)[3]);
	   }
	for (i=0 ; i<i_cube->np ; i++) {
		compute_status("correcting", i, i_cube->np, 1);

        /* Note that in this case "i" (nplane) corresponds to the frame number in the frame list */
        scancorr = mef_overscan_correction(i_cube->plane[i], bb, i, what);
		if (scancorr == NULL) {
			e_error("mef_cube_overscan_correction: during overscan correction in plane %d", i+1);
			cube_del(i_cube);
			return -1 ;
		}
		image_del(i_cube->plane[i]);
		i_cube->plane[i] = scancorr ;
	}
	/* Cube size has changed, recompute sizes */
	i_cube->lx = i_cube->plane[0]->lx;
	i_cube->ly = i_cube->plane[0]->ly;
	return 0;
}


int mef_saturation_check(cube_t * prep, mef_bb * bb)
{
    int                 i ;
    int                 p ;
    int                 npix ;
    int                 limit ;

    limit = (int)(bb->sat_max * (prep->lx * prep->ly));
    for (p=0 ; p<prep->np ; p++) {
        if (prep->np>1) {
           compute_status("saturation count", p, prep->np, 2);
        }
        npix = 0 ;
        for (i=0 ; i<(prep->lx * prep->ly) ; i++) {
            if (prep->plane[p]->data[i] > (pixelvalue)bb->sat_level) {
                npix++ ;
            }
        }
        if (npix > limit) {
           e_error("frame %s has %d pixels above saturation (%g)",
                   bb->science_frame_name[p],
                   npix,
                   bb->sat_level);
           return -1 ;
        }
	e_comment(1,"frame %s has %d pixels above saturation (%g)",
                   bb->science_frame_name[p],
                   npix,
                   bb->sat_level);
    }
    return 0 ;
}



/* There are 4 quadrants in a frame */
#define WFI_NQUAD		4

int mef_gradient_check(
		image_t	*	mef_frame,
		double			max_grad_level
		)
{
	double	avg_frame ;
	double	avg_quad[WFI_NQUAD] ;
	int		i ;
	int		gradient_ok ;

	/* Compute average for the whole frame */
	avg_frame = image_getmean(mef_frame);
	if (fabs(avg_frame)<1e-6) {
		e_warning("frame has zero average: cannot compute gradient check");
		return 1 ;
	}

	/* Compute average value inside each quadrant */
	/* Lower left quadrant */
	avg_quad[0] = image_getmean_vig(
			mef_frame,
			1,
			mef_frame->lx/2,
			1,
			mef_frame->ly/2);
	/* Lower right quadrant */
	avg_quad[1] = image_getmean_vig(
			mef_frame,
			1+mef_frame->lx/2,
			mef_frame->lx,
			1,
			mef_frame->ly/2);
	/* Upper left quadrant */
	avg_quad[2] = image_getmean_vig(
			mef_frame,
			1,
			mef_frame->lx/2,
			1+mef_frame->ly/2,
			mef_frame->ly);
	/* Upper right quadrant */
	avg_quad[3] = image_getmean_vig(
			mef_frame,
			1+mef_frame->lx/2,
			mef_frame->lx,
			1+mef_frame->ly/2,
			mef_frame->ly);

	e_comment(1, "average/quadrants: [%g] %4.2f %4.2f %4.2f %4.2f",
			avg_frame,
			avg_quad[0],
			avg_quad[1],
			avg_quad[2],
			avg_quad[3]);

	/* Compute ratio */
	gradient_ok = 1 ;
	for (i=0 ; i<WFI_NQUAD ; i++) {
		avg_quad[i] = (avg_frame - avg_quad[i]) / avg_frame ;
		if (avg_quad[i] > max_grad_level) {
			e_warning("quadrant ratio above limit (%g)", max_grad_level);
			gradient_ok = 0 ;
		}
	}

	return gradient_ok ;
}



void simplifyFilterName(char *zFilter)
{
	char zChar ;
	int i;

	/* 
	 * we first strip the first apostrofe overwriting 
	 * one position back, and then overwrite the last 
	 * apostrophe 
	 */
	i=0;
        while ( zFilter[i+1] != '\0' ) {
	  zFilter[i] = zFilter[i+1];
          i++;
        }
	zFilter[i-1] = '\0';
	
	/* now we get rid of problematic characters */
	i=0;
	while ( zFilter[i] != '\0' ) {
	  if (zFilter[i] == '#' || zFilter[i] == '/') zFilter[i] = '_' ;	
	  i++;
	}
	return ;
}

/*
 * In mef_valid_subset we check that all the files
 * contain FITS files, with the same filter, and binning.
 */
int	mef_valid_subset(mef_bb * bb, char *what)
{
	qfits_header 	*	fh ;
	framelist 	* 	input_frames ;
	char		*	name_i ;
	char		*	first_name ;
	char			cval[80] ;
	char		*	getval ;
	char			*zFilter ;
	int			i ;

    e_comment(1, "mef_valid_subset: --------- validating %s ----------", what);
	/* Check entries */
	if (bb==NULL) {
		e_error("mef_valid_subset: NULL bb pointer");
		return -1 ;
	}
	if (!what || !*what) {
		e_error("mef_valid_subset: NULL what pointer");
		return -1;
	}
	/* Set parameters to requested frame type */
	if (!strcmp(what, "bias")) {
        e_comment(1, "mef_valid_subset: validating BIAS file %s", bb->name_bias);
		name_i = bb->name_bias ;
	} else if (!strcmp(what, "bpm")) {
        /* for this to work we need to validate first the bias */
        if (is_fits_file(bb->name_bpm)) {
            sprintf(cval, "%s", mef_get_output_filename(bb,"bpm"));
            e_comment(1, "mef_valid_subset: validating BPM file -%s-", cval);
            if (is_fits_file(cval) == 1) {
                e_comment(1, "mef_valid_subset: %s is FITS file", cval);
                name_i = cval;
                e_comment(1, "mef_valid_subset: name_i: %s", name_i);
            } else {
                e_comment(1, "mef_valid_subset: %s is NOT a FITS file", cval);
		        sprintf(name_i, bb->name_bpm) ;
            }
        } else {
            e_comment(1, "mef_valid_subset: bb->name_bpm: %s is NOT a FITS file", bb->name_bpm);
            name_i = bb->name_bpm ;
        }
	} else if (!strcmp(what, "dome")) {
		name_i = bb->name_dome ;
	} else if (!strcmp(what, "sky")) {
		name_i = bb->name_sky ;
	} else if (!strcmp(what, "science")) {
		name_i = bb->science_name_i ;
	} else {
		e_error("mef_valid_subset: unknown frame type [%s] should be 'dome' or 'sky'",what);
		return -1 ;
	}

	if (name_i == NULL) {
		e_comment(1,"mef_valid_subset: Nothing to validate, NULL name for %s.",what);
		return 0;
	} else {
        e_comment(1,"mef_valid_subset: name_i:  %s for %s.",name_i, what);
    }



	/*
	 * Read header from the first, reference frame, and then
	 * compare the values of the filter and binning keywords.
	 * They must be the same for a valid dataset.
	 */
	e_comment(0,"\nmef_valid_subset: reading (map) and validating %s frame list: %s (same filter and binning)\n",what, name_i);


	if ( (fh = mef_header_primary(name_i)) == NULL) {
		e_error("mef_valid_subset: can not read %s primary headers for %s",name_i, what);
		return -1;
	}
	/* here we allow for the possibility that what is passed is
	 * a previoulsy calculated master frame in FITS format, and not a 
	 * list to be used for its construction. In this case, we create a single
	 * frame list with a single file in it, with the passed fits file name.
	 */
	if ( (input_frames = framelist_load(name_i)) == NULL) {
	    if (is_fits_file(name_i)) {
		    input_frames = framelist_new(1);
		    input_frames->name[0] = strdup(name_i);
		    first_name = strdup(name_i);
	    } else {
		    e_error("mef_valid_subset: %s is not a framelist or a FITS file. Aborting", name_i);
		return -1 ;
	    }

	} else {
	    first_name = framelist_firstname(name_i);
	}
	if (first_name==NULL) {
		e_error("mef_valid_subset: cannot get primary FITS header from %s", name_i);
		e_error("mef_valid_subset: can not read %s aborting save", name_i);
		return -1 ;
	}
	/*
	 * now we extract the keywords from this header if it had not been done before
	 * and if it is not a bias frame
	 */
	if (!strcmp(what, "dome") || !strcmp(what, "sky") || !strcmp(what, "science")) {		
	   if (bb->filter_val== NULL) {
		bb->filter_val = strdup(qfits_header_getstr(fh,bb->filter_key));
		if (bb->filter_val == NULL) {
			e_error("%s keyword not present in headers of %s",bb->filter_key,first_name);
			return -1;
		}
		e_comment(1,"filter: %s",bb->filter_val);
	   }
	   zFilter = strdup(bb->filter_val) ;
	   simplifyFilterName(zFilter) ;
	}
	if (bb->binx_val == NULL) {
		bb->binx_val = strdup(qfits_header_getstr(fh,bb->binx_key));
		if (bb->binx_val == NULL) {
			e_error("%s keyword not present in headers of %s",bb->binx_key,first_name);
			return -1;
		}
		e_comment(1,"  binx: %s",bb->binx_val);
	}
	if (bb->biny_val == NULL) {
		bb->biny_val = strdup(qfits_header_getstr(fh,bb->biny_key));
		if (bb->biny_val == NULL) {
			e_error("%s keyword not present in headers of %s",bb->biny_key,first_name);
			return -1;
		}
		e_comment(1,"  biny: %s",bb->biny_val);
	}
	qfits_header_destroy(fh);
	if (!strcmp(what, "bias")) {
	   sprintf(cval,"%dx%d",atoi(bb->binx_val),atoi(bb->biny_val));
	   bb->bias_partition = strdup(cval);
       bb->bpm_partition = strdup(cval);
    } else if (!strcmp(what, "bpm"))  {
       sprintf(cval,"%dx%d",atoi(bb->binx_val),atoi(bb->biny_val));
       bb->bpm_partition = strdup(cval);
	} else {
	   /* We trim spaced to the right of the zFilter variable */
	   int index = -1;
           int iii = 0;
           while(zFilter[iii] != '\0')
                {
                if(zFilter[iii] != ' ' && zFilter[iii] != '\t' && zFilter[iii] != '\n')
                {
                    index= iii;
                    }
                iii++;
                }
           zFilter[index + 1] = '\0';

	   sprintf(cval,"%s_%dx%d",zFilter,atoi(bb->binx_val),atoi(bb->biny_val));

	   bb->data_partition = strdup(cval);
	   bb->flat_partition = strdup(cval);
	}
	e_comment(1,"cval: %s",cval);
	e_comment(1,"data partition = %s   bias partition = %s   bpm partition: %s\n",bb->data_partition,bb->bias_partition, bb->bpm_partition);

	/*
	 * here we loop over all the frames checking consistency
	 */
	if (!bb->noverify) {
	   for (i=0; i<input_frames->n; i++) {
		if (is_fits_file(input_frames->name[i])) {
			fh = qfits_header_read(input_frames->name[i]);
		}
		if (!strcmp(what, "dome") || !strcmp(what, "sky") || !strcmp(what, "science")) {
		    if (!strcmp( bb->filter_val, qfits_header_getstr(fh,bb->filter_key)) && \
			!strcmp( bb->binx_val,   qfits_header_getstr(fh,bb->binx_key)) && \
			!strcmp( bb->biny_val,   qfits_header_getstr(fh,bb->biny_key))       ) {
			e_comment(1,"%-30s --- %s. binx: %s  biny: %s OK.\n",\
				input_frames->name[i],qfits_header_getstr(fh,bb->filter_key), \
				qfits_header_getstr(fh,bb->binx_key), \
				qfits_header_getstr(fh,bb->biny_key));
		    } else {
			e_error("%-30s --- %s <--> %s  %s <--> %s  %s <--> %s",\
				input_frames->name[i], \
				qfits_header_getstr(fh,bb->filter_key), bb->filter_val, \
				qfits_header_getstr(fh,bb->binx_key),   bb->binx_val, \
				qfits_header_getstr(fh,bb->biny_key),   bb->biny_val);
			return -1;
		    }
		} else {
		    if (!strcmp( bb->binx_val,   qfits_header_getstr(fh,bb->binx_key)) && \
			!strcmp( bb->biny_val,   qfits_header_getstr(fh,bb->biny_key))       ) {
			    e_comment(1,"%-30s ---  binx: %s  biny: %s OK.\n",\
				input_frames->name[i], \
				qfits_header_getstr(fh,bb->binx_key), \
				qfits_header_getstr(fh,bb->biny_key));
		    } else {
			    e_error("%-30s <--> %s  %s <--> %s  %s <--> %s",\
                                input_frames->name[i], \
                                qfits_header_getstr(fh,bb->binx_key),   bb->binx_val, \
                                qfits_header_getstr(fh,bb->biny_key),   bb->biny_val);
                            return -1;
                    }
			

		}
		qfits_header_destroy(fh);
	   }
	e_comment(1, "All files verify OK.");
	}
	return 0;
}

/*
 * Routine to build a BPM. Currently only used in the master flat construction
 * where it is needed in the routine that filters the sky. All other operations
 * of the pipeline are on single image pixels, either statistics or combination.
 * The statistics will be affected by bad pixels but this is not too bad for QC.
 *
 */
pixelmap * mef_build_bpm(mef_bb *bb, image_t * bias)
{
	cube_t 	*cube_in;
	image_t **results;
	image_t	*norm_gain;
	pixelmap *bp_map;
    framelist *flist;
    qfits_header *fhdr_extra;
    qfits_header *fhdr_primary;
    qfits_header *fh;
    qfits_header *fh_ext;
    char    *   dateobs_ptr;
    int i;
	char 	cval[80];
    char    cval2[80];
    char    *cval_ptr;
    char    *zname_ptr;
    char    cval_prev[80];
	

        e_comment(1,"loading BPM cube");
        if ( (cube_in = mef_cube_load(bb->name_bpm,bb->xtnum)) == NULL ) {
            e_error("in loading cube [%s]: aborting",bb->name_bpm);
        }
        e_comment(1,"overscan correcting/trimming BPM cube");
        mef_cube_overscan_correction(cube_in, bb, "bpm");
        /*if (bias == NULL) {
            e_error("bias is a NULL pointer");
            cube_del(cube_in);
            return NULL;
        }*/
        e_comment(1,"bias subtracting BPM cube");
        if (bias!=NULL) {
            if (cube_sub_im(cube_in,bias)!=0) {
                e_error("subtracting bias to BPM cube: aborting");
                cube_del(cube_in);
                return NULL;
            }
        }

        /* iproc/detector.c */
        e_comment(1,"regression analysis of BPM cube");
        if (bb->bpm_proportional_flag) results = cube_create_gainmap_proportional(cube_in);
        else results = cube_create_gainmap_robust(cube_in);
        cube_del(cube_in);
        if ( (results == NULL) || (results[0] == NULL) || (results[1] == NULL) ) {
                e_error("creating regresion maps for BPM");
                return NULL;
        }
        e_comment(1,"normalizing gains");
        norm_gain = image_normalize(results[0], NORM_MEAN);
        e_comment(1,"done.");
        e_comment(1,"mean gain = %f   std. dev.: %f",
                        image_getmean(norm_gain),image_getstdev(norm_gain));
        if (results[0] != NULL) image_del (results[0]);
        if (results[1] != NULL) image_del (results[1]);
        if (results[2] != NULL) image_del (results[2]);
        if (results != NULL) free(results);

        if ( (bp_map = image_threshold2pixelmap(norm_gain, bb->bpm_gainthr_lo, bb->bpm_gainthr_hi)) == NULL) {
            e_error("can not create pixel map: NULL output");
            image_del(norm_gain);
            return NULL;
        } else {
            e_comment(1,"total pixels:%d        good pixels: %d        bad pixels: %d",
                         bp_map->lx*bp_map->ly, bp_map->ngoodpix, bp_map->lx*bp_map->ly - bp_map->ngoodpix);

            /* now we add a few headers to the file */
            fhdr_extra = qfits_header_default();
            qfits_header_add(fhdr_extra, "ECLIPSE", get_eclipse_version(), "Based on Eclipse version 5.0.0 by N. Devillard", NULL);
            e_comment(1, "ECLIPSE: %s", qfits_header_getstr(fhdr_extra, "ECLIPSE"));

            /*
            if (fhdr_extra!=NULL){
                e_comment(1, "header console dump 1 of fhdr_extra");
                qfits_header_consoledump(fhdr_extra);
                e_comment(1, "done");
            } else {
                e_comment(1, "fhdr_extra: NULL in dump 1");
            }
            */

            sprintf(cval, "%d", BPP_8_UNSIGNED);
            qfits_header_add_after(fhdr_extra, "SIMPLE", "BITPIX", cval, "bits per pixel", NULL);
            e_comment(1, "BITPIX added");

            sprintf(cval, "2");
            qfits_header_add(fhdr_extra, "NAXIS", cval, "single image", NULL);

            sprintf(cval, "%d", bp_map->lx) ;
            qfits_header_add(fhdr_extra, "NAXIS1", cval, "x axis", NULL);

            sprintf(cval, "%d", bp_map->ly) ;
            qfits_header_add(fhdr_extra, "NAXIS2", cval, "y axis", NULL);

            /* if this is the first extention we create a new ORIGFILE name */
            if (bb->xtnum == 1) {
                mef_create_orig_filename(bb, "bpm");
                e_comment(1,"creating ORIGFILE key: %s",bb->orig_bpm);
            }
            qfits_header_add_after(fhdr_extra, "NAXIS2", "ORIGFILE", bb->orig_bpm, "Original file name", NULL);

            /* REC.FLAT.PRSCX */
            sprintf(cval, "%s X1", bb->prescan_x_key );
            sprintf(cval2, "%d", (((bb->ccd)+(bb->xtnum-1))->prescan_x)[0]);
            qfits_header_add(fhdr_extra, cval, 
                                        cval2,
                                        bb->prescan_x_comment, NULL);

            sprintf(cval, "%s X2", bb->prescan_x_key );
            sprintf(cval2, "%d", (((bb->ccd)+(bb->xtnum-1))->prescan_x)[1]);
            qfits_header_add(fhdr_extra, cval,
                                         cval2,
                                         bb->prescan_x_comment, NULL);

            /* REC.FLAT.OVSCX */
            sprintf(cval, "%s X1", bb->overscan_x_key);
            sprintf(cval2, "%d", (((bb->ccd)+(bb->xtnum-1))->overscan_x)[0]);
            qfits_header_add(fhdr_extra, cval,
                                        cval2,
                                        bb->overscan_x_comment, NULL);

            sprintf(cval, "%s X2", bb->overscan_x_key);
            sprintf(cval2, "%d", (((bb->ccd)+(bb->xtnum-1))->overscan_x)[1]);
            qfits_header_add(fhdr_extra, cval,
                                        cval2,
                                        bb->overscan_x_comment, NULL);


            /* REC.FLAT.RJOVSC */
            sprintf(cval, "%s NLOW", bb->scanrej_key);
            sprintf(cval2, "%d", bb->scanrej[0]);
            qfits_header_add(fhdr_extra, cval, cval2, bb->scanrej_comment, NULL);

            sprintf(cval, "%s NHIGH", bb->scanrej_key);
            sprintf(cval2, "%d", bb->scanrej[1]);
            qfits_header_add(fhdr_extra, cval, cval2, bb->scanrej_comment, NULL);



            /* REC.BIAS.TRIM */
            sprintf(cval, "%s X1", bb->trimreg_key);
            sprintf(cval2, "%d", (((bb->ccd)+(bb->xtnum-1))->trimreg)[0]);
            qfits_header_add(fhdr_extra, cval,
                                        cval2,
                                        bb->trimreg_comment, NULL);

            sprintf(cval, "%s X2", bb->trimreg_key);
            sprintf(cval2, "%d", (((bb->ccd)+(bb->xtnum-1))->trimreg)[1]);
            qfits_header_add(fhdr_extra, cval,
                                        cval2,
                                        bb->trimreg_comment, NULL);

            sprintf(cval, "%s Y1", bb->trimreg_key);
            sprintf(cval2, "%d", (((bb->ccd)+(bb->xtnum-1))->trimreg)[2]);
            qfits_header_add(fhdr_extra, cval,
                                        cval2,
                                        bb->trimreg_comment, NULL);

            sprintf(cval, "%s Y2", bb->trimreg_key);
            sprintf(cval2, "%d", (((bb->ccd)+(bb->xtnum-1))->trimreg)[3]);
            qfits_header_add(fhdr_extra, cval,
                                        cval2,
                                        bb->trimreg_comment, NULL);

         /*
         * bb->bpm_propflag_key
         * bb->bpm_propflag_comment
         * bb->bpm_lgainthr_key
         * bb->bpm_lgainthr_comment
         * bb->bpm_hgainthr_key
         * bb->bpm_hgainthr_comment
         * bb->bpm_frame_i_key
         * bb->bpm_frame_i_comment
         */

            /* MEF.BPM.PROPFLAG */
            sprintf(cval, "%d", bb->bpm_proportional_flag);
            qfits_header_add(fhdr_extra,bb->bpm_propflag_key, cval, bb->bpm_propflag_comment, NULL);

            /* MEF.BPM.LGAINTHR */
            sprintf(cval, "%f",  bb->bpm_gainthr_lo);
            qfits_header_add(fhdr_extra,bb->bpm_lgainthr_key, cval, bb->bpm_lgainthr_comment, NULL);

            /* MEF.BPM.HGAINTHR */
            sprintf(cval, "%f",  bb->bpm_gainthr_hi);
            qfits_header_add(fhdr_extra, bb->bpm_hgainthr_key, cval, bb->bpm_hgainthr_comment, NULL);

            /* We add the list of frames used to determine the BPM */
            flist = framelist_load(bb->name_bpm);
            sprintf(cval_prev,"NAXIS2");
            for (i=0 ; i<flist->n ; i++) {
                sprintf(cval,"%s FRAME%03d", bb->bpm_frame_i_key, i+1);
                e_comment(1, "mef_build_bpm: adding key %s",cval);
                qfits_header_add_after(fhdr_extra,cval_prev, cval, flist->name[i], bb->bpm_frame_i_comment,NULL);
                sprintf(cval_prev, cval);

                fh = qfits_header_read(flist->name[i]);
                if (fh==NULL) {
                    e_error("reading FITS header from [%s]", flist->name[i]);
                    return NULL ;
                }


                /* we save DATE-OBS of the first frame */
                /* Read PRIMARY FITS header from input file */
                if (i==0) {

                    dateobs_ptr = strdup(qfits_header_getstr(fh, "DATE-OBS"));
                    e_comment(1, "mef_build_bpm: frame: %s --  DATE-OBS: %s in %d", flist->name[i], dateobs_ptr, bb->xtnum);

                    /* We add selected FITS headers to first extention
                     *
                     * ORIGIN  = 'ESO     '           / European Southern Observatory
                     * DATE    = '2003-05-30T19:14:54.605' / UT date when this file was written
                     * MJD-OBS =       52789.80202058 / MJD start (2003-05-30T19:14:54.578)
                     * DATE-OBS= '2003-05-30T19:14:54.577' / Date of observation
                     * EXPTIME =               0.0086 / Total integration time
                     * OBJECT  = 'BIAS    '           / Target description
                     * INSTRUME= 'WFI     '           / Instrument used
                     * OBSERVER= 'UNKNOWN '           / Name of observer
                     * PI-COI  = 'UNKNOWN '           / Name(s) of proposer(s)
                     * TELESCOP= 'MPI-2.2 '           / ESO Telescope Name
                    */
                    if (bb->xtnum == 1) {
                        cval_ptr = strdup(qfits_header_getstr(fh, "ORIGIN"));
                        qfits_header_add_after(fhdr_extra, "NAXIS2", "ORIGIN", cval_ptr, "European Southern Observatory", NULL);
                         e_comment(1, "mef_build_bpm: ORIGIN: %s", qfits_header_getstr(fhdr_extra, "ORIGIN"));

                        cval_ptr = strdup(qfits_header_getstr(fh, "TELESCOP"));
                        qfits_header_add_after(fhdr_extra, "ORIGIN", "TELESCOP", cval_ptr, "European Southern Observatory", NULL);
                        e_comment(1, "mef_build_bpm: TELESCOP: %s", qfits_header_getstr(fhdr_extra, "TELESCOP"));

                        cval_ptr = strdup(qfits_header_getstr(fh, "INSTRUME"));
                        qfits_header_add_after(fhdr_extra, "TELESCOP", "INSTRUME", cval_ptr, "European Southern Observatory", NULL);
                        e_comment(1, "mef_build_bpm: INSTRUME: %s", qfits_header_getstr(fhdr_extra, "INSTRUME"));

                        cval_ptr = strdup(qfits_header_getstr(fh, "MJD-OBS"));
                        qfits_header_add_after(fhdr_extra, "INSTRUME", "MJD-OBS", cval_ptr, "European Southern Observatory", NULL);
                        e_comment(1, "mef_build_bpm: MJD-OBS: %s", qfits_header_getstr(fhdr_extra, "MJD-OBS"));

                        cval_ptr = strdup(qfits_header_getstr(fh, bb->binx_key));
                        qfits_header_add_after(fhdr_extra, "MJD-OBS", bb->binx_key, cval_ptr, "Binning factor along X", NULL);
                        e_comment(1, "mef_build_bpm: BINX: %s", qfits_header_getstr(fhdr_extra, bb->binx_key));

                        cval_ptr = strdup(qfits_header_getstr(fh, bb->biny_key));
                        qfits_header_add_after(fhdr_extra, bb->binx_key, bb->biny_key, cval_ptr, "Binning factor along Y", NULL);
                        e_comment(1, "mef_build_bpm: BINY: %s", qfits_header_getstr(fhdr_extra, bb->biny_key));

                        qfits_header_destroy(fh);
                    }
                    /* we read the extension name from the first frame. */
                    fh_ext = qfits_header_readext(flist->name[i],bb->xtnum);
                    cval_ptr =  strdup(qfits_header_getstr(fh_ext, "EXTNAME"));
                    qfits_header_add_after(fhdr_extra, "NAXIS2", "ZNAME", cval_ptr, "Original extension name", NULL);
                    e_comment(1, "mef_build_bpm: ZNAME: %s", qfits_header_getstr(fhdr_extra, "ZNAME"));
                    /*e_comment(1, "mef_build_bpm: header dump of fhdr_extra");
                    qfits_header_consoledump(fhdr_extra);*/
                }

                if (debug_active() >= 1) {
                    e_comment(1, "mef_build_bpm: using frame %s",flist->name[i]);
                    }   
            }
            e_comment(1, "mef_build_bpm: DATE-OBS: %s in xtnum: %d", dateobs_ptr, bb->xtnum);
            /* e_comment(1, "mef_build_bpm: header dump of fhdr_extra");
            qfits_header_consoledump(fhdr_extra);*/
            qfits_header_add_after(fhdr_extra, "NAXIS2", "DATE-OBS", dateobs_ptr, "Date of observation of first frame", NULL);
            e_comment(1, "mef_build_bpm: DATE-OBS: %s", qfits_header_getstr(fhdr_extra, "DATE-OBS"));
            /*e_comment(1, "mef_build_bpm: frame: %s --  DATE-OBS: %s in %d", flist->name[i], dateobs_ptr, bb->xtnum);*/

            /* Adding the prodcatg key */
            sprintf(cval, "%s", bb->phase3_prodcatg_val_bpm);
            qfits_header_add_after(fhdr_extra, "NAXIS2", bb->phase3_prodcatg_keyname, bb->phase3_prodcatg_val_bpm, bb->phase3_prodcatg_comment, NULL);
            e_comment(1, "mef_build_bpm: PRODCATG: %s", qfits_header_getstr(fhdr_extra, bb->phase3_prodcatg_keyname));

            sprintf(cval, "%d", bp_map->ngoodpix);
            qfits_header_add(fhdr_extra, "HIERARCH ESO MPP QC NGOODPIX", cval, "Number of good pixels", NULL);

            sprintf(cval, "%d", bp_map->lx*bp_map->ly - bp_map->ngoodpix);
            qfits_header_add(fhdr_extra, "HIERARCH ESO MPP QC NBADPIX", cval, "Number of bad pixels", NULL);
            e_comment(1, "Extra headers struct for BPM created");

            /* Do a console dump to easily check headers */
            qfits_header_consoledump(fhdr_extra);


            /* TEST we remove the simple file for storage
            sprintf(cval,"%s_%02d.fits",bb->name_bpm_o,bb->xtnum);
            e_comment(1,"saving bad pixel map [%s]",cval);
            pixelmap_dump(bp_map,cval, fhdr_extra);
            */

            /* here we write to MEF file 
             *
             * name_bpm_o
             *
             * */
            sprintf(cval, "%s", mef_get_output_filename(bb,"bpm"));
            e_comment(1,"saving extension %d bad pixel map [%s]",bb->xtnum, cval);
            if (bb->xtnum==1) {
                /* in the first extension we first write the primary headers */
                fhdr_primary = qfits_header_copy(fhdr_extra);
                zname_ptr =  qfits_header_getstr(fhdr_extra, "ZNAME");
                qfits_header_add_after(fhdr_primary, "NAXIS", "EXTEND", "T", "Extension may be present.", NULL);
                qfits_header_mod(fhdr_primary, "NAXIS", "0", "# of axes in frame");
                qfits_header_del(fhdr_primary, "NAXIS1");
                qfits_header_del(fhdr_primary, "NAXIS2");
                qfits_header_del(fhdr_primary, "ZNAME");
                pixelmap_dump(NULL,cval, fhdr_primary);
                qfits_header_destroy(fhdr_primary);

                /* then the extension header and data */
                qfits_header_add_after(fhdr_extra, "SIMPLE", "XTENSION", "IMAGE", "Extension first keyword (see SIMPLE)", NULL);
                qfits_header_add_after(fhdr_extra, "NAXIS2", "EXTNAME", zname_ptr, "Extension first keyword (see SIMPLE)", NULL);
                qfits_header_del(fhdr_extra, "ZNAME");
                qfits_header_del(fhdr_extra, "SIMPLE");
                qfits_header_del(fhdr_extra, "EXTEND");
                pixelmap_dump(bp_map,cval, fhdr_extra);
            } else {
                qfits_header_add_after(fhdr_extra, "SIMPLE", "XTENSION", "IMAGE", "Extension first keyword (see SIMPLE)", NULL);
                cval_ptr =  qfits_header_getstr(fhdr_extra, "ZNAME");
                qfits_header_add_after(fhdr_extra, "NAXIS2", "EXTNAME", cval_ptr, "Extension first keyword (see SIMPLE)", NULL);
                qfits_header_del(fhdr_extra, "ZNAME");
                qfits_header_del(fhdr_extra, "SIMPLE");
                qfits_header_del(fhdr_extra, "EXTEND");
                pixelmap_dump(bp_map,cval, fhdr_extra);
            } 
            e_comment(1,"done");

            /* qfits_header_destroy(fhdr_extra); */
        }
        qfits_header_destroy(fhdr_extra);
        if (norm_gain != NULL) image_del(norm_gain);

	return bp_map;
}



image_t * mef_build_cal(mef_bb * bb, char * what)
{
	cube_t	 *	i_cube ;
	image_t *	scancorr ;
	image_t *  	bias ;
	image_t *	stacked ;
	image_t *  	cur_p ;
	image_t *  	flat ;
	char	 *	name_i ;
	double		lo_thr, hi_thr ;
	int		minframe ;
	double		avg, avg1, sig1, kappa1 ;
    float      zmedian, zstdev;
	int		i, j, p ;
	int	 *	valid ;
	double		*all_means ;
	int		nval ;
	double		sigma ;
	pixelvalue * 	validpix ;
	pixelvalue	curpix ;
	double	    medval ;
    double      stdev_val ;
    double      *pixval_double;
	float		frame_median ;
    float       frame_variance ;
	int		frame_nplanes ;
	int		zIndex;
	char		cmt[5];
	float		normFactor ;

	/* Check entries */
	if (bb==NULL) return NULL ;
	if (!what || !*what) return NULL;

	/* Set parameters to requested frame type */
	e_comment(1, "setting input parameters...");
	if (!strcmp(what, "dome")) {
		name_i = bb->name_dome ;
		lo_thr = bb->dome_framethr_lo ;
		hi_thr = bb->dome_framethr_hi ;
		minframe = bb->dome_minframe ;
	} else if (!strcmp(what, "sky")) {
		name_i = bb->name_sky ;
		lo_thr = bb->sky_framethr_lo ;
		hi_thr = bb->sky_framethr_hi ;
		minframe = bb->sky_minframe ;
	} else if (!strcmp(what, "bias")) {
		name_i = bb->name_bias ;
		minframe = bb->bias_minframe ;
		kappa1   = bb->bias_kappa1 ;
	} else {
		e_error("unknown frame type [%s] should be 'dome' or 'sky'",what);
		return NULL ;
	}

	/* Load input cube */
	e_comment(1, "loading input cube [%s]", what);
	i_cube = mef_cube_load(name_i, bb->xtnum) ;
	if (i_cube==NULL) {
		e_error("loading input data: [%s]", name_i);
		return NULL ;
	}
	if (i_cube->np < minframe) {
		e_error("found only [%d] %s frames - need at least %d",
				i_cube->np,
				what,
				minframe);
		cube_del(i_cube);
		return NULL ;
	}

    /* we correct overscan and trim the cube */
    /* we do it before removing bad planes from
     * cube so we have the full input list represented.
     */
    e_comment(1, "applying overscan/prescan/trimming correction");
    mef_cube_overscan_correction(i_cube,bb, what);
    e_comment(1, "Done.");

	/* Compute average value for each frame, keep those in interval */
	all_means = malloc(i_cube->np*sizeof(double));
	nval = 0 ;
	avg1 = 0.00 ;
	for (i=0 ; i<i_cube->np ; i++) {
		compute_status("computing averages", i, i_cube->np, 1);
		all_means[i] = image_getmean(i_cube->plane[i]);
		avg1 += all_means[i] ;
		/*
		   if (debug_active()>1) {
		   printf("\n");
		   printf("avg/thr: %g [%g - %g]\n", avg, lo_thr, hi_thr);
		   }
		   */
	}
	avg1 /= (double) i_cube->np ;

	/* if we combine bias frame we do a slighltly different rejection */
	if (!strcmp(what, "bias")) {
		/* Compute average and sigma for rejection during bias calc. */
		sig1 = 0.0 ;
		for (i=0 ; i<i_cube->np ; i++) {
			sig1 += (all_means[i]-avg1)*(all_means[i]-avg1) ;
		}
		sig1 /= (double)(i_cube->np-1) ;
		sig1 = sqrt(sig1) ;

		lo_thr = avg1 - kappa1*sig1 ;
		hi_thr = avg1 +  kappa1*sig1 ;

        /* fill array for QC keywords */
        if (bb->nxts == 1) {    /* if we work in only one extension */
                zIndex = 0;
            } else {                        /* we are working in all the extensions */
                zIndex = bb->xtnum-1;
            }
        bb->bias_avg1[zIndex] = avg1;
        bb->bias_sig1[zIndex] = sig1;
        bb->bias_framethr_lo[zIndex] = lo_thr;
        bb->bias_framethr_hi[zIndex] = hi_thr;

		e_comment(1, "frame rejection setup:");
		e_comment(1, "average: %g", avg1);
		e_comment(1, "sigma  : %g", sig1);
		e_comment(1, "kappa  : %g", kappa1);
		e_comment(1, "low    : %g", lo_thr);
		e_comment(1, "high   : %g", hi_thr);
	}

	valid = malloc(i_cube->np * sizeof(int));
	nval = 0 ;
	e_comment(1, "frame rejection status:");
	for (i=0 ; i<i_cube->np ; i++) {
		if ((all_means[i]>lo_thr) && (all_means[i]<hi_thr)) {
			strcpy(cmt, "[X]");
			valid[i] = 1 ;
			nval++ ;
		} else {
			strcpy(cmt, "[ ]");
			valid[i] = 0 ;
		}
		e_comment(1, "%s %s frame %02d: %g", cmt, what, i+1, all_means[i]);
	}
	free(all_means);

	if (nval<minframe) {
		e_error("not enough frames to continue: %d", nval);
		free(valid);
		cube_del(i_cube);
		return NULL ;
	}

	/* Reduce cube to valid frames only */
	if (nval < i_cube->np) {
		e_comment(1, "reducing cube to valid planes only");
		cube_reject_planes(&i_cube, valid);
	}
	free(valid);

	/* Apply prescan/overscan/trimming correction 

	e_comment(1, "applying overscan/prescan/trimming correction");
	mef_cube_overscan_correction(i_cube,bb, what);
	e_comment(1, "Done.");

    *************************************************/

	/*
	 * If we are building the BIAS frame, we are almost done.
	 * We just combine the cube, and return the stacked image...
	 */

	if (!strcmp(what, "bias")) {
		e_comment(1, " %s frame stacking", what);
		stacked = cube_avg_median(i_cube);
		cube_del(i_cube);

		if (stacked==NULL) {
			e_error("in final combination: aborting");
			return NULL ;
		}
	 
		if (bb->nxts == 1) {    /* if we work in only one extension */
	            zIndex = 0;
	        } else {                        /* we are working in all the extensions */
	            zIndex = bb->xtnum-1;
	        }
		bb->bias_median[zIndex] = image_getmedian(stacked);
        bb->bias_stdev[zIndex] = image_getstdev(stacked);
		bb->bias_nplanes[zIndex] = nval;
        e_comment(1, "bias median: %f -- bias stdev: %f -- bias nplanes: %d", bb->bias_median[zIndex], bb->bias_stdev[zIndex], bb->bias_nplanes[zIndex]);
		return stacked;
	}


	/* CCD clip rejection */
	e_comment(1, "CCD clip rejection");
	e_comment(1,"gain = %f",((bb->ccd)+(bb->xtnum-1))->gain);
	e_comment(1,"ron  = %f",((bb->ccd)+(bb->xtnum-1))->ron);

	frame_median = 0.0;
    frame_variance = 0.0;
	frame_nplanes = 0;
    if (bb->nxts == 1) {    /* if we work in only one extension */
        zIndex = 0;
    } else {                        /* we are working in all the extensions */
        zIndex = bb->xtnum-1;
    }
	for (p=0 ; p<i_cube->np ; p++) {
		compute_status("clip rejection on frame", p, i_cube->np, 1);
		cur_p = i_cube->plane[p] ;

		avg = image_getmean(cur_p);
        zmedian = image_getmedian(cur_p);
        zstdev = image_getstdev(cur_p);
		sigma = sqrt(pow(((bb->ccd)+(bb->xtnum-1))->ron/((bb->ccd)+(bb->xtnum-1))->gain, 2.0) +
				(avg / ((bb->ccd)+(bb->xtnum-1))->gain));

        /* here we store the average and sigma values for QC */
        bb->individual_frame_avg[p] = avg;
        bb->individual_frame_median[p] = zmedian;
        bb->individual_frame_sigma[p] = zstdev;
        e_comment(1, "frame median: %f -- frame stdev: %f -- frame nplanes: %d", zmedian, zstdev, i_cube->np);
        e_comment(1, "frame median: %f -- frame stdev: %f -- frame nplanes: %d", bb->individual_frame_median[p], bb->individual_frame_sigma[p], i_cube->np);

		lo_thr = avg - bb->pixrej_lo * sigma ;
		hi_thr = avg + bb->pixrej_hi * sigma ;
		e_comment(1, "rejection interval");
		e_comment(1, "[%g - %g]]", lo_thr, hi_thr);
		/*
		   if (debug_active()>1) {
		   printf("avg= %g sigma= %g thr= [%g - %g]\n",
		   avg, sigma, lo_thr, hi_thr);
		   }
		   */

		/* Accumulate valid pixels in an array */
		validpix = malloc(bb->median_surf * sizeof(pixelvalue));
		nval = 0 ;
		for (j=0 ; j<cur_p->ly ; j++) {
			if (j>=bb->median_reg[2] && j<=bb->median_reg[3]) {
				for (i=0 ; i<cur_p->lx ; i++) {
					if (i>=bb->median_reg[0] && i<=bb->median_reg[1]) {
						curpix = cur_p->data[i+j*cur_p->lx];
						if (((double)curpix > lo_thr) &&
								((double)curpix < hi_thr)) {
							validpix[nval] = curpix ;
							nval ++ ;
						}
					}
				}
			}
		}
		if (nval<1) {
			e_error("no valid pixel found in frame %02d: aborting", p+1);
			cube_del(i_cube);
			free(validpix);
			return NULL ;
		}
		/* Get the median from the list of valid pixels */
		medval = (double) median_pixelvalue(validpix, nval);
        e_comment(1, "medval: %f",  medval);
        pixval_double = pixel2double_array(validpix, nval);

        for (j=0 ; j<nval ; j++) {
            pixval_double[j] -= medval;
        }

        stdev_val = double_rms(pixval_double, nval);
		free(validpix);

		if (fabs(medval)<1e-4) {
			e_error("zero value for median: aborting");
			/* cube_del(i_cube); */
			/* return NULL ; */
		} else {
			/* Divide the frame by this value */
			for (i=0 ; i<(cur_p->lx * cur_p->ly) ; i++) {
				cur_p->data[i] /= medval ;
			}
			frame_median += medval ;
            frame_variance += stdev_val*stdev_val;
			frame_nplanes++ ;
		}
	}
	frame_median = frame_median / frame_nplanes ;
    frame_variance = frame_variance / frame_nplanes ;
    e_comment(1, "frame_median: %f -- frame_variance: %f", frame_median, frame_variance);
	if (bb->nxts == 1) {	/* if we work in only one extension */
		zIndex = 0;
	} else {			/* we are working in all the extensions */
		zIndex = bb->xtnum-1;
	}
	if (!strcmp(what,"dome")) {
		bb->dome_median[zIndex] = frame_median;
        bb->dome_stdev[zIndex] = sqrt(frame_variance);
		bb->dome_nplanes[zIndex] = frame_nplanes;
		normFactor = bb->dome_median[zIndex]/bb->dome_median[0];
	} else if (!strcmp(what,"sky")) {
		bb->sky_median[zIndex] = frame_median;
        bb->sky_stdev[zIndex] = sqrt(frame_variance);
		bb->sky_nplanes[zIndex] = frame_nplanes;
		normFactor = bb->sky_median[zIndex]/bb->sky_median[0];
	}


	/* Stack frames to single frames using a median */
	e_comment(1, "stacking cube to single frame");
	flat = cube_avg_median(i_cube);
	image_cst_op_local(flat,normFactor,'*');	/* we normalize to the median of first extension */
	cube_del(i_cube);

	if (flat==NULL) {
		e_error("in final stacking: aborting");
		return NULL ;
	}
	return flat ;
}

image_t * mef_ff_combine(mef_bb * bb, image_t * dome, image_t * sky, image_t *bias, pixelmap *bp_map)
{
	image_t	*	smoothed ;
	int		zIndex ;

	if (bb==NULL || dome==NULL || sky==NULL) return NULL ;

	if ((dome->lx != sky->lx) || (dome->ly != sky->ly)) {
	     e_error("mef_ff_combine: dome and sky frames have incompatible sizes: aborting");
	     e_error("mef_ff_combine: dome is [%d %d]", dome->lx, dome->ly);
	     e_error("mef_ff_combine: sky is [%d %d]", sky->lx, sky->ly);
	     return NULL ;
	}

	/* Setting appropriate median value */
	if (bb->nxts == 1) {    /* if we work in only one extension */
		zIndex = 0;
	} else {                        /* we are working in all the extensions */
		zIndex = bb->xtnum-1;
	}
	bb->flat_median[zIndex] = bb->sky_median[zIndex];

	/* We subtract the bias if not NULL. Notice that because
	 * the flat fields are normalized to unity we need to
	 * subtract a bias scaled by the same amount used to
	 * normalize the flats.
	 */
	if (bias != NULL) {
	    if ((dome->lx != bias->lx) || (dome->ly != bias->ly)) {
		e_error("mef_ff_combine: flats and bias frames have incompatible sizes: aborting");
		e_error("mef_ff_combine: flats is [%d %d]", dome->lx, dome->ly);
		e_error("mef_ff_combine: bias is [%d %d]", bias->lx, bias->ly);
		return NULL ;
	    }

		
	    e_comment(1, "mef_ff_combine: subtracting bias from sky frame");
	    image_sub_local(sky,image_cst_op(bias,bb->sky_median[0],'/')); /* bias renormalized like flats */
	    e_comment(1, "mef_ff_combine: Done.");
	    e_comment(1, "mef_ff_combine: subtracting bias from dome frame");
	    image_sub_local(dome,image_cst_op(bias,bb->dome_median[0], '/'));
	    e_comment(1, "mef_ff_combine: Done.");
	}

	/* Divide sky by dome */
	e_comment(1, "mef_ff_combine: dividing sky by dome...");
	image_div_local(sky, dome);
	e_comment(1, "mef_ff_combine: Done.");

	/* Smooth result */
	e_comment(1, "mef_ff_combine: applying smoothing filter...");
	if (bp_map == NULL) {
        e_comment(1, "mef_ff_combine: no bp_map case...");
	    smoothed = image_filter_flat(sky, bb->kern_hsize);
	} else {
        e_comment(1, "mef_ff_combine: with bp_map case...");
	    smoothed = mef_image_filter_flat(sky, bb->kern_hsize, bp_map);
	}
	e_comment(1, "mef_ff_combine: Done.");

	/* Multiply by dome */
	e_comment(1, "mef_ff_combine: multiplying smoothed sky-over-dome ratio by dome flat...");
	image_mul_local(smoothed, dome);
	e_comment(1, "mef_ff_combine: Done.");

    /* Now we add some QC values */
    bb->combined_flat_median[zIndex] = image_getmedian(smoothed);
    bb->combined_flat_stdev[zIndex] = image_getstdev(smoothed);


	return smoothed ;
}


image_t * mef_image_filter_flat(image_t * im, int ksize,pixelmap *bpm)
{
        image_t     *   filt ;
        int                             i, j, k, l ;
        double                  acc ;
        int                             nacc ;
        register
        pixelvalue      *       out_p ;

        if (im==NULL || ksize<1) return NULL ;
        if (ksize>im->lx || ksize>im->ly) return NULL ;

        filt = image_new(im->lx, im->ly);

        /*
	 *          * Following is an optimized quadruple loop.
	 *          * Not the most efficient way of implementing a flat filter, but
	 *          * fast enough for most purposes.
	 *                                     */

        /* Loop over all image pixels */
        out_p = filt->data ;
        for (j=0 ; j<filt->ly ; j++) {
	    compute_status("filtering", j, filt->ly, 2);
            for (i=0 ; i<filt->lx ; i++) {
               /* Loop over convolution matrix */
               acc  = 0 ;
               nacc = 0 ;
               for (l=-ksize ; l<=ksize ; l++) {
                  if (((j+l)>=0) && ((j+l)<im->ly)) {
                      for (k=-ksize ; k<=ksize ; k++) {
                          /* Test how many pixels are visible from here and check the BPM */
                          if (((i+k)>=0) && ((i+k)<im->lx) && bpm->data[(i+k)+(j+l)*im->lx] == PIXELMAP_1) {
                                nacc ++ ;
                                acc += (double)im->data[(i+k)+(j+l)*im->lx];
                          }
                      }
                   }
               }

               /* Average accumulator */
               acc /= (double)nacc ;
               *out_p++ = (pixelvalue)acc ;
           }
       }
       return filt ;
}


/*
 * reads a primary header from a FITS file or the
 * first file of a frame list.
 */
qfits_header *mef_header_primary(char *filename)
{
	char		*first_name ;
	char		cval[80];
	qfits_header 	*fh ;

	if (is_fits_file(filename)) {
		fh = qfits_header_read(filename);
	} else {
		first_name = framelist_firstname(filename);
		if (first_name==NULL) {
			e_error("cannot get primary FITS header from %s", filename);
			e_error("aborting save");
			return NULL ;
		}
		if (is_fits_file(first_name)) {
			fh = qfits_header_read(first_name);
		} else {
			e_error("%s is not a valid FITS file name",first_name);
			return NULL;
		}
	}
        sprintf(cval, "%d", BPP_DEFAULT);
        qfits_header_mod(fh, "BITPIX", cval, "Bits per pixel");

	return fh;
}

/* 
 * reads an extension header
 */
qfits_header *mef_header_ext(char *filename, mef_bb *bb)
{
	char            *first_name ;
	qfits_header    *fh, *f0 ;
	int 		xtnum ;
	char		cval[80], *ra_char, *dec_char;
	float           CRVAL1, CRVAL2, CRPIX1, CRPIX2 ;

	xtnum = bb->xtnum ;

	if (is_fits_file(filename)) {
		fh = qfits_header_readext(filename,xtnum);
		/* f0 = qfits_header_readext(filename,0); */
        f0 = qfits_header_read(filename);
	} else {
		first_name = framelist_firstname(filename);
		if (first_name==NULL) {
			e_error("mef_header_ext: cannot get reference FITS header from %s", filename);
			e_error("mef_header_ext: aborting save");
			return NULL;
		}
		if (is_fits_file(first_name)) {
			fh = qfits_header_readext(first_name,xtnum);
			/* f0 = qfits_header_readext(filename,0); */
            f0 = qfits_header_read(first_name);
		} else {
			e_error("mef_header_ext: %s is not a valid FITS file name",first_name);
			return NULL;
		}
	}

	/* here we correct the positional keywords 
	 * Notice that we ignore the headers and deal with
	 * the value that has been input. 
	 *
	((bb->ccd)+(bb->xtnum-1))->crval1 = atoi(qfits_header_getstr(fh,"CRVAL1"));
	((bb->ccd)+(bb->xtnum-1))->crval2 = atoi(qfits_header_getstr(fh,"CRVAL2"));
	((bb->ccd)+(bb->xtnum-1))->crpix1 = atoi(qfits_header_getstr(fh,"CRPIX1"));
	((bb->ccd)+(bb->xtnum-1))->crpix2 = atoi(qfits_header_getstr(fh,"CRPIX2"));
	*/

	/* 
     * we check if we need to correct the coordinate value of reference pixel 
     *
     * SHOULD BE USED ONLY FOR WFI
     *
     * */

	if ( (bb->correct_ref_pix == 1) ) {
            CRVAL1 = ((bb->ccd)+(bb->xtnum-1))->crval1;
            CRVAL2 = ((bb->ccd)+(bb->xtnum-1))->crval2;
	    ra_char = qfits_header_getstr(f0, "RA");
	    dec_char = qfits_header_getstr(f0, "DEC");
        e_comment(1,"mef_header_ext: filename: %s -- ra_char: %s  dec_char: %s", filename, ra_char, dec_char);
        if ((ra_char!=NULL) && (dec_char!=NULL)) {
            e_comment(1,"mef_header_ext: CRVAL1 = %f ---> %s",((bb->ccd)+(bb->xtnum-1))->crval1,ra_char);
            sprintf(cval,"%f",CRVAL1);
            qfits_header_mod(fh,"CRVAL1",ra_char,NULL);

	        e_comment(1,"mef_header_ext: CRVAL2 = %f ---> %s",((bb->ccd)+(bb->xtnum-1))->crval2,dec_char);
            sprintf(cval,"%f",CRVAL2);
            qfits_header_mod(fh,"CRVAL2",dec_char,NULL);
        }
	    e_comment(1,"mef_header_ext: deleting CDELT1");
	    qfits_header_del(fh,"CDELT1");
	    e_comment(1,"mef_header_ext: deleting CDELT2");
	    qfits_header_del(fh,"CDELT2");
	    e_comment(1,"mef_header_ext: modifiyin CTYPE1 to RA---TAN");
	    qfits_header_mod(fh,"CTYPE1","RA---TAN",NULL);
	    e_comment(1,"mef_header_ext: modifiyin CTYPE1 to DEC--TAN");
	    qfits_header_mod(fh,"CTYPE2","DEC--TAN",NULL);
	    e_comment(1,"mef_header_ext: adding CD1_1 = -6.61111E-05");
	    qfits_header_add_after(fh,"CTYPE1","CD1_1","-6.61111E-05","WCS coordinate increment at ref point",NULL);
	    e_comment(1,"mef_header_ext: adding CD1_2 = 0.0");
            qfits_header_add_after(fh,"CD1_1","CD1_2","0.0","WCS coordinate increment at ref point",NULL);
	    e_comment(1,"mef_header_ext: adding CD2_1 = 0.0");
            qfits_header_add_after(fh,"CD1_2","CD2_1","0.0","WCS coordinate increment at ref point",NULL);
	    e_comment(1,"mef_header_ext: adding CD2_2 = 6.61111E-05");
            qfits_header_add_after(fh,"CD2_1","CD2_2","6.61111E-05","WCS coordinate increment at ref point",NULL);
            e_comment(1,"mef_header_ext: extension header CRVAL keywords modified as requested.");
	} 

        /* and now we correct for the croping */
        CRPIX1 = ((bb->ccd)+(bb->xtnum-1))->crpix1 - (float) (((bb->ccd)+(bb->xtnum-1))->trimreg)[0];
        CRPIX2 = ((bb->ccd)+(bb->xtnum-1))->crpix2 - (float) (((bb->ccd)+(bb->xtnum-1))->trimreg)[2];
        e_comment(1,"mef_header_ext: CRPIX1 = %f ---> %f",((bb->ccd)+(bb->xtnum-1))->crpix1, CRPIX1);
        e_comment(1,"mef_header_ext: CRPIX2 = %f ---> %f",((bb->ccd)+(bb->xtnum-1))->crpix2, CRPIX2);
        sprintf(cval,"%f",CRPIX1);
        qfits_header_mod(fh,"CRPIX1",cval,NULL);
        sprintf(cval,"%f",CRPIX2);
        qfits_header_mod(fh,"CRPIX2",cval,NULL);
        e_comment(1,"mef_header_ext: CRPIX keywords modified cropping.");

        /* and finally BITPIX to BPP_DEFAULT */
	sprintf(cval, "%d", BPP_DEFAULT);
	qfits_header_mod(fh, "BITPIX", cval, NULL);
	e_comment(1,"mef_header_ext: extension header BITPIX keyword modified to default %s OK.", cval);
	return fh;
}
/*
 * build a subsets of a primary header, modifying on
 * the fly a few keywords according to image.
 */
qfits_header *mef_header_mainsubset(mef_bb *bb, image_t *flat)
{
	qfits_header *fh_main_subset ;
	qfits_header *fh_ref ;
	char		cval[80] ;
	char		*getval ;



	/*
	 * we will some keywords from the primary headers
	 */
	if (bb->name_mf != NULL) {
           if ( (fh_ref = mef_header_primary(bb->name_mf)) == NULL) {
                e_error("mef_header_mainsubset: can not read %s primary headers",bb->name_mf);
                return NULL;
           }
        } else if (bb->name_sky != NULL) {
	   if ( (fh_ref = mef_header_primary(bb->name_sky)) == NULL) {
		e_error("mef_header_mainsubset: can not read %s primary headers",bb->name_sky);
		return NULL;
	   }
	} else if (bb->name_bias != NULL) {
           if ( (fh_ref = mef_header_primary(bb->name_bias)) == NULL) {
                e_error("mef_header_mainsubset: can not read %s primary headers",bb->name_bias);
                return NULL;
           }
	} else {
	  e_error("mef_header_mainsubset: can not read reference fits file primary headers");
          return NULL; 
	  }

	fh_main_subset = qfits_header_default();
	/* BITPIX */
	sprintf(cval, "%d", BPP_DEFAULT);
	qfits_header_add(fh_main_subset, "BITPIX", cval, "Bits per pixel", NULL);
	/* NAXIS* */
	qfits_header_add(fh_main_subset, "NAXIS", "2", "Dimensions", NULL);
	sprintf(cval, "%d", flat->lx);
	qfits_header_add(fh_main_subset, "NAXIS1", cval, "size in X", NULL);
	sprintf(cval, "%d", flat->ly);
	qfits_header_add(fh_main_subset, "NAXIS2", cval, "size in Y", NULL);
	/* ORIGIN */
	qfits_header_add(fh_main_subset, "ORIGIN", bb->origin, "File originator", NULL);
	/* INSTRUME */
	qfits_header_add(fh_main_subset, "INSTRUME", bb->instrument, "Instrument", NULL);
	/* TELESCOP */
	qfits_header_add(fh_main_subset, "TELESCOP", bb->telescope, "Telescope", NULL);
	/* DATE-OBS */
	getval=NULL ;
	if (fh_ref!=NULL) {
		getval = qfits_header_getstr(fh_ref, "DATE-OBS");
	}
	if (getval==NULL) {
		qfits_header_add(fh_main_subset, "DATE-OBS", "Unknown", "Date of observation", NULL);    } else {
			qfits_header_add(fh_main_subset, "DATE-OBS", getval, "Date of observation", NULL);
		}
	/* MJD-OBS */
	getval=NULL ;
	if (fh_ref!=NULL) {
		getval = qfits_header_getstr(fh_ref, "MJD-OBS");
	}
	if (getval==NULL) {
		qfits_header_add(fh_main_subset, "MJD-OBS", "Unknown", "MJD start of 1st frame", NULL);
	} else {
		qfits_header_add(fh_main_subset, "MJD-OBS", getval, "MJD start of 1st frame", NULL);
	}
	/* INS.FILT.NAME */
	getval = NULL ;
	if (fh_ref!=NULL) {
		getval = qfits_header_getstr(fh_ref, bb->filter_key);
	}
	if (getval==NULL) {
		qfits_header_add(fh_main_subset, "FILTER", "unknown", "Filter name", NULL);
	} else {
		qfits_header_add(fh_main_subset, "FILTER", getval, "Filter name", NULL);
	}
	qfits_header_destroy(fh_ref);


	return fh_main_subset;
}

/*----------trim (char) c from right-side of string *p------------------*/
char *strtrim_right( char *p, char c)
{
    register char *end;
    register int len;

    len = strlen( p);
    while ( *p && len)
    {
        end = p + len-1;
        if( c == *end)
            *end = 0;
        else
            break;
        len = strlen( p);
    }
    return( p);
}

char * rtrim(char * s) {
    int l = strlen(s);

    while(isspace(s[l - 1])) --l;
    while(* s && isspace(* s)) ++s, --l;

    return strndup(s, l);
}

/*
 * build and return ESO Phase3 headers
 */
qfits_header *mef_header_esophase3(mef_bb *bb, char *what, qfits_header    *fh_ref)
{
    qfits_header*fh_phase3 ;
    framelist   *fnames ;
    char    *   cval_ptr;
    char        cval[80] ;
    char        cval2[80] ;
    char        *getval ;
    float       exptime, mjdobs, mjdend;
    int         i, nframes ;

        /* Check entries */
    if (bb==NULL) {
         e_error("mef_header_esophase3: NULL bb pointer");
         return NULL ;
    }
    if (!what || !*what) {
        e_error("mef_header_esophase3: NULL what pointer");
        return NULL;
    }



    /* first the headers common to all frames */

    fh_phase3 = qfits_header_default();
    qfits_header_add(fh_phase3, "PHASE3", "ESOPHASE3", "ESO Phase3 compliant", NULL);

    sprintf(cval, "%s", bb->phase3_prodcatg_keyname);
    if (!strcmp(what,"science")) {
        sprintf(cval2, "%s", bb->phase3_prodcatg_val_science);
        qfits_header_add(fh_phase3, cval, cval2, bb->phase3_prodcatg_comment, NULL);
        nframes = bb->science_nframes;
    } else if (!strcmp(what,"combined")) {
        sprintf(cval2, "%s", bb->phase3_prodcatg_val_mff);
        qfits_header_add(fh_phase3, cval, cval2, bb->phase3_prodcatg_comment, NULL);
        nframes = 1;
    } else if (!strcmp(what,"sky")) {
        sprintf(cval2, "%s", bb->phase3_prodcatg_val_skyff);
        qfits_header_add(fh_phase3, cval, cval2, bb->phase3_prodcatg_comment, NULL);
        nframes = bb->sky_nframes;
    } else if (!strcmp(what,"dome")) {
        sprintf(cval2, "%s", bb->phase3_prodcatg_val_domeff);
        qfits_header_add(fh_phase3, cval, cval2, bb->phase3_prodcatg_comment, NULL);
        nframes = bb->dome_nframes;
    } else if (!strcmp(what,"bias")) {
        sprintf(cval2, "%s", bb->phase3_prodcatg_val_bias);
        qfits_header_add(fh_phase3, cval, cval2, bb->phase3_prodcatg_comment, NULL);
        e_comment(1, "Adding key %s with value %s to %s frame", cval, cval2, what);
        nframes = bb->bias_nframes;
    } else {
        e_error("mef_header_esophase3: unknown frame type [%s]",what);
        return NULL;
    }

    /* Program identification key -- from mefpp.paf */
    cval_ptr = qfits_header_getstr(fh_ref, bb->phase3_progid_hdrkey);
    e_comment(1, "Adding key %s with value %s to %s frame", bb->phase3_progid_keyname, cval_ptr, what);
    if (cval_ptr!=NULL) {
        qfits_header_add_after(fh_phase3, bb->phase3_prodcatg_keyname, 
                                            bb->phase3_progid_keyname, 
                                            cval_ptr, 
                                            bb->phase3_progid_comment, NULL);
    } else {
        qfits_header_add_after(fh_phase3, bb->phase3_prodcatg_keyname,
                                            bb->phase3_progid_keyname,
                                            "UNKNOWN",
                                            bb->phase3_progid_comment, NULL);
    }

    /* Observation identification */
    cval_ptr = qfits_header_getstr(fh_ref, bb->phase3_obid_hdrkey);
    e_comment(1, "Adding key %s with value %s to %s frame", bb->phase3_obid_keyname, cval_ptr, what);
    if (cval_ptr!=NULL) {
        qfits_header_add_after(fh_phase3, bb->phase3_progid_keyname, 
                                          bb->phase3_obid_keyname, 
                                          cval_ptr, 
                                          bb->phase3_obid_comment, NULL);
    } else {
        qfits_header_add_after(fh_phase3, bb->phase3_progid_keyname, 
                                          bb->phase3_obid_keyname, 
                                          "UNKNOWN", 
                                          bb->phase3_obid_comment, NULL);
    }

    /* Number of images combined - only 1 during the pre-processing stage TBD */
    e_comment(1, "Adding key %s with value %s to %s frame", bb->phase3_ncombine_keyname, "1", what);
    sprintf(cval, "%d", nframes);
    qfits_header_add_after(fh_phase3, bb->phase3_obid_keyname, 
                                        bb->phase3_ncombine_keyname, 
                                        cval, 
                                        bb->phase3_ncombine_comment, NULL);

    /* OBSTECH: key -- from mefpp.paf */
    cval_ptr = qfits_header_getstr(fh_ref, bb->phase3_obstech_hdrkey);
    e_comment(1, "Adding key %s with value %s to %s frame", bb->phase3_obstech_keyname, cval_ptr, what);
    if (cval_ptr!=NULL) {
        qfits_header_add_after(fh_phase3, bb->phase3_ncombine_keyname,
                                            bb->phase3_obstech_keyname, 
                                            cval_ptr, 
                                            bb->phase3_obstech_comment, NULL);
    }

    /* FILTER: key -- from mefpp.paf */
    cval_ptr = qfits_header_getstr(fh_ref, bb->filter_key);
    e_comment(1, "PHASE3: adding key %s with value %s to %s frame", bb->phase3_filter_keyname, cval_ptr, what);
    if (cval_ptr!=NULL) {
        qfits_header_add_after(fh_phase3, bb->phase3_obstech_keyname,
                                            bb->phase3_filter_keyname,
                                            cval_ptr,
                                            bb->phase3_filter_comment, NULL);
    }

    /* MJD-END: a simple calculation of MJD-END. */
    exptime = atof(qfits_header_getstr(fh_ref, "EXPTIME"));
    mjdobs = atof(qfits_header_getstr(fh_ref, "MJD-OBS"));
    mjdend = mjdobs + exptime/86400.;
    sprintf(cval, "%.8f", mjdend);
    e_comment(1, "PHASE3: adding key %s with value %s to %s frame", bb->phase3_mjdend_keyname, cval, what);
    qfits_header_add_after(fh_phase3, bb->phase3_obstech_keyname, 
                                        bb->phase3_mjdend_keyname, 
                                        cval, 
                                        bb->phase3_mjdend_comment, NULL);

    /* TIMESYS: we set the time system explicitly */
    e_comment(1, "PHASE3: adding key %s with value %s to %s frame", bb->phase3_timesys_keyname, bb->phase3_timesys_val, what);
    qfits_header_add_after(fh_phase3, bb->phase3_mjdend_keyname, 
                                            bb->phase3_timesys_keyname, 
                                            bb->phase3_timesys_val, 
                                            bb->phase3_timesys_comment, NULL);

    /* Processing software version */
    /* Processing software version */
    sprintf(cval, recipe_version);
    sprintf(cval2, "Branch from wfi 1.19 by N. Devillard");
    e_comment(1, "PHASE3: adding key %s with value %s to %s frame", bb->phase3_procsoft_keyname, cval, what);
    qfits_header_add_after(fh_phase3, bb->phase3_timesys_keyname, 
                                        bb->phase3_procsoft_keyname, 
                                        cval, 
                                        cval2, NULL);

    if (!strcmp(what,"science")) {
        /* FLUXCAL key */
        e_comment(1, "PHASE3: adding key %s with value %s to %s frame", bb->phase3_fluxcal_keyname, bb->phase3_fluxcal_val, what);
        qfits_header_add_after(fh_phase3, bb->phase3_procsoft_keyname, 
                                            bb->phase3_fluxcal_keyname, 
                                            bb->phase3_fluxcal_val, 
                                            bb->phase3_fluxcal_comment, NULL);

        /* we rename the RADECSYS key to RADESYS -- from mefpp.paf */
        cval_ptr = qfits_header_getstr(fh_ref, bb->phase3_radesys_hdrkey);
        e_comment(1, "PHASE3: adding key %s with value %s to %s frame", bb->phase3_radesys_keyname, cval_ptr, what);
        if (cval_ptr!=NULL) {
            qfits_header_add_after(fh_phase3, bb->phase3_fluxcal_keyname,
                                                bb->phase3_radesys_keyname, 
                                                cval_ptr, 
                                                bb->phase3_radesys_comment, NULL);
            qfits_header_del(fh_phase3,bb->phase3_radesys_hdrkey);
        }
    }

    return fh_phase3;
}

/*
 * build and return the ECLIPSE subheader
 */
qfits_header *mef_header_eclipse(mef_bb *bb, char *what)
{
	qfits_header	*fh_eclipse ;
	qfits_header	*fh_ref ;
    qfits_header    *fh_sky_i;
	framelist	*fnames ;
    float       exptime;
    char        *exptime_str;
	char		cval[80] ;
    char        cval2[80] ;
	char		*getval ;
	int		nchips ;
	int		i ;

        /* Check entries */
	if (bb==NULL) {
	     e_error("mef_header_eclipse: NULL bb pointer");
	     return NULL ;
	}
	if (!what || !*what) {
	    e_error("mef_header_eclipse: NULL what pointer");
	    return NULL;
	}

	

	/* first the headers common to all frames */

	fh_eclipse = qfits_header_default();
	qfits_header_add(fh_eclipse, "ECLIPSE",
			get_eclipse_version(), "Based on Eclipse version 5.0.0 by N. Devillard", NULL);


	
	/* REC.XXXX.RECVERS DPR.CATG and DPR.TYPE and REC.FLAT.RECVERS*/
	if (!strcmp(what,"combined")) {
	     sprintf(cval, "%s FLAT RECVERS", bb->recipe_key);
	     qfits_header_add(fh_eclipse, cval, recipe_version, "Recipe version", NULL);
	     qfits_header_add(fh_eclipse, bb->dpr_catg_key, "CALIB", bb->dpr_catg_comment, NULL);
	     qfits_header_add(fh_eclipse, bb->dpr_type_key, "MASTER_FLAT", bb->dpr_type_comment, NULL);
	} else if (!strcmp(what,"sky")) {
	     sprintf(cval, "%s FLAT RECVERS", bb->recipe_key);
	     qfits_header_add(fh_eclipse, cval, recipe_version, "Recipe version", NULL);
	     qfits_header_add(fh_eclipse, bb->dpr_catg_key, "CALIB", bb->dpr_catg_comment, NULL);
	     qfits_header_add(fh_eclipse, bb->dpr_type_key, "MASTER_SKY_FLAT", bb->dpr_type_comment, NULL);
	} else if (!strcmp(what,"dome")) {
	     sprintf(cval, "%s FLAT RECVERS", bb->recipe_key);
	     qfits_header_add(fh_eclipse, cval, recipe_version, "Recipe version", NULL);
	     qfits_header_add(fh_eclipse, bb->dpr_catg_key, "CALIB", bb->dpr_catg_comment, NULL);
	     qfits_header_add(fh_eclipse, bb->dpr_type_key, "MASTER_DOME_FLAT", bb->dpr_type_comment, NULL);
	} else if (!strcmp(what,"bias")) {
	     sprintf(cval, "%s BIAS RECVERS", bb->recipe_key);
	     qfits_header_add(fh_eclipse, cval, recipe_version, "Recipe version", NULL);
	     qfits_header_add(fh_eclipse, bb->dpr_catg_key, "CALIB", bb->dpr_catg_comment, NULL);
	     qfits_header_add(fh_eclipse, bb->dpr_type_key, "MASTER_BIAS", bb->dpr_type_comment, NULL);
	} else {
	     e_error("mef_header_eclipse: unknown frame type [%s]",what);
	     return NULL;
	}

    /* Add bias frames used to master bias product */
	if (!strcmp(what,"bias")) {
	    /* Add REC.BIASi */

	    if ( (fnames = framelist_load(bb->name_bias)) == NULL) {
		    if (is_fits_file(bb->name_bias)) {
		       fnames = framelist_new(1);
		       fnames->name[0] = strdup(bb->name_bias);
		    } else {
		       e_error("mef_header_eclipse: %s is not a framelist or a FITS file. Aborting", bb->name_bias);
		       return NULL ;
		    }
	    }

	    if (fnames!=NULL) {
		for (i=0 ; i<fnames->n ; i++) {
		    sprintf(cval, "%s%03d", bb->bias_frame_i_key, i+1);
		    qfits_header_add(fh_eclipse, cval, get_basename(fnames->name[i]), bb->bias_frame_i_comment, NULL);
		}
		framelist_del(fnames);
	    }
	}

    /* Add master bpm to all products */
    if (!strcmp(what,"bias") || !strcmp(what,"combined") || !strcmp(what,"sky") || !strcmp(what,"dome")) {
        /* REC.FLAT.MBPM */
        if (bb->orig_bpm!=NULL) {
            e_comment(1,"Adding FITS card: %s = %s / %s", bb->master_bpm_key, bb->orig_bpm, bb->master_bpm_comment);
            qfits_header_add(fh_eclipse, bb->master_bpm_key, bb->orig_bpm, bb->master_bpm_comment, NULL);
        } else {
            qfits_header_add(fh_eclipse, bb->master_bpm_key, "unknown", bb->master_bpm_comment, NULL);
        }
    }

    /* Add the master bias to all flat products */
    if (!strcmp(what,"combined") || !strcmp(what,"sky") || !strcmp(what,"dome")) {
        /* REC.FLAT.MBIAS */
        if (bb->orig_bias!=NULL) {
            qfits_header_add(fh_eclipse, bb->master_bias_key, bb->orig_bias, bb->master_bias_comment, NULL);
        } else {
            qfits_header_add(fh_eclipse, bb->master_bias_key, "unknown", bb->master_bias_comment, NULL);
        }
    }

    /* Add the master dome and master sky to master flat products */
    if (!strcmp(what,"combined")) {
        /* REC.FLAT.MDOME */
        if (bb->orig_dome!=NULL) {
            qfits_header_add(fh_eclipse, bb->master_dome_key, bb->orig_dome, bb->master_dome_comment, NULL);
        } else {
            qfits_header_add(fh_eclipse, bb->master_dome_key, "unknown", bb->master_dome_comment, NULL);
        }

        /* REC.FLAT.MSKY */
        if (bb->orig_sky!=NULL) {
            qfits_header_add(fh_eclipse, bb->master_sky_key, bb->orig_sky, bb->master_sky_comment, NULL);
        } else {
            qfits_header_add(fh_eclipse, bb->master_sky_key, "unknown", bb->master_sky_comment, NULL);
        }
    }

    /* Add raw dome frame list to dome flat field */
    /* Also add processing parameters */
	if (!strcmp(what,"dome")) {
	    /* Add REC.FLAT.DOMEi */

	    if ( (fnames = framelist_load(bb->name_dome)) == NULL) {
	         if (is_fits_file(bb->name_dome)) {
	               fnames = framelist_new(1);
	               /* fnames->name[0] = strdup(bb->name_dome); */
                   fnames->name[0] = NULL;

                 } else {
	                e_error("mef_header_eclipse: %s is not a framelist or a FITS file. Aborting", bb->name_dome);
	                return NULL ;
                 }
            }

	    if (fnames!=NULL) {
		    for (i=0 ; i<fnames->n ; i++) {
                if (fnames->name[i]!=NULL) {
			        sprintf(cval, "%s%03d", bb->domeff_frame_i_key, i+1);
			        qfits_header_add(fh_eclipse, cval, get_basename(fnames->name[i]), bb->domeff_frame_i_comment, NULL);
                }
            }
		    framelist_del(fnames);
	    } else {
		    e_warning("mef_header_eclipse: cannot read dome list [%s]: no output in header",
				bb->name_dome);
	    }

	    /*
	     * REC.FLAT.LFRATHD
	     * REC.FLAT.HFRATHD
	     * REC.FLAT.MINFRAD
	     */
	    sprintf(cval, "%g", bb->dome_framethr_lo);
	    qfits_header_add(fh_eclipse, bb->dome_framethr_lo_key, cval, bb->dome_framethr_lo_comment, NULL);

	    sprintf(cval, "%g", bb->dome_framethr_hi);
	    qfits_header_add(fh_eclipse, bb->dome_framethr_hi_key, cval, bb->dome_framethr_hi_comment, NULL);

	    sprintf(cval, "%d", bb->dome_minframe);
	    qfits_header_add(fh_eclipse, bb->dome_minframe_key, cval, bb->dome_minframe_comment, NULL);

	}

    /* To combined only add the master dome and sky used. */
    if (!strcmp(what,"combined")) {
        /* Add REC.FLAT.DOMEi */

        if ( (fnames = framelist_load(bb->name_dome)) == NULL) {
             if (is_fits_file(bb->name_dome)) {
               fnames = framelist_new(1);
               /* fnames->name[0] = strdup(bb->name_dome); */
               fnames->name[0] = NULL;
             } else {
                e_error("mef_header_eclipse: %s is not a framelist or a FITS file. Aborting", bb->name_dome);
                return NULL ;
             }
        }

        if (fnames!=NULL) {
            for (i=0 ; i<fnames->n ; i++) {
                if (fnames->name[i]!=NULL) {
                    sprintf(cval, "%s", bb->domeff_frame_i_key);
                    qfits_header_add(fh_eclipse, cval, get_basename(fnames->name[i]), bb->domeff_frame_i_comment, NULL);
                }
            }
            framelist_del(fnames);
        } else {
            e_warning("mef_header_eclipse: cannot read dome list [%s]: no output in header",
                bb->name_dome);
        }
    }


    /* To the master sky add the list of sky frames used.
     * and the processing parameters.
     */
	if (!strcmp(what,"sky") ) {
	    /* Add REC.FLAT.SKYi */
	    if ( (fnames = framelist_load(bb->name_sky)) == NULL) {
                 if (is_fits_file(bb->name_sky)) {
                       fnames = framelist_new(1);
                       /* fnames->name[0] = strdup(bb->name_sky); */
                       fnames->name[0] = NULL;
                 } else {
                       e_error("mef_header_eclipse: %s is not a framelist or a FITS file. Aborting", bb->name_sky);
                       return NULL ;
                 }
            }

	    if (fnames!=NULL) {
		    for (i=0 ; i<fnames->n ; i++) {
                if (fnames->name[i]!=NULL) {
			        sprintf(cval, "%s%03d",bb->skyff_frame_i_key, i+1);
			        qfits_header_add(fh_eclipse, cval, get_basename(fnames->name[i]), bb->skyff_frame_i_comment, NULL);

                    /* we get the exposure time for that frame */
                    e_comment(1,"reading primary headers of %s",get_basename(fnames->name[i]));
                    if ( (fh_sky_i = mef_header_primary(fnames->name[i])) == NULL) {
                        e_error("mef_header_eclipse: can not read %s primary headers",get_basename(fnames->name[i]));
                        return NULL;
                    }
                    e_comment(1,"Done.");
                    sprintf(cval, "%s%03d EXPTIME",bb->skyff_frame_i_key, i+1);
                    exptime_str = qfits_header_getstr(fh_sky_i, "EXPTIME");
                    if (exptime_str!=NULL) {
                        exptime = atof(exptime_str);
                        qfits_header_add(fh_eclipse, cval, exptime_str, "Exposure time of ski i", NULL);
                    } else {
                        qfits_header_add(fh_eclipse, cval, "-1", "Exposure time of ski i (NULL)", NULL);
                    } 
                    qfits_header_destroy(fh_sky_i);
                }
		    }
		    framelist_del(fnames);
	    } else {
		    e_warning("mef_header_eclipse: cannot read sky list [%s]: no output in header",
				bb->name_sky);
	    }

	    /*
	     * REC.FLAT.LFRATHS
	     * REC.FLAT.HFRATHS
	     * REC.FLAT.MINFRAS
	     */
	    sprintf(cval, "%g", bb->sky_framethr_lo);
	    qfits_header_add(fh_eclipse, bb->sky_framethr_lo_key, cval, bb->sky_framethr_lo_comment, NULL);

	    sprintf(cval, "%g", bb->sky_framethr_hi);
	    qfits_header_add(fh_eclipse, bb->sky_framethr_hi_key, cval, bb->sky_framethr_hi_comment, NULL);

	    sprintf(cval, "%d", bb->sky_minframe);
	    qfits_header_add(fh_eclipse, bb->sky_minframe_key, cval, bb->sky_minframe_comment, NULL);

        /* REC.FLAT.KERNS */
        sprintf(cval, "%d", bb->kern_hsize);
        qfits_header_add(fh_eclipse, bb->kern_hsize_key, cval, bb->kern_hsize_comment, NULL);
	}

	if (!strcmp(what,"combined") || !strcmp(what,"sky") || !strcmp(what,"dome")) {

        /* REC.FLAT.LPIXSIG */
        sprintf(cval, "%f", bb->pixrej_lo);
        qfits_header_add(fh_eclipse, bb->pixrej_lo_key, cval, bb->pixrej_lo_comment, NULL);

        /* REC.FLAT.HPIXSIG */
        sprintf(cval, "%f", bb->pixrej_hi);
        qfits_header_add(fh_eclipse,  bb->pixrej_hi_key, cval, bb->pixrej_hi_comment, NULL);

        /* REC.FLAT.MREGDEF Region for median computation */

        sprintf(cval, "%d", bb->median_reg[0]);
        sprintf(cval2, "%s X1", bb->median_reg_key);
        qfits_header_add(fh_eclipse, cval2, cval, bb->median_reg_comment, NULL);

        sprintf(cval, "%d", bb->median_reg[1]);
        sprintf(cval2, "%s X2", bb->median_reg_key);
        qfits_header_add(fh_eclipse, cval2, cval, bb->median_reg_comment, NULL);

        sprintf(cval, "%d", bb->median_reg[2]);
        sprintf(cval2, "%s Y1", bb->median_reg_key);
        qfits_header_add(fh_eclipse, cval2, cval, bb->median_reg_comment, NULL);

        sprintf(cval, "%d", bb->median_reg[3]);
        sprintf(cval2, "%s Y2", bb->median_reg_key);
        qfits_header_add(fh_eclipse, cval2, cval, bb->median_reg_comment, NULL);

	}

    /* We add keyword that describe the overscan subtraction and trimming */
    /* FITS standard does not permit list so we re-write this part. */
    /* here we add the header keys giving the prescan, overscan and trim regions*/

    /* REC.FLAT.PRSCX */
    sprintf(cval, "%d", (((bb->ccd)+(bb->xtnum-1))->prescan_x)[0]);
    sprintf(cval2, "%s X1", bb->prescan_x_key);
    qfits_header_add(fh_eclipse, cval2, cval, bb->prescan_x_comment, NULL);

    sprintf(cval, "%d", (((bb->ccd)+(bb->xtnum-1))->prescan_x)[1]);
    sprintf(cval2, "%s X2", bb->prescan_x_key);
    qfits_header_add(fh_eclipse, cval2, cval, bb->prescan_x_comment, NULL);

    /* REC.FLAT.OVSCX */
    sprintf(cval, "%d", (((bb->ccd)+(bb->xtnum-1))->overscan_x)[0]);
    sprintf(cval2, "%s X1", bb->overscan_x_key);
    qfits_header_add(fh_eclipse, cval2, cval, bb->overscan_x_comment, NULL);

    sprintf(cval, "%d", (((bb->ccd)+(bb->xtnum-1))->overscan_x)[1]);
    sprintf(cval2, "%s X2", bb->overscan_x_key);
    qfits_header_add(fh_eclipse, cval2, cval, bb->overscan_x_comment, NULL);

    /* REC.BIAS.TRIM */
    sprintf(cval, "%d", (((bb->ccd)+(bb->xtnum-1))->trimreg)[0]);
    sprintf(cval2, "%s X1", bb->trimreg_key);
    qfits_header_add(fh_eclipse, cval2, cval, bb->trimreg_comment, NULL);

    sprintf(cval, "%d", (((bb->ccd)+(bb->xtnum-1))->trimreg)[1]);
    sprintf(cval2, "%s X2", bb->trimreg_key);
    qfits_header_add(fh_eclipse, cval2, cval, bb->trimreg_comment, NULL);

    sprintf(cval, "%d", (((bb->ccd)+(bb->xtnum-1))->trimreg)[2]);
    sprintf(cval2, "%s Y1", bb->trimreg_key);
    qfits_header_add(fh_eclipse, cval2, cval, bb->trimreg_comment, NULL);

    sprintf(cval, "%d", (((bb->ccd)+(bb->xtnum-1))->trimreg)[3]);
    sprintf(cval2, "%s Y2", bb->trimreg_key);
    qfits_header_add(fh_eclipse, cval2, cval, bb->trimreg_comment, NULL);

   /* end re-write */         

	/* REC.FLAT.RDNOISE */
	sprintf(cval, "%f", ((bb->ccd)+(bb->xtnum-1))->ron);
	qfits_header_add(fh_eclipse, bb->ccd_ron_key, cval, bb->ccd_ron_comment, NULL);

	/* REC.FLAT.GAIN */
        sprintf(cval, "%f", ((bb->ccd)+(bb->xtnum-1))->gain);
        qfits_header_add(fh_eclipse, bb->ccd_gain_key, cval, bb->ccd_gain_comment, NULL);

	return fh_eclipse;

}


char *mef_get_input_filename(mef_bb *bb, char *what)
{
	char *name_i;
	char cval[80];

	/* Check entries */
	if (bb==NULL) {
		e_error("mef_get_input_filename: NULL bb pointer");
		return NULL;
	}
	if (!what || !*what) {
		e_error("mef_get_input_filename: NULL what pointer");
		return NULL;
	}
	if (!strcmp(what, "dome")) {
		name_i = strdup(bb->name_dome) ;
	} else if (!strcmp(what, "sky")) {
		name_i = strdup(bb->name_sky);
	} else if (!strcmp(what, "combined")) {
		name_i = strdup(bb->name_sky);
	} else if (!strcmp(what, "bias")) {
		name_i = strdup(bb->name_bias);
	} else {
		e_error("mef_get_input_filename: unknown frame type [%s] should be 'dome', 'sky', or 'combined'",what);
		return NULL;
	}
	return name_i;
}

/*
 * Creates a filename using an iso8601 time stamp.
 */
void *mef_create_orig_filename(mef_bb *bb, char *what)
{
    char cval[80];

    /* Check entries */
    if (bb==NULL) {
        e_error("mef_create_orig_filename: NULL bb pointer");
        return NULL;
    }
    if (!what || !*what) {
        e_error("mef_create_orig_filename: NULL what pointer");
        return NULL;
    }

    e_comment(1,"mef_create_orig_filename: bb->name_bpm: %s", bb->name_bpm);
    if (!strcmp(what, "bias")) {
        /* The final name to use for the file is only written in the ORIGFILE key */
        sprintf(cval, "CMDP.%s.%s.fits", bb->instrument, get_datetimemili_iso8601());
        bb->orig_bias = strdup(cval) ;
        e_comment(1,"mef_create_orig_filename: ORIGFILE: %s", bb->orig_bias);

    } else if (!strcmp(what, "bpm")) {
        /* The final name to use for the file is only written in the ORIGFILE key */
        sprintf(cval, "CMDP.%s.%s.fits", bb->instrument, get_datetimemili_iso8601());
        bb->orig_bpm = strdup(cval) ;    
        e_comment(1,"mef_create_orig_filename: ORIGFILE: %s", bb->orig_bpm);

    } else if (!strcmp(what, "dome")) {
        /* The final name to use for the file is only written in the ORIGFILE key */
        sprintf(cval, "CMDP.%s.%s.fits", bb->instrument, get_datetimemili_iso8601());
        bb->orig_dome = strdup(cval) ;
        e_comment(1,"mef_create_orig_filename: ORIGFILE: %s", bb->orig_dome);

    } else if (!strcmp(what, "sky")) {
        /* The final name to use for the file is only written in the ORIGFILE key */
        sprintf(cval, "CMDP.%s.%s.fits", bb->instrument, get_datetimemili_iso8601());
        bb->orig_sky = strdup(cval) ;
        e_comment(1,"mef_create_orig_filename: ORIGFILE: %s", bb->orig_sky);

    } else if (!strcmp(what, "combined")) {
        /* The final name to use for the file is only written in the ORIGFILE key */
        sprintf(cval, "CMDP.%s.%s.fits", bb->instrument, get_datetimemili_iso8601());
        bb->orig_mff = strdup(cval) ;
        e_comment(1,"mef_create_orig_filename: ORIGFILE: %s", bb->orig_mff);

    } else if (!strcmp(what, "science")) {
        /* The final name to use for the file is only written in the ORIGFILE key */
        sprintf(cval, "SMDP.%s.%s.fits", bb->instrument, get_datetimemili_iso8601());
        bb->orig_science = strdup(cval) ;
        e_comment(1,"mef_create_orig_filename: ORIGFILE: %s", bb->orig_science);
    } else {
        e_error("mef_create_orig_filename: unknown frame type: %s", what);
    }
}

char *mef_get_output_filename(mef_bb *bb, char *what)
{
	char *name_o;
	char cval[80];

	/* Check entries */
	if (bb==NULL) {
		e_error("mef_get_output_filename: NULL bb pointer");
		return NULL;
	}
	if (!what || !*what) {
		e_error("mef_get_output_filename: NULL what pointer");
		return NULL;
	}


	if (!strcmp(what, "dome")) {
		if (bb->flat_partition != NULL) {
                    sprintf(cval,"%s_%s.fits",bb->name_dome_o,bb->flat_partition);
                } else {
                    sprintf(cval,"%s.fits",bb->name_dome_o);
                }
		name_o = strdup(cval) ;

	} else if (!strcmp(what, "sky")) {
		if (bb->flat_partition != NULL) {
                    sprintf(cval,"%s_%s.fits",bb->name_sky_o,bb->flat_partition);
                } else {
                    sprintf(cval,"%s.fits",bb->name_sky_o);
                }
		name_o = strdup(cval) ;

	} else if (!strcmp(what, "combined")) {
		if (bb->flat_partition != NULL) {
                    sprintf(cval,"%s_%s.fits",bb->name_mf_o,bb->flat_partition);
	        } else {
	            sprintf(cval,"%s.fits",bb->name_mf_o);
                }
		name_o = strdup(cval) ;

	} else if (!strcmp(what, "bias")) {
		if (bb->bias_partition != NULL) {
		    sprintf(cval,"%s_%s.fits",bb->name_bias_o,bb->bias_partition);
		} else {
		    sprintf(cval,"%s.fits",bb->name_bias_o);
		}
		name_o = strdup(cval) ;
    } else if (!strcmp(what, "bpm")) {
        if (bb->bpm_partition != NULL) {
            sprintf(cval,"%s_%s.fits",bb->name_bpm_o,bb->bpm_partition);
        } else {
            sprintf(cval,"%s.fits",bb->name_bpm_o);
        }
        name_o = strdup(cval) ;
	} else {
		e_error("mef_get_output_filename: unknown frame type [%s] should be 'bias', 'dome', 'sky', or 'combined'",what);
		return NULL;
	}
	return name_o;
}


qfits_header *mef_get_headers_for( char *what, mef_bb * bb, image_t * zImage)
{
	char		*name_o ;
	char		*name_i ;
	qfits_header	*fh_ref ;
	qfits_header	*fh_main ;
    qfits_header    *fh_phase3 ;
	qfits_header	*fh_main_subset ;
	qfits_header	*fh_eclipse ;
	qfits_header	*fh_extension ;
	qfits_header	*fh_aux ;
    qfits_header    *fh_aux2 ;
	qfitsdumper	qd ;
	FILE		*out ;
	char		cval[80] ;
    char        cval2[80] ;
	char		*getval ;
	int		i ;
	char		*first_name ;
	framelist	*fnames ;
	int		nchips ;
	int		zIndex ;


	/* Check entries */
	if (bb==NULL) {
		e_error("mef_get_headers_for: NULL bb pointer");
		return NULL;
	}
	if (!what || !*what) {
		e_error("mef_get_headers_for: NULL what pointer");
		return NULL;
	}
	name_i = mef_get_input_filename(bb,what);
	e_comment(1,"name_i: %s",name_i);

    /* In this call we fill the orig_<cal> pointers with the proper ORIGFILE name  when created*/
	name_o = mef_get_output_filename(bb,what);
	e_comment(1,"name_o: %s",name_o);
	
	/* 
	 * We put together the frame as follow:
	 *
	 * 	1. Main headers (from reference frame, fh_ref) 
	 * 	 		+ Eclipse headers (fh_eclipse)
	 * 	2. Extension-i: Subset of main headers (fh_main_subset) 
	 * 			 + extension-i headers (fh_extension) 
	 * 			 + eclipse headers (fh_eclipse)
	 * 	3. Extension-i pixels
	 *
	 * this keeps the images as closely in form as the original WFI frames.
	 * At the same time the values that need updated are done so by the use
	 * of the function fits_header_merge.
	 *
	 */

	/* ************************** MAIN HEADERS ****************************
	 *
	 * Read header from the first reference frame, which is the first frame
	 * in the sky batch
	 *
	 */
	e_comment(1,"reading primary headers of %s",name_i);
	if ( (fh_ref = mef_header_primary(name_i)) == NULL) {
		e_error("mef_get_headers_for: can not read %s primary headers",name_i);
		return NULL;
	}
	e_comment(1,"Done.");

    /*
     * *************************** ESO PHASE3 HEADERS ******************************
    */
    e_comment(1,"Building phase3 headers from reference.");
    if (fh_ref != NULL) {
        if ( (fh_phase3 = mef_header_esophase3(bb, what, fh_ref)) == NULL){
            e_comment(1, "mef_get_headers_for: can not get phase3 headers for %s", what);    
        }
    }
    e_comment(1,"Done.");

	/* 
	 * *************************** EXTENSION HEADERS FROM FRAME ********************
	 */
	e_comment(1,"reading extension headers of %s",name_i);
	if ( (fh_extension = mef_header_ext(name_i,bb)) == NULL) {
		e_error("mef_get_headers_for: can not read headers from %d extension of %s",bb->xtnum, bb->name_sky);
		return NULL;
	}
	e_comment(1,"Done.");

	/*
	 * *************************** ECLIPSE HEADERS *********************************
	 */
	e_comment(1,"preparing eclipse headers");
	if ( (fh_eclipse = mef_header_eclipse(bb,what)) == NULL ) {
		e_error("can not get ECLIPSE headers");
		return NULL;
	}
	e_comment(1,"Done.");

	/*
	 * If this is the first extension, we first write primary header
	 */
	if (zImage == NULL) {
		e_comment(1,"Preparing primary header.");
		/* 
		 * we make sure that the EXTEND keyword goes right after NAXIS
		 */
		fh_aux2 = fits_header_merge(fh_ref,fh_phase3);
        fh_aux = fits_header_merge(fh_aux2,fh_eclipse);
		qfits_header_del(fh_aux,"EXTEND");
		qfits_header_add_after(fh_aux,"NAXIS", "EXTEND","T","Extension may be present.",NULL);

        /* Replace the value of the ORIGFILE key by the new value */
        if (!strcmp(what, "bias")) {
            sprintf(cval,"%s", bb->orig_bias);
            qfits_header_mod(fh_aux, "ORIGFILE", cval, "Name for this file");
        } else if (!strcmp(what, "dome")) {
            sprintf(cval,"%s", bb->orig_dome);
            qfits_header_mod(fh_aux, "ORIGFILE", cval, "Name for this file");
        } else if (!strcmp(what, "sky")) {
            sprintf(cval,"%s", bb->orig_sky);
            qfits_header_mod(fh_aux, "ORIGFILE", cval, "Name for this file");
        } else if (!strcmp(what, "combined")) {
            sprintf(cval,"%s", bb->orig_mff);
            qfits_header_mod(fh_aux, "ORIGFILE", cval, "Name for this file");
        }


        /*
         * Here we delete some keys that do not belong in the primary headers
         */
            /* REC.FLAT.PRSCX */
        sprintf(cval, "%s X1", bb->prescan_x_key);
        qfits_header_del(fh_aux, cval);

        sprintf(cval, "%s X2", bb->prescan_x_key);
        qfits_header_del(fh_aux, cval);

        /* REC.FLAT.OVSCX */
        sprintf(cval, "%s X1", bb->overscan_x_key);
        qfits_header_del(fh_aux, cval);

        sprintf(cval, "%s X2", bb->overscan_x_key);
        qfits_header_del(fh_aux, cval);

        /* REC.BIAS.TRIM */
        sprintf(cval, "%s X1", bb->trimreg_key);
        qfits_header_del(fh_aux, cval);

        sprintf(cval, "%s X2", bb->trimreg_key);
        qfits_header_del(fh_aux, cval);

        sprintf(cval, "%s Y1", bb->trimreg_key);
        qfits_header_del(fh_aux, cval);

        sprintf(cval, "%s Y2", bb->trimreg_key);
        qfits_header_del(fh_aux, cval);


		/* 
		 * calling with image=NULL it creates the file (overwrite) 
		 * with primary header.
		 */

	        qfits_header_destroy(fh_ref);
	        qfits_header_destroy(fh_extension);
	        qfits_header_destroy(fh_eclipse);
            qfits_header_destroy(fh_phase3);
            qfits_header_destroy(fh_aux2);
		
		e_comment(1,"Done.");
		return fh_aux;
	}

	/* *************************** SUBSET OF MAIN ***********************************
	 *
	 * building a subset of the main headers to be appended in each extension.
	 * we have to be careful with some keywords which change from the
	 * main header to the extension header
	 */
	if ( (fh_main_subset = mef_header_mainsubset(bb,zImage)) == NULL) {
		e_error("mef_get_headers: can not read subset from primary headers of %s",\
				bb->name_sky);
		return NULL;
	}

	/* 
	 * MERGING HEADERS
	 */
	fh_aux = fits_header_merge(fh_extension,fh_main_subset);
	/* qfits_header_destroy(fh_extension);*/
	fh_extension = fits_header_merge(fh_aux,fh_eclipse);
	qfits_header_del(fh_extension,"SIMPLE");	/* no SIMPLE keyword in extension headers */

	/*
	 * we set BZERO to 0 and BSCALE to 1.0
	 */
	qfits_header_mod(fh_extension,"BZERO","0.0","pixel=FITS*BSCALE+BZERO");

	/* Set BSCALE according to median values */
	if (bb->nxts == 1) {   /* if we work in only one extension */
		zIndex = 0;
	} else {               /* we are working in all the extensions */
		zIndex = bb->xtnum-1;
	}
	qfits_header_mod(fh_extension, "BSCALE", "1.0", "pixel=FITS*BSCALE+BZERO");

    if (!strcmp(what, "bias")) {
        sprintf(cval,"%s AVG1", bb->bias_frame_i_key);
        sprintf(cval2, "%f", bb->bias_avg1[zIndex]);
        qfits_header_add(fh_extension, cval, cval2, "Average of frame combination.", NULL);

        sprintf(cval,"%s KAPPA1", bb->bias_frame_i_key);
        sprintf(cval2, "%f", bb->bias_kappa1);
        qfits_header_add(fh_extension, cval, cval2, "Input kappa1 parameter for rejection.", NULL);

        sprintf(cval,"%s SIG1", bb->bias_frame_i_key);
        sprintf(cval2, "%f", bb->bias_sig1[zIndex]);
        qfits_header_add(fh_extension, cval, cval2, "Sigma of frame combination.", NULL);

        sprintf(cval,"%s FRMTHRLO", bb->bias_frame_i_key);
        sprintf(cval2, "%f", bb->bias_framethr_lo[zIndex]);
        qfits_header_add(fh_extension, cval, cval2, "Calculated low threshold.", NULL);

        sprintf(cval,"%s FRMTHRHI", bb->bias_frame_i_key);
        sprintf(cval2, "%f", bb->bias_framethr_hi[zIndex]);
        qfits_header_add(fh_extension, cval, cval2, "Calculated high threshold.", NULL);

        e_comment(1, "bias_nframes: %d", bb->bias_nframes);
        for (i=0 ; i<bb->bias_nframes ; i++) {
            sprintf(cval,"HIERARCH ESO MPP QC FRAME%03d SCAN MEDIAN", i+1);
            e_comment(1, "key: %s", cval);
            sprintf(cval2, "%f", bb->bias_scan_median[i]);
            e_comment(1, "val: %s", cval2);
            qfits_header_add(fh_extension, cval, cval2, "Median value of scan pixels frame i.", NULL);

            sprintf(cval,"HIERARCH ESO MPP QC FRAME%03d SCAN STDEV", i+1);
            e_comment(1, "key: %s", cval);
            sprintf(cval2, "%f", bb->bias_scan_stdev[i]);
            e_comment(1, "val: %s", cval2);
            qfits_header_add(fh_extension, cval, cval2, "Std deviation of scan pixels frame i.", NULL);
        }

        sprintf(cval, "%f", bb->bias_median[bb->xtnum-1]);
        qfits_header_add(fh_extension, "HIERARCH ESO MPP QC FRMEDIAN", cval, "Median of pixel values.", NULL);

        sprintf(cval, "%f", bb->bias_stdev[bb->xtnum-1]);
        qfits_header_add(fh_extension, "HIERARCH ESO MPP QC FRSTDEV", cval, "Stdev of pixel values.", NULL);
    }

    if (!strcmp(what, "dome")) {
        e_comment(1, "dome_nframes: %d", bb->dome_nframes);
        for (i=0 ; i<bb->dome_nframes ; i++) {
            sprintf(cval,"HIERARCH ESO MPP QC FRAME%03d SCAN MEDIAN", i+1);
            e_comment(1, "key: %s", cval);
            sprintf(cval2, "%f", bb->dome_scan_median[i]);
            e_comment(1, "val: %s", cval2);
            qfits_header_add(fh_extension, cval, cval2, "Median value of scan pixels frame i.", NULL);

            sprintf(cval,"HIERARCH ESO MPP QC FRAME%03d SCAN STDEV", i+1);
            e_comment(1, "key: %s", cval);
            sprintf(cval2, "%f", bb->dome_scan_stdev[i]);
            e_comment(1, "val: %s", cval2);
            qfits_header_add(fh_extension, cval, cval2, "Std deviation of scan pixels frame i.", NULL);

            sprintf(cval,"HIERARCH ESO MPP QC FRAME%03d MEAN", i+1);
            e_comment(1, "key: %s", cval);
            sprintf(cval2, "%f", bb->individual_frame_avg[i]);
            e_comment(1, "val: %s", cval2);
            qfits_header_add(fh_extension, cval, cval2, "Mean of frame i.", NULL);

            sprintf(cval,"HIERARCH ESO MPP QC FRAME%03d MEDIAN", i+1);
            e_comment(1, "key: %s", cval);
            sprintf(cval2, "%f", bb->individual_frame_median[i]);
            e_comment(1, "val: %s", cval2);
            qfits_header_add(fh_extension, cval, cval2, "Median of frame i.", NULL);

            sprintf(cval,"HIERARCH ESO MPP QC FRAME%03d STDEV", i+1);
            e_comment(1, "key: %s", cval);
            sprintf(cval2, "%f", bb->individual_frame_sigma[i]);
            e_comment(1, "val: %s", cval2);
            qfits_header_add(fh_extension, cval, cval2, "Std dev of frame i.", NULL);
        }

        sprintf(cval, "%f", bb->dome_median[bb->xtnum-1]);
        qfits_header_add(fh_extension, "HIERARCH ESO MPP QC FRMEDIAN", cval, "Median of pixel values.", NULL);

        sprintf(cval, "%f", bb->dome_stdev[bb->xtnum-1]);
        qfits_header_add(fh_extension, "HIERARCH ESO MPP QC FRSTDEV", cval, "Stdev of pixel values.", NULL);
    }

    if (!strcmp(what, "sky")) {
        e_comment(1, "sky_nframes: %d", bb->sky_nframes);
        for (i=0 ; i<bb->sky_nframes ; i++) {
            sprintf(cval,"HIERARCH ESO MPP QC FRAME%03d SCAN MEDIAN", i+1);
            e_comment(1, "key: %s", cval);
            sprintf(cval2, "%f", bb->sky_scan_median[i]);
            e_comment(1, "val: %s", cval2);
            qfits_header_add(fh_extension, cval, cval2, "Median value of scan pixels frame i.", NULL);

            sprintf(cval,"HIERARCH ESO MPP QC FRAME%03d SCAN STDEV", i+1);
            e_comment(1, "key: %s", cval);
            sprintf(cval2, "%f", bb->sky_scan_stdev[i]);
            e_comment(1, "val: %s", cval2);
            qfits_header_add(fh_extension, cval, cval2, "Std deviation of scan pixels frame i.", NULL);

            sprintf(cval,"HIERARCH ESO MPP QC FRAME%03d MEAN", i+1);
            e_comment(1, "key: %s", cval);
            sprintf(cval2, "%f", bb->individual_frame_avg[i]);
            e_comment(1, "val: %s", cval2);
            qfits_header_add(fh_extension, cval, cval2, "Mean of frame i.", NULL);

            sprintf(cval,"HIERARCH ESO MPP QC FRAME%03d MEDIAN", i+1);
            e_comment(1, "key: %s", cval);
            sprintf(cval2, "%f", bb->individual_frame_median[i]);
            e_comment(1, "val: %s", cval2);
            qfits_header_add(fh_extension, cval, cval2, "Median of frame i.", NULL);

            sprintf(cval,"HIERARCH ESO MPP QC FRAME%03d STDEV", i+1);
            e_comment(1, "key: %s", cval);
            sprintf(cval2, "%f", bb->individual_frame_sigma[i]);
            e_comment(1, "val: %s", cval2);
            qfits_header_add(fh_extension, cval, cval2, "Std dev of frame i.", NULL);
        }

        sprintf(cval, "%f", bb->sky_median[bb->xtnum-1]);
        qfits_header_add(fh_extension, "HIERARCH ESO MPP QC FRMEDIAN", cval, "Median of pixel values.", NULL);

        sprintf(cval, "%f", bb->sky_stdev[bb->xtnum-1]);
        qfits_header_add(fh_extension, "HIERARCH ESO MPP QC FRSTDEV", cval, "Stdev of pixel values.", NULL);
    }

    /* Minimum QC parameters for the master flat */
    if (!strcmp(what, "combined")) {

        sprintf(cval, "%f", bb->combined_flat_median[bb->xtnum-1]);
        e_comment(1, "Adding HIERARCH ESO MPP QC FRMEDIAN: %s", cval);
        qfits_header_add(fh_extension, "HIERARCH ESO MPP QC FRMEDIAN", cval, "Median of pixel values.", NULL);

        sprintf(cval, "%f", bb->combined_flat_stdev[bb->xtnum-1]);
        e_comment(1, "Adding HIERARCH ESO MPP QC FRSTDEV: %s", cval);
        qfits_header_add(fh_extension, "HIERARCH ESO MPP QC FRSTDEV", cval, "Stdev of pixel values.", NULL);

    }

    if (!strcmp(what, "science")) {
        e_comment(1, "science_nframes: %d", bb->science_nframes);
        for (i=0 ; i<bb->science_nframes ; i++) {
            sprintf(cval,"HIERARCH ESO MPP QC FRAME%03d SCAN MEDIAN", i+1);
            e_comment(1, "key: %s", cval);
            sprintf(cval2, "%f", bb->science_scan_median[i]);
            e_comment(1, "val: %s", cval2);
            qfits_header_add(fh_extension, cval, cval2, "Median value of scan pixels frame i.", NULL);

            sprintf(cval,"HIERARCH ESO MPP QC FRAME%03d SCAN STDEV", i+1);
            e_comment(1, "key: %s", cval);
            sprintf(cval2, "%f", bb->science_scan_stdev[i]);
            e_comment(1, "val: %s", cval2);
            qfits_header_add(fh_extension, cval, cval2, "Std deviation of scan pixels frame i.", NULL);

            sprintf(cval,"HIERARCH ESO MPP QC FRAME%03d MEAN", i+1);
            e_comment(1, "key: %s", cval);
            sprintf(cval2, "%f", bb->individual_frame_avg[i]);
            e_comment(1, "val: %s", cval2);
            qfits_header_add(fh_extension, cval, cval2, "Mean of frame i.", NULL);

            sprintf(cval,"HIERARCH ESO MPP QC FRAME%03d MEDIAN", i+1);
            e_comment(1, "key: %s", cval);
            sprintf(cval2, "%f", bb->individual_frame_median[i]);
            e_comment(1, "val: %s", cval2);
            qfits_header_add(fh_extension, cval, cval2, "Median of frame i.", NULL);

            sprintf(cval,"HIERARCH ESO MPP QC FRAME%03d STDEV", i+1);
            e_comment(1, "key: %s", cval);
            sprintf(cval2, "%f", bb->individual_frame_sigma[i]);
            e_comment(1, "val: %s", cval2);
            qfits_header_add(fh_extension, cval, cval2, "Std dev of frame i.", NULL);
        }
     }

	/*
	if (!strcmp(what, "bias")) {
		qfits_header_mod(fh_extension, "BSCALE", "1.0", "pixel=FITS*BSCALE+BZERO");
	} else if (!strcmp(what, "dome")) {
		sprintf(cval, "%f", bb->dome_median[zIndex]);
		qfits_header_mod(fh_extension, "BSCALE", cval, "pixel=FITS*BSCALE+BZERO");
	} else if (!strcmp(what, "sky")) {
		sprintf(cval, "%f", bb->sky_median[zIndex]);
		qfits_header_mod(fh_extension, "BSCALE", cval, "pixel=FITS*BSCALE+BZERO");
	} else if (!strcmp(what, "combined")) {
		 * this is an ugly kludge to take care of the case when
		 * the dome and sky flats are read and not calculated during
		 * the program run. In this case the pixel values of the flats
		 * are correct and correspond to set BSCALE=1.0 for the
		 * combined flat.
		 
		if (image_getmedian(zImage) > 1000.0) {
		   qfits_header_mod(fh_extension, "BSCALE", "1.0", "pixel=FITS*BSCALE+BZERO");
		} else {
		sprintf(cval, "%f", bb->sky_median[zIndex]);
		qfits_header_mod(fh_extension, "BSCALE", cval, "pixel=FITS*BSCALE+BZERO");
		}
	} else {
		e_error("mef_save: unknown frame type [%s] should be 'dome', 'sky', or 'combined'",what);
		return;
	}
	*/

        qfits_header_destroy(fh_aux);
        qfits_header_destroy(fh_ref);
        qfits_header_destroy(fh_eclipse);
        qfits_header_destroy(fh_main_subset);

	return fh_extension ;

}

void mef_save(mef_bb *bb, image_t *zImage, char *what)
{
	char *name_o ;
	qfits_header    *fh_aux;

	name_o = mef_get_output_filename(bb,what);

	e_comment(1, "saving %s [%s]",what,name_o);
	if (bb->xtnum == 1) {
	    /* saving primary headers after creating the value to go into key ORIGFILE */
        mef_create_orig_filename(bb, what);
	    fh_aux =  mef_get_headers_for(what,bb,NULL);

        e_comment(1, "Creating file %s with ORIGFILE: %s ", name_o, qfits_header_getstr(fh_aux,"ORIGFILE"));

	    mef_hdrpix_dump(NULL,name_o,fh_aux,BPP_DEFAULT);
 	}
	/* saving extension headers and data */
   	fh_aux = mef_get_headers_for(what,bb,zImage);
   	mef_hdrpix_dump(zImage,name_o,fh_aux,BPP_DEFAULT);
	return;
}


void mef_hdrpix_dump(image_t *image,char *filename,qfits_header *fh,int bpp)
{
	FILE		*out;
	qfitsdumper 	qd;


	if (image == NULL) {
		e_comment(1,"save_mef_hdrdump: no pixel data. Dumping headers only");
		out = fopen(filename,"w");
		qfits_header_dump(fh,out);
		fclose(out);
		e_comment(1, "save_mef_hdrdump: done");
		return;
	}

	/*
	 *  We use the qfits routine to copy to file filename
	 */
	qd.filename = filename ;
	qd.npix = image->lx*image->ly;
#ifdef DOUBLEPIX
	qd.ptype = PTYPE_DOUBLE;
	qd.dbuf  = image->data ;
#else
	qd.ptype = PTYPE_FLOAT;
	qd.fbuf  = image->data ;
#endif
	qd.out_ptype = BPP_DEFAULT ;

	e_comment(1, "Appending extension headers onto file %s",filename);
	out = fopen(filename,"a");
	qfits_header_dump(fh,out);
	fclose(out);
	e_comment(1, "Done");
	e_comment(1, "Appending pixel data onto file %s (BPP_DEFAULT=%d)",filename,bpp);
	qfits_pixdump(&qd);
	qfits_zeropad(filename);
	e_comment(1, "Done");
	return;
}

