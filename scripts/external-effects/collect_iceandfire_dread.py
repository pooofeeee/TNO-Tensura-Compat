from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_iceandfire_foundation import IAF,COMPAT,targets
CLASSES=['entity/DreadMobEntity','entity/DreadLichEntity','entity/DreadLichSkullEntity','entity/DreadThrallEntity','entity/DreadGhoulEntity','entity/DreadBeastEntity','entity/DreadScuttlerEntity','entity/DreadKnightEntity','entity/DreadHorseEntity','entity/DreadQueenEntity','entity/ai/DreadAITargetNonDreadGoal','entity/ai/DreadLichAIStrifeGoal','entity/ai/DreadAIRideHorseGoal','item/LichStaffItem','item/DreadQueenStaffItem','registry/IafEntities']

def census():
    archives=[]
    for key in ['iceandfire',COMPAT]:
        t=targets()[key];rows=[];refs=[];count=0
        with zipfile.ZipFile(t['path']) as z:
            for entry in sorted(n for n in z.namelist() if n.endswith('.class')):
                c=ClassFile(z.read(entry));count+=1
                for m in c.methods:
                    body=list(c.instructions(m.get('code',b'')))
                    hits=[i for i in body if any(s in str(i.get('operand','')) for s in ['.onKillEntity(','.necromancyEntity(','DreadQueenEntity'])]
                    if hits:refs.append(dict(entry=entry,method=m['name'],descriptor=m['descriptor'],hits=hits))
                    if 'Dread' in entry or 'LichStaff' in entry:
                        hits=[i for i in body if any(s in str(i.get('operand','')) for s in ['.hurt(','.addFreshEntity(','.setMinionCount(','.knockback(','.setOwner(','.setPos('])]
                        if hits:rows.append(dict(entry=entry,method=m['name'],descriptor=m['descriptor'],hits=hits))
        archives.append(dict(key=key,jar_sha256=t['sha256'],classes=count,combat_callers=rows,legacy_and_queen_references=refs))
    return dict(scope='All Iaf/compat classes parsed for legacy necromancy invocation and Queen references; combat census limited to Dread.',archives=archives)

def save():
    ts=targets();rows=[]
    with zipfile.ZipFile(ts['iceandfire']['path']) as z:
        for s in CLASSES:
            rows.append(dict(id='iaf:dread:'+s,mod_key='iceandfire',entry=IAF+s+'.class',methods=sorted({m['name'] for m in ClassFile(z.read(IAF+s+'.class')).methods})))
    for key in ['iceandfire',COMPAT]:
        with zipfile.ZipFile(ts[key]['path']) as z:
            for n in sorted(z.namelist()):
                if n.startswith('data/') and n.endswith('.json') and (('/tags/entity_type/' in n and b'dread' in z.read(n)) or ('/entity_existence/dread_' in n)):
                    rows.append(dict(id=key+':dread-data:'+n,mod_key=key,entry=n))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Dread combat, native delivery gaps, summon counters and direct compatibility declarations.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/iceandfire-dread.json',s);write_json(OUT/'native-evidence/iceandfire-dread.json',collect(s));write_json(OUT/'iceandfire-dread-census.json',census())
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None)
    a['classes']={'net/minecraft/world/entity/Entity.class':['<init>','killedEntity'],'net/minecraft/world/entity/LivingEntity.class':['die'],'net/minecraft/world/entity/projectile/Projectile.class':['<init>','setOwner','shoot'],'net/minecraft/world/entity/projectile/AbstractArrow.class':['<init>','onHitEntity']}
    r=dict(id='iceandfire-dread-244',scope='Native kill callback signature, projectile constructor position and arrow hurt admission.',archives=[a])
    write_json(OUT/'reference-specifications/iceandfire-dread-244.json',r);write_json(OUT/'reference-evidence/iceandfire-dread-244.json',reference_collect(r,source_aids=True))
    print('Dread witnesses saved')
if __name__=='__main__':save()
