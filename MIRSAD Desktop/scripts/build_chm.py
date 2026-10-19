"""Compile real Windows HTML Help from the same bundled topic registry.

Compiler is a build-time tool only; no registry/DLL registration is performed.
"""
import argparse,hashlib,html,json,re,shutil,subprocess,os,contextlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

@contextlib.contextmanager
def compiler_workspace():
    # hhc strips a leading-dot path component from its project base directory.
    # A temporary DOS alias points at the SAME .build/chm directory; no source,
    # registry, permanent installation or additional runtime copy is created.
    folder=ROOT/'.build/chm';folder.mkdir(parents=True,exist_ok=True)
    drive=next((letter+':' for letter in 'ZYXWVUTSRQP' if not Path(letter+':/').exists()),None)
    if not drive:raise RuntimeError('No free temporary compiler drive alias')
    subst=str(Path(os.environ['SystemRoot'])/'System32/subst.exe')
    subprocess.run([subst,drive,str(folder)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
    try:yield Path(drive+'/')
    finally:subprocess.run([subst,drive,'/D'],check=True,creationflags=subprocess.CREATE_NO_WINDOW)

def build(compiler,workspace):
    data=json.loads((ROOT/'assets/help_index.json').read_text(encoding='utf-8'))
    reports=[]
    for lang in ('en','ar'):
        folder=ROOT/'.build/chm'/lang;folder.mkdir(parents=True,exist_ok=True)
        title='مساعدة مرصاد' if lang=='ar' else 'MIRSAD Help'
        codepage='cp1256' if lang=='ar' else 'cp1252'
        charset='windows-1256' if lang=='ar' else 'windows-1252'
        topic_ids={topic['id'] for topic in data['sections']}
        page_names=[]
        for topic in data['sections']:
            name=topic['id']+'.html';page_names.append(name)
            body=re.sub(r'href="#([a-z0-9_-]+)"',lambda m:'href="'+m[1]+'.html"' if m[1] in topic_ids else m[0],topic[lang+'_body'])
            page='<!doctype html><html lang="'+lang+'" dir="'+('rtl' if lang=='ar' else 'ltr')+'"><head><meta http-equiv="Content-Type" content="text/html; charset='+charset+'"><title>'+html.escape(topic[lang])+'</title><style>body{font-family:Segoe UI,Tahoma,Arial;font-size:11pt;margin:24px;line-height:1.6;color:#171717;background:#fff}table{border-collapse:collapse;width:100%}td,th{border:1px solid #aaa;padding:8px;text-align:inherit}a{color:#086770}h1{font-size:23pt}code{font-family:Consolas,monospace;direction:ltr;unicode-bidi:embed}</style></head><body><h1>'+html.escape(topic[lang])+'</h1>'+body+'<hr><p>MIRSAD '+data['version']+' · Ahmad Ibrahim</p></body></html>'
            # HTML Help's legacy indexer requires its language codepage. Numeric
            # references preserve symbols outside that codepage without data loss.
            (folder/name).write_bytes(page.encode(codepage,'xmlcharrefreplace'))
        def entry(label,local=None):
            return '<li><object type="text/sitemap"><param name="Name" value="'+html.escape(label,quote=True)+'">'+('<param name="Local" value="'+local+'">' if local else '')+'</object>'
        toc=['<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN"><html><head><meta http-equiv="Content-Type" content="text/html; charset=windows-'+('1256' if lang=='ar' else '1252')+'"></head><body><ul>']
        for group in data['groups']:
            toc.append(entry(group[lang])+'<ul>')
            toc.extend(entry(topic[lang],topic['id']+'.html') for topic in data['sections'] if topic['group']==group['id'])
            toc.append('</ul>')
        toc.append('</ul></body></html>')
        codepage='cp1256' if lang=='ar' else 'cp1252'
        (folder/'contents.hhc').write_bytes(''.join(toc).encode(codepage,'xmlcharrefreplace'))
        keyword='<html><body><ul>'+''.join(entry(t[lang],t['id']+'.html') for t in data['sections'])+'</ul></body></html>'
        (folder/'index.hhk').write_bytes(keyword.encode(codepage,'xmlcharrefreplace'))
        name='MIRSAD_Help_'+lang.upper()+'.chm'
        target=ROOT.parent/'Help'/name
        project='[OPTIONS]\nCompatibility=1.1 or later\nCompiled file='+str(target)+'\nContents file=contents.hhc\nIndex file=index.hhk\nDefault topic=start.html\nDisplay compile progress=No\nFull-text search=Yes\nLanguage='+('0xc01 Arabic (Saudi Arabia)' if lang=='ar' else '0x409 English (United States)')+'\nTitle='+title+'\nDefault Window=main\n\n[WINDOWS]\nmain="'+title+'","contents.hhc","index.hhk","start.html","start.html",,,,,0x63520,300,0x104e,[50,50,1200,850],0x0,,1,,,0\n\n[FILES]\n'+'\n'.join(page_names)+'\n'
        (folder/'help.hhp').write_bytes(project.encode(codepage,'xmlcharrefreplace'))
        target.unlink(missing_ok=True)
        alias=workspace/lang
        process=subprocess.run([str(compiler.resolve()),str(alias/'help.hhp')],cwd=alias,capture_output=True,timeout=120,
            creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        (folder/'compile.log').write_bytes(process.stdout+process.stderr)
        # Microsoft's hhc returns 1 on successful compilation. Verify the actual
        # product, not a conventional zero-exit assumption.
        if not target.is_file() or target.stat().st_size<20000 or target.read_bytes()[:4]!=b'ITSF' or b'Error:' in process.stdout:raise RuntimeError('CHM compilation failed: '+str(folder/'compile.log'))
        if b'/$FIftiMain' not in target.read_bytes():raise RuntimeError('CHM full-text index was not created: '+str(folder/'compile.log'))
        embedded=ROOT/'assets'/name;shutil.copy2(target,embedded)
        reports.append(dict(language=lang,topics=len(page_names),bytes=target.stat().st_size,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),compiler_exit=process.returncode,full_text_index=True))
    report=dict(version=data['version'],compiler_sha256=hashlib.sha256(compiler.read_bytes()).hexdigest(),outputs=reports)
    (ROOT.parent/'Help/chm_manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--compiler',type=Path,default=ROOT/'.build/tools/htmlhelp/extracted/mirsad-help-compiler.exe')
    args=parser.parse_args()
    with compiler_workspace() as workspace:build(args.compiler,workspace)
