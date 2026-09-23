from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_eternalstarlight_soul_hunger import ES,census
from assemble_eternalstarlight_soul_hunger import CP,STEM,FACTS
from eternalstarlight_combat_common import preserve_section

def validate_soul_hunger():
    e=read_json(OUT/'native-evidence/eternalstarlight-soul-hunger.json');assert collect(read_json(OUT/'native-specifications/eternalstarlight-soul-hunger.json'))==e
    r=read_json(OUT/'reference-evidence/eternalstarlight-soul-hunger-244.json');assert reference_collect(read_json(OUT/'reference-specifications/eternalstarlight-soul-hunger-244.json'))==r
    v=read_json(OUT/'vanilla-evidence/eternalstarlight-soul-hunger.json');assert prepare(read_json(OUT/'vanilla-specifications/eternalstarlight-soul-hunger.json'))==v
    route=read_json(OUT/'reference-routing/eternalstarlight-soul-hunger.json');assert sha256(route['archive'])==route['sha256']
    with zipfile.ZipFile(route['archive']) as z:assert not(set(route['absent_entries'])&set(z.namelist()))
    assert census()==read_json(OUT/'eternalstarlight-soul-hunger-census.json')
    w={x['entry']:x for x in e['witnesses']}
    def body(cl,method):return next(m['instructions'] for m in w[ES+cl+'.class']['methods'] if m['name']==method)
    def hit(b,s):return [i for i in b if str(s) in str(i.get('operand',''))]
    def pos(b,s):return hit(b,s)[0]['offset']
    def after(b,s):return b[b.index(hit(b,s)[0])+1]
    chain='common/entity/projectile/ChainOfSouls';b=body(chain,'tick')
    assert pos(b,'ArmorStand')<pos(b,'ESDamageTypes.SOUL_ABSORB')<pos(b,'.modifyDamage(')<pos(b,'.hurt(')<pos(b,'.doPostAttackEffects(')<pos(b,'.heal(')<pos(b,'CHAIN_OF_SOULS_CANNOT_PULL')<pos(b,'.shouldRetract(')
    assert after(b,'.hurt(')['opcode']=='0x99' and not hit(b,'.getHealth(') and not hit(b,'.invulnerableTimeI') and not hit(b,'.shouldHarm(')
    assert hit(b,'.onHit(') and not hit(b,'onProjectileImpact') and not hit(b,'hitTargetOrDeflectSelf')
    latch=body(chain,'onHitEntity');assert pos(latch,'.isValidTarget(')<pos(latch,'.shouldHarm(')<pos(latch,'.setTarget(')
    valid=body(chain,'isValidTarget');assert hit(valid,'LivingEntity') and hit(valid,'.isAlive(') and not hit(valid,'ArmorStand')
    saved=body(chain,'addAdditionalSaveData');assert not hit(saved,'absorbSoulTicks')
    dagger=body('common/item/combat/DaggerOfHungerItem','inventoryTick');assert pos(dagger,'ESDamageTypes.DAGGER_OF_HUNGER')<pos(dagger,'.hurt(')<hit(dagger,'.applyComponentsAndValidate(')[1]['offset'] and after(dagger,'.hurt(')['opcode']=='0x57'
    post=body('common/item/combat/DaggerOfHungerItem','postHurtEnemy');assert pos(post,'.addEffect(')<pos(post,'.eat(')<pos(post,'HUNGER_LEVEL') and after(post,'.addEffect(')['opcode']=='0x57'
    dual=body('common/item/combat/DualWieldingSwordItem','use');assert pos(dual,'OFF_HAND')<pos(dual,'.getMainHandItem(')<pos(dual,'OFFHAND_ATTACK')<pos(dual,'.attack(')<pos(dual,'OFFHAND_ATTACK_STRENGTH_TIMER')
    vor=body('common/entity/projectile/VoraciousArrow','doPostHurtEffects');assert pos(vor,'.addEffect(')<pos(vor,'net/minecraft/world/entity/player/Player')<pos(vor,'.eat(')<pos(vor,'DAGGER_OF_HUNGER') and after(vor,'.addEffect(')['opcode']=='0x57'
    tag=w['data/eternal_starlight/tags/entity_type/chan_of_souls_cannot_pull.json']['data'];assert tag['values']==['#c:bosses']
    tags={x['id']:set(x['tags']) for x in read_json(OUT/'eternalstarlight-damage-tags.json')['declarations']};assert {'minecraft:bypasses_armor','minecraft:bypasses_shield','minecraft:bypasses_enchantments'}<=tags['eternal_starlight:soul_absorb']
    assert not tags['eternal_starlight:soul_absorb']&{'minecraft:bypasses_resistance','minecraft:bypasses_cooldown','minecraft:bypasses_invulnerability'}
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==7 and len(d['delivery_paths'])==11
    assert all(v in (OUT/(STEM+'-review.md')).read_text(encoding='utf-8') for v in FACTS.values())
    return dict(schema='tno.external_effects.es_soul_hunger_integrity.v1',checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),loader_witnesses=len(r['witnesses']),raw_fallback_classes=len(v['classes']),reviewed_packages=7,reviewed_paths=11,semantic_order_source_admission_checks='PASS',accepted_counts_preserved=preserve_section(d),promoted_records=0,whole_eternalstarlight_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_soul_hunger();write_json(OUT/'eternalstarlight-r2h3d-integrity.json',d);print(json.dumps(d,indent=2))
