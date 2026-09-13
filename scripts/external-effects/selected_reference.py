"""Pin and optionally decompile selected exact installed/reference classes, never run them."""
import argparse
import subprocess
from catalog_common import *
from classfile import ClassFile
from decompile import JAVA,VINE

def collect(spec,source_aids=False):
    result=[]
    for archive in spec['archives']:
        assert sha256(archive['path'])==archive['sha256']
        with zipfile.ZipFile(archive['path']) as jar:
            for entry,wanted in archive.get('classes',{}).items():
                data=jar.read(entry);cls=ClassFile(data)
                methods=[m for m in cls.methods if m['name'] in wanted or wanted==['*']]
                assert wanted==['*'] or set(wanted)<={m['name'] for m in methods},entry
                result.append(dict(archive_sha256=archive['sha256'],entry=entry,entry_sha256=byte_hash(data),
                    class_name=cls.name,superclass=cls.super,interfaces=cls.interfaces,
                    methods=[dict(name=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),
                        code_hex=m.get('code',b'').hex(),instructions=list(cls.instructions(m.get('code',b'')))) for m in methods]))
                if source_aids:
                    folder=WORK/'selected-reference'/spec['id']; file=folder/'classes'/entry
                    source_file=folder/'source'/(cls.name.split('/')[-1]+'.java')
                    if file.exists() and file.read_bytes()==data and source_file.exists():continue
                    file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(data)
                    dest=folder/'source';dest.mkdir(parents=True,exist_ok=True)
                    with (folder/(cls.name.replace('/','_')+'.log')).open('w',encoding='utf-8') as log:
                        subprocess.run([str(JAVA),'-Xmx2G','-jar',str(VINE),'--folder','--log-level=warn','--thread-count=1',str(file),str(dest)],stdout=log,stderr=subprocess.STDOUT,check=True)
            for entry in archive.get('resources',[]):
                data=jar.read(entry)
                row=dict(archive_sha256=archive['sha256'],entry=entry,entry_sha256=byte_hash(data))
                if entry.endswith('.json'):row['data']=json.loads(data)
                else:row['text']=data.decode('utf-8')
                result.append(row)
    return dict(schema='tno.external_effects.selected_reference.v1',id=spec['id'],baseline=BASELINE,
        scope=spec['scope'],status='STATIC_EVIDENCE',witnesses=result)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('--source-aids',action='store_true');a=p.parse_args()
    spec=read_json(OUT/'reference-specifications'/f'{a.name}.json')
    result=collect(spec,a.source_aids);write_json(OUT/'reference-evidence'/f'{a.name}.json',result)
    print(f'{a.name}: {len(result["witnesses"])} witnesses pinned')
