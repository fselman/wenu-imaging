# partition list of calibration frames
from os.path import isfile, join
import glob
import math
import datetime
import os
from pathlib import Path
import logging

# 3rd party imports
from astropy.io import fits
import ephem

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

# This class must be modified to consist of partitions as defined in pymefpp_run
# and the homogenized pymefpp_create assoc. At the end we should have the following
# classes:
#
# Exposure:       with the data of a single exposure
# Partition:      with the data of a single partition
# PartitionsTree: with a dictionaries of partitions and their association.
#
class PartitionsTree:

    distanceCriteria = 3.0 # distance below which exposures are grouped
    
    def __init__(self):

        self.partList = {}
        self.OBstartDict = {}
        self.filterDict = {}
        self.biasDict = {}
        self.domeDict = {}
        self.skyDict = {}
        
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
            logging.info("dpr type: {exposure.dpr_type} not classifiable.")
            key_str = 'unknown/'+'%s'%exposure.dpr_type


        if key_str in self.partList:
            self.partList[key_str].append(exposure)
        else:
            self.partList[key_str] = [exposure]
            self.OBstartDict[key_str] = exposure.OBstart
            self.filterDict[key_str] = exposure.filter

    def getDistance(self,partition, observation):
        ra = 0.0
        dec = 0.0
        n = 0
        for obs in partition:
            n+=1
            ra+=obs.ra
            dec+=obs.dec
        ra = ra / float(n)
        dec = dec / float(n)
        return math.sqrt((ra-observation.ra)**2 + (dec - observation.dec)**2)

    def timeDistance(self, time_str1, time_str2):
        FMT = '%Y-%m-%dT%H:%M:%S'
        return abs((datetime.strptime(time_str1, FMT) - datetime.strptime(time_str2, FMT)).total_seconds())

            
    def getKeyVal(self, filename, key):
        with fits.open(filename) as hdu_list:
            primary_header = hdu_list[0].header
            val = primary_header[key]
            return val

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

def createFrameList(base_dir, list_name, frameDict):
    for aFramePartitionKey, aFramePartitionList in frameDict.items():
        subdir_str = aFramePartitionKey
        try:
            os.makedirs(base_dir+aFramePartitionKey)
        except:
            pass
        
        with open(base_dir+aFramePartitionKey+'/'+list_name, 'w') as f:
            pass
        
        for aFrame in aFramePartitionList:
            logging.info("{0} -- {1}".format(subdir_str, aFrame.filename))
            try:
                os.makedirs(base_dir+'/'+subdir_str)
            except:
                pass
        
            try:
                with open(base_dir+'/'+subdir_str+'/'+list_name, 'a') as f:
                    print(aFrame.filename, file=f)
            except:
                raise Exception('could not change directory to: '+reduced_cal_dir+subdir_str)


