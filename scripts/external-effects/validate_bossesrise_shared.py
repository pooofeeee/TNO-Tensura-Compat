from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_bossesrise_shared import census
from collect_bossesrise_foundation import PKG
from assemble_bossesrise_shared import FACTS,CP,STEM
from bossesrise_combat_common import preserve_section

def validate_shared():
    e=read_json(OUT/'native-evidence/bossesrise-shared.json');assert collect(read_json(OUT/'native-specifications/bossesrise-shared.json'))==e
    r=read_json(OUT/'reference-evidence/bossesrise-shared-244.json');assert reference_collect(read_json(OUT/'reference-specifications/bossesrise-shared-244.json'))==r
    c=read_json(OUT/'bossesrise-shared-census.json');assert census()==c and len(c['rows'])==39
    w={x['entry']:x for x in e['witnesses']};rw={x['entry']:x for x in r['witnesses']}
    def methods(s,n):return [m for m in w[PKG+s+'.class']['methods'] if m['name']==n]
    def b(s,n):return methods(s,n)[0]['instructions']
    def h(body,s):return [i for i in body if s in str(i.get('operand',''))]
    for base in ['entity/boss/AbstractBossEntity','entity/boss/AbstractStateBossEntity']:
        v=next(m['instructions'] for m in methods(base,'attackEntity') if 'DamageSource;' in m['descriptor'])
        order=[h(v,s)[0]['offset'] for s in ['ATTACK_DAMAGE','modifyDamage(','.hurt(','.doPostAttackEffects(','.setLastHurtMob(']];assert order==sorted(order)
        assert any(i['opcode']=='0x99' and i['offset']>h(v,'.hurt(')[0]['offset'] for i in v) or any(i['opcode']=='0x9a' and i['offset']>h(v,'.hurt(')[0]['offset'] for i in v)
        death=b(base,'maybeCancelDeath');order=[h(death,s)[0]['offset'] for s in ['isDeadOrDying(','.BYPASSES_INVULNERABILITY','.shouldCancelDeath(','.setHealth(']];assert order==sorted(order)
        assert any(isinstance(i.get('operand'),float) and abs(i['operand']-.1)<.000001 for i in death)
        assert not h(death,'.heal(')
    v=b('entity/boss/AbstractStateBossEntity','actuallyHurt');assert h(v,'.actuallyHurt(')[0]['offset']<h(v,'.maybeCancelDeath(')[0]['offset']
    native=next(m['instructions'] for m in rw['net/minecraft/world/entity/LivingEntity.class']['methods'] if m['name']=='actuallyHurt')
    order=[h(native,s)[0]['offset'] for s in ['onLivingDamagePre(','.setHealth(','.onDamageTaken(','.onLivingDamagePost(']];assert order==sorted(order)
    v=b('entity/boss/AbstractStateBossEntity','shouldCancelDeath');assert [i['opcode'] for i in v]==['0x3','0xac']
    v=b('entity/boss/AbstractStateBossEntity','simulatePlayerKill');assert h(v,'.PLAYER_ATTACK') and h(v,'.getSourceEntity(') and any(i.get('operand')==999.0 for i in v)
    assert not any('.onDying(' in str(x['hits']) for x in c['rows'])
    assert any('.onSpawn(' in str(x['hits']) and 'UnderworldKnightOnEntityTickUpdateProcedure' in x['entry'] for x in c['rows'])
    v=b('entity/boss/part/AbstractEntityPart','hurt');assert len(h(v,'.hurt('))==1 and h(v,'.getParent(') and not any(i['opcode'] in ['0x6a','0x6e'] for i in v)
    v=b('entity/OwnableByAllEntity','getOwner');assert h(v,'.getOwnerUUID(') and h(v,'.getEntity(') and h(v,'.getPlayerByUUID(')
    for cls in ['OwnerHurtByTargetGoal','OwnerHurtTargetGoal','DoNotAttackOwnerGoal']:
        v=b('entity/OwnableByAllEntity$'+cls,'canAttack');assert h(v,'.getOwner(') and h(v,'.canAttack(')
    v=next(m['instructions'] for m in methods('util/SpatialUtil','pushEntity') if m['descriptor'].endswith(';D)V'))
    assert h(v,'.dot(') and h(v,'.normalize(') and h(v,'.push(') and not h(v,'.knockback(') and h(v,'PlayerPushMessage.<init>')
    assert h(b('network/PlayerPushMessage','handleData'),'CLIENTBOUND')
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==6 and len(d['delivery_paths'])==13
    assert sum(m['stage_scaling_needed'] for m in d['mechanic_packages'])==1 and not d['remaining_subsection_native_ambiguities']
    preserved=preserve_section(d);assert preserved==dict(effects=543,sources=1303,paths=1303,comparisons=543,primitives=717)
    return dict(schema='tno.external_effects.bossesrise_shared_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),reference_witnesses=len(r['witnesses']),shared_caller_methods=39,mechanic_packages=6,native_paths=13,numeric_stage_candidates=1,death_callback_order='legacy_before_Post__state_after_Post',unused_onDying_not_promoted=True,accepted_counts_preserved=preserved,whole_mod_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_shared();write_json(OUT/'bossesrise-r2i2b-integrity.json',d);print(json.dumps(d,indent=2))
