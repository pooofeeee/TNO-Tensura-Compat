from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_bossesrise_knight_offense import census,source_tags
from collect_bossesrise_foundation import PKG,targets,KEY
from classfile import ClassFile
from assemble_bossesrise_knight_offense import FACTS,CP,STEM
from bossesrise_combat_common import preserve_section

def validate_knight_offense():
    e=read_json(OUT/'native-evidence/bossesrise-knight-offense.json');assert collect(read_json(OUT/'native-specifications/bossesrise-knight-offense.json'))==e
    r=read_json(OUT/'reference-evidence/bossesrise-knight-offense-244.json');assert reference_collect(read_json(OUT/'reference-specifications/bossesrise-knight-offense-244.json'))==r
    raw=read_json(OUT/'vanilla-evidence/bossesrise-knight-offense.json');assert prepare(read_json(OUT/'vanilla-specifications/bossesrise-knight-offense.json'))==raw
    c=read_json(OUT/'bossesrise-knight-offense-census.json');assert census()==c
    profiles=read_json(OUT/'bossesrise-knight-source-profiles.json');assert source_tags()==profiles
    bytype={x['id']:x for x in profiles['profiles']};assert len(bytype)==7
    assert 'neoforge:is_magic' in bytype['minecraft:indirect_magic']['tags'] and 'minecraft:is_projectile' not in bytype['minecraft:indirect_magic']['tags']
    assert 'minecraft:is_explosion' in bytype['minecraft:explosion']['tags'] and 'minecraft:bypasses_armor' not in bytype['minecraft:explosion']['tags']
    w={x['entry']:x for x in e['witnesses']};rw={x['entry']:x for x in r['witnesses']}
    def b(short,n):return next(m['instructions'] for m in w[PKG+short+'.class']['methods'] if m['name']==n)
    def h(body,s):return [i for i in body if s in str(i.get('operand',''))]
    assert [i['opcode'] for i in b('entity/boss/knight/UnderworldKnightEntity$2','canPerformAttack')]==['0x3','0xac']
    wave='entity/projectile/SwordWaveEntity';v=b(wave,'onHitEntity')
    assert h(v,'.indirectMagic(') and h(v,'Mth.ceil(') and h(v,'.MOVEMENT_SLOWDOWN')
    assert h(v,'.hurt(')[0]['offset']<h(v,'.addEffect(')[0]['offset'] and not h(v,'.discard(')
    assert b(wave,'isOnFire')[0]['opcode']=='0x3' and h(b(wave,'deflect'),'.discardWithParticles(') and not h(b(wave,'deflect'),'.setOwner(')
    for method in ['addAdditionalSaveData','readAdditionalSaveData']:assert not h(b(wave,method),'.baseDamage') and not h(b(wave,method),'.knockback')
    shock='entity/projectile/SoulShockwaveEntity';v=b(shock,'onHitEntity');assert h(v,'AbstractArrow.onHitEntity(')[0]['offset']<h(v,'.onHitSomething(')[0]['offset']
    v=b(shock,'onHitSomething');assert h(v,'AABB.ofSize(') and h(v,'.MOVEMENT_SLOWDOWN') and not h(v,'.explode(')
    v=next(m['instructions'] for m in w[PKG+shock+'.class']['methods'] if m['name'].startswith('lambda$onHitSomething$') and h(m['instructions'],'.hurt('))
    assert h(v,'.EXPLOSION') and any(i.get('operand')==4.0 for i in v)
    ix=next(i for i,x in enumerate(v) if '.hurt(' in str(x.get('operand','')));assert v[ix+1]['opcode']=='0x57'
    rift='entity/projectile/RiftProjectileEntity';v=b(rift,'onHitEntity');assert h(v,'.magic()') and any(i.get('operand')==2.0 for i in v)
    assert not h(v,'.indirectMagic(') and h(v,'.hurt(')[0]['offset']<h(v,'.doPostAttackEffects(')[0]['offset']
    big=b('entity/projectile/BigRiftProjectileEntity','onHitEntity');assert h(big,'RiftProjectileEntity.onHitEntity(')[0]['offset']<h(big,'.addEffect(')[0]['offset']
    assert not h(big,'.hurt(')
    assert not any('.attackJumpspin1(' in str(x['hits']) for x in c['rows'])
    assert not any(i['opcode']=='0xb8' and 'SoulShockwaveEntity.shoot(' in str(i['operand']) for x in c['rows'] if not x['entry'].endswith('/SoulShockwaveEntity.class') for i in x['hits'])
    for short in ['procedures/SoulSkeletonOnEntityTickUpdateProcedure','procedures/SoulKnightWitherSkeletonOnEntityTickUpdateProcedure']:
        v=b(short,'execute');assert h(v,'.MOB_ATTACK') and h(v,'.ATTACK_DAMAGE') and h(v,'.setDeltaMovement(')
        ix=next(i for i,x in enumerate(v) if '.hurt(' in str(x.get('operand','')));assert v[ix+1]['opcode']=='0x57'
        assert not h(v,'.hasLineOfSight(')
    v=b('procedures/SoulKnightWitherSkeletonOnEntityTickUpdateProcedure','execute');assert h(v,'.isBlocking(') and h(v,'.WITHER')
    # Its isBlocking receiver is the attacker parameter (local1), not victim iterator.
    ix=next(i for i,x in enumerate(v) if '.isBlocking(' in str(x.get('operand','')))
    assert [x['opcode'] for x in v[ix-4:ix]]==['0x2b','0xc0','0x3a','0x19']
    with zipfile.ZipFile(targets()[KEY]['path']) as jar:
        cls=ClassFile(jar.read(PKG+'procedures/SoulKnightWitherSkeletonOnEntityTickUpdateProcedure.class'));code=next(m['code'] for m in cls.methods if m['name']=='execute')
    assert code[v[ix-2]['offset']+1]==code[v[ix-1]['offset']+1]
    wither=next(x for x in raw['classes'] if x['class_name'].endswith('/WitherMobEffect'));assert '.wither()' in str(wither) and any(i.get('operand')==1.0 for m in wither['methods'] if m['name']=='applyEffectTick' for i in m['instructions'])
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==12 and len(d['delivery_paths'])==21
    assert sum(m['stage_scaling_needed'] for m in d['mechanic_packages'])==9 and not d['remaining_subsection_native_ambiguities']
    preserved=preserve_section(d);assert preserved==dict(effects=543,sources=1303,paths=1303,comparisons=543,primitives=717)
    return dict(schema='tno.external_effects.bossesrise_knight_offense_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),reference_witnesses=len(r['witnesses']),raw_reference_classes=len(raw['classes']),native_source_profiles=7,mechanic_packages=12,native_paths=21,numeric_stage_candidates=9,unused_helper_deliveries_excluded=True,independent_status_and_area_callbacks_verified=True,accepted_counts_preserved=preserved,knight_family_complete=True,whole_mod_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_knight_offense();write_json(OUT/'bossesrise-r2i3b-integrity.json',d);print(json.dumps(d,indent=2))
