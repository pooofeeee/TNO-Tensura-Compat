from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_eternalstarlight_armor_resources import ES,census
from assemble_eternalstarlight_armor_resources import CP,STEM,FACTS
from eternalstarlight_combat_common import preserve_section

def validate_armor_resources():
    e=read_json(OUT/'native-evidence/eternalstarlight-armor-resources.json');assert collect(read_json(OUT/'native-specifications/eternalstarlight-armor-resources.json'))==e
    r=read_json(OUT/'reference-evidence/eternalstarlight-armor-resources-244.json');assert reference_collect(read_json(OUT/'reference-specifications/eternalstarlight-armor-resources-244.json'))==r
    v=read_json(OUT/'vanilla-evidence/eternalstarlight-armor-resources.json');assert prepare(read_json(OUT/'vanilla-specifications/eternalstarlight-armor-resources.json'))==v
    route=read_json(OUT/'reference-routing/eternalstarlight-armor-resources.json');assert sha256(route['archive'])==route['sha256']
    with zipfile.ZipFile(route['archive']) as z:assert not(set(route['absent_entries'])&set(z.namelist()))
    assert census()==read_json(OUT/'eternalstarlight-armor-resources-census.json')
    w={x['entry']:x for x in e['witnesses']+r['witnesses']}
    def body(cl,method):return next(m['instructions'] for m in w[cl+'.class']['methods'] if m['name']==method and m.get('instructions'))
    def es(cl,method):return body(ES+cl,method)
    def hit(b,s):return [i for i in b if str(s) in str(i.get('operand',''))]
    def pos(b,s):return hit(b,s)[0]['offset']
    b=es('common/handler/ESCommonHandler','onPostLivingHurt')
    assert pos(b,'ThermalSpringstoneArmorItem')<pos(b,'.setRemainingFireTicks(')<pos(b,'THERMAL_SPRINGSTONE_WEAPONS')<pos(b,'GlaciteArmorItem')<pos(b,'.setTicksFrozen(')<pos(b,'GLACITE_WEAPONS')<pos(b,'.canFreeze(')<pos(b,'MALARITE_WEAPONS')<pos(b,'PUNGENCY_FRUIT_WEAPONS')
    assert all(i['offset']>pos(b,'PUNGENCY_FRUIT_WEAPONS') for i in hit(b,'.hurt(')) # later Starfire spread already reviewed
    ds=[m['instructions'] for m in w[ES+'common/item/armor/DeepsilverArmorItem.class']['methods'] if m['name'].startswith('lambda$tick$')]
    assert any(hit(b,'DeepsilverArmorItem') for b in ds) and any(hit(b,'.removeEffect(') for b in ds)
    assert w['data/eternal_starlight/tags/mob_effect/deepsilver_armor_can_remove.json']['data']['values']==['minecraft:poison','minecraft:wither','minecraft:nausea','minecraft:hunger','minecraft:slowness','minecraft:infested','minecraft:blindness']
    b=body('net/minecraft/world/entity/LivingEntity','removeEffect');assert pos(b,'.onEffectRemoved(')<pos(b,'.removeEffectNoUpdate(')
    b=es('common/handler/ESCommonHandler','onLivingDecreaseAirSupply');assert pos(b,'AIR_SAC_MASK')<pos(b,'.isSwimming(')<pos(b,'.nextBoolean(')<pos(b,'ESDataAttachments.MOVEMENT')
    b=es('neoforge/event/CommonEvents','onLivingBreathe');assert pos(b,'.canBreathe(')<pos(b,'.getConsumeAirAmount(')<pos(b,'.onLivingDecreaseAirSupply(')<pos(b,'.setCanBreathe(')<pos(b,'.setConsumeAirAmount(')
    b=es('common/mixin/ProjectileMixin','getMovementToShoot');assert pos(b,'.getOwner(')<pos(b,'ThrownPotion')<pos(b,'THROWN_POTION_DISTANCE')<pos(b,'.scale(')
    b=es('common/mixin/LivingEntityMixin','eat');assert pos(b,'LUNARIS_CACTUS_GEL')<pos(b,'.isBeneficial(')<pos(b,'.removeEffect(')<pos(b,'PUNGENCY_STEW')<pos(b,'MobEffects.HUNGER')
    b=body('net/minecraft/world/entity/LivingEntity','heal');assert pos(b,'.onLivingHeal(')<pos(b,'.getHealth(')<pos(b,'.setHealth(')
    equipment=[m['instructions'] for m in w['net/minecraft/world/entity/LivingEntity.class']['methods'] if m['name'].startswith('lambda$collectEquipmentChanges$')]
    assert any(hit(b,'.removeModifier(') and hit(b,'.addTransientModifier(') and pos(b,'.removeModifier(')<pos(b,'.addTransientModifier(') for b in equipment)
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==14 and len(d['delivery_paths'])==22
    assert all(v in (OUT/(STEM+'-review.md')).read_text(encoding='utf-8') for v in FACTS.values())
    return dict(schema='tno.external_effects.es_armor_resources_integrity.v1',checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),loader_witnesses=len(r['witnesses']),raw_fallback_classes=len(v['classes']),reviewed_packages=14,reviewed_paths=22,semantic_order_source_admission_checks='PASS',accepted_counts_preserved=preserve_section(d),promoted_records=0,whole_eternalstarlight_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_armor_resources();write_json(OUT/'eternalstarlight-r2h5c-integrity.json',d);print(json.dumps(d,indent=2))
