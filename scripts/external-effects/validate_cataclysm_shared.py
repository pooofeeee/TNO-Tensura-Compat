from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_cataclysm_shared import inheritance,tag_members,PKG,BOSSES
from assemble_cataclysm_shared import CP,STEM,FACTS
from cataclysm_combat_common import preserve_section

def validate_shared():
    e=read_json(OUT/'native-evidence/cataclysm-shared.json');assert collect(read_json(OUT/'native-specifications/cataclysm-shared.json'))==e and len(e['witnesses'])==6
    r=read_json(OUT/'reference-evidence/cataclysm-shared-244.json');assert reference_collect(read_json(OUT/'reference-specifications/cataclysm-shared-244.json'))==r and len(r['witnesses'])==2
    assert inheritance()==read_json(OUT/'cataclysm-boss-inheritance.json') and len(inheritance()['classes'])==13
    t=read_json(OUT/'cataclysm-shared-tags.json');assert tag_members()==t and len(t['effect_whitelist']['values'])==31 and not t['effect_whitelist'].get('replace',False)
    assert set(t['damage_tags']['cataclysm:block_self_regen'])=={'minecraft:generic_kill','minecraft:out_of_world','minecraft:mob_attack','minecraft:player_attack'}
    assert 'neoforge:poison' in t['damage_tags']['cataclysm:bypasses_hurt_time'] and 'cataclysm:stun' not in t['effect_whitelist']['values']
    w={x['entry']:x for x in e['witnesses']+r['witnesses']}
    def b(short,name):return next(m['instructions'] for m in w[PKG+short+'.class']['methods'] if m['name']==name)
    def hits(ins,s):return [i for i in ins if s in str(i.get('operand',''))]
    def offset(ins,s):return hits(ins,s)[0]['offset']
    for base in BOSSES:
        ins=b(base,'hurt');assert offset(ins,'.isInvulnerableTo(')<offset(ins,'BYPASSES_INVULNERABILITY')<offset(ins,'.hurt(')<offset(ins,'Math.min(')<offset(ins,'.calculateRange(')<offset(ins,'BYPASSES_HURT_TIME')<hits(ins,'.hurt(')[1]['offset']<offset(ins,'BLOCK_SELF_REGEN')<offset(ins,'.HealCooldown(')
        assert len(hits(ins,'.DamageCap('))==2 and not hits(ins,'.DpsCap(') and not hits(ins,'.setHealth(')
        assert any(isinstance(i.get('operand'),float) and abs(i['operand']-.1)<1e-7 for i in ins)
        assert any(i.get('operand')==1.5 for i in ins)
        # Rejected downstream hit restores prior bucket after the regen-success branch.
        assert hits(ins,'.damageBucket')[-1]['opcode']=='0xb5' and hits(ins,'.damageBucket')[-1]['offset']>offset(ins,'.HealCooldown(')
        ins=b(base,'tick');assert offset(ins,'.self_regen')<offset(ins,'.isClientSide(')<offset(ins,'.isNoAi(')<offset(ins,'.heal(')<offset(ins,'.ReturnToHome(')<offset(ins,'.DpsCap(')
        assert len(hits(ins,'.heal('))==1 and any(i.get('operand')==20.0 for i in ins)
        ins=b(base,'canBeAffected');assert offset(ins,'.getEffect(')<offset(ins,'.getDelegate(')<offset(ins,'EFFECTIVE_FOR_BOSSES')<offset(ins,'.canBeAffected(')
        ins=b(base,'ReturnToHome');assert offset(ins,'.getHomePos(')<offset(ins,'.changeDimension(')<offset(ins,'.closerToCenterThan(')<offset(ins,'.moveTo(') and not hits(ins,'.heal(')
        assert any(i.get('operand')==16.0 for i in ins)
        for name in ['addAdditionalSaveData','readAdditionalSaveData']:
            ins=b(base,name);assert not any(hits(ins,s) for s in ['.damageBucket','.self_regen','.homeTicks'])
    ins=b('entity/etc/Animation_Monsters','calculateRange');assert hits(ins,'.getEntity(') and hits(ins,'.distanceToSqr(') and not hits(ins,'.getDirectEntity(')
    ins=b(BOSSES[1],'awardKillScore');assert offset(ins,'ServerPlayer')<offset(ins,'.getLife(')<offset(ins,'.setLife(')<offset(ins,'.Retry(')<offset(ins,'.awardKillScore(')
    assert len(b(BOSSES[1],'Retry'))==1
    ins=b(BOSSES[1],'lambda$PlayerCounter$1');assert all(hits(ins,s) for s in ['.isSpectator(','.isCreative(','.isAlive(','.distanceToSqr('])
    ins=b('entity/etc/Animation_Monsters','die');assert offset(ins,'CommonHooks.onLivingDeath(')<offset(ins,'.getEntity(')<offset(ins,'.killedEntity(')<offset(ins,'.AfterDefeatBoss(')
    ins=b('entity/etc/Animation_Monsters','onDeathUpdate');assert offset(ins,'.onDeathAIUpdate(')<offset(ins,'.deathTime')<offset(ins,'.remove(')
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==7 and len(d['delivery_paths'])==16
    assert not d['remaining_subsection_native_ambiguities'] and sum(x['stage_scaling_needed'] for x in d['mechanic_packages'])==1
    preserved=preserve_section(d);assert preserved==dict(effects=669,sources=1620,paths=1620,comparisons=669,primitives=882)
    return dict(schema='tno.external_effects.cataclysm_shared_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',native_witnesses=6,reference_witnesses=2,hierarchy_classes=13,mechanic_packages=7,delivery_paths=16,numeric_scaling_points=1,accepted_counts_preserved=preserved,promoted_records=0,whole_mod_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_shared();write_json(OUT/'cataclysm-r2k2a-integrity.json',d);print(json.dumps(d,indent=2))
