from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_eternalstarlight_special_weapons import ES,census
from assemble_eternalstarlight_special_weapons import CP,STEM,FACTS
from eternalstarlight_combat_common import preserve_section

def validate_special_weapons():
    e=read_json(OUT/'native-evidence/eternalstarlight-special-weapons.json');assert collect(read_json(OUT/'native-specifications/eternalstarlight-special-weapons.json'))==e
    r=read_json(OUT/'reference-evidence/eternalstarlight-special-weapons-244.json');assert reference_collect(read_json(OUT/'reference-specifications/eternalstarlight-special-weapons-244.json'))==r
    assert census()==read_json(OUT/'eternalstarlight-special-weapons-census.json')
    w={x['entry']:x for x in e['witnesses']+r['witnesses']}
    def body(cl,method):return next(m['instructions'] for m in w[cl+'.class']['methods'] if m['name']==method and m.get('instructions'))
    def es(cl,method):return body(ES+cl,method)
    def hit(b,s):return [i for i in b if str(s) in str(i.get('operand',''))]
    def pos(b,s):return hit(b,s)[0]['offset']
    def after(b,s):return b[b.index(hit(b,s)[0])+1]
    b=es('common/item/combat/CrescentSpearItem','releaseUsing');assert pos(b,'.clip(')<pos(b,'.getTridentSpinAttackStrength(')<pos(b,'.push(')<pos(b,'.startAutoSpinAttack(')<pos(b,'.addCooldown(')
    b=body('net/minecraft/world/entity/LivingEntity','checkAutoSpinAttack');assert pos(b,'.doAutoAttackOnTouch(')<pos(b,'.setDeltaMovement(')<pos(b,'.setLivingEntityFlag(')<pos(b,'autoSpinAttackDmgF')<pos(b,'autoSpinAttackItemStack')
    b=es('common/mixin/LivingEntityMixin','doCrescentSpearDamage');assert pos(b,'.shouldHarm(')<pos(b,'attackStrengthTicker')<pos(b,'.attack(')<pos(b,'invulnerableTime')<pos(b,'CRESCENT_SPEAR_DASH')
    assert len(hit(b,'CRESCENT_SPEAR_DASH'))==1 and not hit(b,'.hurt(')
    b=es('common/item/combat/HammerItem','performCriticalAttack');assert pos(b,'.playerAttack(')<pos(b,'ATTACK_DAMAGE')<pos(b,'.hurt(')<pos(b,'KNOCKBACK_RESISTANCE') and after(b,'.hurt(')['opcode']=='0x99' and not hit(b,'.shouldHarm(')
    b=body('net/minecraft/world/entity/player/Player','attack');assert pos(b,'.fireCriticalHit(')<pos(b,'.fireSweepAttack(')<pos(b,'.hurt(')<pos(b,'.hurtEnemy(')
    b=es('common/mixin/PlayerMixin','damageShield');assert pos(b,'.hurtAndBreak(')<pos(b,'.stopUsingItem(')<pos(b,'.addCooldown(')
    b=es('common/handler/ESCommonHandler','onModifyLivingHurtDamage');assert pos(b,'CONCENTRATED_TARGET')<pos(b,'CONCENTRATED_WEAPON')<pos(b,'CONCENTRATION_LEVEL')<pos(b,'WARHAMMER_PENDANT')<pos(b,'ESDataAttachments.MOVEMENT')<pos(b,'BYPASSES_INVULNERABILITY')
    b=es('neoforge/event/CommonEvents','onShieldBlock');assert pos(b,'.getOriginalBlock(')<pos(b,'.onShieldBlock(') and not hit(b,'.getBlocked(')
    b=es('common/handler/ESCommonHandler','onShieldBlock');assert pos(b,'.getDirectEntity(')<pos(b,'.canFreeze(')<pos(b,'.setTicksFrozen(') and not hit(b,'.hurt(')
    b=body('net/minecraft/world/entity/projectile/Projectile','hitTargetOrDeflectSelf');assert pos(b,'.deflection(')<pos(b,'.getOwner(')<pos(b,'.deflect(')<pos(b,'.onHit(')
    b=es('common/item/combat/UnrealiumCrossbowItem','createProjectile');assert pos(b,'AbstractArrow')<pos(b,'.getPierceLevel(')<pos(b,'.setBaseDamage(')<pos(b,'.setPierceLevel(')
    b=es('common/item/combat/MoonringGreatswordItem','postHurtEnemy');assert pos(b,'.isOnCooldown(')<pos(b,'.createThorn(')<pos(b,'.setCooldown(')
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==11 and len(d['delivery_paths'])==17
    ids={p['id'] for p in d['delivery_paths']}
    for x in d['existing_package_deliveries']:
        assert set(x['delivery_paths'])<=ids and x['package_id'] in {m['id'] for m in read_json(OUT/x['section'])['mechanic_packages']}
    assert all(v in (OUT/(STEM+'-review.md')).read_text(encoding='utf-8') for v in FACTS.values())
    return dict(schema='tno.external_effects.es_special_weapons_integrity.v1',checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),loader_witnesses=len(r['witnesses']),reviewed_packages=11,reviewed_paths=17,existing_package_extensions=2,semantic_order_source_admission_checks='PASS',accepted_counts_preserved=preserve_section(d),promoted_records=0,whole_eternalstarlight_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_special_weapons();write_json(OUT/'eternalstarlight-r2h5b-integrity.json',d);print(json.dumps(d,indent=2))
