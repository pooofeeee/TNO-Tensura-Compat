from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_bossesrise_equipment import helper_census
from collect_bossesrise_foundation import PKG
from assemble_bossesrise_equipment import FACTS,CP,STEM
from bossesrise_combat_common import preserve_section

def validate_equipment():
    e=read_json(OUT/'native-evidence/bossesrise-equipment.json');assert collect(read_json(OUT/'native-specifications/bossesrise-equipment.json'))==e
    r=read_json(OUT/'reference-evidence/bossesrise-equipment-244.json');assert reference_collect(read_json(OUT/'reference-specifications/bossesrise-equipment-244.json'))==r
    raw=read_json(OUT/'vanilla-evidence/bossesrise-equipment.json');assert prepare(read_json(OUT/'vanilla-specifications/bossesrise-equipment.json'))==raw
    c=read_json(OUT/'bossesrise-equipment-helper-census.json');assert helper_census()==c and c['rows']==[]
    w={x['entry']:x for x in e['witnesses']}
    def b(short,n):return next(m['instructions'] for m in w[PKG+short+'.class']['methods'] if m['name']==n)
    def h(v,s):return [i for i in v if s in str(i.get('operand',''))]
    def off(v,s):return h(v,s)[0]['offset']
    a='event/DragonArmorEvents'
    v=b(a,'onPlayerHurt');assert off(v,'.handleDragonBonesBoots(')<off(v,'.handleDragonBonesChestplate(') and not h(v,'.getNewDamage(')
    v=b(a,'handleDragonBonesBoots');assert h(v,'.fallDistanceF') and h(v,'.getKnownMovement(') and h(v,'.clamp(') and any(i.get('operand')==4.5 for i in v)
    assert off(v,'ServerLevel.explode(')<off(v,'Explosion.explode()')<off(v,'.getNearbyPlayers(') and h(v,'.NONE') and not h(v,'.getSource(')
    v=b(a,'handleDragonBonesChestplate');assert h(v,'.getDirectEntity(') and h(v,'/Projectile') and off(v,'.getOwner(')<off(v,'.setOwner(')<off(v,'.setBaseDamage(')<off(v,'.shoot(')
    assert any(i.get('operand')==.1 for i in v) and any(i.get('operand')==1.5 for i in v) and not h(v,'.getNewDamage(')
    v=b(a,'onPlayerTick');assert len(h(v,'.addEffect('))==5 and h(v,'.DAMAGE_RESISTANCE') and h(v,'.isCrouching(')
    v=b('item/KnightSwordItem','releaseUsing');assert h(v,'SwordWaveEntity.<init>') and h(v,'.setOwner(') and h(v,'.setBaseDamage(') and h(v,'.addCooldown(') and not h(v,'.hurtAndBreak(')
    v=b('item/PirateSaberItem','finishUsingItem');assert len(h(v,'.setOwnerUUID('))==2 and len(h(v,'.addFreshEntity('))==2 and h(v,'.hasInfiniteMaterials(') and h(v,'.hurtAndBreak(') and not h(v,'.noBlockCollision(')
    v=b('item/EnhancedShieldItem','<init>');assert not h(v,'.attributes(')
    rw={x['entry']:x for x in r['witnesses']}
    def rb(k,n):return [m['instructions'] for m in rw[k+'.class']['methods'] if m['name']==n]
    lv=next(v for v in rb('net/minecraft/world/level/Level','explode') if h(v,'.onExplosionStart('))
    assert off(lv,'.onExplosionStart(')<off(lv,'Explosion.explode()')<off(lv,'.finalizeExplosion(')
    assert any(i['opcode']=='0xb0' and off(lv,'.onExplosionStart(')<i['offset']<off(lv,'Explosion.explode()') for i in lv)
    ev=rb('net/minecraft/world/level/Explosion','explode')[0];assert off(ev,'.onExplosionDetonate(')<off(ev,'.hurt(')
    pv=rb('net/minecraft/world/entity/player/Player','actuallyHurt')[0];assert off(pv,'.setHealth(')<off(pv,'.onLivingDamagePost(')
    iv=rb('net/neoforged/neoforge/common/extensions/IItemStackExtension','getAttributeModifiers')[0];assert h(iv,'.ATTRIBUTE_MODIFIERS') and h(iv,'.getDefaultAttributeModifiers(') and h(iv,'.computeModifiedAttributes(')
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==14 and len(d['delivery_paths'])==21 and sum(m['stage_scaling_needed'] for m in d['mechanic_packages'])==8
    assert all(set(p['labels'])<=set(DELIVERIES) for p in d['delivery_paths'])
    prior={m['id']:m for f in ['bossesrise-r2i3b-knight-offense.json','bossesrise-r2i4-infernal-dragon.json','bossesrise-r2i7b-kraken-offense.json'] for m in read_json(OUT/f)['mechanic_packages']}
    reuse=[m for m in d['mechanic_packages'] if m.get('extends_existing_package')];assert len(reuse)==10
    for m in reuse:
        for k in ['single_scaling_point','stage_scaling_needed','primary_classification','tno_categories']:assert m[k]==prior[m['id']][k]
    preserved=preserve_section(d);assert preserved==dict(effects=543,sources=1303,paths=1303,comparisons=543,primitives=717)
    return dict(schema='tno.external_effects.bossesrise_equipment_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),reference_witnesses=len(r['witnesses']),raw_reference_classes=len(raw['classes']),mechanic_packages=14,new_packages=4,extends_existing_packages=10,native_paths=21,numeric_stage_candidates=8,native_double_explosion_and_start_cancellation_path_verified=True,genuine_Post_and_existing_hazard_delivery_verified=True,unused_enhanced_shield_helper_not_promoted=True,accepted_counts_preserved=preserved,whole_mod_complete=False,runtime_tests=0,**boundary_flags())
if __name__=='__main__':
    d=validate_equipment();write_json(OUT/'bossesrise-r2i8c-integrity.json',d);print(json.dumps(d,indent=2))
