from os import listdir
from os.path import isfile, join
import glob
from astropy.io import fits
import math
import operator
import copy
#import datetime
import os
from datetime import datetime
from pathlib import Path

class Exposure:
    
    def __init__(self, filename):

        self.filename = filename
        with fits.open(filename) as hdu_list:
            primary_header = hdu_list[0].header
            self.dpr_catg = self.getKeyVal(primary_header, 'HIERARCH ESO DPR CATG')
            self.dpr_type = self.getKeyVal(primary_header, 'HIERARCH ESO DPR TYPE')
            self.obsid = self.getKeyVal(primary_header, 'HIERARCH ESO OBS ID')
            self.OBstart = self.getKeyVal(primary_header, 'HIERARCH ESO OBS START')
            self.dateobs = self.getKeyVal(primary_header, 'DATE-OBS')
            self.tplnexp = self.getKeyVal(primary_header, 'HIERARCH ESO TPL NEXP')
            self.tplexpno = self.getKeyVal(primary_header, 'HIERARCH ESO TPL EXPNO')
            self.filter = self.getKeyVal(primary_header, 'HIERARCH ESO INS FILT1 NAME')
            self.exptime = self.getKeyVal(primary_header, 'EXPTIME')

            if (self.dpr_catg == 'SCIENCE' and self.dpr_type == 'OBJECT') or \
                (self.dpr_catg == 'CALIB' and self.dpr_type == 'STD,ZEROPOINT'):
                self.ra = self.getKeyVal(primary_header, 'RA')
                self.dec = self.getKeyVal(primary_header, 'DEC')
                self.tel_alpha = self.getKeyVal(primary_header, 'HIERARCH ESO TEL TARG ALPHA')
                self.tel_delta = self.getKeyVal(primary_header, 'HIERARCH ESO TEL TARG DELTA')
                self.target = self.getKeyVal(primary_header, 'HIERARCH ESO OBS TARG NAME').replace(' ', '_')
        
                # we add the FLI
                yyyy = int(self.dateobs[0:4])
                mm = int(self.dateobs[5:7])
                dd = int(self.dateobs[8:10])
                fli = self.get_phase_on_day(yyyy,mm,dd)
                if fli <= 0.5:
                    fli = fli*2.0
                else:
                    fli = 2.0*(1-fli)
                self.fli = fli  

    def get_phase_on_day(self, year, month, day):
        """Returns a floating-point number from 0-1. where 0=new, 0.5=full, 1=new"""
        #Ephem stores its date numbers as floating points, which the following uses
        #to conveniently extract the percent time between one new moon and the next
        #This corresponds (somewhat roughly) to the phase of the moon.

        #Use Year, Month, Day as arguments
        date=ephem.Date(datetime.date(year,month,day))

        nnm = ephem.next_new_moon    (date)
        pnm = ephem.previous_new_moon(date)

        lunation=(date-pnm)/(nnm-pnm)

        #Note that there is a ephem.Moon().phase() command, but this returns the
        #percentage of the moon which is illuminated. This is not really what we want.

        return lunation

            
    def getKeyVal(self,primary_header, key):
        val = primary_header[key]
        return val


class ExposuresPartition:
    
    def __init__(self, filename, frametype):

        #print('ExposurePartition  filename: '+filename+'\nExposurePartition frametype: '+frametype, end='\r')
        
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
        
    def insertExposure(self, exposure):

        # we select the partition according to exposure dpr.type
        if 'BIAS' in exposure.dpr_type:
            key_str = 'bias/'+'%d'%exposure.obsid+'/'+exposure.OBstart
        elif 'FLAT,DOME' in exposure.dpr_type:
            key_str = 'dome/'+'%d'%exposure.obsid+'/'+exposure.filter+'/'+exposure.OBstart
        elif 'FLAT,SKY' in exposure.dpr_type:
            key_str = 'sky/'+'%d'%exposure.obsid+'/'+exposure.filter+'/'+exposure.OBstart
        elif ('CALIB' in exposure.dpr_catg) and ('STD,ZEROPOINT' in exposure.dpr_type):
            key_str = 'std/'+exposure.target + '_' + \
                    exposure.filter+'/'+\
                    exposure.OBstart
        elif ('SCIENCE' in exposure.dpr_catg) and ('OBJECT' in exposure.dpr_type):
            key_str = 'science/'+exposure.target+'_'+\
                    ("%010.3f"%exposure.tel_alpha).replace('.','p')+'_'+\
                    ("%09.1f"%exposure.tel_delta).replace('.','p').replace('-','m')+'/'+\
                    exposure.filter+'/'+\
                    exposure.OBstart
        else:
            print('dpr type: %s'%exposure.dpr_type, ' not classifiable.', end='\r')
            key_str = 'unknown/'+'%s'%exposure.dpr_type


        self.base_path = key_str
        self.exposureList.append(exposure)
        self.OBstart = exposure.OBstart
        self.filter = exposure.filter
        if key_str in self.partList:
            self.partList[key_str].append(exposure)
        else:
            self.partList[key_str] = [exposure]
            self.OBstartDict[key_str] = exposure.OBstart
            self.filterDict[key_str] = exposure.filter
        
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

class SciencePartition:
    
    def __init__(self, filename):

        self.base_path = os.path.dirname(filename)
        self.filter = self.getFilter(filename)
        self.OBstart = self.getOBstart(filename)
        self.bpmPartition = None
        self.biasPartition = None
        self.biasFrame = None
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
    
class BiasPartition:
    
    def __init__(self, filename):

        self.base_path = os.path.dirname(filename)
        self.OBstart = self.getOBstart(filename)
        self.bpmPartition = None
        #self.biasPartition = None
        self.mffPartition = None
        
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
