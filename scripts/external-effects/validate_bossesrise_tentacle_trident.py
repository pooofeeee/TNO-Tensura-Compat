from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_bossesrise_tentacle_trident import support
from collect_bossesrise_foundation import PKG
from assemble_bossesrise_tentacle_trident import FACTS,CP,STEM
from bossesrise_combat_common import preserve_section

def validate_tentacle_trident():
    e=read_json(OUT/'native-evidence/bossesrise-tentacle-trident.json');assert collect(read_json(OUT/'native-specifications/bossesrise-tentacle-trident.json'))==e
    r=read_json(OUT/'reference-evidence/bossesrise-tentacle-trident-244.json');assert reference_collect(read_json(OUT/'reference-specifications/bossesrise-tentacle-trident-244.json'))==r
    raw=read_json(OUT/'vanilla-evidence/bossesrise-tentacle-trident.json');assert prepare(read_json(OUT/'vanilla-specifications/bossesrise-tentacle-trident.json'))==raw
    s=read_json(OUT/'bossesrise-tentacle-trident-support.json');assert support()==s
    assert not any('DispenserBlock.register' in str(row) for row in s['calls'])
    assert 'KrakenTridentTridentItemMixin' in s['resources'][0]['text'] and 'ID_LOYALTY' in s['resources'][1]['text']
    w={x['entry']:x for x in e['witnesses']}
    def b(short,n):return next(m['instructions'] for m in w[PKG+short+'.class']['methods'] if m['name']==n)
    def h(v,s):return [i for i in v if s in str(i.get('operand',''))]
    def off(v,s):return h(v,s)[0]['offset']
    def pop_after(v,s):
        ix=next(i for i,x in enumerate(v) if s in str(x.get('operand','')));assert v[ix+1]['opcode']=='0x57',s
    u='item/UndyingTentacleItem';g='entity/boss/kraken/summons/GhostTentacleEntity';t='entity/projectile/ThrownKrakenTridentEntity'
    v=b(u,'use');assert h(v,'.hurtAndBreak(') and h(v,'.addCooldown(') and not h(v,'.hurt(')
    v=b(u,'spawnGhost');assert off(v,'.noBlockCollision(')<off(v,'.setOwnerUUID(')<off(v,'.addFreshEntity(');pop_after(v,'.addFreshEntity(');assert v[-2]['operand']==1
    v=b(u,'finishUsingItem');assert len(h(v,'.spawnGhost('))==4 and not h(v,'.hurtAndBreak(') and not h(v,'.hurt(')
    assert b(g+'$1','canPerformAttack')[0]['operand']==0
    v=b(g,'baseTick');assert off(v,'.isBlocking(')<off(v,'.MOB_ATTACK')<off(v,'.hurt(')<off(v,'.setDeltaMovement(');pop_after(v,'.hurt(')
    assert h(v,'.kill(') and any(i.get('operand')==200 for i in v) and not h(v,'.hasLineOfSight(')
    assert h(b(g,'readAdditionalSaveData'),'Dataattack_cooldown') and h(b(g,'addAdditionalSaveData'),'attack_cooldown')
    for n in ['onHitEntity','onHitBlock']:
        v=b(t,n);assert off(v,'ThrownTrident.'+n+'(')<off(v,'.pullEntities(')
    v=b(t,'pullEntity');assert off(v,'.getOwner(')<off(v,'.trident(')<off(v,'.hurt(')<off(v,'.push(');pop_after(v,'.hurt(');assert any(i.get('operand')==5.0 for i in v)
    v=b(t,'lambda$pullEntities$0');assert h(v,'.isPushable(') and any(i.get('operand')==25.0 for i in v) and not h(v,'.getOwner(') and not h(v,'.isAlive(')
    v=b('mixins/KrakenTridentTridentItemMixin','releaseUsing');assert h(v,'.KRAKEN_TRIDENT') and h(v,'ThrownKrakenTridentEntity.<init>') and h(v,'/ThrownTrident.<init>')
    assert any(i.get('operand')==2500 for m in w[PKG+'init/BossesRiseItems.class']['methods'] for i in m['instructions'])
    rw={x['entry']:x for x in r['witnesses']};rv=next(m['instructions'] for m in rw['net/minecraft/world/entity/LivingEntity.class']['methods'] if m['name']=='kill');assert h(rv,'.genericKill(') and h(rv,'.hurt(')
    tr=next(x for x in raw['classes'] if x['class_name']=='net/minecraft/world/entity/projectile/ThrownTrident')
    v=next(m['instructions'] for m in tr['methods'] if m['name']=='onHitEntity');assert any(i.get('operand')==8.0 for i in v) and off(v,'.dealtDamageZ')<off(v,'.hurt(') and h(v,'.modifyDamage(') and h(v,'.ENDERMAN')
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==7 and len(d['delivery_paths'])==16 and sum(m['stage_scaling_needed'] for m in d['mechanic_packages'])==3
    preserved=preserve_section(d);assert preserved==dict(effects=543,sources=1303,paths=1303,comparisons=543,primitives=717)
    return dict(schema='tno.external_effects.bossesrise_tentacle_trident_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),reference_witnesses=len(r['witnesses']),raw_reference_classes=len(raw['classes']),mechanic_packages=7,native_paths=16,numeric_stage_candidates=3,native_throw_redirect_and_no_dispenser_registration_verified=True,super_hit_before_independent_area_verified=True,ghost_AI_disabled_timed_melee_and_terminal_native_hurt_verified=True,accepted_counts_preserved=preserved,whole_mod_complete=False,runtime_tests=0,**boundary_flags())
if __name__=='__main__':
    d=validate_tentacle_trident();write_json(OUT/'bossesrise-r2i8b-integrity.json',d);print(json.dumps(d,indent=2))
