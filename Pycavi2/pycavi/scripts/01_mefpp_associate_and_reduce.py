# importing needed system modules
import sys
import os

# here we import the local mefpp_run library
# where the python scripts are
sys.path.insert(0, os.getcwd())
from mefpp_associate_reduction import *

# and define some paths
# the root directory where the calibrated and science images will go
root_dir = "/home/lientur/Investigacion/OmegaCam/Raw_images_for_test/"
raw_data_dir = root_dir + "raw_images/"  # where the raw images are
reduced_cal_dir = root_dir + "calibs/"
bpm_cal_dir = reduced_cal_dir + "bpm"
reduced_science_dir = root_dir + "science/"
log_dir = root_dir + "logs/"
mefpp_dir = "/home/lientur/Investigacion/OmegaCam/mefpp/"

# create a list with all the images in the raw data dir
listing = glob.glob(raw_data_dir+'OMEGA.*.fits')


# this part run mefpp notebook 1
# create the root dir if not exist, then all the rest of folders

check_and_create_folder(reduced_cal_dir)
check_and_create_folder(reduced_science_dir)
check_and_create_folder(log_dir)
check_and_create_folder(bpm_cal_dir)

# we prepare the logs
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s:%(levelname)s:%(message)s",
                    handlers=[
                        logging.FileHandler(log_dir + "/pymeffpp_partition_data.log"),
                        logging.StreamHandler()
                    ])

# we find all OMEGACAM fits files below the raw data directory
logging.info('%d OmegaCAM frames in %s' % (len(listing), raw_data_dir))

exposurePartition = PartitionsTree()
i_exposure = 0

for file_name in listing:

    i_exposure += 1
    exposure = Exposure(file_name)
    exposurePartition.insertExposure(exposure)
    biasDict = {k: v for (k, v) in exposurePartition.partList.items() if 'bias/' in k}
    domeDict = {k: v for (k, v) in exposurePartition.partList.items() if 'dome/' in k}
    skyDict = {k: v for (k, v) in exposurePartition.partList.items() if 'sky/' in k}
    stdDict = {k: v for (k, v) in exposurePartition.partList.items() if 'std/' in k}
    sciDict = {k: v for (k, v) in exposurePartition.partList.items() if 'science/' in k}
    if i_exposure % 10:
        Total = len(biasDict) + len(domeDict) + len(skyDict) + len(stdDict) + len(sciDict)
        print("BIAS:     %d" % len(biasDict),
              "DOME:     %d" % len(domeDict),
              "SKY:      %d" % len(skyDict),
              "STD:      %d" % len(stdDict),
              "SCIENCE:  %d" % len(sciDict),
              "Total     %d" % Total, end='\r')

# we create directory structure to reduce the calibration data

# bad pixel masks BPM are needed but static at this point we create
# a directory to contain them
Path(bpm_cal_dir + "/bpm.list").touch()
Path(bpm_cal_dir + "/toreduce_bpm").touch()

createFrameList(reduced_cal_dir, 'bias.list', biasDict)
createFrameList(reduced_cal_dir, 'dome.list', domeDict)
createFrameList(reduced_cal_dir, 'sky.list', skyDict)
createFrameList(reduced_science_dir, 'science.list', sciDict)

# ##################################################
# Here start the second script, 02_pymefpp_associate
# ##################################################

bpm_list = glob.glob(reduced_cal_dir + '**/bpm.list', recursive=True)
logging.info('number of bpm partitions: {0}'.format(len(bpm_list)))
bpm_partitions = []
for bpm_file in bpm_list:
    bpm_partitions.append(BiasPartition(bpm_file))

for part in bpm_partitions:
    logging.info(part.OBstart)

bias_partitions = get_partition(reduced_cal_dir + "**/bias.list")
dome_partitions = get_partition(reduced_cal_dir + "**/dome.list")
sky_partitions = get_partition(reduced_cal_dir + "**/sky.list")
sci_partitions = get_partition(reduced_science_dir + "**/science.list")

# We associate a bpm partition to each science frame
associate_bpm(sci_partitions, bpm_partitions)

# we associate a bias partition to each science partition
for sci_part in sci_partitions:
    # here we look for the closest in time bias partition
    sci_date = sci_part.OBstart

    # we find the bias closest in time
    biasBestDeltaT = 3600. * 24. * 10.0
    for bias_part in bias_partitions:
        bias_date = bias_part.OBstart
        deltaT = timeDistance(sci_date, bias_date)
        if deltaT < biasBestDeltaT:
            biasBestDeltaT = deltaT
            sci_part.biasPartition = bias_part

    #
    skyBestDeltaT = 3600. * 24. * 30.0
    for sky_part in sky_partitions:
        if sci_part.filter != sky_part.filter:
            continue
        sky_date = sky_part.OBstart
        deltaT = timeDistance(sci_date, sky_date)

        if deltaT < skyBestDeltaT:
            skyBestDeltaT = deltaT
            sci_part.skyPartition = sky_part
            sci_part.mffPartition = sky_part

    print('science: %s %s' % (sci_part.filter, sci_part.OBstart,) +
          'bias: %s (%3.1f)' % (sci_part.biasPartition.OBstart, biasBestDeltaT / 3600.0 / 24.,) +
          'sky: %s %s (%3.1f)' % (
          sci_part.skyPartition.filter, sci_part.skyPartition.OBstart, skyBestDeltaT / 3600.0 / 24.,))

# at this point we have the biases and mff for each science frame. Now we link
for sci_part in sci_partitions:
    mbias = sci_part.biasPartition.base_path + '/OMEGACAM_MB_1x1.fits'
    if not Path(mbias).is_file():
        try:
            os.symlink(mbias, sci_part.base_path + '/OMEGACAM_MB_1x1.fits')
        except:
            pass
        Path(sci_part.biasPartition.base_path + '/toreduce_sci').touch()

    mff = sci_part.mffPartition.base_path + '/OMEGACAM_MFF_' + sci_part.filter + '_1x1.fits'
    if not Path(mff).is_file():
        try:
            os.symlink(mff, sci_part.base_path + '/OMEGACAM_MFF_' + sci_part.filter + '_1x1.fits')
        except:
            pass
        Path(sci_part.mffPartition.base_path + '/toreduce_mff').touch()

# We associate a bpm partition to each sky frame partition
associate_bpm(sky_partitions, bpm_partitions)

# here we associate dome and bias to each sky partition
for sky_part in sky_partitions:
    sky_date = sky_part.OBstart

    # we find the bias closest in time
    biasBestDeltaT = 3600. * 24. * 10.0
    for bias_part in bias_partitions:
        bias_date = bias_part.OBstart
        deltaT = timeDistance(sky_date, bias_date)
        if deltaT < biasBestDeltaT:
            biasBestDeltaT = deltaT
            sky_part.biasPartition = bias_part

    # we find the dome closest in time and we link the domeff to a file that
    # will be present there once it is created

    domeBestDeltaT = 3600. * 24. * 30.0
    for dome_part in dome_partitions:
        if sky_part.filter == dome_part.filter:
            dome_date = dome_part.OBstart
            deltaT = timeDistance(sky_date, dome_date)
            if deltaT < domeBestDeltaT:
                domeBestDeltaT = deltaT
                sky_part.domePartition = dome_part
        else:
            pass

    print('sky: %s %s' % (sky_part.filter, sky_part.OBstart,) +
          '     bias: %s (%4.2f)' % (sky_part.biasPartition.OBstart, biasBestDeltaT / 3600.0 / 24.,) +
          ' dome: %s %s (%4.2f)' % (
          sky_part.domePartition.filter, sky_part.domePartition.OBstart, domeBestDeltaT / 3600.0 / 24.,))

# at this point we have the biases and domes for each sky ff frame. Now we link
for sky_part in sky_partitions:
    mbias = sky_part.biasPartition.base_path + '/OMEGACAM_MB_1x1.fits'
    if not Path(mbias).is_file():
        try:
            os.symlink(mbias, sky_part.base_path + '/OMEGACAM_MB_1x1.fits')
        except:
            pass
        Path(sky_part.biasPartition.base_path + '/toreduce_sky').touch()

    domeff = sky_part.domePartition.base_path + '/OMEGACAM_DOMEFF_' + sky_part.filter + '_1x1.fits'
    if not Path(domeff).is_file():
        try:
            os.symlink(domeff, sky_part.base_path + '/OMEGACAM_DOMEFF_' + sky_part.filter + '_1x1.fits')
        except:
            pass
        Path(sky_part.domePartition.base_path + '/toreduce_sky').touch()


# We associate a bpm partition to each dome ff frame
associate_bpm(dome_partitions, bpm_partitions)

for dome_part in dome_partitions:

    dome_date = dome_part.OBstart
    # we find the bias closest in time
    biasBestDeltaT = 3600. * 24. * 10.0
    for bias_part in bias_partitions:
        bias_date = bias_part.OBstart
        deltaT = timeDistance(dome_date, bias_date)
        if deltaT < biasBestDeltaT:
            biasBestDeltaT = deltaT
            dome_part.biasPartition = bias_part

    mbias = dome_part.biasPartition.base_path + '/OMEGACAM_MB_1x1.fits'
    if not Path(mbias).is_file():
        try:
            os.symlink(mbias, dome_part.base_path + '/OMEGACAM_MB_1x1.fits')
        except:
            pass
        Path(dome_part.biasPartition.base_path + '/toreduce_dome').touch()

# here we associate biases to each dome partition
for dome_part in dome_partitions:
    dome_date = dome_part.OBstart

    # we find the bias closest in time
    biasBestDeltaT = 3600. * 24. * 10.0
    for bias_part in bias_partitions:
        bias_date = bias_part.OBstart
        deltaT = timeDistance(dome_date, bias_date)

        # print(sci_date, bias_date, deltaT)
        if deltaT < biasBestDeltaT:
            biasBestDeltaT = deltaT
            dome_part.biasPartition = bias_part

    print('dome: %s %s' % (dome_part.filter, dome_part.OBstart,) +
          '     bias: %s (%5.3f)' % (dome_part.biasPartition.OBstart, biasBestDeltaT / 3600.0 / 24.,))

# at this point we have the biases  for each dome ff frame. Now we link
for dome_part in dome_partitions:
    mbias = dome_part.biasPartition.base_path + '/OMEGACAM_MB_1x1.fits'
    if not Path(mbias).is_file():
        try:
            os.symlink(mbias, dome_part.base_path + '/OMEGACAM_MB_1x1.fits')
        except:
            pass
        Path(dome_part.biasPartition.base_path + '/toreduce_dome').touch()

# Finally associate a bpm partition to each bias frame
associate_bpm(bias_partitions, bpm_partitions)

# Here we start to write the notebook 03, pymefpp_run

science_list = glob.glob(reduced_science_dir+'**/science.list', recursive=True)

# select data to reduce
# for the moment reduce all the images in sci_partitions
# by doing science_partition_list = sci_partitions[0:5] for example we reduce only the first 5 images

print('--------------------- science frame associations -------------------')
science_partition_list = sci_partitions
i = 0
for partition in science_partition_list:
    print(i, partition.base_path)
    i += 1

for scipart in science_partition_list:
    bias_part_list = []
    dome_part_list = []
    sky_part_list = []

    sci_part_list = []

    # -------------- DATA ASSOCIATION SECTION ---------------
    print('scipart: ' + scipart.base_path)
    sci_part_list.append(scipart)

    associateBPM(scipart, scipart)
    print('        bpm part:  ' + scipart.bpmPartition.base_path)
    associateBias(scipart, scipart)
    print('        bias part:  ' + scipart.biasPartition.base_path)
    bias_part_list.append(scipart.biasPartition)
    associateMFF(scipart, scipart)
    print('        MFF  part:  ' + scipart.mffPartition.base_path)

    # associations for the MFF frame
    mffpart = scipart.mffPartition
    print('         mffpart: ' + mffpart.base_path)
    associateBPM(mffpart, scipart)
    print('                  bpm  part:  ' + mffpart.bpmPartition.base_path)
    associateBias(mffpart, scipart)
    print('                  bias part:  ' + mffpart.biasPartition.base_path)
    bias_part_list.append(mffpart.biasPartition)
    associateDome(mffpart, scipart)
    print('                  dome part:  ' + mffpart.domePartition.base_path)
    dome_part_list.append(mffpart.domePartition)
    associateSky(mffpart, scipart)
    print('                   sky part:  ' + mffpart.skyPartition.base_path)
    sky_part_list.append(mffpart.skyPartition)

    # associations for the SKY frame
    skypart = mffpart.skyPartition
    print('  ---> skypart: ' + skypart.base_path)
    associateBPM(skypart, scipart)
    print('                  bpm  part:  ' + skypart.bpmPartition.base_path)
    associateBias(skypart, scipart)
    print('                  bias part:  ' + skypart.biasPartition.base_path)
    bias_part_list.append(skypart.biasPartition)
    associateDome(skypart, scipart)
    print('                  dome part:  ' + skypart.domePartition.base_path)
    dome_part_list.append(skypart.domePartition)

    # associations for the dome frame
    domepart = ExposuresPartition(skypart.domePartition.frame, 'FLAT,DOME')
    print('  ---> domepart: ' + domepart.base_path)
    associateBPM(domepart, scipart)
    print('                  bpm  part:  ' + domepart.bpmPartition.base_path)
    associateBias(domepart, scipart)
    print('                  bias part:  ' + domepart.biasPartition.base_path)
    bias_part_list.append(domepart.biasPartition)
    print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')

    # --------------------- DATA REDUCTION SECTION ---------------------
    # here we reduce the bpm frames which for now is only a cp operation
    mefpp_reduce_bpm(mefpp_dir, reduced_cal_dir)

    # we start reducing the biases
    mefpp_reduce_bias(mefpp_dir, bias_part_list)

    # reduction of dome frames
    mefpp_reduce_dome(mefpp_dir, dome_part_list)

    # reduction of sky frames
    mefpp_reduce_sky(mefpp_dir, sky_part_list)

    # we reduce the science frames here
    mefpp_reduce_science(mefpp_dir, sci_part_list)

    # finally we normalize the science frames
    mefpp_normalize_science(sci_part_list)

    print("Frame {} reduced successfully".format(scipart.base_path))

print("All frames has been reduced without problems :)")
