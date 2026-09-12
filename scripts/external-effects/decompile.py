"""Prepare ignored source aids from the pinned JARs; bytecode remains authoritative."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
from catalog_common import *

JAVA=Path('C:/Program Files/Java/jdk-21/bin/java.exe')
VINE=Path('C:/Users/youra/.gradle/caches/modules-2/files-2.1/org.vineflower/vineflower/1.10.1/4f48c5947b21f9ebc743e7c80215ee839d3dc668/vineflower-1.10.1.jar')

def decompile(target):
    folder=WORK/target['key']; dest=folder/'source'; dest.mkdir(parents=True,exist_ok=True)
    reportpath=folder/'decompile.json'
    if reportpath.exists():
        old=read_json(reportpath)
        if old['jar_sha256']==target['sha256'] and old['exit_code']==0:
            print('Reuse decompile: '+target['key'],flush=True);return old
        raise RuntimeError('Preserve interrupted decompilation before retry: '+str(folder))
    command=[str(JAVA),'-Xmx2G','-jar',str(VINE),'--folder','--skip-extra-files=true',
        '--thread-count=2','--log-level=warn','--remove-synthetic=false',target['path'],str(dest)]
    with (folder/'decompile.log').open('w',encoding='utf-8') as log:
        result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=1200)
    javafiles=list(dest.rglob('*.java'))
    report=dict(mod_key=target['key'],jar_sha256=target['sha256'],decompiler_sha256=sha256(VINE),
        command=command,exit_code=result.returncode,java_files=len(javafiles),
        log_sha256=sha256(folder/'decompile.log'),source_status='READING_AID_ONLY',
        warning='A successful process is not proof every method decompiled. Inspect error markers and verify relevant bytecode.')
    write_json(reportpath,report)
    print(f'Decompile {target["key"]}: exit {result.returncode}, {len(javafiles)} Java files',flush=True)
    return report

if __name__=='__main__':
    inv=read_json(OUT/'jar-inventory.json')
    targets=[t for t in inv['targets']+inv['compat_candidates'] if t['status']!='UNAVAILABLE' and t['role']!='BASE_TENSURA_REFERENCE']
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures=[pool.submit(decompile,t) for t in targets]
        results=[f.result() for f in as_completed(futures)]
    write_json(OUT/'decompilation-provenance.json',dict(schema='tno.external_effects.decompilation.v1',
        status='SOURCE_AIDS_PREPARED',baseline=BASELINE,results=sorted(results,key=lambda r:r['mod_key'])))
