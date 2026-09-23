from catalog_common import *
from native_evidence import collect
from collect_eternalstarlight_ether_blade_wilt import ES,census
from assemble_eternalstarlight_ether_blade_wilt import CP,STEM,FACTS
from eternalstarlight_combat_common import preserve_section

def validate_ether_blade_wilt():
    e=read_json(OUT/'native-evidence/eternalstarlight-ether-blade-wilt.json');assert collect(read_json(OUT/'native-specifications/eternalstarlight-ether-blade-wilt.json'))==e
    assert census()==read_json(OUT/'eternalstarlight-ether-blade-wilt-census.json')
    w={x['entry']:x for x in e['witnesses']}
    def body(cl,method):return next(m['instructions'] for m in w[ES+cl+'.class']['methods'] if m['name']==method and m.get('instructions'))
    def hit(b,s):return [i for i in b if str(s) in str(i.get('operand',''))]
    def pos(b,s):return hit(b,s)[0]['offset']
    def after(b,s):return b[b.index(hit(b,s)[0])+1]
    b=body('common/entity/projectile/ThioquartzShard','onHitEntity');assert pos(b,'.getOwner(')<pos(b,'ESDamageTypes.ETHER')<pos(b,'.hurt(')<pos(b,'IN_ETHER_TICKS')<pos(b,'.discard(')
    assert after(b,'.hurt(')['opcode']=='0x99' and not hit(b,'.shouldHarm(') and not hit(b,'invulnerableTime')
    b=body('common/entity/projectile/ThrownShatteredBlade','onHitEntity');assert pos(b,'ATTACK_DAMAGE')<pos(b,'ESDamageTypes.SHATTERED_BLADE')<pos(b,'.modifyDamage(')<pos(b,'dealtDamageZ')<pos(b,'.hurt(')<pos(b,'EntityType.ENDERMAN')<pos(b,'.playerAttack(')<pos(b,'.doPostAttackEffectsWithItemSource(')
    assert after(b,'.hurt(')['opcode']=='0x99' and not hit(b,'.length(') and not hit(b,'.getBaseDamage(') and not hit(b,'.onHitEntity(')
    b=body('common/entity/projectile/WiltedPetal','onHitEntity');assert pos(b,'ESDamageTypes.WILT')<pos(b,'.hurt(')<pos(b,'.discard(') and after(b,'.hurt(')['opcode']=='0x57' and not hit(b,'.addEffect(')
    b=body('common/handler/ESCommonHandler','onEntityTick');assert pos(b,'AbstractArrow')<pos(b,'.inGroundZ')<pos(b,'eternal_starlight:wilted')<pos(b,'MobEffects.WITHER')<pos(b,'WiltedPetal')
    ether=pos(b,'ESDamageTypes.ETHER');assert pos(b,'ETHER_RESISTANCE')<ether<pos(b,'EtherFluid.armorModifier(')
    assert any('IN_ETHER_TICKS' in str(i.get('operand','')) for i in b if i['offset']>ether)
    b=body('common/block/fluid/EtherFluid','armorModifier');assert hit(b,'Operation.ADD_VALUE')
    b=body('common/item/combat/WiltedCrossbowItem','createProjectile');assert pos(b,'eternal_starlight:wilted')<pos(b,'AbstractArrow')<pos(b,'.setBaseDamage(') and hit(b,1.5)
    b=body('common/mixin/EntityMixin','checkInsideBlocks');assert pos(b,'ESTags$Fluids.ETHER')<pos(b,'IN_ETHER')<pos(b,'.setData(')
    tags={x['id']:set(x['tags']) for x in read_json(OUT/'eternalstarlight-damage-tags.json')['declarations']}
    assert {'minecraft:bypasses_armor','minecraft:bypasses_shield','minecraft:bypasses_enchantments'}<=tags['eternal_starlight:ether']
    assert not tags['eternal_starlight:ether']&{'minecraft:bypasses_resistance','minecraft:is_projectile','minecraft:bypasses_invulnerability'}
    for k in ['wilt','shattered_blade']:assert 'minecraft:is_projectile' in tags['eternal_starlight:'+k]
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==8 and len(d['delivery_paths'])==13
    assert all(v in (OUT/(STEM+'-review.md')).read_text(encoding='utf-8') for v in FACTS.values())
    return dict(schema='tno.external_effects.es_ether_blade_wilt_integrity.v1',checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),reviewed_packages=8,reviewed_paths=13,custom_damage_types_closed=3,semantic_order_source_admission_checks='PASS',accepted_counts_preserved=preserve_section(d),promoted_records=0,whole_eternalstarlight_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_ether_blade_wilt();write_json(OUT/'eternalstarlight-r2h4b-integrity.json',d);print(json.dumps(d,indent=2))
