"""Reproducible direct vanilla factory-call census for Lich shield sources."""
from vanilla_reference import *

def audit():
    names=MojangNames();owner=names.named['net/minecraft/world/damagesource/DamageSources'];rows=[]
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for entry in jar.namelist():
            if not entry.endswith('.class'):continue
            data=jar.read(entry)
            if owner.encode() not in data:continue
            cls=ClassFile(data);targets=set()
            for i,cp in enumerate(cls.cp):
                if cp and cp[0] in (10,11):
                    value=names.readable_cp(cls,i)
                    if any(value.startswith('net/minecraft/world/damagesource/DamageSources.'+s+'(') for s in ['magic','indirectMagic','sonicBoom']):targets.add(value)
            if not targets:continue
            for method in cls.methods:
                hits=[i for i in names.instructions(cls,method.get('code',b'')) if i.get('operand') in targets]
                if hits:rows.append(dict(class_name=names.obfuscated.get(cls.name,cls.name),method=names.member(cls.name,method['name'],method['descriptor']),code_sha256=byte_hash(method.get('code',b'')),calls=hits))
    return dict(schema='tno.external_effects.source_audit.v1',baseline=BASELINE,client_jar_sha256=sha256(CLIENT),factory_names=['magic','indirectMagic','sonicBoom'],callers=rows,scope='Raw Minecraft1.21.1 direct factory calls; installed loader replacements and native delivery predicates reviewed separately. Does not assert every modpack/datapack-generated source.')

if __name__=='__main__':
    result=audit();write_json(OUT/'lich-vanilla-source-audit.json',result);print(len(result['callers']))
