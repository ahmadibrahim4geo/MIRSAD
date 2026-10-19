"""Install/uninstall the candidate only in disposable build space, with a separate QA AppId."""
import argparse
import hashlib
import json
import os
import subprocess
import tempfile
import shutil
import time
from contextlib import contextmanager
from pathlib import Path
from distribution import ROOT


@contextmanager
def qa_directory():
    scratch=Path(tempfile.mkdtemp(prefix="install-qa-",dir=ROOT/".build")).resolve()
    if not scratch.is_relative_to((ROOT/".build").resolve()):raise RuntimeError("Invalid QA cleanup root")
    try:yield scratch
    finally:
        # Inno's uninstaller can leave a short-lived helper after its parent
        # exits. Retry only this verified disposable directory.
        for attempt in range(60):
            try:
                shutil.rmtree(scratch);break
            except FileNotFoundError:break
            except PermissionError:
                if attempt==59:raise
                time.sleep(.25)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--channel",choices=("development","stable"),default="development")
    parser.add_argument("--candidate",action="store_true",help="Compare installed files with verified build scratch")
    args=parser.parse_args()
    if args.candidate and args.channel!="development":parser.error("Build scratch is development-only.")
    setup_dir=ROOT/"runtime/installers"/args.channel
    setup=setup_dir/"MIRSAD-Setup.exe"
    manifest=json.loads((setup_dir/"installer_manifest.json").read_text(encoding="utf-8"))
    if hashlib.sha256(setup.read_bytes()).hexdigest()!=manifest["installer_sha256"]:
        raise SystemExit("Installer changed after compilation.")
    report=ROOT/".test-output/installer_acceptance.json"
    report.parent.mkdir(exist_ok=True)
    with qa_directory() as scratch:
        scratch=Path(scratch).resolve()
        if not scratch.is_relative_to((ROOT/".build").resolve()):raise RuntimeError("Invalid test installation root")
        target=scratch/"app"
        environment=dict(os.environ,TEMP=str(scratch),TMP=str(scratch),MIRSAD_OFFLINE="1")
        subprocess.run([str(setup),"/VERYSILENT","/SUPPRESSMSGBOXES","/NORESTART","/NOICONS","/TASKS=",
                        "/QA=1","/DIR="+str(target),"/LOG="+str(report.with_suffix(".install.log"))],
                       check=True,timeout=180,env=environment)
        try:
            source=ROOT/".build/dist/MIRSAD" if args.candidate else ROOT/"runtime"/args.channel
            for path in source.rglob("*"):
                if path.is_file():
                    installed=target/path.relative_to(source)
                    if not installed.is_file() or hashlib.sha256(path.read_bytes()).digest()!=hashlib.sha256(installed.read_bytes()).digest():
                        raise RuntimeError("Installed payload mismatch: "+str(path.relative_to(source)))
            subprocess.run([str(target/"MIRSAD.exe"),"--ui-workspace-test",str(report.with_name("installed_workspace.json"))],
                           check=True,cwd=Path.home(),timeout=150,env=environment)
            workspace=json.loads(report.with_name("installed_workspace.json").read_text(encoding="utf-8"))
            if not workspace["passed"]:raise RuntimeError("Installed workspace acceptance failed")
            unknown=target/"user-note.txt";unknown.write_text("Keep user-created files",encoding="utf-8")
            project=scratch/"User project";project.mkdir();(project/"observations.txt").write_text("Keep project",encoding="utf-8")
        finally:
            uninstaller=next(target.glob("unins*.exe"))
            subprocess.run([str(uninstaller),"/VERYSILENT","/SUPPRESSMSGBOXES","/NORESTART",
                            "/LOG="+str(report.with_suffix(".uninstall.log"))],check=True,timeout=90,env=environment)
        if (target/"MIRSAD.exe").exists():raise RuntimeError("Uninstall left the installed application")
        if not unknown.is_file() or not (project/"observations.txt").is_file():raise RuntimeError("Uninstall removed user data")
        result=dict(passed=True,installer_sha256=manifest["installer_sha256"],payload_readback="passed",
                    installed_workspace="passed",uninstall="passed",user_files_preserved=True,
                    qa_app_id="MIRSAD.Desktop.InstallationQA",production_installation_changed=False)
        report.write_text(json.dumps(result,indent=2),encoding="utf-8")
        manifest["installation_acceptance_passed"]=True
        (setup_dir/"installer_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
        print(report)


if __name__=="__main__":main()
