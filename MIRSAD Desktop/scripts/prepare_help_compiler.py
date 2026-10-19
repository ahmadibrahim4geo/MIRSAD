"""Prepare Microsoft's signed HTML Help Workshop compiler locally, without install.

The original Microsoft download is no longer available. EC Software (Help+Manual)
hosts the unchanged Microsoft installer. Pin its hash, validate Authenticode,
extract the cabinet, and use registration-free COM for the build-time indexer.
Nothing is copied into Windows or registered globally. The compiler is not shipped.
"""
import argparse,hashlib,json,os,shutil,struct,subprocess,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
URL='https://www.helpandmanual.com/download/htmlhelp.exe'
INSTALLER_SHA='cf8fe5a02d3c2bf0c8728dd399dc3b2587c4139ffb23ef4268f34535a6157b87'
COMPILER_SHA='3e96894609819ae3d595ff6e0fbe9ce6c9ac17bdeda256b994831992f668cb99'
# CLSID and ProgID pairs from this pinned itcc.dll's ATL class map. Both names
# are needed: CLSID-only activation compiles pages but silently omits full text.
CLASSES=(('4662daa2-d393-11d0-9a56-00c04fb68bf7','CmdInt'),
 ('4662daa3-d393-11d0-9a56-00c04fb68bf7','SvMgr'),
 ('4662daa4-d393-11d0-9a56-00c04fb68bf7','GroupBuild'),
 ('8fa0d5aa-dedf-11d0-9a61-00c04fb68bf7','FTIBuild'),
 ('8fa0d5ab-dedf-11d0-9a61-00c04fb68bf7','WWFilterBuild'),
 ('8fa0d5a9-dedf-11d0-9a61-00c04fb68bf7','SystemWordSink'))


def prepare(download=False,powershell=None):
    folder=ROOT/'.build/tools/htmlhelp';folder.mkdir(parents=True,exist_ok=True)
    installer=folder/'htmlhelp.exe'
    if not installer.exists():
        if not download:raise RuntimeError('Run prepare_help_compiler.py --download once to obtain the build-time compiler.')
        with urllib.request.urlopen(URL,timeout=60) as response:
            content=response.read(10_000_001)
        if len(content)>10_000_000:raise RuntimeError('Unexpected compiler download size')
        if hashlib.sha256(content).hexdigest()!=INSTALLER_SHA:raise RuntimeError('Compiler installer hash differs; review the upstream file before changing the pin.')
        installer.write_bytes(content)
    content=installer.read_bytes()
    if hashlib.sha256(content).hexdigest()!=INSTALLER_SHA:raise RuntimeError('Compiler installer hash mismatch')
    literal=str(installer).replace("'","''")
    command="$ErrorActionPreference='Stop'; $s=Get-AuthenticodeSignature -LiteralPath '"+literal+"'; [pscustomobject]@{status=[string]$s.Status;subject=$s.SignerCertificate.Subject}|ConvertTo-Json -Compress"
    powershell7=Path(os.environ.get('ProgramFiles','C:/Program Files'))/'PowerShell/7/pwsh.exe'
    runner=str(powershell) if powershell else (str(powershell7) if powershell7.is_file() else (shutil.which('pwsh.exe') or str(Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe')))
    child_env=dict(os.environ);child_env.pop('PSModulePath',None)
    result=subprocess.run([runner,'-NoProfile','-NonInteractive','-Command',command],capture_output=True,text=True,check=True,env=child_env)
    signature=json.loads(result.stdout)
    if signature['status']!='Valid' or 'Microsoft' not in signature['subject']:raise RuntimeError('Microsoft installer signature is not valid')
    cabinet=None
    for offset in range(len(content)-36):
        if content[offset:offset+4]!=b'MSCF':continue
        size=struct.unpack_from('<I',content,offset+8)[0]
        if size>1_000_000 and offset+size<=len(content):cabinet=content[offset:offset+size];break
    if cabinet is None:raise RuntimeError('Installer cabinet not found')
    cab=folder/'workshop.cab';cab.write_bytes(cabinet)
    extracted=folder/'extracted';extracted.mkdir(exist_ok=True)
    subprocess.run([str(Path(os.environ['SystemRoot'])/'System32/expand.exe'),'-F:*',str(cab),str(extracted)],capture_output=True,check=True)
    compiler=extracted/'mirsad-help-compiler.exe'
    if hashlib.sha256((extracted/'hhc.exe').read_bytes()).hexdigest()!=COMPILER_SHA:raise RuntimeError('Compiler binary hash mismatch')
    manifest='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0"><assemblyIdentity name="MIRSAD.Local.HelpCompiler" version="1.0.0.0" type="win32" processorArchitecture="x86"/><file name="itcc.dll">'
    manifest+=''.join('<comClass clsid="{'+guid+'}" threadingModel="Both" progid="ITIR.'+name+'"><progid>ITIR.'+name+'.4</progid></comClass>' for guid,name in CLASSES)
    manifest+='</file></assembly>'
    # Write before first launch: Windows caches executable activation contexts.
    compiler.with_suffix('.exe.manifest').write_text(manifest,encoding='utf-8')
    shutil.copy2(extracted/'hhc.exe',compiler)
    report=dict(url=URL,installer_sha256=INSTALLER_SHA,signature=signature,compiler_sha256=COMPILER_SHA,
        manifest_sha256=hashlib.sha256(manifest.encode()).hexdigest(),installation='local extraction; no global COM registration')
    (folder/'download.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(compiler)
    return compiler


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--download',action='store_true');parser.add_argument('--powershell',type=Path)
    args=parser.parse_args();prepare(args.download,args.powershell)
