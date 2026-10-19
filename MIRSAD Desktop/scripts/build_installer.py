"""Build one installer from a verified fixed channel; never promote implicitly."""
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from distribution import ROOT, bundle_hash


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--channel",choices=("development","stable"),default="development")
    parser.add_argument("--candidate",action="store_true",help="Package the verified build scratch while development is open")
    parser.add_argument("--compiler",type=Path,default=ROOT/".build/tools/inno/ISCC.exe")
    args=parser.parse_args()
    if args.candidate and args.channel!="development":parser.error("Build scratch is development-only.")
    source=ROOT/".build/dist/MIRSAD" if args.candidate else ROOT/"runtime"/args.channel
    manifest=json.loads((source/"build_manifest.json").read_text(encoding="utf-8"))
    digest=bundle_hash(source)
    if manifest.get("bundle_sha256")!=digest or not manifest.get("gui_smoke_passed") or not manifest.get("ui_worker_export_passed"):
        raise SystemExit("Installer requires an unchanged, tested application bundle.")
    if args.channel=="stable" and not (source/"release.json").exists():
        raise SystemExit("Stable has no explicitly approved release.")
    output=ROOT/"runtime/installers"/args.channel
    output.mkdir(parents=True,exist_ok=True)
    scratch=ROOT/".build/installer-temp";scratch.mkdir(parents=True,exist_ok=True)
    subprocess.run([str(args.compiler.resolve()),"/Qp","/DSourceDir="+str(source),
                    "/DOutputDir="+str(output),"/DProductVersion="+manifest["version"],
                    str(ROOT/"scripts/installer.iss")],check=True,
                   env=dict(os.environ,TEMP=str(scratch),TMP=str(scratch)))
    setup=output/"MIRSAD-Setup.exe"
    (output/"installer_manifest.json").write_text(json.dumps(dict(version=manifest["version"],
        channel=args.channel,bundle_sha256=digest,installer_sha256=hashlib.sha256(setup.read_bytes()).hexdigest(),
        approved=args.channel=="stable",signed=False),indent=2),encoding="utf-8")
    print(setup)


if __name__=="__main__":main()
