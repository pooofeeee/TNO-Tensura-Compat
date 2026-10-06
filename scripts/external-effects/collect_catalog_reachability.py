"""Exact symbolic callers for the integrity audit's suspicious boundaries only.

This is a byte-string prefilter and classfile cross-reference check, not a
discovery/semantic scan. Constructor method references and direct subclasses
are included: invocation-only absence is insufficient for registered entities.
"""
import argparse
import hashlib
import zipfile

from catalog_common import OUT, read_json, write_json
from classfile import ClassFile, Reader
from collect_cataclysm_ignited_revenant_offense import instructions

QUERIES = [
    ('entity/AnimationMonster/The_Watcher_Entity', '<init>'),
    ('entity/effect/Bolt_strike_Entity', '<init>'),
    ('entity/projectile/AbstractElemental_Spear', '<init>'),
    ('entity/AI/AnimalSwimMoveControllerSink', '<init>'),
    ('entity/AnimationMonster/AI/PredictiveChargeAttackAnimationGoal', '<init>'),
    ('items/The_Immolator', 'yall'),
    ('entity/InternalAnimationMonster/IABossMonsters/Scylla/Scylla_Entity', 'Whip'),
    ('entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Entity', 'chargeDamage'),
    ('message/MessageCharge', '<init>'),
    ('message/MessageMovePlayer', '<init>'),
]


def collect(jar_path):
    target = next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='cataclysm')
    with open(jar_path, 'rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    assert digest == target['sha256']
    queries = [('com/github/L_Ender/cataclysm/'+entry, name) for entry,name in QUERIES]
    calls, handles, subclasses = [], [], []
    def matches(value):
        return any(str(value).startswith(entry+'.'+name+'(') for entry,name in queries)
    with zipfile.ZipFile(jar_path) as jar:
        for entry in sorted(jar.namelist()):
            if not entry.endswith('.class'):
                continue
            raw = jar.read(entry)
            if not any(owner.encode() in raw for owner,name in queries):
                continue
            cls = ClassFile(raw)
            entry_hash = hashlib.sha256(raw).hexdigest()
            if cls.super in {owner for owner,name in queries}:
                subclasses.append(dict(entry=entry, superclass=cls.super, entry_sha256=entry_hash))
            for attribute,data in cls.attributes:
                if attribute!='BootstrapMethods':
                    continue
                reader=Reader(data)
                bootstraps=[(reader.u2(), [reader.u2() for _ in range(reader.u2())])
                            for _ in range(reader.u2())]
                for index,(handle,args) in enumerate(bootstraps):
                    resolved=[cls.resolve(arg) for arg in args]
                    if any(matches(arg) for arg in resolved):
                        handles.append(dict(entry=entry, entry_sha256=entry_hash,
                            bootstrap_index=index, arguments=resolved))
            for method in cls.methods:
                code=method.get('code',b'')
                hits=[i for i in instructions(cls,code) if i['opcode'] in
                    ['0xb6','0xb7','0xb8','0xb9','0xba'] and matches(i['operand'])]
                if hits:
                    calls.append(dict(entry=entry, entry_sha256=entry_hash,
                        method=method['name'], descriptor=method['descriptor'],
                        code_sha256=hashlib.sha256(code).hexdigest(), invocations=hits))
    return dict(schema='tno.external_effects.targeted_reachability.v1', jar_sha256=digest,
        queries=[dict(entry=e, method=n) for e,n in queries], direct_callers=calls,
        method_reference_bootstraps=handles, direct_subclasses=subclasses,
        limitations='Exact installed symbolic invocation, bootstrap and subclass references only. '
            'No claim about external/reflective/command callers. Registered entity factories '
            'remain reachable even without an ordinary native attack producer.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jar');parser.add_argument('output')
    args=parser.parse_args();result=collect(args.jar);write_json(args.output,result)
    print(f'{len(result["queries"])} exact queries; {len(result["direct_callers"])} caller methods; '
          f'{len(result["method_reference_bootstraps"])} method references')
