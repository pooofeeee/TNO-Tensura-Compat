from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_bossesrise_yeti_offense import census,profiles
from collect_bossesrise_foundation import PKG
from assemble_bossesrise_yeti_offense import FACTS,CP,STEM
from bossesrise_combat_common import preserve_section

def validate_yeti_offense():
    e=read_json(OUT/'native-evidence/bossesrise-yeti-offense.json');assert collect(read_json(OUT/'native-specifications/bossesrise-yeti-offense.json'))==e
    r=read_json(OUT/'reference-evidence/bossesrise-yeti-offense-244.json');assert reference_collect(read_json(OUT/'reference-specifications/bossesrise-yeti-offense-244.json'))==r
    raw=read_json(OUT/'vanilla-evidence/bossesrise-yeti-offense.json');assert prepare(read_json(OUT/'vanilla-specifications/bossesrise-yeti-offense.json'))==raw
    c=read_json(OUT/'bossesrise-yeti-offense-census.json');assert census()==c
    p=read_json(OUT/'bossesrise-yeti-source-profiles.json');assert profiles()==p
    table={x['id']:x['tags'] for x in p['profiles']};assert len(table)==3
    assert 'minecraft:is_freezing' in table['minecraft:freeze'] and 'minecraft:bypasses_armor' in table['minecraft:freeze']
    assert 'minecraft:is_projectile' not in table['minecraft:indirect_magic']
    assert not any(t in tags for tags in table.values() for t in ['minecraft:bypasses_effects','minecraft:bypasses_resistance','minecraft:bypasses_enchantments','minecraft:bypasses_invulnerability','minecraft:bypasses_cooldown'])
    w={x['entry']:x for x in e['witnesses']};rw={x['entry']:x for x in r['witnesses']}
    prefix='entity/boss/yeti/'
    def b(short,n):return next(m['instructions'] for m in w[PKG+short+'.class']['methods'] if m['name']==n)
    def h(v,s):return [i for i in v if s in str(i.get('operand',''))]
    def pop_after(v,s):
        ix=next(i for i,x in enumerate(v) if s in str(x.get('operand','')));assert v[ix+1]['opcode']=='0x57',s
    for entity in ['IceSpikeEntity','IceSpikeClusterEntity']:
        methods=w[PKG+prefix+entity+'.class']['methods']
        v=next(m['instructions'] for m in methods if m['name'].startswith('lambda$baseTick$') and h(m['instructions'],'.hurt('))
        assert h(v,'.freeze(') and h(v,'.hurt(')[0]['offset']<h(v,'.setTicksFrozen(')[0]['offset'];pop_after(v,'.hurt(')
        for n in ['addAdditionalSaveData','readAdditionalSaveData']:assert not h(b(prefix+entity,n),'.damageF')
    v=b(prefix+'IceSpikeEntity','canHurt');assert len(h(v,'.getOwnerUUID('))==2 and not h(v,'.equals(') and any(i['opcode']=='0xa6' and i['offset']==42 for i in v)
    assert not h(v,'.canFreeze(')
    v=b(prefix+'IceSpikeClusterEntity','hurt');assert not h(v,'.hurt(') and not h(v,'.getHealth(') and h(v,'.DATA_REMAINING_HIT') and any(i.get('operand')==8 for i in v)
    v=b(prefix+'IceSpikeClusterEntity','interact');assert h(v,'.setOwnerUUID(') and h(v,'.setHeld(') and h(v,'.getNewShardIndex(')
    pr=prefix+'IceSpikeProjectileEntity';v=b(pr,'onHitEntity');assert h(v,'.indirectMagic(') and h(v,'Mth.ceil(') and h(v,'.MOVEMENT_SLOWDOWN') and not h(v,'.setTicksFrozen(')
    v=b(pr,'playerTouch');assert h(v,'.FREEZE') and any(i.get('operand')==8.0 for i in v) and h(v,'.setTicksFrozen(')[0]['offset']<h(v,'.hurt(')[0]['offset']
    pop_after(v,'.hurt(');assert not h(v,'.onProjectileImpact(') and not h(v,'.canHarmPlayer(') and not h(v,'.canFreeze(')
    v=b(pr,'tick');assert h(v,'.canHarmPlayer(') and h(v,'.onProjectileImpact(') and h(v,'.hitTargetOrDeflectSelf(')
    assert h(b(pr,'addAdditionalSaveData'),'.baseDamageD') and not h(b(pr,'addAdditionalSaveData'),'.knockbackI')
    sh=prefix+'GlacialShoveEntity';v=b(sh,'tick');assert h(v,'.isInvulnerable(') and h(v,'.pushEntity(') and not h(v,'.hurt(') and h(v,'.shouldSetAttackZ')
    assert any(i.get('operand')=='Owner' for i in b(sh,'addAdditionalSaveData')) and any(i.get('operand')=='owner' for i in b(sh,'readAdditionalSaveData'))
    for n in ['addAdditionalSaveData','readAdditionalSaveData']:assert not h(b(sh,n),'.DATA_TARGET') and not h(b(sh,n),'.DATA_DELAY') and not h(b(sh,n),'.shouldSetAttack')
    assert all(row['entry'].startswith(PKG+'geckolib/') for row in c['rows'] if '.getEvil(' in str(row['hits']))
    assert not any(i['opcode']=='0xb8' and 'IceSpikeProjectileEntity.shoot(' in str(i['operand']) for row in c['rows'] if not row['entry'].endswith('/IceSpikeProjectileEntity.class') for i in row['hits'])
    v=b('item/IceGauntletItem','placeProper');assert h(v,'.COLLIDER') and h(v,'.NONE') and h(v,'.MISS')
    player=rw['net/minecraft/world/entity/player/Player.class']['methods'];assert any(h(m['instructions'],'.playerTouch(') for m in player if m['name']=='touch')
    assert any(h(m['instructions'],'.touch(') and h(m['instructions'],'.isRemoved(') for m in player if m['name']=='aiStep')
    living=rw['net/minecraft/world/entity/LivingEntity.class']['methods'];v=next(m['instructions'] for m in living if m['name']=='aiStep');assert h(v,'.canFreeze(') and h(v,'.freeze(') and any(i.get('operand')==40 for i in v)
    y=next(x for x in read_json(OUT/'native-evidence/bossesrise-yeti-defense.json')['witnesses'] if x['entry'].endswith('/YetiEntity.class'))
    hits=[m['instructions'] for m in y['methods'] if m['name'].startswith('lambda$tick$') and h(m['instructions'],'.attackEntity(')]
    assert len(hits)==6 and sum(bool(h(v,'.invulnerableTimeI')) for v in hits)==4
    for v in hits:pop_after(v,'.attackEntity(')
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==11 and len(d['delivery_paths'])==23
    assert sum(m['stage_scaling_needed'] for m in d['mechanic_packages'])==7 and not d['remaining_subsection_native_ambiguities']
    preserved=preserve_section(d);assert preserved==dict(effects=543,sources=1303,paths=1303,comparisons=543,primitives=717)
    return dict(schema='tno.external_effects.bossesrise_yeti_offense_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),reference_witnesses=len(r['witnesses']),raw_reference_classes=len(raw['classes']),mechanic_packages=11,native_paths=23,numeric_stage_candidates=7,native_Player_touch_dispatch_proven=True,independent_controls_and_iframe_resets_verified=True,spike_UUID_reference_admission_and_reload_loss_verified=True,Glacial_Shove_roll_skip_and_Owner_mismatch_verified=True,accepted_counts_preserved=preserved,yeti_family_complete=True,whole_mod_complete=False,runtime_tests=0,**boundary_flags())
if __name__=='__main__':
    d=validate_yeti_offense();write_json(OUT/'bossesrise-r2i5b-integrity.json',d);print(json.dumps(d,indent=2))
