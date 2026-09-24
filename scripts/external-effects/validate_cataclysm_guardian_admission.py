from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_cataclysm_guardian_admission import setter_calls,G,PKG
from assemble_cataclysm_guardian_admission import CP,STEM,FACTS,explosion_tags
from cataclysm_combat_common import preserve_section

def validate_guardian_admission():
    e=read_json(OUT/'native-evidence/cataclysm-guardian-admission.json');assert collect(read_json(OUT/'native-specifications/cataclysm-guardian-admission.json'))==e and len(e['witnesses'])==11
    r=read_json(OUT/'reference-evidence/cataclysm-guardian-admission-244.json');assert reference_collect(read_json(OUT/'reference-specifications/cataclysm-guardian-admission-244.json'))==r and len(r['witnesses'])==4
    v=read_json(OUT/'vanilla-evidence/cataclysm-guardian-admission.json');assert prepare(read_json(OUT/'vanilla-specifications/cataclysm-guardian-admission.json'))==v and len(v['classes'])==1
    u=read_json(OUT/'cataclysm-guardian-state-callers.json');assert setter_calls()==u and len(u['rows'])==4
    assert {(x['entry'].split('/')[-1],x['method']) for x in u['rows']}=={('AltarOfVoid_Block_Entity.class','spawnMyBoss'),('Ender_Guardian_Entity$1.class','start'),('Ender_Guardian_Entity.class','readAdditionalSaveData'),('Ender_Guardian_Entity.class','tick')}
    w={x['entry']:x for x in e['witnesses']+r['witnesses']}
    def body(path,name):return next(m['instructions'] for m in w[path+'.class']['methods'] if m['name']==name)
    def b(name):return body(PKG+G,name)
    def hits(ins,s):return [i for i in ins if s in str(i.get('operand',''))]
    def off(ins,s):return hits(ins,s)[0]['offset']
    def pos(ins,s):return next(j for j,i in enumerate(ins) if s in str(i.get('operand','')))
    ins=b('hurt');order=['GUARDIAN_MASS_DESTRUCTION','BYPASSES_INVULNERABILITY','.getDirectEntity(','.getIsHelmetless(','/AbstractArrow','/ShulkerBullet','/Ender_Guardian_Bullet_Entity','/AbstractGolem','LLibrary_Boss_Monster.hurt('];assert [off(ins,s) for s in order]==sorted(off(ins,s) for s in order)
    assert any(i.get('operand')==.5 for i in ins) and not hits(ins,'.getEntity(') and not hits(ins,'IS_PROJECTILE')
    ins=b('isInvulnerableTo');assert off(ins,'DamageTypes.IN_WALL')<off(ins,'LLibrary_Boss_Monster.isInvulnerableTo(')
    for method,field in [('DamageCap','damageCap'),('DpsCap','dpsCap'),('RangeLimit','rangeCap'),('NatureRegen','natureHeal')]:assert hits(b(method),'CMCommonConfig$EnderGuardian.'+field)
    ins=b('defineSynchedData');assert ins[pos(ins,'.IS_HELMETLESS')+1]['operand']==0 and ins[pos(ins,'.USED_MASS_DESTRUCTION')+1]['operand']==1
    ins=b('setIsHelmetless');assert all(any(i.get('operand')==n for i in ins) for n in [15.0,20.0]) and len(hits(ins,'.setBaseValue('))==4
    ins=b('isHelmetless');assert off(ins,'.getHealth(')<off(ins,'.getMaxHealth(') and any(i.get('operand')==2.0 for i in ins) and any(i['opcode']=='0x6e' for i in ins)
    ins=b('tick');assert off(ins,'LLibrary_Boss_Monster.tick(')<off(ins,'.setIsHelmetless(')<off(ins,'.BrokenHelmet(')<off(ins,'.isNoAi(')<off(ins,'.getUsedMassDestruction(')<off(ins,'GUARDIAN_MASS_DESTRUCTION')
    ins=b('readAdditionalSaveData');assert hits(ins,'is_Helmetless') and hits(ins,'used_mass_destruction') and hits(ins,'.setIsHelmetless(') and not hits(ins,'.BrokenHelmet(')
    ins=body(PKG+'blockentities/AltarOfVoid_Block_Entity','spawnMyBoss');order=['MobSpawnType.SPAWNER','.finalizeSpawn(','.setUsedMassDestruction(','.setHomePos(','.addFreshEntity('];assert [off(ins,s) for s in order]==sorted(off(ins,s) for s in order) and ins[pos(ins,'.setUsedMassDestruction(')-1]['operand']==0
    ins=body(PKG+G+'$1','start');assert ins[pos(ins,'.setUsedMassDestruction(')-1]['operand']==1
    ins=b('BrokenHelmet');assert off(ins,'.isClientSide')<off(ins,'ExplosionInteraction.TRIGGER')<off(ins,'Level.explode(') and any(i.get('operand')==2.0 for i in ins) and not hits(ins,'.hurt(')
    ins=b('teleport');order=['.blocksMotion(','EventHooks.onEnderTeleport(','.isCanceled(','.getTargetX(','.ProperTeleport(','.gameEvent('];assert [off(ins,s) for s in order]==sorted(off(ins,s) for s in order)
    ins=b('ProperTeleport');order=['.hasChunkAt(','.blocksMotion(','.teleportTo(','.noCollision(','.containsAnyLiquid('];assert [off(ins,s) for s in order]==sorted(off(ins,s) for s in order) and len(hits(ins,'.teleportTo('))==2 and off(ins,'.containsAnyLiquid(')<hits(ins,'.teleportTo(')[1]['offset']<off(ins,'.getNavigation(')
    ins=body(PKG+G+'$HugmeGoal','tick');assert off(ins,'.setTeleportPos(')<off(ins,'.teleport(') and ins[pos(ins,'.teleport(')+1]['opcode']=='0x57'
    ins=body(PKG+G+'$TeleportStrikeGoal','tick');assert hits(ins,'.teleportTo(') and all(not hits(ins,s) for s in ['.teleport(','onEnderTeleport','.ProperTeleport(','.containsAnyLiquid(','.noCollision(']) and all(any(i.get('operand')==n for i in ins) for n in [40,8.0,4.0,48])
    ins=body('net/neoforged/neoforge/event/EventHooks','onEnderTeleport');assert off(ins,'EnderEntity.<init>')<off(ins,'.post(')
    ins=body('net/minecraft/world/level/Explosion','makeDamageCalculator');assert hits(ins,'EntityBasedExplosionDamageCalculator.<init>')
    inherited=next(c for c in read_json(OUT/'cataclysm-boss-inheritance.json')['classes'] if c['entry']==PKG+G+'.class');assert 'canBeAffected' not in {m['method'] for m in inherited['overrides']}
    cfg=read_json(OUT/'cataclysm-installed-common-config.json')['values']['mobs']['ender_guardian'];assert cfg['cap_config']==dict(damage_cap=22.0,dps_cap=13.0,dps_limit_time=20,range_cap=12.0) and cfg['nature_heal_config']['nature_heal']==25.0
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==4 and len(d['delivery_paths'])==17 and sum(m['stage_scaling_needed'] for m in d['mechanic_packages'])==1 and len(d['reused_mechanic_bindings'])==2
    tags=explosion_tags();assert d['source_paths'][0]['tags']==tags and {'minecraft:is_explosion','minecraft:no_knockback'}<=set(tags) and not set(tags)&{'minecraft:bypasses_armor','minecraft:bypasses_shield','minecraft:bypasses_effects','minecraft:bypasses_resistance','minecraft:bypasses_enchantments'}
    assert not d['remaining_subsection_native_ambiguities'] and all(p['runtime_status']=='NOT_RUN' for p in d['delivery_paths']);preserved=preserve_section(d);assert preserved==dict(effects=669,sources=1620,paths=1620,comparisons=669,primitives=882)
    return dict(schema='tno.external_effects.cataclysm_guardian_admission_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',native_witnesses=11,reference_witnesses=4,vanilla_witnesses=1,state_setter_caller_methods=4,mechanic_packages=4,delivery_paths=17,new_numeric_scaling_points=1,reused_shared_mechanics=2,accepted_counts_preserved=preserved,promoted_records=0,whole_mod_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_guardian_admission();write_json(OUT/'cataclysm-r2k3a-integrity.json',d);print(json.dumps(d,indent=2))
