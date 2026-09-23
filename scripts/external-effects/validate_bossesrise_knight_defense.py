from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_bossesrise_knight_defense import census,arena_entity,KNIGHT
from collect_bossesrise_foundation import PKG
from assemble_bossesrise_knight_defense import FACTS,CP,STEM
from bossesrise_combat_common import preserve_section

def validate_knight_defense():
    e=read_json(OUT/'native-evidence/bossesrise-knight-defense.json');assert collect(read_json(OUT/'native-specifications/bossesrise-knight-defense.json'))==e
    r=read_json(OUT/'reference-evidence/bossesrise-knight-defense-244.json');assert reference_collect(read_json(OUT/'reference-specifications/bossesrise-knight-defense-244.json'))==r
    c=read_json(OUT/'bossesrise-knight-defense-census.json');assert census()==c
    arena=read_json(OUT/'bossesrise-knight-arena-initialization.json');assert arena_entity()==arena and len(arena['entities'])==1
    a=arena['entities'][0];assert a['BossPhase']==-1 and a['SpawnAnimtime']==0 and a['UndeadCinematic']==0 and a['Health']==150 and 'ImmuneStacks' not in a and 'HpGate75' not in a
    w={x['entry']:x for x in e['witnesses']};rw={x['entry']:x for x in r['witnesses']}
    def b(short,n):return next(m['instructions'] for m in w[PKG+short+'.class']['methods'] if m['name']==n)
    def h(body,s):return [i for i in body if s in str(i.get('operand',''))]
    v=b(KNIGHT,'processHurt');order=[h(v,s)[0]['offset'] for s in ['.BYPASSES_INVULNERABILITY','.isCinematic(','.isInvulnerable(','.hpGate75','.hpGate50','.hpGate25']];assert order==sorted(order)
    assert all(h(v,'.'+s+'L') for s in ['IN_FIRE','FALL','LIGHTNING_BOLT','WITHER','WITHER_SKULL'])
    assert h(v,'.removeOneImmuneStack(')[0]['offset']<h(v,'java/lang/Math.min(')[0]['offset']
    assert any(i.get('operand')==20.0 for i in v) and any(isinstance(i.get('operand'),float) and abs(i['operand']-.1)<.000001 for i in v)
    entity=next(m['instructions'] for m in rw['net/minecraft/world/entity/Entity.class']['methods'] if m['name']=='isInvulnerableTo')
    assert h(entity,'.invulnerableZ') and not h(entity,'.isInvulnerable(') and h(entity,'.isEntityInvulnerableTo(')
    mark='entity/boss/knight/KnightMarkEntity';v=b(mark,'hurt')
    assert any(i.get('operand')==2.0 for i in v) and any(i.get('operand')==4.0 for i in v)
    assert h(v,'.removeOneImmuneStack(')[0]['offset']<h(v,'.processHurt(')[0]['offset']
    ix=next(i for i,x in enumerate(v) if '.processHurt(' in str(x.get('operand','')));assert v[ix+1]['opcode']=='0x57'
    assert any(i['operand']=='Owner' for i in b(mark,'addAdditionalSaveData')) and any(i['operand']=='owner' for i in b(mark,'readAdditionalSaveData'))
    assert h(b(mark,'baseTick'),'.getOwnerUUID(') and any(i.get('operand')==100.0 for i in b(mark,'baseTick'))
    v=b(KNIGHT,'placeMark');assert h(v,'.setOwnerUUID(') and h(v,'.startRiding(') and h(v,'.addFreshEntity(')
    ix=next(i for i,x in enumerate(v) if '.startRiding(' in str(x.get('operand','')));assert v[ix+1]['opcode']=='0x57'
    for n,opcode in [('canFreeze','0x3'),('isPushable','0x3'),('fireImmune','0x4')]:assert b(KNIGHT,n)[0]['opcode']==opcode
    v=b(KNIGHT,'shouldCancelDeath');assert h(v,'.isTimerDone(') and any(i.get('operand')=='fake_dead' for i in v) and any(i.get('operand')=='jump_back' for i in v)
    v=b(KNIGHT,'tick');assert h(v,'.setHealth(') and h(v,'.fellOutOfWorld(') and h(v,'.playerAttack(') and any(i.get('operand')==999.0 for i in v)
    assert h(b(KNIGHT,'baseTick'),'UnderworldKnightOnEntityTickUpdateProcedure.execute(')
    # No native positive writer is hidden among unrelated field users: only initialization/save/read,
    # legacy decrement and native hurt guards read this field in the whole installed artifact.
    spawn=[x for x in c['rows'] if '.DATA_SPAWN_ANIMTIME' in str(x['hits'])]
    assert all(x['method'] in ['defineSynchedData','addAdditionalSaveData','readAdditionalSaveData','onSpawn','hurt'] for x in spawn)
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==5 and len(d['delivery_paths'])==15
    assert not any(m['stage_scaling_needed'] for m in d['mechanic_packages']) and not d['remaining_subsection_native_ambiguities']
    preserved=preserve_section(d);assert preserved==dict(effects=543,sources=1303,paths=1303,comparisons=543,primitives=717)
    return dict(schema='tno.external_effects.bossesrise_knight_defense_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),reference_witnesses=len(r['witnesses']),census_methods=len(c['rows']),native_arena_knights=1,mechanic_packages=5,native_paths=15,numeric_stage_candidates=0,stack_break_independent_of_HP=True,mark_Owner_owner_roundtrip_mismatch=True,legacy_spawn_counter_dormant_in_arena=True,accepted_counts_preserved=preserved,whole_mod_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_knight_defense();write_json(OUT/'bossesrise-r2i3a-integrity.json',d);print(json.dumps(d,indent=2))
