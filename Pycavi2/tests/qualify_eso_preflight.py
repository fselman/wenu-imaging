"""Guarded private ESO preflight qualification; synthetic inputs only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import runpy
import subprocess
import sys

MAIN="6c4b0f0eff639da8dbef890f0df10f86c70bb0ee"
FILES=["Pycavi2/pycavi/pycavi_paths.py","Pycavi2/pycavi/pycavi_project.py",
       "Pycavi2/pycavi/pycavi_inspection_stages.py","Pycavi2/pycavi/pycavi_product_paths.py",
       "Pycavi2/pycavi/pycavi_preflight.py","Pycavi2/pycavi/config/omegacam.cfg",
       "Pycavi2/pycavi/config/wfi.cfg","Pycavi2/tests/test_eso_preflight.py"]


def require(ok,message):
    if not ok:raise RuntimeError(message)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host",choices=("mac","chapman"),default="mac")
    parser.add_argument("--revision",required=True)
    parser.add_argument("--run",type=Path,required=True)
    args=parser.parse_args()
    # Host/environment guards: use the previously selected target tools and checkout only.
    settings={"mac":("Darwin","MC02VV0HPHTDG","/Users/fselman/Developer/wenu-imaging",
                     "/Users/fselman/anaconda3/envs/wenu-imaging"),
              "chapman":("Linux","chapman4","/home1/fselman/Software/wenu-imaging",
                         "/home/fselman/.conda/envs/wenu-imaging")}
    system,host,root,prefix=settings[args.host]
    require((platform.system(),platform.node().split(".")[0])==(system,host),"Wrong host")
    require(Path(sys.prefix).resolve()==Path(prefix).resolve() and Path(sys.executable).resolve()==(Path(prefix)/"bin/python").resolve(),"Wrong Python")
    require(os.getpriority(os.PRIO_PROCESS,0)>=10,"Require niceness >=10")
    repo=Path(root).resolve(strict=True)
    def git(*parts):
        return subprocess.check_output(["/usr/bin/git","-C",str(repo),*parts])
    require(Path(git("rev-parse","--show-toplevel").decode().strip()).resolve()==repo,"Wrong checkout")
    require(git("rev-parse",args.revision+"^{commit}").decode().strip()==args.revision,"Expected exact fetched source")
    require(Path(__file__).read_bytes()==git("show",args.revision+":Pycavi2/tests/qualify_eso_preflight.py"),"Runner differs from source")
    guard_path=repo/"Pycavi2/tests/qualify_inspection_stages.py"
    require(guard_path.read_bytes()==git("show",MAIN+":Pycavi2/tests/qualify_inspection_stages.py"),"Protection helper changed")
    guard=runpy.run_path(str(guard_path));before=guard["checkout"](repo)
    require(before["head"]==MAIN and before["branch"]=="main" and before["upstream"]=="origin/main" and not before["status"],"Expected inspected clean main")
    allowed={"git@github.com:fselman/wenu-imaging.git","https://github.com/fselman/wenu-imaging.git","ssh://git@ssh.github.com:443/fselman/wenu-imaging.git"}
    require(before["origin"] in allowed and before["push"] in allowed,"Unexpected origin")
    run=args.run.resolve(strict=True)
    require(run.parent==(Path.home()/"Software/build/wenu-imaging").resolve() and not args.run.is_symlink(),"Unexpected private run directory")
    # Installed protection: hash the selected module, engine and configuration; never execute them.
    paths=guard["protected_paths"]();installed=[guard["identity"](p) for p in paths]
    receipt={"revision":args.revision,"host":host,"status":"running","source_sha256":{},"suite_expected":10}
    finished=False;print("RETAINED RUN:",run,flush=True)
    try:
        # Private source export: only the pinned shared reader, ESO service, mappings and controls.
        source=run/"source"
        for name in FILES:
            content=git("show",args.revision+":"+name)
            p=source/name;p.parent.mkdir(parents=True,exist_ok=True)
            with p.open("xb") as f:f.write(content)
            receipt["source_sha256"][name]=hashlib.sha256(content).hexdigest()
        # Synthetic contracts: actual backend/public CLI, no-array reads and immutable input bytes/mode/mtime.
        log=run/"eso-preflight-tests.log"
        env=dict(os.environ,TMPDIR=str(run),PYTHONDONTWRITEBYTECODE="1",OPENBLAS_NUM_THREADS="1",OMP_NUM_THREADS="1",MKL_NUM_THREADS="1",NUMEXPR_NUM_THREADS="1")
        command=[sys.executable,"-B",str(source/"Pycavi2/tests/test_eso_preflight.py")]
        with log.open("x") as f:
            result=subprocess.run(command,cwd=run,env=env,stdout=f,stderr=subprocess.STDOUT)
        print(log.read_text(),flush=True)
        receipt["exit"]=result.returncode
        require(result.returncode==0,"ESO preflight synthetic controls failed")
        finished=True
    finally:
        # Preservation verification: retain receipts and compare the installation/clean checkout on all exits.
        checks={"installed_files":installed==[guard["identity"](p) for p in paths],"checkout":before==guard["checkout"](repo)}
        receipt["preservation"]=checks;receipt["status"]="passed" if finished and all(checks.values()) else "failed"
        receipt["observational_inputs"]="none opened; synthetic fixtures only"
        with (run/"qualification.json").open("x") as f:json.dump(receipt,f,indent=2);f.write("\n")
        print("QUALIFICATION:",receipt["status"]);print("PRESERVATION:",checks);print("RETAINED EVIDENCE:",run)
        require(all(checks.values()),"Preservation failed")


if __name__=="__main__":main()
