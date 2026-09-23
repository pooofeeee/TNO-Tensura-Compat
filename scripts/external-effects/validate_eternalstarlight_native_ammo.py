from catalog_common import *
from native_evidence import collect
from collect_eternalstarlight_native_ammo import ES,census
from assemble_eternalstarlight_native_ammo import CP,STEM,FACTS
from eternalstarlight_combat_common import preserve_section

def validate_native_ammo():
    e=read_json(OUT/'native-evidence/eternalstarlight-native-ammo.json');assert collect(read_json(OUT/'native-specifications/eternalstarlight-native-ammo.json'))==e
    assert census()==read_json(OUT/'eternalstarlight-native-ammo-census.json')
    w={x['entry']:x for x in e['witnesses']}
    def body(cl,method):return next(m['instructions'] for m in w[ES+cl+'.class']['methods'] if m['name']==method and m.get('instructions'))
    def hit(b,s):return [i for i in b if str(s) in str(i.get('operand',''))]
    def pos(b,s):return hit(b,s)[0]['offset']
    def after(b,s):return b[b.index(hit(b,s)[0])+1]
    p='common/entity/projectile/'
    b=body(p+'AshenSnowball','onHitEntity');assert pos(b,'Blaze')<pos(b,'.thrown(')<pos(b,'.hurt(')<pos(b,'MobEffects.BLINDNESS') and after(b,'.hurt(')['opcode']=='0x99'
    b=body(p+'AshenSnowball','onHit');assert pos(b,'.onHit(')<pos(b,'.shouldHarm(')<pos(b,'MOVEMENT_SLOWDOWN')<pos(b,'.discard(') and not hit(b,'.hurt(')
    b=body(p+'FrozenBomb','onHit');assert pos(b,'ExplosionInteraction.TNT')<pos(b,'.explode(')<pos(b,'.shouldHarm(')<pos(b,'.canFreeze(')<pos(b,'.setTicksFrozen(')<pos(b,'MOVEMENT_SLOWDOWN') and not hit(b,'.hurt(')
    b=body(p+'GlaciteArrow','doPostHurtEffects');assert pos(b,'.canFreeze(')<pos(b,'.setTicksFrozen(') and not hit(b,'.hurt(')
    b=body(p+'MalariteArrow','doPostHurtEffects');assert pos(b,'MobEffects.POISON')<pos(b,'.getEffectSource(')<pos(b,'.addEffect(')
    b=body(p+'AethersentArrow','doPostHurtEffects');assert not hit(b,'.hurt(') and not hit(b,'.explode(') and not hit(b,'AethersentMeteor')
    b=body(p+'AirSacArrow','applyGravity');assert pos(b,'.isInWater(')<pos(b,'.getGravity(')<pos(b,'.setDeltaMovement(') and hit(b,0.5)
    b=body(p+'ThrownSpear','onHitEntity');assert pos(b,'.getDamageScale(')<pos(b,'.getItemDamage(')<pos(b,'.thrown(')<pos(b,'.modifyDamage(')<pos(b,'dealtDamageZ')<pos(b,'.hurt(')<pos(b,'EntityType.ENDERMAN')<pos(b,'.doPostAttackEffectsWithItemSource(')<pos(b,'.doPostHurtEffects(')
    assert not hit(b,'.playerAttack(') and not hit(b,'.mobAttack(') and not hit(b,'.length(') and after(b,'.hurt(')['opcode']=='0x99'
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==9 and len(d['delivery_paths'])==16
    assert all(v in (OUT/(STEM+'-review.md')).read_text(encoding='utf-8') for v in FACTS.values())
    return dict(schema='tno.external_effects.es_native_ammo_integrity.v1',checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),reviewed_packages=9,reviewed_paths=16,semantic_order_source_admission_checks='PASS',accepted_counts_preserved=preserve_section(d),promoted_records=0,whole_eternalstarlight_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_native_ammo();write_json(OUT/'eternalstarlight-r2h5a-integrity.json',d);print(json.dumps(d,indent=2))
