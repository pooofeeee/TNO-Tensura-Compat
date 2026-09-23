from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_iceandfire_foundation import IAF,targets
CLASSES=['entity/HydraEntity','entity/HydraHeadEntity','entity/HydraBreathEntity','entity/HydraArrowEntity','item/tool/HydraArrowItem','item/HydraHeartItem','entity/SeaSerpentEntity','entity/SeaSerpentBubblesEntity','entity/SeaSerpentArrowEntity','item/tool/SeaSerpentArrowItem','item/armor/SeaSerpentArmorItem','entity/ai/SeaSerpentAIMeleeJumpGoal','entity/ai/SeaSerpentAIAttackMeleeGoal','registry/IafRecipes']
def census():
    t=targets()['iceandfire'];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for entry in sorted(n for n in z.namelist() if n.endswith('.class') and any(s in n for s in ['Hydra','SeaSerpent'])):
            c=ClassFile(z.read(entry))
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if any(s in str(i.get('operand','')) for s in ['.hurt(','.heal(','.addEffect(','.removeEffect(','.setHeadCount(','.setSeveredHead(','.onHitHead('])]
                if hits:rows.append(dict(entry=entry,method=m['name'],descriptor=m['descriptor'],hits=hits))
    return dict(jar_sha256=t['sha256'],rows=rows,scope='Hydra/Sea Serpent combat/resource callers; no unrelated completion.')
def save():
    with zipfile.ZipFile(targets()['iceandfire']['path']) as z:rows=[dict(id='iaf:hydra-serpent:'+s,mod_key='iceandfire',entry=IAF+s+'.class',methods=sorted({m['name'] for m in ClassFile(z.read(IAF+s+'.class')).methods})) for s in CLASSES]
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Hydra and Sea Serpent plus related special gear.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/iceandfire-hydra-serpent.json',s);write_json(OUT/'native-evidence/iceandfire-hydra-serpent.json',collect(s));write_json(OUT/'iceandfire-hydra-serpent-census.json',census())
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None);a['classes']={'net/minecraft/world/item/ArrowItem.class':['createArrow','asProjectile'],'net/minecraft/world/item/ProjectileWeaponItem.class':['createProjectile'],'net/minecraft/world/entity/projectile/AbstractArrow.class':['onHitEntity']}
    r=dict(id='iceandfire-hydra-serpent-244',scope='Legitimate weapon versus dispenser arrow construction and native post-hurt callback admission.',archives=[a])
    write_json(OUT/'reference-specifications/iceandfire-hydra-serpent-244.json',r);write_json(OUT/'reference-evidence/iceandfire-hydra-serpent-244.json',reference_collect(r,source_aids=True))
    raw=dict(classes={'net/minecraft/world/damagesource/DamageSources':['fallingBlock']},resources=[])
    write_json(OUT/'vanilla-specifications/iceandfire-hydra-serpent.json',raw);write_json(OUT/'vanilla-evidence/iceandfire-hydra-serpent.json',prepare(raw))
    print('Hydra/Sea Serpent witnesses saved')
if __name__=='__main__':save()
