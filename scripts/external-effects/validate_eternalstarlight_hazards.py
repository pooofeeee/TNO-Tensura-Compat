from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_eternalstarlight_hazards import ES,census
from assemble_eternalstarlight_hazards import CP,STEM,FACTS
from eternalstarlight_combat_common import preserve_section

def validate_hazards():
    e=read_json(OUT/'native-evidence/eternalstarlight-hazards.json');assert collect(read_json(OUT/'native-specifications/eternalstarlight-hazards.json'))==e
    r=read_json(OUT/'reference-evidence/eternalstarlight-hazards-244.json');assert reference_collect(read_json(OUT/'reference-specifications/eternalstarlight-hazards-244.json'))==r
    v=read_json(OUT/'vanilla-evidence/eternalstarlight-hazards.json');assert prepare(read_json(OUT/'vanilla-specifications/eternalstarlight-hazards.json'))==v
    route=read_json(OUT/'reference-routing/eternalstarlight-hazards.json');assert sha256(route['archive'])==route['sha256']
    with zipfile.ZipFile(route['archive']) as z:assert not(set(route['absent_entries'])&set(z.namelist()))
    assert census()==read_json(OUT/'eternalstarlight-hazards-census.json')
    w={x['entry']:x for x in e['witnesses']+r['witnesses']}
    def body(cl,method):return next(m['instructions'] for m in w[cl+'.class']['methods'] if m['name']==method and m.get('instructions'))
    def es(cl,method):return body(ES+cl,method)
    def hit(b,s):return [i for i in b if str(s) in str(i.get('operand',''))]
    def pos(b,s):return hit(b,s)[0]['offset']
    def after(b,s):return b[b.index(hit(b,s)[0])+1]
    b=es('common/block/AbyssalFireBlock','entityInside');assert pos(b,'ABYSSAL_FIRE_IMMUNE')<pos(b,'.inFire(')<pos(b,'.hurt(')<pos(b,'ABYSSAL_FIRE_TICKS') and after(b,'.hurt(')['opcode']=='0x57'
    b=es('common/handler/ESCommonHandler','onEntityTick');assert pos(b,'ABYSSAL_FIRE_TICKS')<pos(b,'ABYSSAL_FIRE_IMMUNE')<pos(b,'invulnerableTime')<pos(b,'.onFire(')<pos(b,'.hurt(')
    b=es('common/block/AmaramberFireBlock','entityInside');assert pos(b,'.inFire(')<pos(b,'.hurt(')<pos(b,'REGENERATION')<pos(b,'.addEffect(') and after(b,'.hurt(')['opcode']=='0x57'
    b=es('common/enchantment/effect/Freeze','apply');assert hit(b,'.setTicksFrozen(') and not hit(b,'.canFreeze(') and not hit(b,'.hurt(')
    b=es('common/enchantment/effect/PushTowardsEntity','apply');assert pos(b,'.owner(')<pos(b,'.randomBetween(')<pos(b,'.subtract(')<pos(b,'.addDeltaMovement(') and not hit(b,'KNOCKBACK_RESISTANCE')
    assert 'net/minecraft/world/level/block/Fallable' not in w[ES+'common/block/IcicleBlock.class'].get('interfaces',[])
    b=es('common/block/IcicleBlock','spawnFallingStalactite');assert pos(b,'.fall(')<pos(b,'IcicleThickness.TIP')<pos(b,'.setHurtsEntities(')
    b=body('net/minecraft/world/entity/item/FallingBlockEntity','causeFallDamage');assert pos(b,'NO_CREATIVE_OR_SPECTATOR')<pos(b,'LIVING_ENTITY_STILL_ALIVE')<pos(b,'.fallingBlock(')<pos(b,'fallDamageMax')<pos(b,'.getEntities(')
    b=es('common/entity/projectile/AetherstrikeRocketEntity','explode');assert pos(b,'GameEvent.EXPLODE')<pos(b,'STARLIGHT_KEY')<pos(b,'.canSeeSky(')<pos(b,'.setActiveWeather(')<pos(b,'.addCooldown(')<pos(b,'.discard(') and not hit(b,'.hurt(') and not hit(b,'.explode(')
    b=es('common/block/entity/GolemSteelJetBlockEntity','tick');assert pos(b,'hurtMarked')<pos(b,'.addDeltaMovement(')<pos(b,'.setIgnoreFallDamageFromCurrentImpulse(') and not hit(b,'.hurt(')
    data={x['entry']:x['data'] for x in e['witnesses'] if 'data' in x}
    assert len([k for k in data if k.startswith('data/eternal_starlight/enchantment/')])==13
    g=data['data/eternal_starlight/enchantment/glacial_sowing.json']['effects']['minecraft:post_attack'][0];assert g['requirements']['predicate']['type']=='eternal_starlight:shot_seeds' and g['affected']=='victim'
    p=data['data/eternal_starlight/enchantment/poisoning.json']['effects']['minecraft:post_attack'][0];assert (p['enchanted'],p['affected'])==('victim','attacker')
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==13 and len(d['delivery_paths'])==21
    assert all(v in (OUT/(STEM+'-review.md')).read_text(encoding='utf-8') for v in FACTS.values())
    return dict(schema='tno.external_effects.es_hazards_integrity.v1',checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),loader_witnesses=len(r['witnesses']),raw_fallback_classes=len(v['classes']),reviewed_packages=13,reviewed_paths=21,semantic_order_source_admission_checks='PASS',accepted_counts_preserved=preserve_section(d),promoted_records=0,whole_eternalstarlight_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_hazards();write_json(OUT/'eternalstarlight-r2h7a-integrity.json',d);print(json.dumps(d,indent=2))
