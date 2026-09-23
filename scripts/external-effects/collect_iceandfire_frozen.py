"""Incremental Frozen witnesses; never rewrites the protected R2g1 evidence."""
from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_iceandfire_foundation import IAF,targets

BATCH='iceandfire-frozen'
FULL=['effect/FrozenStatusEffect','item/ability/FrozenTargetAbility','item/ability/IceDragonBloodToolAbility','item/ability/DragonsteelIceToolAbility','item/ability/DamageBonusAbility','item/ability/PostHitAbility']
LIMITED={**{'item/tool/ActivePostHit'+x+'Item':['<init>','hurtEnemy'] for x in ['Sword','Axe','Pickaxe','Shovel','Hoe']},'item/ability/BuiltinAbilities':['<clinit>'],'config/IafCommonConfig$ToolsConfig':['<init>'],'mixin/LivingEntityMixin':['handleFrozenEffectRemove'],'entity/util/dragon/IafDragonDestructionManager':['applyDragonEffect','destroyAreaBreath','destroyAreaCharge']}

def census():
    rows=[]
    with zipfile.ZipFile(targets()['iceandfire']['path']) as z:
        for entry in z.namelist():
            if not entry.endswith('.class'):continue
            c=ClassFile(z.read(entry))
            for m in c.methods:
                ins=list(c.instructions(m.get('code',b'')))
                hits=[i for i in ins if any(s in str(i.get('operand')) for s in ['IafStatusEffects.FROZEN','BuiltinAbilities.ICE_DRAGON_BLOOD_TOOL','BuiltinAbilities.DRAGONSTEEL_ICE_TOOL','FrozenTargetAbility.<init>','destroyAreaBreath(','destroyAreaCharge('])]
                if hits:rows.append(dict(entry=entry,method=m['name'],descriptor=m['descriptor'],hits=hits))
    return dict(schema='tno.external_effects.iaf_frozen_callers.v1',jar_sha256=targets()['iceandfire']['sha256'],rows=rows)

def save():
    callers=census();write_json(OUT/'iceandfire-frozen-callers.json',callers)
    limited={k:list(v) for k,v in LIMITED.items()}
    item='registry/IafItems'
    limited[item]=['<clinit>','registerToolOrWeapon']+[r['method'] for r in callers['rows'] if r['entry']==IAF+item+'.class' and r['method']!='<clinit>']
    with zipfile.ZipFile(targets()['iceandfire']['path']) as z:
        manager='entity/util/dragon/IafDragonDestructionManager'
        limited[manager]+=[m['name'] for m in ClassFile(z.read(IAF+manager+'.class')).methods if m['name'].startswith(('lambda$destroyAreaBreath$','lambda$destroyAreaCharge$'))]
        rows=[dict(id=BATCH+'-'+s.replace('/','-'),mod_key='iceandfire',entry=IAF+s+'.class',methods=sorted({m['name'] for m in ClassFile(z.read(IAF+s+'.class')).methods})) for s in FULL]
    rows += [dict(id=BATCH+'-'+s.replace('/','-'),mod_key='iceandfire',entry=IAF+s+'.class',methods=sorted(set(ms))) for s,ms in limited.items()]
    rows += [dict(id=BATCH+'-fire-dragon-tag',mod_key='iceandfire',entry='data/iceandfire/tags/entity_type/fire_dragon.json')]
    spec=dict(schema='tno.external_effects.native_spec.v1',baseline=BASELINE,evidence_specifications=rows)
    write_json(OUT/'native-specifications'/f'{BATCH}.json',spec)
    write_json(OUT/'native-evidence'/f'{BATCH}.json',collect(spec))
    config=MODS.parent/'config/iceandfire/iaf-common.json'
    write_json(OUT/'iceandfire-frozen-config-snapshot.json',dict(path=str(config),sha256=sha256(config),data=read_json(config),scope='Installed snapshot, not proof of runtime load/reload; durations captured by ability construction.'))
    print('Frozen native witnesses:',len(rows),'caller methods:',len(callers['rows']))

if __name__=='__main__':save()
