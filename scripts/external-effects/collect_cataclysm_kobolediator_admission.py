"""Capture only R2k14a Kobolediator admission/state/encounter witnesses.

Reuse parent/native admission, raw-state, effect exclusions, shared state goals,
config-attribute helper and attribute registration without recapture.
"""
import argparse
import hashlib
from pathlib import Path
import zipfile

from catalog_common import BASELINE, OUT, read_json, write_json
from classfile import ClassFile, Reader
from collect_cataclysm_ignited_revenant_offense import instructions

PKG='com/github/L_Ender/cataclysm/'
K='entity/InternalAnimationMonster/Kobolediator_Entity'
D=K+'$KobolediatorDoNothingGoal'
A='entity/etc/Animation_Monsters'
REGISTRY='init/ModEntities'
PYRAMID='structures/Cursed_Pyramid_Structure$Piece'
SPEC_FILE=OUT/'native-specifications/cataclysm-kobolediator-admission.json'
EVIDENCE_FILE=OUT/'native-evidence/cataclysm-kobolediator-admission.json'
METHODS={
    K:['kobolediator','canBlockDamageSource','decreaseAirSupply','defineSynchedData',
       'setAwaken','getAwaken','isSleep','setSleep','canBeSeenAsEnemy','finalizeSpawn',
       'die','deathtimer','addAdditionalSaveData','readAdditionalSaveData',
       'removeWhenFarAway','shouldDespawnInPeaceful','canRide','<clinit>'],
    D:['<init>','canUse','tick','stop','isInterruptable','requiresUpdateEveryTick'],
    A:['canBePushedByEntity'],
    REGISTRY:[],
    PYRAMID:[],
}
FRAGMENTS={
    K:{'<init>':[[0,3],[116,123],[132,160]],'hurt':[[0,86],[98,125]],'registerGoals':[[272,335]]},
    REGISTRY:{'lambda$static$81':[[0,17],[25,31]],'<clinit>':[[1389,1403]]},
    PYRAMID:{'handleDataMarker':[[132,145],[458,553]]},
}


def specification():
    return dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,
        evidence_specifications=[dict(id='cataclysm:kobolediator-admission:'+n,mod_key='cataclysm',
            entry=PKG+n+'.class',methods=methods,method_fragments=FRAGMENTS.get(n,{}))
            for n,methods in sorted(METHODS.items())])


def collect(jar_path):
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='cataclysm')
    jar_path=Path(jar_path)
    with jar_path.open('rb') as stream:
        assert hashlib.file_digest(stream,'sha256').hexdigest()==target['sha256']
    assert jar_path.stat().st_size==target['size_bytes']
    witnesses=[]
    with zipfile.ZipFile(jar_path) as jar:
        for spec in specification()['evidence_specifications']:
            raw=jar.read(spec['entry']);c=ClassFile(raw)
            row=dict(id=spec['id'],mod_key='cataclysm',jar_sha256=target['sha256'],entry=spec['entry'],
                entry_sha256=hashlib.sha256(raw).hexdigest(),class_name=c.name,superclass=c.super,interfaces=c.interfaces,methods=[])
            if spec['entry']==PKG+K+'.class':
                row['declared_method_names']=sorted({m['name'] for m in c.methods})
                row['declared_fields']=[dict(name=f['name'],descriptor=f['descriptor']) for f in c.fields]
                ctor=next(m for m in c.methods if m['name']=='<init>')
                row['constructor_nonvisual_invocations']=[i['operand'] for i in instructions(c,ctor['code'])
                    if i['opcode'] in {'0xb6','0xb7','0xb8','0xb9'} and not str(i['operand']).startswith('net/minecraft/world/entity/AnimationState.')]
            for name in spec['methods']+list(spec['method_fragments']):
                matches=[m for m in c.methods if m['name']==name]
                assert matches,(spec['entry'],name)
                for m in matches:
                    code=m.get('code',b'');ins=instructions(c,code);ranges=spec['method_fragments'].get(name)
                    if ranges:
                        ins=[i for i in ins if any(a<=i['offset']<=b for a,b in ranges)]
                        assert all(any(i['offset']==v for i in ins) for span in ranges for v in span)
                    row['methods'].append(dict(name=name,descriptor=m['descriptor'],code_sha256=hashlib.sha256(code).hexdigest(),
                        instructions=ins,**({'instruction_offset_ranges':ranges} if ranges else {})))
            if spec['entry']==PKG+REGISTRY+'.class':
                r=Reader(next(data for name,data in c.attributes if name=='BootstrapMethods'))
                bs=[(r.u2(),[r.u2() for _ in range(r.u2())]) for _ in range(r.u2())]
                indices=sorted({int(i['operand'].split('#')[1].split(':')[0]) for m in row['methods'] for i in m['instructions'] if i['opcode']=='0xba'})
                row['registration_bootstraps']=[dict(index=i,handle=c.resolve(bs[i][0]),arguments=[c.resolve(a) for a in bs[i][1]]) for i in indices]
                placement=next(m for m in c.methods if m['name']=='registerSpawnPlacements')
                row['kobolediator_spawn_placement_bindings']=[i['offset'] for i in instructions(c,placement['code']) if '.KOBOLEDIATORL' in str(i['operand'])]
                factory=next(m for m in c.methods if m['name']=='lambda$static$81')
                row['factory_invocations']=[i['operand'] for i in instructions(c,factory['code']) if i['opcode'] in {'0xb6','0xb7','0xb8','0xb9'}]
            witnesses.append(row)
    return dict(schema='tno.external_effects.native_evidence.v1',baseline=BASELINE,status='STATIC_EVIDENCE',witnesses=witnesses,
        note='Five exact entries: Kobolediator admission/raw state/awaken-heal/NBT/finalize and native lifecycle; '
             'its dormant prerequisite goal; exact factory/ID binding; only its Cursed Pyramid marker branch. '
             'One previously uncaptured Animation_Monsters canBePushedByEntity binding closes inherited collision admission. '
             'Sounds, visual constructors/state methods, utility/offensive goals, tick/aiStep/attacks/terrain/payloads excluded. '
             'Shared parents/goals/native healing/effect exclusions/config helper/attribute binding and protected Remnant marker '
             'evidence reused without recapture. No recursive scan, runtime or Stage decisions.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jar',type=Path,help='Exact pinned Cataclysm 3.27 JAR')
    evidence=collect(parser.parse_args().jar)
    write_json(SPEC_FILE,specification());write_json(EVIDENCE_FILE,evidence)
    print(f'Kobolediator admission: {len(evidence["witnesses"])} scoped witnesses captured')
