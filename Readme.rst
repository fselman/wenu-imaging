Mefpp python scripts
+++++++++++++++++++++

Here are the scripts required to run mefpp. They are divided in the Jupyter-notebook and console versions. They were scripted by F.Selman in a first instance, then slightly improved by L.Celedon. It was build over Python 3.8.

Pycavi flow
==========

The main flow of a pycavi processing is as follows:

* Download data:  science with calibration files from the ESO archive.
* Select calibrations (optional): if the data is from WFI, then select the calibration files for the chosen science files.
* Verify quality of calibrations (optional): for WFI calibrations do a minimal check on the downloaded calibrations.
* Agregate calibrations (optional): for WFI data you might need to aggregate sky flats from more than one execution sequence.
* Data pre-processing: 

	o 00_pycavi_project_config.ipynb: copy the pycavi notebooks the directory 
      where the data processing will be carried out, then run this notebook.
      It will create a configuration file for the project indicating 
      the instrument used to acquire the data, the directory where the raw
      frames are stored (it could have subdirectory structure, it will
      find all .fits files), the project directory which is the directory
      where the processing will take place. 
    o 01_pycavi_partition_data.ipynb Associates the raw images according to obs-date, 
      filter, object and type (science, bias, dome flats, sky flats, science and stnadard
      field frames). It will create a data structure and it will instantaiate the
      data structure on disk, writing in a series of subdirectories list files, each
      containing the full path to files that will be combined to create master calibartion
      products, or in the case of science and standard star field, will be processed together.
    o 03_pycavi_run.ipynb: this notebook will search for the .list files and create symbolic
      links with the name of the master products. Initially all these links will be broken.
      Then the mefpp processing engine will be used to pre-process all the calibration
      files in order: first the biases, then the domes (which needs the previous biases),
      then the sky frames that use the biases and domes, producing the master frames.
      An important set of calibration files, the bad pixel maps, BPMs, will be copied
      to the static_cal subdirectory, and a link will be inserted in each data partition.
      It is assumed that a single set of BPMs will be used for each data reduction project.
      Finally, it will process the science and standard star field frames using the master 
      biases and master flats. The average gains and exposure times will be used to produce
      frames in e/s. Note that the saturation level FITS key, SATLEVEL, will be inserted to contain
      the actual saturation level in e/s. At the same time a FITS key, ONEADU, will be inserted
      containing the e/s level corresponding to 1 ADU in the original frames.
            
* Astrometry:
			A good astrometry is necessary for the frame combination.  Pycavi relies on two steps: 
            a first improvement of the WCS found
            in the headers is carried on by solve-field from astrometry.net. This solution is then
            refined using the Scamp software from astromatic.  The notebooks 04_pycavi_solve and
            05_pycavi_scamp are the ones in charge to run solve-field and Scamp respectively.
            The notebooks must be run in order, otherwise the flow will fail. The solve-field run
            is necessary because the error in the pointings in  the headers of OmegaCam
            frames could be up to 2 arcmin and scamp cannot deal with uncertainties larger
            than approx 5 arcsec.
* Combination of frames:
			Once the astrometry is done, all the multi extension frames images belonging to a single
            science data partition (images with same target, filter, obsid, and filter) are combined
            to crete a single frame. This is done by calling the SWarp package from astromatic. 
            The call to the package is done in notebook 06_pymefpp_swarp.ipynb.
* Calibration in flux:
			Last step is to calibrate the SWarped frame to convert e/s to physical units of erg/s/cm2.
            To compute the multiplicative factor to go from e/s to physical units, pycavi uses the photometry
            available from Skymapper or SDSS to compare with the raw magnitudes obtained from the same stars in the field.
            The magnitude zero point required to go from raw to standard AB magnitudes is calculated and inserted
           into the headers of the combined image. 

			o A catalogue of the objects found in the calibrated frame is generated using SExtractor.
            The magnitudes obtained from this catalogue are used to compare agains the standard magnitudes
            to create check plots of the calibration.
			
External software and Python packages required
==============================================
	
	The mefpp flow relies on external software to accomplish some parts of the work. Below is the list of software that must be installed before run mefpp.

		* SExtractor  (can be downloaded and installed from https://www.astromatic.net/software/sextractor/)
		* Scamp		(can be installed from terminal "sudo apt-get install scamp")
		* SWarp		(can be installed from terminal "sudo apt-get install swarp")
		* Astrometry_dot_net		(can be downloaded and installed from http://astrometry.net/doc/build.html)
		
	Additionaly, certain python packages are required:

		* ephem		(https://pypi.org/project/ephem/)
		* numpy		(https://numpy.org/)
		* astropy		(https://www.astropy.org/)
		* pandas		(https://pandas.pydata.org/)
		* matplotlib		(https://matplotlib.org/)
		* astroplan		(https://astroplan.readthedocs.io/en/latest/)
		* scipy		(https://scipy.org/)
		* photutils		(https://photutils.readthedocs.io/en/stable/)
		
	Please be sure all the aforementioned packages and software are correctly installed on your machine before start running mefpp.
	
Using the notebooks/scripts
===========================

The notebooks and scripts are designed to work without much intervention of the user one after another.
All variables are set in the first notebook and read in subsequent ones.

Testing the notebooks
=====================

The notebooks and scripts were tested on a linux laptop (intel core i7, 8 processors) using the images 
of a field near CP Pup in the filters r_SDSS and NB_659 (ESO program ID: 099.D-0533(A)). The whole process
took less than 1 hour for each filter (10 images per filter). The most consuming part is the astrometry, 
for which SExtractor/Scamp could take several minutes per image. The resulting check plot of the calibration
process for both filters can be found in the folder check_plots. The check plot for the r_SDSS filter shows 
field dependent sytematics arising from the light concentration effect. A notebook is being designed
to correct for this effect. At present the photometry should be accurate to +- 10% accros the field.

Possible isues
==============

The most likely part of the flow to present some failures is the astromatic process.
The Scamp configuration parameters defined within the notebook are the result of testing
in the filters r_SDSS and NB_659, but they could not be the optimal for bluer bands.
If the SWarped image shows signal of bad astrometry I suggest to play a bit with the SCamp parameters.
Other possible source of uncertainty is the photometry. Currently only aperture photometry is supported
by pycavi, therefore, for dense crowded fields we should expect higher uncertainty in the raw photometry
during the calibration process.


