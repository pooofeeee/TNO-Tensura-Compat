"""Read exact cached vanilla 1.21.1 classes, naming bytecode through Mojang mappings."""
import re
from classfile import ClassFile
from catalog_common import *

CACHE=Path('C:/Users/youra/.gradle/caches/neoformruntime/artifacts')
CLIENT=CACHE/'minecraft_1.21.1_client.jar'
MAPPING=CACHE/'minecraft_1.21.1_client_mappings.txt'
MANIFEST=CACHE/'minecraft_1.21.1_version_manifest.json'
PRIMITIVES={'void':'V','boolean':'Z','byte':'B','short':'S','char':'C','int':'I','float':'F','long':'J','double':'D'}

class MojangNames:
    def __init__(self):
        self.named={};self.obfuscated={};self.members={};lines=[];current=None
        for line in MAPPING.read_text(encoding='utf-8').splitlines():
            if not line or line.startswith('#'):continue
            if not line.startswith(' '):
                named,obfuscated=line[:-1].split(' -> ')
                named=named.replace('.','/');self.named[named]=obfuscated;self.obfuscated[obfuscated]=named;current=obfuscated
            else:lines.append((current,line.strip()))
        for owner,line in lines:
            left,name=line.rsplit(' -> ',1)
            left=re.sub(r'^\d+:\d+:','',left)
            if '(' in left:
                match=re.match(r'(.+?) ([^ ]+)\((.*?)\)',left)
                if not match:continue
                ret,named,args=match.groups()
                desc='('+''.join(self.descriptor(t) for t in args.split(',') if t)+')'+self.descriptor(ret)
            else:
                typ,named=left.split(' ',1);desc=self.descriptor(typ)
            self.members[(owner,name,desc)]=named
        self.supers={}

    def descriptor(self,typ):
        if typ.endswith('[]'):return '['+self.descriptor(typ[:-2])
        if typ in PRIMITIVES:return PRIMITIVES[typ]
        path=typ.replace('.','/')
        return 'L'+self.named.get(path,path)+';'

    def member(self,owner,name,desc):
        current=owner;seen=set()
        while current and current not in seen:
            seen.add(current)
            if (current,name,desc) in self.members:return self.members[(current,name,desc)]
            if current not in self.supers:
                try:self.supers[current]=ClassFile(self.jar.read(current+'.class')).super
                except KeyError:self.supers[current]=None
            current=self.supers[current]
        return name

    def readable_cp(self,cls,index):
        tag,value=cls.cp[index]
        if tag in (9,10,11):
            owner=cls.resolve(value[0]); _,nt=cls.cp[value[1]]
            name=cls.resolve(nt[0]);desc=cls.resolve(nt[1])
            mapped=self.member(owner,name,desc)
            named_desc=re.sub(r'L([^;]+);',lambda m:'L'+self.obfuscated.get(m[1],m[1])+';',desc)
            return self.obfuscated.get(owner,owner)+'.'+mapped+named_desc
        if tag==7:return self.obfuscated.get(cls.resolve(index),cls.resolve(index))
        return cls.resolve(index)

    def instructions(self,cls,code):
        result=[]
        for instruction in cls.instructions(code):
            op=int(instruction['opcode'],16);p=instruction['offset']+1;index=None
            if op==0x12:index=code[p]
            elif op in (0x13,0x14,0xbb,0xbd,0xc0,0xc1,0xc5) or 0xb2<=op<=0xba:index=int.from_bytes(code[p:p+2],'big')
            if index:instruction['operand']=self.readable_cp(cls,index)
            result.append(instruction)
        return result

def prepare(spec):
    manifest=read_json(MANIFEST);assert manifest['id']=='1.21.1'
    for key,path in [('client',CLIENT),('client_mappings',MAPPING)]:
        with path.open('rb') as stream:actual=hashlib.file_digest(stream,'sha1').hexdigest()
        assert actual==manifest['downloads'][key]['sha1'], path
    names=MojangNames();records=[];resources=[]
    inv=read_json(OUT/'jar-inventory.json')
    sources=next(x for x in inv['vanilla_reference_artifacts'] if x['path'].endswith('-sources.jar'))
    assert sha256(sources['path'])==sources['sha256']
    with zipfile.ZipFile(CLIENT) as jar,zipfile.ZipFile(sources['path']) as aid:
        names.jar=jar
        for named,wanted in spec['classes'].items():
            entry=names.named[named]+'.class';data=jar.read(entry);cls=ClassFile(data)
            methods=[]
            for m in cls.methods:
                mapped=names.member(cls.name,m['name'],m['descriptor'])
                if mapped in wanted:
                    methods.append(dict(name=mapped,obfuscated_name=m['name'],obfuscated_descriptor=m['descriptor'],
                        code_sha256=byte_hash(m.get('code',b'')),code_hex=m.get('code',b'').hex(),
                        instructions=names.instructions(cls,m.get('code',b''))))
            assert set(wanted)<={m['name'] for m in methods}, (named,wanted)
            source_entry=named+'.java';source_data=aid.read(source_entry)
            destination=WORK/'vanilla-mapped-source'/source_entry;destination.parent.mkdir(parents=True,exist_ok=True)
            destination.write_bytes(source_data)
            records.append(dict(class_name=named,raw_entry=entry,raw_class_sha256=byte_hash(data),methods=methods,
                                mapped_source_entry=source_entry,mapped_source_sha256=byte_hash(source_data)))
        for entry in spec.get('resources',[]):
            data=jar.read(entry);resources.append(dict(entry=entry,sha256=byte_hash(data),data=json.loads(data)))
        for entry in spec.get('absent_resources',[]):
            assert entry not in jar.namelist(), 'Expected resource absence changed: '+entry
            resources.append(dict(entry=entry,present=False))
    return dict(schema='tno.external_effects.vanilla_witness.v1',baseline=BASELINE,status='RAW_VANILLA_BYTECODE_PINNED',
        version='1.21.1',client_jar_sha256=sha256(CLIENT),mappings_sha256=sha256(MAPPING),manifest_sha256=sha256(MANIFEST),
        cached_manifest_sha1_checks_passed=True,mapped_source_jar=sources,classes=records,resources=resources,
        resolution_hierarchy={names.obfuscated.get(k,k):names.obfuscated.get(v,v) for k,v in sorted(names.supers.items())},
        note='Raw vanilla bytecode is authoritative. Mapped NeoForge source is a reading aid; loader additions must be distinguished explicitly. No Minecraft process is started.')

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('name');args=parser.parse_args()
    spec=read_json(OUT/'vanilla-specifications'/f'{args.name}.json')
    result=prepare(spec);write_json(OUT/'vanilla-evidence'/f'{args.name}.json',result)
    print(f'{len(result["classes"])} raw vanilla classes, {sum(len(r["methods"]) for r in result["classes"])} selected method witnesses')
