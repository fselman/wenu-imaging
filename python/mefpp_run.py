import os
import glob
import shutil
import subprocess
from pathlib import Path
import traceback
class ExposurePartition:
    
    def __init__(self, filename, frametype):

        self.base_path = os.path.dirname(filename)
        self.frametype = frametype

        self.filter = None
        if frametype != 'BIAS' or frametype != 'BPM':
            self.filter = self.getFilter(filename)
        self.framelist = filename
        self.frame = None
        
        # for the moment the BPM have no time stamp
        self.OBstart = None
        if frametype != 'BPM':
            self.OBstart = self.getOBstart(filename)
            
        # we construct the names according to file type
        self.framelist = None
        self.frame = None
        if frametype == 'BPM':
            self.framelist = None
            self.frame = self.base_path+'/OMEGACAM_BPM_01.fits'
        elif frametype == 'BIAS':
            self.framelist = self.base_path+'/bias.list'
            self.frame = self.base_path+'/OMEGACAM_MB_1x1.fits'
        elif frametype == 'FLAT,DOME':
            self.framelist = self.base_path+'/dome.list'
            self.frame = self.base_path+'/OMEGACAM_DOMEFF_'+self.filter+'_1x1.fits'
        elif frametype == 'FLAT,SKY':
            self.framelist = self.base_path+'/sky.list'
            self.frame = self.base_path+'/OMEGACAM_SKYFF_'+self.filter+'_1x1.fits'
        elif frametype == 'MFF':
            self.framelist = self.base_path+'/mff.list'
            self.frame = self.base_path+'/OMEGACAM_MFF_'+self.filter+'_1x1.fits'
        elif frametype == 'SCIENCE' or frametype == 'SKY':
            self.framelist = self.base_path+'/science.list'            
            self.frame = None


        self.bpmPartition = None
        self.bpmFrame = None
        self.bpm_have = False
        self.bpm_have_link = False

        self.biasPartition = None
        self.biasFrame = None
        self.bias_have = False
        self.bias_have_link = False

        self.domePartition = None
        self.domeFrame = None

        self.skyPartition = None
        self.SkyFrame = None

        self.mffPartition = None
        self.mffFrame = None
        
    def getFilter(self,filename):
        fields = filename.split('/')
        return fields[-3]
        
    def getOBstart(self, filename):
        fields = filename.split('/')
        return fields[-2]

def timeDistance(time_str1, time_str2):
    FMT = '%Y-%m-%dT%H:%M:%S'
    return abs((datetime.strptime(time_str1, FMT) - datetime.strptime(time_str2, FMT)).total_seconds())

def getKeyVal(filename, key):
    with fits.open(filename) as hdu_list:
        primary_header = hdu_list[0].header
        val = primary_header[key]
        return val


def runCmd( str_cmd, basepath, p_shell=True ):
    """ 
    A wrapper to run system commands.
      
    Parameters
    ----------
    str_cmd: str      
      Command string to be executed in the shell
    
    p_shell: bool
      If True (default), command will be executed through the shell, and all 
      cout/cerr messages will be available.
      If False, exception is the only way to find out problems during the call.

    Returns
    -------
      0 if some error, or 1 if all was OK

    Notes
    -----
    TODO:
      - allow to launch commands in background 
      - best checking of error when shell=True
    """
           
    print("log.info: Running command: %s \n"%(str_cmd,))
    
    try:
        cwd = os.getcwd()
        os.chdir(basepath)
        print('\n---- runCmd: ', str_cmd)
        p = subprocess.Popen(str_cmd, bufsize = 0, shell = p_shell, stdin = subprocess.PIPE, 
                             stdout = subprocess.PIPE, stderr = subprocess.PIPE, 
                             close_fds = True)
        #Warning
        #We use communicate() rather than .stdin.write, .stdout.read or .stderr.read 
        #to avoid deadlocks due to any of the other OS pipe buffers filling up and 
        #blocking the child process.(Python Ref.doc)

        (stdoutdata, stderrdata) = p.communicate()
        err = stdoutdata.decode('ascii') + " " + stderrdata.decode('ascii')

        # IMPORTANT: Next checking (only available when shell=True) not always detect all kind of errors !!
        if err.count('WARNING: Significant inaccuracy'):
            print("Canno't get accuracy astrometric calibration")
            return 2
        elif (err.count('ERROR ') or err.count('error ') or err.count("Error ")\
          or err.count('*Error*')\
          or err.count('Segmentation fault') or err.count("command not found") \
          or err.count("No such file or directory")):
            print("An error happened while running command --> %s \n"%(err,))
            print(stderrdata.decode('ascii'))
            return 1 # ERROR
        else:
            print(stdoutdata.decode('ascii'))
            return 0 # NO ERROR
            os.chdir(cwd)
    except Exception:
        traceback.print_exc()
       
def associateBPM(part, scipart):

    have_bpm_link = True
    have_bpm = True
    for i in range(1,33):
        bpm_name = part.base_path+'/OMEGACAM_BPM_%02d.fits'%(i,)
        if not Path(bpm_name).is_symlink():
            have_bpm_link = False
        else:
            have_bpm_link = have_bpm_link and True
        
        if not Path(bpm_name).exists():
            have_bpm = False
        else:
            have_bpm = have_bpm and True

    # was scipart instead of part
    scipart.bpm_have = have_bpm
    scipart.bpm_have_link = have_bpm_link
 
    if have_bpm_link:
        bpm_frame = Path(bpm_name).resolve().as_posix()
        part.bpmFrame = bpm_frame
        part.bpmPartition = ExposurePartition(bpm_frame, 'BPM')

def associateBias(part, scipart):
    have_bias_link = True
    have_bias = True

    bias_name = part.base_path+'/OMEGACAM_MB_1x1.fits'
    if not Path(bias_name).is_symlink():
        have_bias_link = False

    if not Path(bias_name).exists():
        have_bias = False

    part.bias_have = have_bias
    part.bias_have_link = have_bias_link
    
    if have_bias_link:
        bias_frame = Path(bias_name).resolve().as_posix()
        part.biasFrame = bias_frame
        part.biasPartition = ExposurePartition(bias_frame, 'BIAS')


def associateDome(part, scipart):
    have_dome_link = True
    have_dome = True

    dome_name = part.base_path+'/OMEGACAM_DOMEFF_'+scipart.filter+'_1x1.fits'
    if not Path(dome_name).is_symlink():
        have_dome_link = False

    if not Path(dome_name).exists():
        have_dome = False

    part.dome_have = have_dome
    part.dome_have_link = have_dome_link
    
    if have_dome_link:
        dome_frame = Path(dome_name).resolve().as_posix()
        part.domeFrame = dome_frame
        part.domePartition = ExposurePartition(dome_frame, 'FLAT,DOME')

def associateSky(part, scipart):
    have_sky_link = True
    have_sky = True

    #sky_name = part.base_path+'/OMEGACAM_SKYFF_'+scipart.filter+'_1x1.fits'
    sky_name = part.base_path+'/sky.list'
    if not Path(sky_name).is_symlink():
        have_sky_link = False

    if not Path(sky_name).exists():
        have_sky = False

    part.sky_have = have_sky
    part.sky_have_link = have_sky_link
    
    if have_sky_link or have_sky:
        sky_frame = Path(sky_name).resolve().as_posix()
        part.skyPartition = ExposurePartition(sky_frame, 'FLAT,SKY')

def associateMFF(part, scipart):
    have_mff_link = True
    have_mff = True

    mff_name = part.base_path+'/OMEGACAM_MFF_'+scipart.filter+'_1x1.fits'
    if not Path(mff_name).is_symlink():
        have_mff_link = False

    if not Path(mff_name).exists():
        have_mff = False

    part.mff_have = have_mff
    part.mff_have_link = have_mff_link
    
    if have_mff_link:
        mff_frame = Path(mff_name).resolve().as_posix()
        part.mffFrame = mff_frame
        part.mffPartition = ExposurePartition(mff_frame, 'MFF')

def mefpp_reduce_bpm(mefpp_dir, calib_dir):
    # here we reduce the bpm frames which for now is only a cp operation
    bpm_files_list =  [mefpp_dir+'/ins/mef/static_cal/'+'OMEGACAM_BPM_%02d.fits'%i for i in range(1,33)]
    for file in bpm_files_list:
        # print(file)
        shutil.copy(file, calib_dir+'/bpm/')
    print('mefpp_reduce_bpm: done copying BPMs')


def mefpp_reduce_bias(mefpp_dir, bias_part_list):
    
    print('mefpp_reduce_bias: length of bias partition list: %d'%len(set(bias_part_list)))
    for bias_part in set(bias_part_list):
    
        basepath = bias_part.base_path
        bias_list = basepath+'/bias.list'
        print('mefpp_reduce_bias: ',bias_list)

        bias_list_exists = False
        if Path(bias_list).exists():
            bias_list_exists = True
    
        mefpp_paf_exists = False
        if Path(basepath+'/mefpp.paf').exists():
            mefpp_paf_exists = True
    
        if not mefpp_paf_exists:
            if Path(mefpp_dir+'/ins/mef/mefpp.paf').exists():
                shutil.copy(mefpp_dir+'/ins/mef/omegacam.paf', basepath+'/mefpp.paf')
                if Path(basepath+'/mefpp.paf').exists():
                    mefpp_paf_exists = True
                else:
                    raise Exception('mefpp_reduce_bias: could not create mefpp file.')
            else:
                pass
            
        bpm_files_list = glob.glob(basepath+'/OMEGACAM_BPM_??.fits', recursive=False)
        bpm_exists = True
        for bpm_file in bpm_files_list:
            if not Path(bpm_file).exists():
                bpm_exists = bpm_exists and False
    
        bias_already_reduced = False
        if Path(basepath+'/OMEGACAM_MB_1x1.fits').exists():
            bias_already_reduced = True    
    
        if (not bias_already_reduced) and (bias_list_exists and mefpp_paf_exists and bpm_exists):
            print('\n\n', basepath.split()[-1], bias_list_exists, mefpp_paf_exists, bpm_exists, bias_already_reduced)
            #os.chdir(basepath)
            command_line = 'nohup '+mefpp_dir+'/bin/mefpp ' + \
			'--bias ' + bias_list + \
			' --biassave > ' + basepath + '/mefpp.log'
            print('basepath: ', basepath)
            print('bias_already_reduced: ', bias_already_reduced)
            print('bias_list_exists: ', bias_list_exists)
            print('mefpp_paf_exists: ', mefpp_paf_exists)
            print('bpm_exists: ', bpm_exists)
            print('\n', command_line)
            print('\nbias_list: ', bias_list)
            rcode = runCmd(command_line, basepath)
            if (rcode == 1):
                raise Exception('Error running '+command_line)
            else:
                print('success running '+command_line)
            #os.chdir(cwd)
        else:
            print('basepath: ', basepath)
            print('bias_already_reduced: ', bias_already_reduced)
            print('bias_list_exists: ', bias_list_exists)
            print('mefpp_paf_exists: ', mefpp_paf_exists)
            print('bpm_exists: ', bpm_exists)

def mefpp_reduce_dome(mefpp_dir, dome_part_list):
    
    print('mefpp_reduce_dome: length of dome partition list: %d'%len(set(dome_part_list)))            
    for dome_part in dome_part_list:
    
        basepath = dome_part.base_path
        dome_list = basepath+'/dome.list'
    
        mefpp_paf_exists = False
    
        dome_list_exists = False
        if Path(dome_list).exists():
            dome_list_exists = True
    
        mefpp_paf_exists = False
        if Path(basepath+'/mefpp.paf').exists():
            mefpp_paf_exists = True
    
        if not mefpp_paf_exists:
            if Path(mefpp_dir+'/ins/mef/mefpp.paf').exists():
                shutil.copy(mefpp_dir+'/ins/mef/omegacam.paf', basepath+'/mefpp.paf')
                if Path(basepath+'/mefpp.paf').exists():
                    mefpp_paf_exists = True
                else:
                    raise Exception('Could not create mefpp file.')
            else:
                pass
            
        bpm_files_list = glob.glob(basepath+'/OMEGACAM_BPM_??.fits', recursive=False)
        bpm_exists = True
        for bpm_file in bpm_files_list:
            if not Path(bpm_file).exists():
                bpm_exists = bpm_exists and False
            
        # here we check the presence of the required master bias frame
        mb_exists = False
        if Path(basepath+'/OMEGACAM_MB_1x1.fits').exists():
            #print(basepath+'/OMEGACAM_MB_1x1.fits exists')
            mb_exists = True
        else:
            #print(basepath+'/OMEGACAM_MB_1x1.fits does not exists')
            pass
    
        dome_already_reduced = False
        if Path(basepath+'/OMEGACAM_DOMEFF_'+dome_part.filter+'_1x1.fits').exists():
            dome_already_reduced = True    
        
        print(basepath.split()[-1], dome_list_exists, mefpp_paf_exists, bpm_exists, mb_exists, dome_already_reduced)

        if (not dome_already_reduced) and (dome_list_exists and mefpp_paf_exists and bpm_exists and mb_exists):
            print(basepath.split()[-1], dome_list_exists, mefpp_paf_exists, bpm_exists, mb_exists, dome_already_reduced)
            #os.chdir(basepath)
            command_line = 'nohup '+mefpp_dir+'/bin/mefpp ' + \
			' --bias '+basepath+'/OMEGACAM_MB_1x1.fits ' + \
			' --dome '+dome_list+ \
			' --domesave > '+basepath+'/mefpp.log'
            print(command_line)
            rcode = runCmd(command_line, basepath)
            if (rcode == 1):
                raise Exception('Error running '+command_line)
            else:
                print('success running '+command_line)
            #os.chdir(cwd)
        else:
            print('skipping dome reduction')
            
def mefpp_reduce_sky(mefpp_dir, sky_part_list):
    
    print('mefpp_reduce_sky: length of sky partition list: %d'%len(set(sky_part_list)))             
    for sky_part in set(sky_part_list):
    
        basepath = sky_part.base_path
        sky_list = basepath+'/sky.list'
    
        mefpp_paf_exists = False
    
        sky_list_exists = False
        if Path(sky_list).exists():
            sky_list_exists = True
    
        mefpp_paf_exists = False
        if Path(basepath+'/mefpp.paf').exists():
            mefpp_paf_exists = True
    
        if not mefpp_paf_exists:
            if Path(mefpp_dir+'/ins/mef/mefpp.paf').exists():
                shutil.copy(mefpp_dir+'/ins/mef/omegacam.paf', basepath+'/mefpp.paf')
                if Path(basepath+'/mefpp.paf').exists():
                    mefpp_paf_exists = True
                else:
                    raise Exception('Could not create mefpp file.')
            else:
                pass
            
        bpm_files_list = glob.glob(basepath+'/OMEGACAM_BPM_??.fits', recursive=False)
        bpm_exists = True
        for bpm_file in bpm_files_list:
            if not Path(bpm_file).exists():
                bpm_exists = bpm_exists and False
            
        # here we check the presence of the required master bias frame
        mb_exists = False
        if Path(basepath+'/OMEGACAM_MB_1x1.fits').exists():
            #print(basepath+'/OMEGACAM_MB_1x1.fits exists')
            mb_exists = True
        else:
            #print(basepath+'/OMEGACAM_MB_1x1.fits does not exists')
            pass
    
        # here we check for the required dome ff
        domeff_exists = False
        domeff_name = basepath+'/OMEGACAM_DOMEFF_'+sky_part.filter+'_1x1.fits'
        if Path(domeff_name).exists():
            print(domeff_name+' exists')
            domeff_exists = True
        else:
            print(domeff_name+' does not exist')
            pass    
    
        sky_already_reduced = False
        skyff_name = basepath+'/OMEGACAM_SKYFF_'+sky_part.filter+'_1x1.fits'
        if Path(skyff_name).exists():
            print(skyff_name+' exists')
            sky_already_reduced = True    
        else:
            print(skyff_name+' does not exist')
        
        print(basepath.split()[-1], sky_list_exists, mefpp_paf_exists, bpm_exists, mb_exists, domeff_exists, sky_already_reduced)

        if (not sky_already_reduced) and (sky_list_exists and mefpp_paf_exists and bpm_exists and mb_exists and domeff_exists):
            print(basepath.split()[-1], sky_list_exists, mefpp_paf_exists, bpm_exists, mb_exists, domeff_exists, sky_already_reduced)
            #os.chdir(basepath)
            command_line = 'nohup '+mefpp_dir+'/bin/mefpp '+ \
				' --bias '+basepath+'/OMEGACAM_MB_1x1.fits ' + \
                                ' --dome '+basepath+'/OMEGACAM_DOMEFF_'+sky_part.filter+'_1x1.fits ' + \
                                ' --sky '+sky_list+ ' --skysave ' + \
                                '  > '+basepath+'/mefpp.log'
            print('\n', command_line)
            rcode = runCmd(command_line, basepath)
            if (rcode == 1):
                raise Exception('Error running '+command_line)
            else:
                print('success running '+command_line)
            #os.chdir(cwd)
        else:
            print('skipping sky reduction')
            
def mefpp_reduce_science(mefpp_dir, sci_part_list):

    for sci_part in set(sci_part_list):
    
        basepath = sci_part.base_path
        sci_list = basepath+'/science.list'
    
        mefpp_paf_exists = False
    
        sci_list_exists = False
        if Path(sci_list).exists():
            sci_list_exists = True
    
        mefpp_paf_exists = False
        if Path(basepath+'/mefpp.paf').exists():
            mefpp_paf_exists = True
    
        if not mefpp_paf_exists:
            if Path(mefpp_dir+'/ins/mef/mefpp.paf').exists():
                shutil.copy(mefpp_dir+'/ins/mef/omegacam.paf', basepath+'/mefpp.paf')
                if Path(basepath+'/mefpp.paf').exists():
                    mefpp_paf_exists = True
                else:
                    raise Exception('Could not create mefpp file.')
            else:
                pass
            
        bpm_files_list = glob.glob(basepath+'/OMEGACAM_BPM_??.fits', recursive=False)
        bpm_exists = True
        for bpm_file in bpm_files_list:
            if not Path(bpm_file).exists():
                bpm_exists = bpm_exists and False
            
        # here we check the presence of the required master bias frame
        mb_exists = False
        if Path(basepath+'/OMEGACAM_MB_1x1.fits').exists():
            #print(basepath+'/OMEGACAM_MB_1x1.fits exists')
            mb_exists = True
        else:
            #print(basepath+'/OMEGACAM_MB_1x1.fits does not exists')
            pass
        
        # here we check for the required master ff
        mff_exists = False
        mff_name = basepath+'/OMEGACAM_MFF_'+sci_part.filter+'_1x1.fits'
        if Path(mff_name).exists():
            print(mff_name+' exists')
            mff_exists = True
        else:
            print(mff_name+' does not exist')
            pass        

        
        print(basepath.split()[-1], sci_list_exists, mefpp_paf_exists, bpm_exists, mb_exists, mff_exists)

        if True and (sci_list_exists and mefpp_paf_exists and bpm_exists and mb_exists and mff_exists):
            print(basepath.split()[-1], sci_list_exists, mefpp_paf_exists, bpm_exists, mb_exists, mff_exists)
 
            command_line = 'nohup '+mefpp_dir+'/bin/mefpp ' + \
				' --bias '+basepath+'/OMEGACAM_MB_1x1.fits ' + \
                                ' --mff '+basepath+'/OMEGACAM_MFF_'+sci_part.filter+'_1x1.fits ' + \
                                ' --science '+sci_list + \
                                '  > '+basepath+'/mefpp.log'
            print('\n', command_line)
            rcode = runCmd(command_line, basepath)
            if (rcode == 1):
                raise Exception('Error running '+command_line)
            else:
                print('success running '+command_line)
        else:
            print('skipping reduction')


