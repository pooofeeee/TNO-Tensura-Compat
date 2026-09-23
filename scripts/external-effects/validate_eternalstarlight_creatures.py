from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_eternalstarlight_creatures import ES,census
from assemble_eternalstarlight_creatures import CP,STEM,FACTS
from eternalstarlight_combat_common import preserve_section

def validate_creatures():
    e=read_json(OUT/'native-evidence/eternalstarlight-creatures.json');assert collect(read_json(OUT/'native-specifications/eternalstarlight-creatures.json'))==e
    r=read_json(OUT/'reference-evidence/eternalstarlight-creatures-244.json');assert reference_collect(read_json(OUT/'reference-specifications/eternalstarlight-creatures-244.json'))==r
    v=read_json(OUT/'vanilla-evidence/eternalstarlight-creatures.json');assert prepare(read_json(OUT/'vanilla-specifications/eternalstarlight-creatures.json'))==v
    route=read_json(OUT/'reference-routing/eternalstarlight-creatures.json');assert sha256(route['archive'])==route['sha256']
    with zipfile.ZipFile(route['archive']) as z:assert not(set(route['absent_entries'])&set(z.namelist()))
    assert census()==read_json(OUT/'eternalstarlight-creatures-census.json')
    w={x['entry']:x for x in e['witnesses']+r['witnesses']}
    def bodies(cl,method):return [m['instructions'] for m in w[cl+'.class']['methods'] if m['name']==method and m.get('instructions')]
    def es(cl,method):return bodies(ES+cl,method)[0]
    def hit(b,s):return [i for i in b if str(s) in str(i.get('operand',''))]
    def pos(b,s):return hit(b,s)[0]['offset']
    def after(b,s):return b[b.index(hit(b,s)[0])+1]
    b=es('common/entity/projectile/GleechEgg','onHitEntity');assert pos(b,'.thrown(')<pos(b,'.hurt(')<pos(b,'GLEECH_IMMUNE')<pos(b,'.attachTo(')<pos(b,'.addFreshEntity(')<pos(b,'.setTarget(') and after(b,'.hurt(')['opcode']=='0x57'
    b=es('common/entity/living/monster/Gleech','attachTo');assert after(b,'.startRiding(')['opcode']=='0x57'
    b=next(b for b in bodies('net/minecraft/world/entity/Entity','startRiding') if hit(b,'canMountEntity'));assert pos(b,'.couldAcceptPassenger(')<pos(b,'.canMountEntity(')<pos(b,'.canRide(')
    for cl in ['Creteor','TinyCreteor']:
        b=es('common/entity/living/monster/'+cl,'explode');assert pos(b,'.explode(')<pos(b,'.spawnLingeringCloud(')<pos(b,'.triggerOnDeathMobEffects(')<pos(b,'.discard(')
        b=es('common/entity/living/monster/'+cl,'spawnLingeringCloud');assert hit(b,'.addEffect(') and not hit(b,'.setOwner(')
    b=es('common/entity/living/monster/Creteor','hurt');assert pos(b,'.setActivated(')<pos(b,'.hurt(')
    b=es('common/entity/living/npc/boarwarf/golem/AstralGolem','hurt');assert hit(b,'.defenseMultiplier(') and pos(b,'.defenseMultiplier(')<pos(b,'.hurt(')
    b=es('common/entity/living/npc/boarwarf/Boarwarf','hurt');assert pos(b,'.angerNearbyAstralGolems(')<pos(b,'.hurt(')
    b=es('common/entity/living/animal/Luminofish','aiStep');assert pos(b,'.doHurtTarget(')<pos(b,'POISON')<pos(b,'.addEffect(') and after(b,'.doHurtTarget(')['opcode']=='0x57'
    b=es('common/entity/living/animal/ShadowSnail','hurt');assert pos(b,'PANIC_CAUSES')<pos(b,'.setHideState(')<pos(b,'BYPASSES_INVULNERABILITY')<pos(b,'.hurt(')
    b=es('common/entity/living/monster/Stranghoul','hurt');assert pos(b,'.getDirectEntity(')<pos(b,'STRANGHOUL_VULNERABLE_TO')<pos(b,'.hurt(')
    b=es('common/entity/living/monster/ThirstWalker','doHurtTarget');assert pos(b,'.doHurtTarget(')<pos(b,'HUNGER')<pos(b,'.stopBeingAngry(')<pos(b,'.tryFlee(')
    b=es('common/entity/living/GrimstoneGolem','registerGoals');assert not hit(b,'MeleeAttack')
    b=es('common/entity/living/animal/YetiAi','initIdleActivity');assert not hit(b,'MeleeAttack')
    data={x['entry']:x['data'] for x in e['witnesses'] if 'data' in x};assert data['data/eternal_starlight/eternal_starlight/astral_golem_material/deepsilver.json']['defense_multiplier']==1.2
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==18 and len(d['delivery_paths'])==29
    assert all(v in (OUT/(STEM+'-review.md')).read_text(encoding='utf-8') for v in FACTS.values())
    return dict(schema='tno.external_effects.es_creatures_integrity.v1',checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),loader_witnesses=len(r['witnesses']),raw_fallback_classes=len(v['classes']),reviewed_packages=18,reviewed_paths=29,semantic_order_source_admission_checks='PASS',accepted_counts_preserved=preserve_section(d),promoted_records=0,whole_eternalstarlight_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_creatures();write_json(OUT/'eternalstarlight-r2h7b-integrity.json',d);print(json.dumps(d,indent=2))
