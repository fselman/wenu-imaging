import os
import glob
import sys
import numpy as np
import subprocess
import time
import multiprocessing

# to logg messages and debug
from textwrap import wrap# to logg messages and debug
import logging

from astropy.io import fits

def solvefield(file_name):
    
    dir_name = file_name[:-30]+'_solve_field'
    logging.debug('solvefield: mef file: {0}'.format(dir_name[:-24]+'.fits'))
    logging.debug('file_name: {0}'.format(file_name))
    logging.debug('dir_name: {0}'.format(dir_name))
    
    try:
        hdu_list = fits.open(file_name)        
        an_hdu = hdu_list[0]    
        crval1 = an_hdu.header['CRVAL1']
        crval2 = an_hdu.header['CRVAL2']
        crpix1 = an_hdu.header['CRPIX1']
        crpix2 = an_hdu.header['CRPIX2']
        hdu_list.close()
    except Exception as e:
        print(e)
        logging.debug('solvefield: problem extracting keys from file {0}'.format(file_name))
    
    # solve-field --ra 123.871525418909 --dec -49.1901672273134 --radius=1.0 --scale-low 0.02 --scale-high 0.25 ESO_CCD__66.fits
    pos_pars = '--ra '+ "%10.6f"%(crval1) + ' --dec ' + "%10.6f"%(crval2) + ' --radius=1.0 '
    scale_pars = ' --scale-low 0.02 --scale-high 0.25 --overwrite '
    wcs_pars = ' --crpix-x '+ "%10.6f"%(crpix1) + ' --crpix-y ' + "%10.6f"%(crpix2) + ' --no-tweak '
    solve_command_pars =  ' -D '+dir_name+ ' ' +pos_pars + scale_pars + wcs_pars + ' --new-fits ' + file_name[:-5]+'_newwcs.fits '+ file_name 
    solve_command_print =  ' -D ' + dir_name + \
                            '\n       ' + pos_pars + \
                            '\n     ' + scale_pars + \
                            '\n     ' + wcs_pars + \
                            '\n      --new-fits ' + file_name[:-5]+'_newwcs.fits '+ \
                            '\n      ' + file_name
    logging.debug('solvefield: {0}'.format(solve_command_print))
    os.system('/usr/local/astrometry/bin/solve-field '+solve_command_pars)
    logfile = file_name[:-5]+'_subprocess.log'
    
    # ATTEMPT TO USE A DIFFERENT TASK FOR BETTER MESSAGING. NOT CLEAR WHY IT DOES NOT WORK.
    #
    #logging.debug('/usr/local/astrometry/bin/solve-field ', '-D ', f"{dir_name}", \
    #    '--ra ', "%10.6f"%(crval1), '--dec ', "%10.6f"%(crval2), \
    #    '--radius ', '1.0', '--scale-low ', '0.02',  \
    #    '--scale-high ', '0.25', '--overwrite ', \
    #     '--crpix-x ', "%10.6f"%(crpix1), '--crpix-y ', "%10.6f"%(crpix2), \
    #    '--no-tweak ', '--new-fits ', f"{file_name[:-5]+'_newwcs.fits '}", f"{file_name}")
    #command_list = ['/usr/local/astrometry/bin/solve-field ', 
    #    '-D ', f"{dir_name}",
    #    '--ra ', "%10.6f"%(crval1),
    #    '--dec ', "%10.6f"%(crval2),
    #   '--radius ', '1.0',  
    #    '--scale-low ', '0.02',
    #   '--scale-high ', '0.25',
    #   '--overwrite ', '--verbose', 
    #   '--crpix-x ', "%10.6f"%(crpix1),
    #    '--crpix-y ', "%10.6f"%(crpix2),
    #   '--no-tweak ',
    #   '--new-fits ', f"{file_name[:-5]+'_newwcs.fits '}",
    #   f"{file_name}"]
    #print(command_list)
    #output = subprocess.check_output(command_list, stderr=subprocess.STDOUT, shell=True)

    logging.debug('solvefield: appending output to: {0}'.format(logfile))
    output_str = output.decode()
    for line in output_str.split('\n'):
        with open(logfile, "a") as f:
            print(line, file=f)
    f.close()
    #print('solve-field '+ext_file_name)

    
def run_solve_field(argv):

    filename = argv+'.fits'
    dir_name = os.path.abspath(argv)
    try:
        # Create target Directory
        os.mkdir(dir_name)
        logging.debug("run_solve_field: directory {0} created ".format(dir_name)) 
    except FileExistsError:
        logging.debug("run_solve_field: directory {0} already exists".format(dir_name))

    # here we create a directory where we will save all data from solve-field
    hdu_list = fits.open(filename)
    list_of_extensions = []
    list_of_filenames = []
    for an_hdu in  hdu_list[1:]:
        list_of_extensions.append(an_hdu.header['EXTNAME'])
        ext_file_name = an_hdu.header['EXTNAME'].replace('#','_')
        #print(ext_file_name, an_hdu.header['CRVAL1'], an_hdu.header['CRVAL2'])
        solve_field_dir_name = dir_name+'/'+ext_file_name+'_solve_field/'
        try:
            # Create target Directory
            os.mkdir(solve_field_dir_name)
            logging.debug("run_solve_field: solve-field directory {0} Created ".format(solve_field_dir_name)) 
        except Exception as e:
            logging.debug(e)
            logging.debug("run_solve_field: solve-field directory {0} already exists".format(solve_field_dir_name))
        list_of_filenames.append(solve_field_dir_name+'/'+ext_file_name+'.fits')
        fits.writeto(solve_field_dir_name+'/'+ext_file_name+'.fits', an_hdu.data, an_hdu.header, overwrite=True)
    hdu_list.close()
    logging.info('run_solve_field: processing extensions...')
    
    
    #list_of_extensions = ["ESO_CCD_#%2d" % (i,) for i in range(65, 97)]
    processlist = list()
    for xtension in list_of_extensions:
        file_name = solve_field_dir_name+'/'+ext_file_name+'.fits'
        logging.debug('run_solve_field: {0}: adding extension: {1} to processpool: '.format(filename, xtension,))
        processlist.append([file_name])
        logging.debug("added.")
    logging.info('run_solve_field: number of extensions: {:02d}'.format(len(list_of_filenames)))
    cpu_count = 32
    try:
        logging.debug('run_solve_field: creating processing pool.')
        pool = multiprocessing.Pool(processes = cpu_count)
        logging.debug('...done.')
    except Exception as e:
        logging.debug('exception found attempting multiprocessing pool...')
        print(e)
    num_tasks = len(processlist)
    logging.debug('run_solve_field: number of tasks: {:02d}'.format(num_tasks))
    processresult = pool.imap_unordered(solvefield,list_of_filenames)
    pool.close()
    pool.join()
    
    #logging.debug("run_solve_field: run_solvefield: {:02d} tasks".format(num_tasks))
    
    #all_finished = False
    #while (not all_finished):

    #    remaining = processresult.tasks_remaining() # How many of the map call haven't been done yet?
    #    if (remaining == 0): break # Jump out of while loop
    #    logging.debug("run_solve_field: Waiting for {0} tasks to complete...".format(remaining))
    #    time.sleep(2)

    logging.info("solve_field: ------------ done ----------")

class extWCS(object):
    """Very simple WCS class to contain WCS solution for
    each extension headers of a MEF file."""
    def __init__(self, extension_name, ctype1, ctype2, equinox, crval1, crval2, crpix1, crpix2, cd1_1, cd1_2, cd2_1, cd2_2):
        self.name = extension_name
        self.wcs = {}
        self.wcs['CTYPE1'] = ctype1.strip("'")
        self.wcs['CTYPE2'] = ctype2.strip("'")
        self.wcs['EQUINOX'] = equinox
        self.wcs['CRVAL1'] = crval1
        self.wcs['CRVAL2'] = crval2
        self.wcs['CRPIX1'] = crpix1
        self.wcs['CRPIX2'] = crpix2
        self.wcs['CD1_1'] = cd1_1
        self.wcs['CD1_2'] = cd1_2
        self.wcs['CD2_1'] = cd2_1
        self.wcs['CD2_2'] = cd2_2
        self.wcs['THETA'] =  np.arccos(cd1_1)
    
def get_wcs_fromfile(wcs_file, ext_name):
    """This script reads the wcs file output from solve-field
    and returns a WCS structure with the WCS keywords receiving
    their values from the wcs file."""
    f = open(wcs_file, 'r')
    wcs_lines = f.readlines()
    f.close()
    for aline in wrap(wcs_lines[0], 80):
        field = aline.split()
        #print(aline)
        if 'CTYPE1' in aline:
            ctype1 = field[2]
            logging.debug('get_wcs_fromfile: CTYPE1: {0}'.format(ctype1,))
        if 'CTYPE2' in aline:
            ctype2 = field[2]
            logging.debug('get_wcs_fromfile: CTYPE2: {0}'.format(ctype2,))
        if 'EQUINOX' in aline:
            equinox = float(field[2])
            logging.debug('get_wcs_fromfile: EQUINOX: {0}'.format(equinox,))
        if 'CRVAL1' in aline:
            crval1 = float(field[2])
            logging.debug('get_wcs_fromfile: CRVAL1: {0}'.format(crval1,))
        if 'CRVAL2' in aline:
            crval2 = float(field[2])
            logging.debug('get_wcs_fromfile: CRVAL2: {0}'.format(crval2,))
        if 'CRPIX1' in aline:
            crpix1 = float(field[2])
            logging.debug('get_wcs_fromfile: CRPIX1: {0}'.format(crpix1,))
        if 'CRPIX2' in aline:
            crpix2 = float(field[2])
            logging.debug('get_wcs_fromfile: CRPIX2: {0}'.format(crpix2,))
        if 'CD1_1' in aline:
            cd1_1 = float(field[2])
            logging.debug('get_wcs_fromfile: CD1_1: {0}'.format(cd1_1,))
        if 'CD1_2' in aline:
            cd1_2 = float(field[2])
            logging.debug('get_wcs_fromfile: CD1_2: {0}'.format(cd1_2,))
        if 'CD2_1' in aline:
            cd2_1 = float(field[2])
            logging.debug('get_wcs_fromfile: CD2_1: {0}'.format(cd2_1,))
        if 'CD2_2' in aline:
            cd2_2 = float(field[2])
            logging.debug('get_wcs_fromfile: CD2_2: {0}'.format(cd2_2,))
    thisWCS = extWCS(ext_name, ctype1, ctype2, equinox, crval1, crval2, crpix1, crpix2, cd1_1, cd1_2, cd2_1, cd2_2)
    return thisWCS
    
def create_wcs_frame(argv):
    """Creates the <root>_pre_wcs.fits file from input 
    <root>_pre.fits, the output of mefpp, by adding the
    WCS solutions found by solve-field for each extension.
    The file is written into the directory <root>_pre"""
    
    file_name = os.path.basename(argv)
    dir_name = os.path.abspath(file_name[:-5])
    logging.info('create_wcs_frame: file_name: {0}'.format(file_name))
                 
    if os.path.isfile(file_name):
        logging.info('create_wcs_frame: file exists: {0}'.format(file_name))
    if os.path.isdir(dir_name):
        logging.info('create_wcs_frame: directory exists: {0}'.format(dir_name))
    
    hdu_list = fits.open(file_name)
    ext_wcs = {}
    for an_hdu in  hdu_list[1:]:
        #list_of_extensions.append(an_hdu.header['EXTNAME'])
        ext_file_name = an_hdu.header['EXTNAME'].replace('#','_')
        solve_field_dir_name = dir_name+'/'+ext_file_name+'_solve_field/'
        if os.path.isdir(solve_field_dir_name):
            logging.debug('create_wcs_frame: solve field directory exists: {0}'.format(solve_field_dir_name))
        else:
            logging.debug('*** create_wcs_frame: solve field directory does not exists: {0}'.format(solve_field_dir_name))
            break
            
        wcs_file = solve_field_dir_name+'/'+ext_file_name+'.wcs'
        if os.path.isfile(wcs_file):
            logging.debug('create_wcs_frame: WCS file exists: {0}'.format(wcs_file))
        else:
            logging.debug('*** create_wcs_frame: **WCS file does not exists: {0}'.format(wcs_file))
            raise Exception('create_wcs_frame: ERROR **WCS file does not exists: {0}'.format(wcs_file))
            #break
        #print(get_wcs_fromfile(wcs_file))
        ext_wcs[an_hdu.header['EXTNAME']] = get_wcs_fromfile(wcs_file, an_hdu.header['EXTNAME'])


    # here we loop over the ext_wcs dictionary to print the WCS keys
    zkeys = ext_wcs.keys()
    logging.debug('number of wcs keys: {0}'.format(len(zkeys)))

#    for extension_key in ext_wcs.keys():
#        for val, key in ext_wcs[extension_key].wcs.items():
#            logging.info('create_wcs_frame: ext_wcs[{0}].{1}: {2}'.format(extension_key, key, val))
#            #logging.debug('create_wcs_frame: theta: {0} degrees'.format(360.*ext_wcs[akey].theta/(2.*np.pi)))

    # here we are ready to create the modified MEF file with the corrected headers
    for an_hdu in  hdu_list[1:]:
        #list_of_extensions.append(an_hdu.header['EXTNAME'])
        header = an_hdu.header
        header_name = header['EXTNAME']
        for key, val in ext_wcs[header_name].wcs.items():
            header[key] = ext_wcs[header_name].wcs[key]
            logging.info('create_wcs_frame: header[{0}][{1}] = {2}'.format(header_name, key, ext_wcs[header_name].wcs[key]))
        #header['CRVAL1'] = ext_wcs[header_name].crval1
        #header['CRVAL2'] = ext_wcs[header_name].crval2
        #header['CRPIX1'] = ext_wcs[header_name].crpix1
        #header['CRPIX2'] = ext_wcs[header_name].crpix2
        #header['CD1_1'] = ext_wcs[header_name].cd1_1
        #header['CD1_2'] = ext_wcs[header_name].cd1_2
        #header['CD2_1'] = ext_wcs[header_name].cd2_1
        #header['CD2_2'] = ext_wcs[header_name].cd2_2

    logging.info('create_wcs_frame: creating {0}'.format(dir_name+'/'+file_name[:-5]+'_wcs.fits',))
    hdu_list.writeto(dir_name+'/'+file_name[:-5]+'_wcs.fits', output_verify='ignore', overwrite=True)    
    hdu_list.close()
