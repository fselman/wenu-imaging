Quick summary for the impatient
+++++++++++++++++++++++++++++++

    #. Create, and move into, the working dirtectory
    #. Source the file .eclipse-rc which should have been created
       when mefpp was installed.  

       *  Make sure that verbose is larger than 0.

    #. Copy wfi.paf or omegacam.paf into working directory **as mefpp.paf**. 
    #. Explore data with dfits and fitsort
    #. Partition data by creating ascii lists using dfits and fitsort. These lists should contain the full paths to the raw files.

           * bpm.list
           * bias.list
           * dome.list
           * sky.list
           * science.list

    #. Produce calibrations:

           * **Produce the bad pixel mask:** BPM, which needs to exist in the working directory before running the commans below.

             * Copy from the static_cal directory WFI_BPM_1x1.fits or OCAM_BPM_1x1.fits to the working directory.
             * Or create a BPM with the command:

               - ``$mefpp --bpm bpm.list 2>&1 | tee process_bpm.log``

           * **Master bias frame:**

             * ``$mefpp --bias bias.list --biassave  2>&1 | tee process_bias.log``

               - this creates creates WFI_MB_1x1.fits in workdir.

           * **Master dome frame:**

             * ``$mefpp --bias WFI_MB_1x1.fits --dome dome.list --domesave  2>&1 | tee process_dome.log`` 

               - this creates WFI_DOMEFF_BB_Rc_162_ESO844_1x1.fits in workdir.

           * **Master sky and master flat frames:**

             * ``$mefpp --bias WFI_MB_1x1.fits --dome WFI_DOMEFF_BB_Rc_162_ESO844_1x1.fits --skyff sky.list --skysave --mffsave WFI_MFF  2>&1 | tee process_sky.log``

               - this creates two files:

                 - WFI_SKYFF_BB_Rc_162_ESO844_1x1.fits combining the sky frames
                 - WFI_MFF_BB_Rc_162_ESO844_1x1.fits combining the master dome and master sky frames.

    #. reduce science frames listed in science.list

        * ``$mefpp --bias WFI_MB_1x1.fits --mff WFI_SKYFF_BB_Rc_162_ESO844_1x1.fits --science science.list  2>&1 | tee process_science.log``

          * this produces a set of files with the same names as the files in science.list but with suffix *_pre.fits* instead of *.fits*.


.. tip::
   Although the calibration files created have the same name for a given product
   they do have in their headers the FITS key ORIGFILE which uniquely identify it with
   an ISO time in milisecond giving the time of creation. The simple redundant names are
   kept because they simplify the running of the pycavi processing system which
   is tightly integrated with mefpp.
