from catalog_common import *
from native_evidence import collect
from collect_eternalstarlight_sonar_meteor_seeds import ES,census
from assemble_eternalstarlight_sonar_meteor_seeds import CP,STEM,FACTS
from eternalstarlight_combat_common import preserve_section

def validate_sonar_meteor_seeds():
    e=read_json(OUT/'native-evidence/eternalstarlight-sonar-meteor-seeds.json');assert collect(read_json(OUT/'native-specifications/eternalstarlight-sonar-meteor-seeds.json'))==e
    assert census()==read_json(OUT/'eternalstarlight-sonar-meteor-seeds-census.json')
    w={x['entry']:x for x in e['witnesses']}
    def body(cl,method):return next(m['instructions'] for m in w[ES+cl+'.class']['methods'] if m['name']==method and m.get('instructions'))
    def hit(b,s):return [i for i in b if str(s) in str(i.get('operand',''))]
    def pos(b,s):return hit(b,s)[0]['offset']
    def after(b,s):return b[b.index(hit(b,s)[0])+1]
    moth='common/entity/living/animal/CrystallizedMoth';b=body(moth,'hurt');assert pos(b,'ESDamageTypes.SONAR')<pos(b,'.hurt(') and not hit(b,'BYPASSES_INVULNERABILITY')
    b=body(moth+'$CrystallizedMothAttackGoal','tick');assert pos(b,'.hasLineOfSight(')<pos(b,'ESDamageTypes.SONAR')<pos(b,'ATTACK_DAMAGE')<pos(b,'.hurt(') and after(b,'.hurt(')['opcode']=='0x57' and not hit(b,'invulnerableTime')
    b=body('common/entity/projectile/SonarBomb','onHit');assert pos(b,'.shouldHarm(')<pos(b,'.mobProjectile(')<pos(b,'VULNERABLE_TO_SONAR_BOMB')<pos(b,'.hurt(') and not hit(b,'ESDamageTypes.SONAR') and not hit(b,'.explode(')
    b=body('common/entity/projectile/AethersentMeteor','onHit');assert pos(b,'.shouldHarm(')<pos(b,'invulnerableTime')<pos(b,'ESDamageTypes.METEOR')<pos(b,'.getEntityDamageSource(')<pos(b,'.hurt(')<pos(b,'.dropAndDiscard(')
    assert b[b.index(hit(b,'.getEntityDamageSource(')[0])-1]['operand'].endswith('.getOwner()Lnet/minecraft/world/entity/Entity;')
    assert after(b,'.hurt(')['opcode']=='0x57' and not hit(b,'.explode(')
    for method in ['addAdditionalSaveData','readAdditionalSaveData']:
        assert not any(i['opcode']=='0xb7' and '.'+method+'(' in str(i.get('operand','')) for i in body('common/entity/projectile/AethersentMeteor',method))
    b=body('common/entity/projectile/ShotSeeds','onHitEntity');assert pos(b,'ESDamageTypes.SEEDS')<pos(b,'.modifyDamage(')<pos(b,'.length(')<pos(b,'.damageMultiplier(')<pos(b,'invulnerableTime')<pos(b,'.hurt(')<pos(b,'.doPostAttackEffectsWithItemSource(')<pos(b,'.igniteForSeconds(')
    assert after(b,'.hurt(')['opcode']=='0x99' and not hit(b,'.shouldHarm(')
    assert not any(m['name'] in ['addAdditionalSaveData','readAdditionalSaveData'] for m in w[ES+'common/entity/projectile/ShotSeeds.class']['methods'])
    b=body('common/item/combat/SeedsLauncherItem','draw');assert hit(b,'.processProjectileCount(') and hit(b,'.useAmmo(')
    b=body('common/handler/ESCommonHandler','onPostLivingHurt');assert pos(b,'METEOR_COUNTERATTACK_CHANCE')<pos(b,'.createMeteorShower(')
    b=body('common/handler/ESCommonHandler','onProjectileImpact');star=pos(b,'eternal_starlight:starfall');assert next(i['offset'] for i in hit(b,'ARROW_TYPE') if i['offset']>star)<pos(b,'.createMeteorShower(')
    tags={x['id']:set(x['tags']) for x in read_json(OUT/'eternalstarlight-damage-tags.json')['declarations']}
    assert 'minecraft:bypasses_shield' in tags['eternal_starlight:sonar'] and 'minecraft:is_projectile' in tags['eternal_starlight:seeds']
    assert not tags['eternal_starlight:meteor'] & {'minecraft:is_projectile','minecraft:is_explosion','minecraft:is_fire','minecraft:bypasses_armor'}
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==8 and len(d['delivery_paths'])==15
    assert all(v in (OUT/(STEM+'-review.md')).read_text(encoding='utf-8') for v in FACTS.values())
    return dict(schema='tno.external_effects.es_sonar_meteor_seeds_integrity.v1',checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),reviewed_packages=8,reviewed_paths=15,custom_damage_types_closed=3,semantic_order_source_admission_checks='PASS',accepted_counts_preserved=preserve_section(d),promoted_records=0,whole_eternalstarlight_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_sonar_meteor_seeds();write_json(OUT/'eternalstarlight-r2h4a-integrity.json',d);print(json.dumps(d,indent=2))
