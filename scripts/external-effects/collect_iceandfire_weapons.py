from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_iceandfire_foundation import IAF,targets
CLASSES=['item/ability/BuiltinAbilities','item/ability/DamageBonusAbility','item/ability/FireDragonBloodToolAbility','item/ability/DragonsteelFireToolAbility','item/ability/LightningDragonBloodToolAbility','item/ability/LightningMultihitAbility','item/ability/SummonLightningAbility','item/ability/IgniteTargetAbility','item/ability/TakeKnockbackAbility','item/tool/ActivePostHitSwordItem','item/tool/ActivePostHitAxeItem','item/tool/ActivePostHitPickaxeItem','item/tool/ActivePostHitShovelItem','item/tool/ActivePostHitHoeItem','item/tool/DragonBowItem','item/tool/DragonArrowItem','entity/DragonArrowEntity','item/tool/TideTridentItem','entity/TideTridentEntity','item/tool/HippogryphSwordItem','item/tool/HippocampusSlapperItem','item/DeathwormGauntletItem']

def census():
    t=targets()['iceandfire'];rows=[];meta=[]
    with zipfile.ZipFile(t['path']) as z:
        for entry in sorted(n for n in z.namelist() if n.endswith('.class')):
            c=ClassFile(z.read(entry))
            for m in c.methods:
                b=list(c.instructions(m.get('code',b'')))
                h=[i for i in b if 'bolt_skip_loot' in str(i.get('operand',''))]
                if h:meta.append(dict(entry=entry,method=m['name'],hits=h))
                if entry in {IAF+s+'.class' for s in CLASSES}:
                    h=[i for i in b if any(s in str(i.get('operand','')) for s in ['.hurt(','.addFreshEntity(','.addEffect(','.igniteForSeconds(','.knockback(','.startAutoSpinAttack('])]
                    if h:rows.append(dict(entry=entry,method=m['name'],descriptor=m['descriptor'],hits=h))
    return dict(jar_sha256=t['sha256'],combat_callers=rows,loot_tag_uses=meta)

def save():
    t=targets()['iceandfire'];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for s in CLASSES:
            rows.append(dict(id='iaf:weapons:'+s,mod_key='iceandfire',entry=IAF+s+'.class',methods=sorted({m['name'] for m in ClassFile(z.read(IAF+s+'.class')).methods})))
        c=ClassFile(z.read(IAF+'registry/IafItems.class'))
        names=['<clinit>']+[m['name'] for m in c.methods if any('BuiltinAbilities.' in str(i.get('operand','')) for i in c.instructions(m.get('code',b'')))]
        rows.append(dict(id='iaf:weapons:IafItems',mod_key='iceandfire',entry=IAF+'registry/IafItems.class',methods=names))
        for n in sorted(z.namelist()):
            if n.startswith('data/') and n.endswith('.json') and any(s in n for s in ['/tags/item/dragon_arrows','/tags/entity_type/fire_dragon','/tags/entity_type/ice_dragon']):rows.append(dict(id='iaf:weapon-data:'+n,mod_key='iceandfire',entry=n))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Remaining HP-special weapons; Frozen reused, not repeated.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/iceandfire-weapons.json',s);write_json(OUT/'native-evidence/iceandfire-weapons.json',collect(s));write_json(OUT/'iceandfire-weapons-census.json',census())
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None)
    a['classes']={'net/minecraft/world/entity/LightningBolt.class':['<init>','tick','spawnFire','setCause','getDamage'],'net/minecraft/world/entity/Entity.class':['thunderHit'],'net/minecraft/world/entity/player/Player.class':['attack','startAutoSpinAttack','doAutoAttackOnTouch'],'net/minecraft/world/entity/LivingEntity.class':['checkAutoSpinAttack'],'net/minecraft/world/entity/projectile/AbstractArrow.class':['tick','canHitEntity'],'net/minecraft/world/item/TridentItem.class':['use','asProjectile']}
    with zipfile.ZipFile(a['path']) as z:assert 'net/minecraft/world/entity/projectile/ThrownTrident.class' not in z.namelist()
    r=dict(id='iceandfire-weapons-244',scope='Native lightning, Player post-hit and spin delivery; raw ThrownTrident used only because absent from installed patched archive.',archives=[a],raw_fallback_absent_classes=['net/minecraft/world/entity/projectile/ThrownTrident.class'])
    write_json(OUT/'reference-specifications/iceandfire-weapons-244.json',r);write_json(OUT/'reference-evidence/iceandfire-weapons-244.json',reference_collect(r,source_aids=True))
    raw=dict(classes={'net/minecraft/world/entity/projectile/ThrownTrident':['<init>','tick','findHitEntity','getWeaponItem']},resources=[])
    write_json(OUT/'vanilla-specifications/iceandfire-weapons.json',raw);write_json(OUT/'vanilla-evidence/iceandfire-weapons.json',prepare(raw))
    print('Weapon witnesses saved')
if __name__=='__main__':save()
