from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_bossesrise_yeti_defense import census,YETI
from collect_bossesrise_foundation import PKG
from assemble_bossesrise_yeti_defense import FACTS,CP,STEM
from bossesrise_combat_common import preserve_section

def validate_yeti_defense():
    e=read_json(OUT/'native-evidence/bossesrise-yeti-defense.json');assert collect(read_json(OUT/'native-specifications/bossesrise-yeti-defense.json'))==e
    r=read_json(OUT/'reference-evidence/bossesrise-yeti-defense-244.json');assert reference_collect(read_json(OUT/'reference-specifications/bossesrise-yeti-defense-244.json'))==r
    raw=read_json(OUT/'vanilla-evidence/bossesrise-yeti-defense.json');assert prepare(read_json(OUT/'vanilla-specifications/bossesrise-yeti-defense.json'))==raw
    c=read_json(OUT/'bossesrise-yeti-defense-census.json');assert census()==c
    w={x['entry']:x for x in e['witnesses']}
    def b(n,short=YETI):return next(m['instructions'] for m in w[PKG+short+'.class']['methods'] if m['name']==n)
    def h(v,s):return [i for i in v if s in str(i.get('operand',''))]
    v=b('hurt');assert h(v,'.discard(')[0]['offset']<h(v,'.BYPASSES_INVULNERABILITY')[0]['offset']<h(v,'.FALL')[0]['offset']<h(v,'.getDirectEntity(')[0]['offset']
    assert len(h(v,'.BYPASSES_INVULNERABILITY'))==2 and h(v,'net/minecraft/world/entity/projectile/AbstractArrow')
    arrow=h(v,'net/minecraft/world/entity/projectile/AbstractArrow')[0]['offset'];trident=h(v,'.TRIDENT')[0]['offset'];assert arrow<trident
    assert len([i for i in v if i['opcode']=='0x6a' and i['offset']>arrow and i['offset']<506])==2
    assert all(h(v,'.'+s+'L') for s in ['FALL','DROWN','FALLING_ANVIL','WITHER','WITHER_SKULL'])
    ix=next(i for i,x in enumerate(v) if '.setHealth(' in str(x.get('operand','')));assert [i['opcode'] for i in v[ix+1:ix+3]]==['0x4','0xac']
    assert len(h(v,'AbstractBossEntity.hurt('))==1 and h(v,'.setHealth(')[0]['offset']<h(v,'AbstractBossEntity.hurt(')[0]['offset']
    assert h(v,'.DATA_HIT_TICK')[0]['offset']<h(v,'.getHealth(')[0]['offset']
    assert b('shouldCancelDeath')[0]['opcode']=='0x3'
    assert not b('checkFallDamage') or [i['opcode'] for i in b('checkFallDamage')]==['0xb1']
    assert h(b('tick'),'.setTicksFrozen(') and h(b('baseTick'),'.setTicksFrozen(')
    assert h(b('tick'),'.canReach(') and h(b('tick'),'.setNoAi(') and h(b('setState'),'.DEATH')
    assert h(b('finalizeSpawn'),'.STRUCTURE') and h(b('finalizeSpawn'),'.YETI_ATK')
    v=b('onBreakBlock',YETI+'$YetiEvents');assert h(v,'.ICE') and h(v,'.INTRO') and h(v,'.setCanceled(') and h(v,'.setBlock(')
    tridents=[x for x in r['witnesses'] if x.get('entry','').endswith('/ThrownTrident.class')]+[x for x in raw['classes'] if x['class_name'].endswith('/ThrownTrident')]
    assert len(tridents)==1 and any('AbstractArrow.<init>' in str(i.get('operand','')) for m in tridents[0]['methods'] for i in m['instructions'])
    # Legacy positive counter writer remains gated by shared onDamageTaken/shouldCancelDeath,
    # which this native subclass rejects. No ordinary defeat path inferred from that body.
    writer=[x for x in c['rows'] if x['entry'].endswith('/BossCancelDieProcedure.class') and any('.DATA_DIE_ANIMTIME' in str(i['operand']) for i in x['hits'])];assert len(writer)==1 and writer[0]['method']=='execute'
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==4 and len(d['delivery_paths'])==12
    assert not any(m['stage_scaling_needed'] for m in d['mechanic_packages']) and not d['remaining_subsection_native_ambiguities']
    preserved=preserve_section(d);assert preserved==dict(effects=543,sources=1303,paths=1303,comparisons=543,primitives=717)
    return dict(schema='tno.external_effects.bossesrise_yeti_defense_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),reference_witnesses=len(r['witnesses']),raw_reference_classes=len(raw['classes']),mechanic_packages=4,native_paths=12,numeric_stage_candidates=0,raw_lethal_branch_precedes_inherited_hurt=True,native_trident_reductions_multiply=True,legacy_999_not_promoted=True,accepted_counts_preserved=preserved,whole_mod_complete=False,runtime_tests=0,**boundary_flags())
if __name__=='__main__':
    d=validate_yeti_defense();write_json(OUT/'bossesrise-r2i5a-integrity.json',d);print(json.dumps(d,indent=2))
