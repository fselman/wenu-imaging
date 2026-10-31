"""Private Intel Mac qualification of simple ASI inputs; no installation/reduction."""
import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
import platform
import runpy
import subprocess
import sys
import tomllib

MAIN = "6c4b0f0eff639da8dbef890f0df10f86c70bb0ee"
FILES = ["Pycavi2/tools/fits_preparation.py", "Pycavi2/tools/prepare_zwo_bath.py",
         "Pycavi2/tools/prepare_zwo_asi.py", "Pycavi2/tools/asi_preparation_profiles.py",
         "Pycavi2/tests/test_zwo_bath_preparation.py", "Pycavi2/tests/test_zwo_asi_preparation.py",
         "Pycavi2/tests/test_asi_simple_profiles.py",
         "Pycavi2/config/preparation/zwo_asi1600mm_bath.toml",
         "Pycavi2/config/preparation/bath_observatory.toml",
         "Pycavi2/config/preparation/zwo_asi1600mm_pro.toml",
         "Pycavi2/config/preparation/bath_directories.toml",
         "docs/manuals/cameras/ASI1600_Manual_EN_V1.5.pdf"]


def require(ok, message):
    if not ok: raise RuntimeError(message)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision",required=True)
    parser.add_argument("--run",type=Path,required=True)
    args=parser.parse_args()
    # Host/environment guards: only the previously inspected Intel Mac and imaging Python.
    require(platform.system()=="Darwin" and platform.node().split(".")[0]=="MC02VV0HPHTDG", "Wrong host")
    prefix=Path("/Users/fselman/anaconda3/envs/wenu-imaging")
    require(Path(sys.prefix).resolve()==prefix.resolve() and Path(sys.executable).resolve()==(prefix/"bin/python").resolve(), "Wrong Python")
    require(os.getpriority(os.PRIO_PROCESS,0)>=10,"Require niceness >=10")
    repo=Path("/Users/fselman/Developer/wenu-imaging")
    def git(*parts):
        return subprocess.check_output(["/usr/bin/git","-C",str(repo),*parts])
    require(git("rev-parse",args.revision+"^{commit}").decode().strip()==args.revision,"Require exact fetched commit")
    require(Path(git("rev-parse","--show-toplevel").decode().strip()).resolve()==repo.resolve(),"Wrong checkout")
    require(Path(__file__).read_bytes()==git("show",args.revision+":Pycavi2/tests/qualify_asi_simple_profiles.py"),"Runner source differs")
    guard_path=repo/"Pycavi2/tests/qualify_inspection_stages.py"
    require(guard_path.read_bytes()==git("show",MAIN+":Pycavi2/tests/qualify_inspection_stages.py"),"Protection helper changed")
    guard=runpy.run_path(str(guard_path)); before=guard["checkout"](repo)
    allowed={"git@github.com:fselman/wenu-imaging.git","ssh://git@ssh.github.com:443/fselman/wenu-imaging.git"}
    require(before["head"]==MAIN and before["branch"]=="main" and before["upstream"]=="origin/main" and not before["status"],"Expected clean inspected main")
    require(before["origin"] in allowed and before["push"] in allowed,"Unexpected origin")
    run=args.run.resolve(strict=True)
    require(run.parent==(Path.home()/"Software/build/wenu-imaging").resolve() and not args.run.is_symlink(),"Unexpected private run directory")
    protected=guard["protected_paths"](); installed=[guard["identity"](p) for p in protected]
    raw=Path.home()/"Pictures/ZWO_Bath"
    require(raw.is_dir() and not raw.is_symlink(),"Unexpected raw root")
    # Protection snapshots: retain all raw file identities, without reading observational pixels.
    def raw_metadata():
        result={}
        for directory,dirs,names in os.walk(raw,followlinks=False):
            for name in names:
                p=Path(directory)/name;s=p.lstat()
                result[str(p.relative_to(raw))]=[s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_mode]
        return result
    original=raw_metadata(); receipt={"revision":args.revision,"status":"running","source_sha256":{}}
    finished=False;print("RETAINED RUN:",run,flush=True)
    try:
        # Private export: materialize only pinned helper/test/profile/manual files.
        source=run/"source"
        for name in FILES:
            content=git("show",args.revision+":"+name)
            p=source/name;p.parent.mkdir(parents=True,exist_ok=True)
            with p.open("xb") as f:f.write(content)
            receipt["source_sha256"][name]=hashlib.sha256(content).hexdigest()
        config=source/"Pycavi2/config/preparation"
        camera=tomllib.loads((config/"zwo_asi1600mm_pro.toml").read_text())
        require(receipt["source_sha256"]["docs/manuals/cameras/ASI1600_Manual_EN_V1.5.pdf"]==camera["manual"]["sha256"],"Manual identity mismatch")
        env=dict(os.environ,TMPDIR=str(run),PYTHONDONTWRITEBYTECODE="1",OPENBLAS_NUM_THREADS="1",OMP_NUM_THREADS="1",MKL_NUM_THREADS="1",NUMEXPR_NUM_THREADS="1")
        # Synthetic controls: exercise legacy 9, existing generic 11 and simple-input 12 groups.
        for name in ("test_zwo_bath_preparation.py","test_zwo_asi_preparation.py","test_asi_simple_profiles.py"):
            log=run/(name+".log")
            with log.open("x") as f:
                result=subprocess.run([sys.executable,"-B",str(source/"Pycavi2/tests"/name)],cwd=run,env=env,stdout=f,stderr=subprocess.STDOUT)
            print(log.read_text(),flush=True)
            require(result.returncode==0,"Synthetic controls failed: "+name)
        # Header-only dataset generation: the new public CLI learns all Bath frame settings.
        plan=run/"bath-dataset.toml";log=run/"bath-dataset.log"
        command=[sys.executable,"-B",str(source/"Pycavi2/tools/prepare_zwo_asi.py"),"plan",
                 "--observatory",str(config/"bath_observatory.toml"),"--camera",str(config/"zwo_asi1600mm_pro.toml"),
                 "--directories",str(config/"bath_directories.toml"),"--root",str(raw),"--report",str(plan)]
        with log.open("x") as f:
            result=subprocess.run(command,cwd=run,env=env,stdout=f,stderr=subprocess.STDOUT)
        print(log.read_text(),flush=True);require(result.returncode==0,"Dataset plan contains blocked inputs")
        # Plan verification: compare expected role counts and report names/unknown acquisition modes.
        value=tomllib.loads(plan.read_text());counts=collections.Counter(r["classification"]["ESO DPR TYPE"] for r in value["entries"])
        require(not value["errors"] and counts=={"BIAS":10,"DARK":10,"OBJECT":196,"FLAT":44},"Unexpected Bath classifications")
        receipt["plan_sha256"]=hashlib.sha256(plan.read_bytes()).hexdigest()
        receipt["roles"]=dict(counts)
        receipt["telescope_names"]=dict(collections.Counter(r["additions"]["WENU PROV TELESCOPE"] for r in value["entries"]))
        receipt["mode_unknown"]=sum("detector_mode" in r["missing_metadata"] for r in value["entries"])
        print("TELESCOPE NAMES:",json.dumps(receipt["telescope_names"],indent=2))
        print("DETECTOR MODE UNKNOWN:",receipt["mode_unknown"])
        print("GENERATED DATASET TOML:",plan)
        finished=True
    finally:
        # Preservation verification: always retain a receipt and compare installation/raw/main state.
        checks={"installed_files":installed==[guard["identity"](p) for p in protected],
                "raw_metadata":original==raw_metadata(),"checkout":before==guard["checkout"](repo)}
        receipt["preservation"]=checks;receipt["status"]="passed" if finished and all(checks.values()) else "failed"
        with (run/"qualification.json").open("x") as f:json.dump(receipt,f,indent=2);f.write("\n")
        print("QUALIFICATION:",receipt["status"]);print("PRESERVATION:",checks);print("RETAINED EVIDENCE:",run)
        require(all(checks.values()),"Preservation failed")


if __name__=="__main__":main()
