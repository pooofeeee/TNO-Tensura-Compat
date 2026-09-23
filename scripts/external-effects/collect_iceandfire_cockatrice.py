"""Cockatrice combat and Scepter witnesses; reuse accepted gaze/attachment authority."""
from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from collect_iceandfire_foundation import IAF,targets
from vanilla_reference import prepare

CLASSES=['entity/CockatriceEntity','entity/ai/CockatriceAIStareAttackGoal','entity/ai/CockatriceAITargetGoal','entity/ai/CockatriceAIAggroLookGoal','entity/ai/CockatriceAITargetItemsGoal','entity/ai/EntityAIAttackMeleeNoCooldownGoal','item/CockatriceScepterItem','data/component/MiscData','event/ServerEvents','event/ClientEvents']

def census():
    t=targets()['iceandfire'];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for entry in sorted(n for n in z.namelist() if n.endswith('.class')):
            c=ClassFile(z.read(entry))
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if any(x in str(i.get('operand','')) for x in ['.checkScepterTarget(','.addScepterTarget(','.getTargetedByScepters(','.setTamingLevel(']) or ('Cockatrice' in entry and any(x in str(i.get('operand','')) for x in ['.hurt(','.heal(','.addEffect(']))]
                if hits:rows.append(dict(entry=entry,method=m['name'],descriptor=m['descriptor'],hits=hits))
    return dict(jar_sha256=t['sha256'],classes_scanned=726,rows=rows,scope='Whole archive Scepter/taming consumers and Cockatrice primitive callers; no unrelated completion claim.')

def save():
    rows=[]
    with zipfile.ZipFile(targets()['iceandfire']['path']) as z:
        for short in CLASSES:
            c=ClassFile(z.read(IAF+short+'.class'));names=sorted({m['name'] for m in c.methods})
            if short=='event/ServerEvents':names=[n for n in names if n.startswith('lambda$') or n in ['signalChickenAlarm','onLivingSetTarget','onPlayerAttack']]
            if short=='event/ClientEvents':names=[n for n in names if n.startswith('lambda$') or n=='onPostRenderLiving']
            rows.append(dict(id='iaf:cockatrice:'+short,mod_key='iceandfire',entry=IAF+short+'.class',methods=names))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Cockatrice/Scepter combat only; shared event witness availability is not unrelated review completion.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/iceandfire-cockatrice.json',s);write_json(OUT/'native-evidence/iceandfire-cockatrice.json',collect(s));write_json(OUT/'iceandfire-cockatrice-census.json',census())
    a=read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]
    absent=['net/minecraft/world/effect/WitherMobEffect.class']
    with zipfile.ZipFile(a['path']) as z:assert all(e not in z.namelist() for e in absent)
    raw=dict(classes={'net/minecraft/world/effect/WitherMobEffect':['applyEffectTick','shouldApplyEffectTickThisTick'],'net/minecraft/world/damagesource/DamageSources':['wither']},resources=[])
    write_json(OUT/'vanilla-specifications/iceandfire-cockatrice.json',raw);write_json(OUT/'vanilla-evidence/iceandfire-cockatrice.json',prepare(raw))
    write_json(OUT/'reference-routing/iceandfire-cockatrice.json',dict(archive=a['path'],sha256=a['sha256'],absent_entries=absent,authority='Raw Minecraft1.21.1 for absent exact-patched WitherMobEffect. DamageSources absence already protected at R2g5b.'))
    print('Cockatrice witnesses saved')

if __name__=='__main__':save()
