"""Prepare the fixed tiny two-extension F1 dataset; no native processing."""
import argparse
from datetime import datetime,timezone
import hashlib,json,re
from pathlib import Path
import numpy as np
from astropy.io import fits


def prepare(work, repo):
    work.mkdir(exist_ok=False)
    record=dict(purpose=__doc__,status='running',native_execution=False,native_launches_consumed=0,
                created_utc=datetime.now(timezone.utc).isoformat(),configuration='one robust BPM configuration, 0.5-1.5 thresholds',
                geometry=dict(raw=[9,18],science=[9,9],extensions=2,overscan_columns=[10,18]))
    report=work/'run-provenance.json'
    save=lambda:report.write_text(json.dumps(record,indent=2)+'\n')
    save()
    paf=repo/'mefpp2/ins/mef/config/omegacam.paf'
    parent=paf.read_bytes();record['parent_paf_sha256']=hashlib.sha256(parent).hexdigest()
    # Synthetic geometry only; the production configuration file remains unchanged.
    text=parent.decode();settings={'MEF.NCHIPS':2,'MEF.USE.PRESCAN':0,'MEF.USE.OVERSCAN':1,
        'MEF.SCANREJ.MIN':0,'MEF.SCANREJ.MAX':0,'MEF.BPM.PROPFLAG':0,'MEF.BPM.LGAINTHR':.5,
        'MEF.BPM.HGAINTHR':1.5,'MEF.MEDIAN.REG.X1':0,'MEF.MEDIAN.REG.X2':8,
        'MEF.MEDIAN.REG.Y1':0,'MEF.MEDIAN.REG.Y2':8,'MEF.KERN.HSIZE':1}
    for xt in (1,2):
        for suffix,value in [('PRESCAN.X.MIN',1),('PRESCAN.X.MAX',1),('OVERSCAN.X.MIN',10),('OVERSCAN.X.MAX',18),
                             ('CROP.X.MIN',1),('CROP.X.MAX',9),('CROP.Y.MIN',1),('CROP.Y.MAX',9)]:
            settings['MEF.'+suffix+'.CHIP'+str(xt)]=value
    for key,value in settings.items():
        text,n=re.subn(r'^'+re.escape(key)+r'\s+[^;\n]*;',key+' '+str(value)+';',text,flags=re.M)
        if n!=1:raise RuntimeError('Missing/duplicate synthetic PAF setting: '+key)
    (work/'mefpp.paf').write_text(text)
    record['synthetic_paf_overrides']=settings;save()
    # Known-answer data: nonidentical bias planes avoid zero-width clipping intervals.
    gain=np.ones((9,9),np.float32);gain[1,2]=.25;gain[6,7]=2.
    mask=np.ones((9,9),np.uint8);mask[1,2]=mask[6,7]=0
    levels={'bias':[-1,0,1],'bpm':[1000,2000,3000],
            'dome':[12000,16000,20000,24000,26000],
            'sky':[8000,10000,12000,14000,16000],'science':[1000]}
    for kind,values in levels.items():
        names=[]
        for number,level in enumerate(values):
            name=f'{kind}{number}.fits';names.append(name)
            header=fits.Header()
            for k,v in {'ORIGFILE':name,'ORIGIN':'ESO FROZEN F1','TELESCOP':'VST','INSTRUME':'OMEGACAM',
                'DATE-OBS':f'2026-10-28T00:00:{number:02d}.000','MJD-OBS':61341.+number/86400.,
                'EXPTIME':float(level if kind=='bpm' else 1),'OBJECT':kind.upper(),'OBSERVER':'F1',
                'PI-COI':'F1','RA':0.,'DEC':0.,'UTC':0.,'RADECSYS':'ICRS',
                'ESO DPR CATG':'SCIENCE' if kind=='science' else 'CALIB','ESO DPR TYPE':kind.upper(),
                'ESO DPR TECH':'IMAGE','ESO OBS PROG ID':'F1','ESO OBS ID':1,
                'ESO INS FILT1 NAME':'S2','ESO DET WIN1 BINX':1,'ESO DET WIN1 BINY':1}.items():header[k]=v
            hdus=[fits.PrimaryHDU(header=header)]
            for xt,response in ((1,1.),(2,2.)):
                data=np.full((9,18),10.,np.float32)
                science=np.full((9,9),float(level),np.float32)
                if kind!='bias':science*=response
                if kind=='bpm':science*=gain if xt==1 else gain[:,::-1]
                data[:,:9]+=science
                ext=fits.Header()
                for k,v in {'EXTNAME':'F1_CCD_A' if xt==1 else 'F1_CCD_B','CRVAL1':0.,'CRVAL2':0.,
                            'CRPIX1':5.,'CRPIX2':5.,'CTYPE1':'RA---TAN','CTYPE2':'DEC--TAN',
                            'CD1_1':-1./3600,'CD1_2':0.,'CD2_1':0.,'CD2_2':1./3600}.items():ext[k]=v
                hdus.append(fits.ImageHDU(data=data,header=ext))
            fits.HDUList(hdus).writeto(work/name)
        (work/(kind+'.list')).write_text('\n'.join(names)+'\n')
    # Independent expectations: bias zero, shared-normalized flats 1 and 2,
    # combined flats 1 and 2, corrected science 1000 on both detectors.
    for xt in (1,2):
        for kind,array in {'bias':np.zeros((9,9),np.float32),'flat':np.full((9,9),float(xt),np.float32),
                           'science':np.full((9,9),1000.,np.float32),'bpm':mask if xt==1 else mask[:,::-1]}.items():
            np.save(work/f'expected-{kind}-{xt}.npy',array)
    record['native_argv']=['--pafname','mefpp.paf','--bias','bias.list','--biassave','--biassub',
        '--bpm','bpm.list','--dome','dome.list','--domesave','--sky','sky.list','--skysave','--science','science.list']
    record['frame_counts']={k:len(v) for k,v in levels.items()}
    record['expected_good_mask_pixels']=79
    record['input_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(work.iterdir()) if p.is_file() and p!=report}
    record['parent_configuration_preserved']=paf.read_bytes()==parent
    record['status']='prepared-not-native-qualified';save()
    return record


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work',type=Path,required=True)
    args=parser.parse_args()
    result=prepare(args.work.resolve(),Path(__file__).resolve().parents[2])
    print('F1 FIXTURE:',result['status'],'frames:',sum(result['frame_counts'].values()),'native launches: 0')
