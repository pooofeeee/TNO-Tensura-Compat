from catalog_common import *
from native_evidence import collect
from collect_bossesrise_kraken_defense import KRAKEN,TENTACLE
from collect_bossesrise_foundation import PKG
from assemble_bossesrise_kraken_defense import FACTS,CP,STEM
from bossesrise_combat_common import preserve_section

def validate_kraken_defense():
    e=read_json(OUT/'native-evidence/bossesrise-kraken-defense.json');assert collect(read_json(OUT/'native-specifications/bossesrise-kraken-defense.json'))==e
    w={x['entry']:x for x in e['witnesses']}
    def b(short,n,desc=None):return next(m['instructions'] for m in w[PKG+short+'.class']['methods'] if m['name']==n and (desc is None or desc in m['descriptor']))
    def h(v,s):return [i for i in v if s in str(i.get('operand',''))]
    def off(v,s):return h(v,s)[0]['offset']
    v=b(KRAKEN,'hurt');assert off(v,'.hasCausedDamage(')<off(v,'.IS_PROJECTILE')<off(v,'AbstractStateBossEntity.hurt(')<off(v,'.damageTowardsKnockdownF')
    assert any(i.get('operand')==5.0 for i in v) and any(i.get('operand')==.25 for i in v) and any(i.get('operand')==100.0 for i in v)
    assert h(v,'.isKnockedDown(') and h(v,'.isDying(')
    v=b(TENTACLE,'hurt','KrakenTentacleEntityPart;');assert h(v,'.hasCausedDamage(') and not h(v,'.IS_PROJECTILE') and h(v,'.reallyHurt(')
    v=b(KRAKEN,'onSyncedDataUpdated');assert h(v,'.DATA_IS_HIDDEN') and h(v,'.setInvulnerable(') and h(v,'.refreshDimensions(')
    v=b(KRAKEN,'tick');assert h(v,'.isArenaLoaded(') and h(v,'.isEmpty(') and h(v,'.isDeadOrDying(')
    v=b(KRAKEN,'onTentacleDestroyed');assert h(v,'.deadTentaclesI') and h(v,'.CANNON') and h(v,'.spawnPirates(') and not h(v,'RemovalReason')
    v=b(TENTACLE,'remove');assert off(v,'.updateOwnerReference(')<off(v,'.onTentacleDestroyed(') and not h(v,'.KILLED') and not h(v,'.DISCARDED')
    v=b(TENTACLE,'killQuietly');assert off(v,'.setHealth(')<off(v,'.die(') and h(v,'.genericKill(') and not h(v,'.hurt(')
    assert any(i.get('operand')==115 for i in b(TENTACLE,'tickDeath'))
    v=b(KRAKEN,'spawnTentacleInternal');assert h(v,'.getAttributeBaseValue(') and any(i.get('operand')==12.0 for i in v) and h(v,'.setOwner(')
    v=b(KRAKEN,'spawnCannonGrabbyTentacle');assert h(v,'.startRiding(') and h(v,'.discard(')
    v=b('block/entity/KrakenSpawnerBlockEntity','tick');assert h(v,'.KRAKEN') and h(v,'.setBossPhase(') and not h(v,'.finalizeMobSpawn(') and not h(v,'.finalizeSpawn(')
    v=b('entity/boss/kraken/KrakenCinematicEntity','hurt');assert not h(v,'.hurt(') and len(v)==2
    v=b('entity/boss/kraken/KrakenCinematicEntity','playAnimation');assert any(i.get('operand')==490 for i in v) and any(i.get('operand')==290 for i in v)
    v=b(KRAKEN,'shouldCancelDeath');assert h(v,'.setBossPhase(') and h(v,'.isInDyingState(')
    for n in ['addAdditionalSaveData','readAdditionalSaveData']:
        v=b(KRAKEN,n);assert all(h(v,s) for s in ['owned_tentacles','tentacle_respawn_timers','damage_towards_knockdown','is_hidden'])
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==5 and len(d['delivery_paths'])==14
    assert not any(m['stage_scaling_needed'] for m in d['mechanic_packages']) and not d['remaining_subsection_native_ambiguities']
    preserved=preserve_section(d);assert preserved==dict(effects=543,sources=1303,paths=1303,comparisons=543,primitives=717)
    return dict(schema='tno.external_effects.bossesrise_kraken_defense_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),mechanic_packages=5,native_paths=14,numeric_stage_candidates=0,source_priority_hidden_backingfield_and_independent_part_HP_verified=True,unfiltered_removal_resource_callback_verified=True,native_spawn_configuration_and_death_order_verified=True,accepted_counts_preserved=preserved,kraken_family_complete=False,whole_mod_complete=False,runtime_tests=0,**boundary_flags())
if __name__=='__main__':
    d=validate_kraken_defense();write_json(OUT/'bossesrise-r2i7a-integrity.json',d);print(json.dumps(d,indent=2))
