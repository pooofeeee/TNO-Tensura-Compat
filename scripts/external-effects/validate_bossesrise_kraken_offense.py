from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_bossesrise_kraken_offense import census,profiles,TENTACLE
from collect_bossesrise_foundation import PKG
from assemble_bossesrise_kraken_offense import FACTS,CP,STEM
from bossesrise_combat_common import preserve_section

def validate_kraken_offense():
    e=read_json(OUT/'native-evidence/bossesrise-kraken-offense.json');assert collect(read_json(OUT/'native-specifications/bossesrise-kraken-offense.json'))==e
    r=read_json(OUT/'reference-evidence/bossesrise-kraken-offense-244.json');assert reference_collect(read_json(OUT/'reference-specifications/bossesrise-kraken-offense-244.json'))==r
    raw=read_json(OUT/'vanilla-evidence/bossesrise-kraken-offense.json');assert prepare(read_json(OUT/'vanilla-specifications/bossesrise-kraken-offense.json'))==raw
    c=read_json(OUT/'bossesrise-kraken-offense-census.json');assert census()==c
    p=read_json(OUT/'bossesrise-kraken-source-profiles.json');assert profiles()==p
    w={x['entry']:x for x in e['witnesses']};rw={x['entry']:x for x in r['witnesses']}
    def b(short,n,desc=None):return next(m['instructions'] for m in w[PKG+short+'.class']['methods'] if m['name']==n and (desc is None or desc in m['descriptor']))
    def h(v,s):return [i for i in v if s in str(i.get('operand',''))]
    def off(v,s):return h(v,s)[0]['offset']
    def pop_after(v,s):
        ix=next(i for i,x in enumerate(v) if s in str(x.get('operand','')));assert v[ix+1]['opcode']=='0x57',s
    v=b(TENTACLE,'attackEntityWithSlam');assert h(v,'.KRAKEN_TENTACLE_SMASH') and h(v,'.getOwner(') and off(v,'.hurt(')<off(v,'.pushEntity(');pop_after(v,'.hurt(')
    assert any(i.get('operand')==.5 for i in v) and not h(v,'.doPostAttackEffects(')
    v=b(TENTACLE,'hasLineOfSight',';F)');assert not h(v,'.clip(') and h(v,'.CRATE') and h(v,'.getDeltaFromTargetRotation(')
    goal='entity/boss/kraken/goals/'
    for n in ['KrakenTentacleAttackGoal','KrakenTentacleCrateGoal','KrakenTentacleRunawayGoal']:
        assert h(b(goal+n,'<init>'),'.adjustedTickDelay(')
        assert not any(m['name']=='requiresUpdateEveryTick' for m in w[PKG+goal+n+'.class']['methods'])
    assert not h(b(goal+'KrakenTentacleAttackGoal','canContinueToUse'),'.getTarget(')
    v=b(goal+'KrakenTentacleRunawayGoal','performHit');assert h(v,'.pushEntity(') and not h(v,'.hurt(')
    v=b(goal+'KrakenTentacleCrateGoal','performHit');assert h(v,'.setOwner(') and h(v,'.shoot(') and not h(v,'CratePile')
    crate='entity/projectile/ThrownCrateEntity';v=b(crate,'onHitEntity');assert h(v,'KrakenTentacleEntityPart') and h(v,'.magic(') and off(v,'.hurt(')<off(v,'.explode(')<off(v,'.discard(')
    cannon='entity/decoration/CannonEntity';v=b(cannon,'interact');assert off(v,'.shrink(')<off(v,'CannonballEntity.<init>') and h(v,'.setOwner(') and h(v,'.shootFromRotation(') and any(i.get('operand')==60 for i in v)
    v=b(cannon,'hurt');assert off(v,'KrakenTentacleEntity.hurt(')<off(v,'.isInvulnerableTo(');assert h(v,'.MELEE_WEAPON_TOOLS') and h(v,'.mayBuildZ')
    ball='entity/projectile/CannonballEntity';v=b(ball,'onHitEntity');assert h(v,'.CANNONBALL_HIT') and any(i.get('operand')==10.0 for i in v) and off(v,'.hurt(')<off(v,'.explode(')
    for short in [crate,ball]:
        v=b(short,'tick');assert h(v,'.canHarmPlayer(') and h(v,'.onProjectileImpact(') and h(v,'.hitTargetOrDeflectSelf(')
    pirates='entity/boss/kraken/summons/'
    for n in ['PirateRookEntity','PirateCaptainEntity']:
        v=b(pirates+n+'$1','canPerformAttack');assert len(v)==2 and v[0].get('operand')==0
        v=b(pirates+n,'baseTick');assert off(v,'.isBlocking(')<off(v,'.addCooldown(')<off(v,'.hurt(')<off(v,'.setDeltaMovement(');pop_after(v,'.hurt(')
        v=b(pirates+n,'readAdditionalSaveData');assert h(v,'Dataattack_cooldown') and h(v,'attack_cooldown')
    v=b(pirates+'CrossbowPirateEntity','performRangedAttack');assert h(v,'.performCrossbowAttack(') and not h(v,'.ATTACK_DAMAGE')
    constructors=[row for row in c['rows'] if any(i['opcode']=='0xbb' and str(i['operand']).endswith('/CannonballEntity') for i in row['hits'])];assert len(constructors)==1 and constructors[0]['entry'].endswith('/CannonEntity.class')
    ghosts=[row for row in c['rows'] if any(i['opcode']=='0xbb' and str(i['operand']).endswith('/GhostTentacleEntity') for i in row['hits'])];assert len(ghosts)==1 and ghosts[0]['entry'].endswith('/UndyingTentacleItem.class')
    classes={x['class_name']:x for x in raw['classes']}
    g={m['name']:m['instructions'] for m in classes['net/minecraft/world/entity/ai/goal/Goal']['methods']};assert g['requiresUpdateEveryTick'][0].get('operand')==0 and h(g['reducedTickDelay'],'.positiveCeilDiv(')
    ds=next(m['instructions'] for m in classes['net/minecraft/world/damagesource/DamageSources']['methods'] if m['name']=='explosion' and h(m['instructions'],'.PLAYER_EXPLOSION'))
    assert h(ds,'.EXPLOSION') and not h(ds,'world/entity/player/Player') and sum(i['opcode']=='0xc6' for i in ds)==2
    ex=next(m['instructions'] for m in rw['net/minecraft/world/level/Explosion.class']['methods'] if m['name']=='getIndirectSourceEntityInternal');assert h(ex,'Projectile.getOwner(') and h(ex,'world/entity/LivingEntity')
    table={x['id']:x['tags'] for x in p['profiles']};assert len(table)==7
    for k in ['cannonball_hit','kraken_tentacle_smash']:
        tags=table['block_factorys_bosses:'+k];assert 'minecraft:bypasses_armor' in tags and 'minecraft:bypasses_shield' in tags and 'neoforge:is_physical' not in tags and 'neoforge:is_magic' not in tags
    for k in ['explosion','player_explosion']:assert 'minecraft:bypasses_armor' not in table['minecraft:'+k] and 'minecraft:bypasses_shield' not in table['minecraft:'+k]
    assert not any(t in tags for tags in table.values() for t in ['minecraft:bypasses_effects','minecraft:bypasses_resistance','minecraft:bypasses_enchantments','minecraft:bypasses_invulnerability','minecraft:bypasses_cooldown'])
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==11 and len(d['delivery_paths'])==24
    assert sum(m['stage_scaling_needed'] for m in d['mechanic_packages'])==7 and not d['remaining_subsection_native_ambiguities']
    preserved=preserve_section(d);assert preserved==dict(effects=543,sources=1303,paths=1303,comparisons=543,primitives=717)
    return dict(schema='tno.external_effects.bossesrise_kraken_offense_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),reference_witnesses=len(r['witnesses']),raw_reference_classes=len(raw['classes']),mechanic_packages=11,native_paths=24,numeric_stage_candidates=7,living_owned_player_explosion_source_proven=True,adjusted_goal_ticks_and_native_producers_verified=True,pirate_AI_melee_disabled_and_timed_callback_verified=True,independent_explosion_control_and_prop_resources_verified=True,accepted_counts_preserved=preserved,kraken_family_complete=True,whole_mod_complete=False,runtime_tests=0,**boundary_flags())
if __name__=='__main__':
    d=validate_kraken_offense();write_json(OUT/'bossesrise-r2i7b-integrity.json',d);print(json.dumps(d,indent=2))
