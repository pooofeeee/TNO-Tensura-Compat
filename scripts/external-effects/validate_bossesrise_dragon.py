from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_bossesrise_dragon import census,profiles,DRAGON,GUARDS
from collect_bossesrise_foundation import PKG
from assemble_bossesrise_dragon import FACTS,CP,STEM
from bossesrise_combat_common import preserve_section

def validate_dragon():
    e=read_json(OUT/'native-evidence/bossesrise-dragon.json');assert collect(read_json(OUT/'native-specifications/bossesrise-dragon.json'))==e
    r=read_json(OUT/'reference-evidence/bossesrise-dragon-244.json');assert reference_collect(read_json(OUT/'reference-specifications/bossesrise-dragon-244.json'))==r
    raw=read_json(OUT/'vanilla-evidence/bossesrise-dragon.json');assert prepare(read_json(OUT/'vanilla-specifications/bossesrise-dragon.json'))==raw
    c=read_json(OUT/'bossesrise-dragon-census.json');assert census()==c
    p=read_json(OUT/'bossesrise-dragon-source-profiles.json');assert profiles()==p
    table={x['id']:x['tags'] for x in p['profiles']};assert len(table)==8
    assert 'minecraft:is_fire' not in table['minecraft:arrow'] and 'minecraft:is_projectile' in table['minecraft:arrow']
    assert 'minecraft:bypasses_armor' not in table['minecraft:in_fire'] and 'minecraft:bypasses_armor' in table['minecraft:on_fire']
    assert 'minecraft:is_fire' not in table['minecraft:magic'] and 'neoforge:is_magic' in table['minecraft:magic']
    assert not any(tag in tags for tags in table.values() for tag in ['minecraft:bypasses_resistance','minecraft:bypasses_effects','minecraft:bypasses_invulnerability','minecraft:bypasses_cooldown','minecraft:bypasses_enchantments'])
    w={x['entry']:x for x in e['witnesses']};rw={x['entry']:x for x in r['witnesses']}
    def b(short,n):return next(m['instructions'] for m in w[PKG+short+'.class']['methods'] if m['name']==n)
    def rb(short,n):return next(m['instructions'] for m in rw[short+'.class']['methods'] if m['name']==n)
    def h(v,s):return [i for i in v if s in str(i.get('operand',''))]
    def pop_after(v,s):
        ix=next(i for i,x in enumerate(v) if s in str(x.get('operand','')));assert v[ix+1]['opcode']=='0x57',s
    v=b(DRAGON,'hurt');assert h(v,'.BYPASSES_INVULNERABILITY')[0]['offset']<h(v,'.DATA_BOSS_PHASE')[0]['offset']<h(v,'.IN_FIRE')[0]['offset']<h(v,'.getEntity(')[0]['offset']
    assert len(h(v,'.getEntity('))==2 and not h(v,'.getDirectEntity(')
    assert h(v,'IceSpikeProjectileEntity') and any(i['opcode']=='0x6a' for i in v) and any(i['opcode']=='0x6e' for i in v)
    assert h(b('entity/boss/yeti/IceSpikeProjectileEntity','onHitEntity'),'.indirectMagic(')
    assert not any(i['opcode']=='0xb2' and '.DRAGON_ATK' in str(i['operand']) for row in c['rows'] for i in row['hits'])
    for n,opcode in [('canFreeze','0x3'),('isPushable','0x3'),('fireImmune','0x4'),('causeFallDamage','0x3')]:assert b(DRAGON,n)[0]['opcode']==opcode
    v=b(DRAGON,'tick');assert h(v,'.manageState(')[0]['offset']<h(v,'.handleAttackDamage(')[0]['offset']
    assert h(v,'.PLAYER_ATTACK') and any(i.get('operand')==999999.0 for i in v);pop_after(v,'.hurt(')
    v=b(DRAGON,'handleAttackDamage');assert not h(v,'.isCinematic(') and not h(v,'.isDeath(') and len(h(v,'.dealMeleeAttackDamage('))==3
    v=b(DRAGON,'lambda$dealMeleeAttackDamage$6');pop_after(v,'.attackEntity(');assert h(v,'.push(') and not h(v,'.hasLineOfSight(')
    v=b(DRAGON,'lambda$spawnFireBreath$5');assert h(v,'.FIRE_RESISTANCE') and h(v,'.magic(') and any(i.get('operand')==250 for i in v) and any(i.get('operand')==100 for i in v)
    assert h(v,'.setRemainingFireTicks(')[0]['offset']<h(v,'.hasEffect(')[0]['offset']<h(v,'.hurt(')[0]['offset'];pop_after(v,'.hurt(')
    v=b(DRAGON,'spawnFireBreath');assert h(v,'.isAir(') and h(v,'.COBBLESTONE') and h(v,'.FIRE') and h(v,'.players(')
    ball='entity/projectile/BlazingFireBallEntity'
    for n,callback in [('onHitEntity','BlazingFireBallProjectileHitsLivingEntityProcedure'),('onHitBlock','BlazingFireBallProjectileHitsBlockProcedure')]:
        v=b(ball,n);assert h(v,'AbstractArrow.'+n)[0]['offset']<h(v,callback)[0]['offset']
    entity=b('procedures/BlazingFireBallProjectileHitsLivingEntityProcedure','execute');assert h(entity,'.spawn(') and not h(entity,'.explode(') and not h(entity,'instanceof')
    block=b('procedures/BlazingFireBallProjectileHitsBlockProcedure','execute');assert h(block,'.spawn(')[0]['offset']<h(block,'.explode(')[0]['offset'] and h(block,'.NONE')
    v=b('procedures/BlazingFireBallWhileProjectileFlyingTickProcedure','execute');assert h(v,'.igniteForSeconds(') and not h(v,'.getOwner(') and not h(v,'.hurt(')
    v=b('entity/FireAreaEntity','tick');assert h(v,'.fireImmune(') and h(v,'.inFire(');pop_after(v,'.hurt(');assert h(v,'.hurt(')[0]['offset']<h(v,'.igniteForSeconds(')[0]['offset']
    assert not any(i['opcode']=='0xb8' and 'BlazingFireBallEntity.shoot(' in str(i['operand']) for row in c['rows'] if not row['entry'].endswith('/BlazingFireBallEntity.class') for i in row['hits'])
    for guard in GUARDS:
        short='entity/boss/dragon/guardians/'+guard+'Entity';assert w[PKG+short+'.class']['superclass']=='net/minecraft/world/entity/monster/Monster'
        assert h(b(short+'$1','canPerformAttack'),'.hasLineOfSight(') and h(b(short,'baseTick'),guard+'OnEntityTickUpdateProcedure.execute(')
    for guard in GUARDS[:2]:
        v=b('procedures/'+guard+'OnEntityTickUpdateProcedure','execute');assert h(v,'.MOB_ATTACK') and h(v,'.setDeltaMovement(') and not h(v,'.hasLineOfSight(');pop_after(v,'.hurt(')
    v=b('procedures/FlamingSkeletonGuardSwordOnEntityTickUpdateProcedure','execute');assert h(v,'.isBlocking(') and h(v,'.addCooldown(') and any(i.get('operand')==100 for i in v)
    v=rb('net/minecraft/world/level/Explosion','explode');pop_after(v,'.hurt(');assert h(v,'.onExplosionDetonate(') and h(v,'.getExplosionKnockback(')
    v=rb('net/minecraft/world/level/Explosion','getIndirectSourceEntityInternal');assert h(v,'PrimedTnt') and h(v,'Projectile') and h(v,'LivingEntity') and not h(v,'FireArea')
    v=rb('net/minecraft/world/entity/Entity','baseTick');assert h(v,'.onFire(')
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==14 and len(d['delivery_paths'])==23
    assert sum(m['stage_scaling_needed'] for m in d['mechanic_packages'])==9 and not d['remaining_subsection_native_ambiguities']
    preserved=preserve_section(d);assert preserved==dict(effects=543,sources=1303,paths=1303,comparisons=543,primitives=717)
    return dict(schema='tno.external_effects.bossesrise_dragon_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),reference_witnesses=len(r['witnesses']),raw_reference_classes=len(raw['classes']),native_source_profiles=8,mechanic_packages=14,native_paths=23,numeric_stage_candidates=9,causing_entity_not_direct_projectile_verified=True,independent_ignition_pool_explosion_guard_control_verified=True,unused_Dragon_damage_config_verified=True,accepted_counts_preserved=preserved,whole_mod_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_dragon();write_json(OUT/'bossesrise-r2i4-integrity.json',d);print(json.dumps(d,indent=2))
