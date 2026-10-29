"""Offline source/log baseline mapper; not a PAF loader or runtime-equivalence test."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import shlex
import struct
import tarfile

SOURCE_BLOBS={
 'mefpp2/ins/mef/common/mefp_lib.c':'edde7862e5ed59ccfd78489d7c12d14d9c37710d',
 'mefpp2/ins/mef/common/mefp_lib.h':'b1e7f399ac631d48fc009eaa3403e19c4c697d0c',
 'mefpp2/ins/mef/recipes/mefpp.c':'9487b09943069de3cc57ad11668f8e09d04230ef',
 'mefpp2/qfits5/src/pafs.c':'1b06e73e3843efa2d19b75f1f21620ad2988c808',
}
ARCHIVE_SHA='3a6519ff91e31e69ace2f34126085d9c936d487222135acc4a86281809615a81'


def require(ok,message):
    if not ok:raise RuntimeError(message)


def sha(data):return hashlib.sha256(data).hexdigest()


def paf_occurrences(data):
    # Emulate only the observed simple line/token form of qfits_paf_query.
    # First occurrence and ASCII paired-quote stripping are preserved.
    rows=collections.defaultdict(list)
    for n,line in enumerate(data.decode('utf-8').splitlines(),1):
        match=re.match(r'((?:MEF|PHASE3)\.\S+)\s+(.*)',line)
        if match:
            value=match[2].split(';',1)[0].rstrip().lstrip()
            if len(value)>=2 and value[0]==value[-1]=='"':value=value[1:-1]
            rows[match[1]].append({'line':n,'value':value})
    return rows


def fields(header,name):
    clean=re.sub(r'/\*.*?\*/','',header,flags=re.S)
    block=clean.split('typedef struct _mef_'+name+'_ {',1)[1].split('} mef_'+name,1)[0]
    result={}
    for part in block.split(';'):
        part=re.sub(r'\s+',' ',part).strip()
        if not part:continue
        m=re.fullmatch(r'([A-Za-z_][\w ]*?)\s*(\*\s*\*?\s*)?([A-Za-z_]\w*)\s*(\[[^\]]+\])?',part)
        require(bool(m),'unparsed field: '+part)
        result[m[3]]=m[1].strip()+(' '+m[2].strip() if m[2] else '')+(m[4] or '')
    return result


def domain(key):
    if '%d' in key or key in ('MEF.NCHIPS','MEF.CORRECT.REFPIXELS','MEF.REFPIX.X','MEF.REFPIX.Y'):return 'instrument_detector_config'
    if key in ('MEF.ORIGIN','MEF.TELESCOPE','MEF.INSTRUMENT'):return 'instrument_metadata'
    if '.NAME.O' in key:return 'product_naming_default'
    if key.startswith('PHASE3.') or key.endswith(('.KEY','.COMMENT')):return 'product_metadata_mapping'
    if key.startswith(('MEF.BIAS.','MEF.BPM.','MEF.DOMEFF.','MEF.SKYFF.')):return 'calibration_algorithm_config'
    return 'processing_config'


def map_baseline(archive,source_root):
    raw=archive.read_bytes();require(sha(raw)==ARCHIVE_SHA,'archive identity')
    with tarfile.open(archive) as bundle:
        ms=bundle.getmembers();names=[m.name for m in ms]
        require(len(names)==len(set(names)) and all(m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts for m in ms),'unsafe members')
        data={m.name:bundle.extractfile(m).read() for m in ms}
    manifest=json.loads(data['manifest.json']);require(set(data)==set(manifest['files'])|{'manifest.json'},'manifest membership')
    for name,row in manifest['files'].items():require(sha(data[name])==row['sha256'] and len(data[name])==row['bytes'],'manifest identity: '+name)
    lock=json.loads(data['input-lock.json'])
    require(len(lock['sources'])==89 and lock['source_bytes_unchanged'] and lock['checkout_unchanged'],'input lock status')
    for name,row in lock['sources'].items():require(sha(data[name])==row['sha256'] and len(data[name])==row['bytes'],'source link: '+name)
    sources={}
    for name,expected in SOURCE_BLOBS.items():
        blob=(source_root/name).read_bytes()
        require(hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()==expected,'current source identity: '+name)
        sources[name]=blob.decode('utf-8')
    source=sources['mefpp2/ins/mef/common/mefp_lib.c']
    begin=source.index('mef_bb * mef_bb_new_from_paf');end=source.index('void mef_bb_clear_work',begin);constructor=source[begin:end]
    ctypes={name:fields(sources['mefpp2/ins/mef/common/mefp_lib.h'],name) for name in ('bb','ccd')}
    matches=list(re.finditer(r'sprintf\(buffer,\s*"([^"]+)"[^;]*;',constructor));registry=[]
    for i,match in enumerate(matches):
        block=constructor[match.end():matches[i+1].start() if i+1<len(matches) else len(constructor)]
        getter=re.search(r'mef_paf_value\(cfgfile, buffer, (\d), &value\)',block)
        if not getter:continue
        dest=re.search(r'((?:bb->|\(ccd\+i\)->)[\w]+(?:\[[^\]]+\])?)\s*=\s*([^;]+);',block)
        require(dest is not None,'unmapped getter destination')
        target=dest[1];family='ccd' if target.startswith('(ccd+i)') else 'bb';field=target.split('->')[1].split('[')[0]
        ctype=ctypes[family][field]
        conversions=re.findall(r'(?:ivalue|fvalue|dvalue)\s*=\s*([^;]+);',block)
        registry.append({'key_template':match[1],'kind_code':int(getter[1]),'legacy_target':target,
                         'legacy_storage_type':ctype,'conversion':conversions[0].strip() if conversions else 'string copy after qfits query',
                         'source_line':source[:begin+match.start()].count('\n')+1,'proposed_owner_domain':domain(match[1])})
    require(len(registry)==151 and sum('%d' in r['key_template'] for r in registry)==14,'constructor coverage changed')
    profiles={};partitions=[];log_checks=0
    argument_options={'--bias':'name_bias','--bpm':'name_bpm','--dome':'name_dome','--sky':'name_sky','--mff':'name_mf','--science':'science_name_i','--mffsave':'name_mf_o'}
    flags={'--biassave':'bias_save','--biassub':'bias_subtract','--domesave':'dome_save','--skysave':'sky_save'}
    for instrument in ('omegacam','wfi'):
        project_label=instrument+'/config/'+instrument+'.paf';project=data[project_label]
        require(project==data['repository-config/'+instrument+'.paf'],'project/repository instrument PAF differs')
        occurrences=paf_occurrences(project);nchips=int(occurrences['MEF.NCHIPS'][0]['value']);values={};rendered={}
        for entry in registry:
            for chip in range(1,nchips+1) if '%d' in entry['key_template'] else [None]:
                key=entry['key_template']%chip if chip else entry['key_template'];rows=occurrences[key];require(bool(rows),'missing key: '+key)
                literal=rows[0]['value'];kind=entry['kind_code']
                if kind==0: value=literal;display=value
                elif key=='MEF.NCHIPS':value=int(literal);display=str(value)
                elif kind==1:
                    if entry['conversion']=='atoi(value)':
                        prefix=re.match(r'[+-]?\d+',literal);value=int(prefix[0]) if prefix else 0
                    else:value=int(float(literal))
                    display=str(value)
                    if entry['legacy_storage_type']=='float':value=struct.unpack('!f',struct.pack('!f',value))[0]
                elif kind==2:value=struct.unpack('!f',struct.pack('!f',float(literal)))[0];display=format(value,'.6f')
                else:value=float(literal);display=format(value,'.6f')
                values[key]={'source_line':rows[0]['line'],'literal':literal,'modeled_stored_value':value}
                rendered[key]=display
        profiles[instrument]={'project_paf_sha256':sha(project),'nchips':nchips,'constructor_keys':len(values),
                              'duplicates':{k:v for k,v in occurrences.items() if len(v)>1},
                              'not_read_by_constructor':sorted(set(occurrences)-set(values)),'values':values}
        for retained in lock['projects'][instrument]['commands']:
            partition=retained['partition'];prefix=instrument+'/'+partition+'/'
            require(data[prefix+'mefpp.paf']==project,'partition PAF override: '+partition)
            tokens=shlex.split(retained['retained_last_command']);require(tokens[:2]==['nohup',str(Path(lock['projects'][instrument]['project']).parents[1]/'native/bin/mefpp')],'unexpected executable prefix')
            argv=tokens[2:];request={};i=0
            while i<len(argv):
                option=argv[i]
                if option in argument_options:
                    require(i+1<len(argv),'missing option argument');request[argument_options[option]]=argv[i+1];i+=2
                elif option in flags:request[flags[option]]=1;i+=1
                else:raise RuntimeError('unreviewed CLI option/positional argument: '+option)
            observed=collections.defaultdict(list)
            for line in data[prefix+'mefpp.log'].decode('utf-8').splitlines():
                m=re.search(r'mef_bb_new:\s*([A-Z][A-Z0-9_.]+):[\t ]*(.*)',line)
                if m:observed[m[1]].append(m[2].strip())
            for key,text in rendered.items():require(key in observed and all(v==text for v in observed[key]),'constructor log differs: '+partition+' '+key)
            log_checks+=len(rendered)
            list_members={}
            for field,value in request.items():
                if isinstance(value,str) and value.endswith('.list'):
                    raw_list=data[prefix+value].decode('utf-8');list_members[field]=[v for v in raw_list.splitlines() if v.strip() and not v.lstrip().startswith('#')]
            services=(['mef_sci_pp'] if 'science_name_i' in request else ['mef_cal_skyff','mef_cal_mff'] if 'name_mf_o' in request else ['mef_cal_domeff'] if 'name_dome' in request else ['mef_cal_bias'])
            partitions.append({'instrument':instrument,'partition':partition,'paf':'mefpp.paf','paf_selection':'legacy cwd default; no --pafname override',
                               'retained_command':retained['retained_last_command'],'cli_field_overrides':request,'list_members':list_members,
                               'planned_service_mapping':services,'constructor_log_fields_verified':len(rendered)})
    require(log_checks==4668 and len(partitions)==12,'paired log coverage')
    return {'schema_version':1,'status':'source-and-retained-log-baseline-mapped','archive_sha256':ARCHIVE_SHA,
            'source_revision':'7341c895e9e1eb7008915e1e2cf961532b7eb8a6','source_git_blobs':SOURCE_BLOBS,
            'scope':'finite source/log-derived model; not production PAF decoding or full-precision runtime equivalence',
            'registry':registry,'profiles':profiles,'partitions':partitions,'constructor_log_fields_verified':log_checks,
            'limits':['constructor logs round floating values; binary32 values are source-derived model values',
                      'snapshot does not prove unrecorded historical invocations or all runtime mutations',
                      'domains and typed public layouts remain implementation design; no scientific defaults changed']}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--archive',type=Path,required=True);parser.add_argument('--source-root',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    result=map_baseline(args.archive,args.source_root)
    with args.output.open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps({'status':result['status'],'getter_templates':len(result['registry']),'constructor_log_fields_verified':result['constructor_log_fields_verified'],'partitions':len(result['partitions'])}))
