from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_eternalstarlight_energy import ES,hierarchy,producer_census
from assemble_eternalstarlight_energy import CP,STEM,FACTS
from eternalstarlight_combat_common import preserve_section

def validate_energy():
    e=read_json(OUT/'native-evidence/eternalstarlight-energy.json');assert collect(read_json(OUT/'native-specifications/eternalstarlight-energy.json'))==e
    r=read_json(OUT/'reference-evidence/eternalstarlight-energy-244.json');assert reference_collect(read_json(OUT/'reference-specifications/eternalstarlight-energy-244.json'))==r
    v=read_json(OUT/'vanilla-evidence/eternalstarlight-energy.json');assert prepare(read_json(OUT/'vanilla-specifications/eternalstarlight-energy.json'))==v
    routing=read_json(OUT/'reference-routing/eternalstarlight-energy.json');assert sha256(routing['archive'])==routing['sha256']
    with zipfile.ZipFile(routing['archive']) as z:assert not(set(routing['absent_entries'])&set(z.namelist()))
    assert producer_census()==read_json(OUT/'eternalstarlight-energy-producer-census.json')
    h=read_json(OUT/'eternalstarlight-firework-weapon-hierarchy.json');assert hierarchy()==h
    assert [i['opcode'] for i in h['classes'][0]['getWeaponItem'][0]]==['0x1','0xb0']
    assert all('getWeaponItem' not in [m['name'] for m in c['declared_methods']] for c in h['classes'][1:])
    w={x['entry']:x for x in e['witnesses']}
    def body(cl,method):return next(m['instructions'] for m in w[ES+cl+'.class']['methods'] if m['name']==method)
    def hit(b,s):return [i for i in b if s in str(i.get('operand',''))]
    def pos(b,s):return hit(b,s)[0]['offset']
    def after(b,s):return b[b.index(hit(b,s)[0])+1]
    spark=body('common/entity/projectile/EnergySpark','hurtTarget');assert pos(spark,'.invulnerableTimeI')<pos(spark,'.hurt(')<pos(spark,'.discard(') and after(spark,'.hurt(')['opcode']=='0x57'
    assert not hit(spark,'.shouldHarm(') and not hit(spark,'.igniteForSeconds(')
    ball=body('common/entity/projectile/BallLightning','tick');assert hit(ball,'ESDamageTypes.ELECTRIC_SHOCK') and not hit(ball,'.blockHitResult(') and after(ball,'.hurt(')['opcode']=='0x99'
    burst=body('common/entity/projectile/BallLightning','explodeAndDiscard');assert hit(burst,'ESDamageTypes.ENERGIZED_FLAME') and hit(burst,'net/minecraft/world/entity/player/Player') and after(burst,'.hurt(')['opcode']=='0x57' and not hit(burst,'.igniteForSeconds(') and not hit(burst,'Level.explode(')
    flame=body('common/entity/attack/EnergizedFlame','tick');assert pos(flame,'.hurt(')<pos(flame,'.igniteForSeconds(') and after(flame,'.hurt(')['opcode']=='0x57'
    primary=body('common/entity/projectile/ThrownBoomerang','onHitEntity');assert pos(primary,'.thrown(')<pos(primary,'.dealtDamageZ')<pos(primary,'.hurt(')<pos(primary,'EntityType.ENDERMAN')<pos(primary,'.playerAttack(')<pos(primary,'.doPostHurtEffects(')
    arc=body('common/entity/projectile/ThrownEnergyBoomerang','doPostHurtEffects');assert pos(arc,'.igniteForSeconds(')<pos(arc,'.isOnCooldown(')<pos(arc,'.invulnerableTimeI')<pos(arc,'.hurt(')<pos(arc,'.setCooldown(') and after(arc,'.hurt(')['opcode']=='0x99'
    smash=body('common/entity/living/boss/golem/StarlightGolemSmashPhase','tick');assert hit(smash,'ESDamageTypes.GROUND_SMASH') and hit(smash,'ESDamageTypes.getDamageSource(') and not hit(smash,'.shouldHarm(')
    debris=body('common/entity/misc/ESFallingBlock','tick');assert hit(debris,'.fallingBlock(') and after(debris,'.hurt(')['opcode']=='0x57' and w[ES+'common/entity/misc/ESFallingBlock.class']['superclass']=='net/minecraft/world/entity/Entity'
    tags={x['id']:set(x['tags']) for x in read_json(OUT/'eternalstarlight-damage-tags.json')['declarations']}
    for id in ['electric_shock','energized_flame','ground_smash']:assert not tags['eternal_starlight:'+id]&{'minecraft:is_fire','minecraft:is_lightning','minecraft:bypasses_armor','minecraft:bypasses_shield','minecraft:bypasses_enchantments'}
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==7 and len(d['delivery_paths'])==15
    assert all(s in (OUT/(STEM+'-review.md')).read_text(encoding='utf-8') for s in FACTS.values())
    return dict(schema='tno.external_effects.es_energy_integrity.v1',checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),loader_witnesses=len(r['witnesses']),raw_fallback_classes=len(v['classes']),reviewed_packages=7,reviewed_paths=15,semantic_order_source_admission_checks='PASS',accepted_counts_preserved=preserve_section(d),promoted_records=0,whole_eternalstarlight_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_energy();write_json(OUT/'eternalstarlight-r2h3a-integrity.json',d);print(json.dumps(d,indent=2))
