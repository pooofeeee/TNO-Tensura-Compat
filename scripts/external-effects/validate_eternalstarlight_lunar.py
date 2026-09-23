from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_eternalstarlight_lunar import ES,producer_census
from assemble_eternalstarlight_lunar import CP,STEM,FACTS
from eternalstarlight_combat_common import preserve_section

def validate_lunar():
    e=read_json(OUT/'native-evidence/eternalstarlight-lunar.json');assert collect(read_json(OUT/'native-specifications/eternalstarlight-lunar.json'))==e
    r=read_json(OUT/'reference-evidence/eternalstarlight-lunar-244.json');assert reference_collect(read_json(OUT/'reference-specifications/eternalstarlight-lunar-244.json'))==r
    assert producer_census()==read_json(OUT/'eternalstarlight-lunar-producer-census.json')
    w={x['entry']:x for x in e['witnesses']}
    def body(cl,method):return next(m['instructions'] for m in w[ES+cl+'.class']['methods'] if m['name']==method)
    def hit(b,s):return [i for i in b if str(s) in str(i.get('operand',''))]
    def pos(b,s):return hit(b,s)[0]['offset']
    def after(b,s):return b[b.index(hit(b,s)[0])+1]
    base='common/entity/living/boss/monstrosity/LunarMonstrosity'
    h=body(base,'hurt');assert pos(h,'LUNAR_MONSTROSITY_ALLIES')<pos(h,'.setPhase(')<pos(h,'6.0')<pos(h,'ESMobEffects.STARFIRE')<pos(h,'Math.min(')<pos(h,'ESBoss.hurt(')<hit(h,'.setPhase(')[-1]['offset']
    block=body(base,'blockedByShield');assert hit(block,'.setBehaviorState(') and not hit(block,'.setBehaviorTicks(')
    bite=body(base,'doBiteDamage');assert hit(bite,'ESDamageTypes.BITE') and hit(bite,'getEntityDamageSource(') and after(bite,'.hurt(')['opcode']=='0x57' and not hit(bite,'.shouldHarm(')
    soul=body(base+'SoulPhase','tick');assert hit(soul,'.knockbackNearbyEntities(') and not hit(soul,'ESDamageTypes') and not hit(soul,'.hurt(')
    breath=body('common/entity/attack/ray/LunarMonstrosityBreath','lambda$doHurtTarget$0');assert pos(breath,'ESDamageTypes.POISON')<pos(breath,'.hurt(')<pos(breath,'.hasEffect(')<pos(breath,'.addEffect(') and after(breath,'.hurt(')['opcode']=='0x99'
    thorn=body('common/entity/attack/LunarThorn','tick');assert pos(thorn,'.addEffect(')<pos(thorn,'.hurt(') and after(thorn,'.hurt(')['opcode']=='0x57'
    spore=body('common/entity/projectile/LunarSpore','explodeAndDiscard');assert hit(spore,'net/minecraft/world/entity/player/Player') and pos(spore,'.invulnerableTimeI')<pos(spore,'.hurt(') and after(spore,'.hurt(')['opcode']=='0x57'
    assert not hit(spore,'Level.explode(') and not hit(spore,'.addEffect(')
    cloud=body('common/entity/attack/PoisonousCloud','tick');assert len(hit(cloud,'.invulnerableTimeI'))==3 and pos(cloud,'.hurt(')<hit(cloud,'.invulnerableTimeI')[-1]['offset']<pos(cloud,'.addEffect(')
    wand=body('common/item/combat/WandOfTeleportationItem','teleportPlayer');assert pos(wand,'.createThornCircle(')<pos(wand,'ESEntities.TANGLED_HUSK')<pos(wand,'.postTeleportEvent(')<pos(wand,'.teleportTo(')<pos(wand,'.hurtAndBreak(')
    platform=body('neoforge/platform/ESNeoPlatform','postTeleportEvent');assert hit(platform,'EntityTeleportEvent') and hit(platform,'.isCanceled(') and not hit(platform,'.getTarget')
    husk=body('common/entity/attack/TangledHusk','tick');assert hit(husk,'ESDamageTypes.getEntityDamageSource(') and not hit(husk,'getIndirectEntityDamageSource(') and pos(husk,'.hurt(')<pos(husk,'.addDeltaMovement(') and after(husk,'.hurt(')['opcode']=='0x99'
    skull=body('common/entity/living/monster/TangledSkull','tick');assert pos(skull,'.addEffect(')<pos(skull,'.explode(') and hit(skull,'ExplosionInteraction.NONE') and not hit(skull,'.setOwner(')
    item=body('common/item/combat/TangledSkullItem','use');assert hit(item,'.setShot(') and not hit(item,'.setOwner(')
    explosion=next(m['instructions'] for c in r['witnesses'] if c['entry']=='net/minecraft/world/level/Explosion.class' for m in c['methods'] if m['name']=='getIndirectSourceEntityInternal');assert hit(explosion,'net/minecraft/world/entity/LivingEntity')
    tags={x['id']:set(x['tags']) for x in read_json(OUT/'eternalstarlight-damage-tags.json')['declarations']}
    for id in ['bite','poison']:assert not tags['eternal_starlight:'+id]&{'minecraft:is_projectile','minecraft:bypasses_armor','minecraft:bypasses_shield','minecraft:bypasses_enchantments'}
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==13 and len(d['delivery_paths'])==23
    assert all(v in (OUT/(STEM+'-review.md')).read_text(encoding='utf-8') for v in FACTS.values())
    return dict(schema='tno.external_effects.es_lunar_integrity.v1',checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),loader_witnesses=len(r['witnesses']),reviewed_packages=13,reviewed_paths=23,semantic_order_source_admission_checks='PASS',accepted_counts_preserved=preserve_section(d),promoted_records=0,whole_eternalstarlight_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_lunar();write_json(OUT/'eternalstarlight-r2h3c-integrity.json',d);print(json.dumps(d,indent=2))
