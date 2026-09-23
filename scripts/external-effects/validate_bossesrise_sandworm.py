from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_bossesrise_sandworm import census,profiles,SW
from collect_bossesrise_foundation import PKG
from assemble_bossesrise_sandworm import FACTS,CP,STEM
from bossesrise_combat_common import preserve_section

def validate_sandworm():
    e=read_json(OUT/'native-evidence/bossesrise-sandworm.json');assert collect(read_json(OUT/'native-specifications/bossesrise-sandworm.json'))==e
    r=read_json(OUT/'reference-evidence/bossesrise-sandworm-244.json');assert reference_collect(read_json(OUT/'reference-specifications/bossesrise-sandworm-244.json'))==r
    raw=read_json(OUT/'vanilla-evidence/bossesrise-sandworm.json');assert prepare(read_json(OUT/'vanilla-specifications/bossesrise-sandworm.json'))==raw
    c=read_json(OUT/'bossesrise-sandworm-census.json');assert census()==c
    p=read_json(OUT/'bossesrise-sandworm-source-profiles.json');assert profiles()==p
    w={x['entry']:x for x in e['witnesses']};rw={x['entry']:x for x in r['witnesses']}
    def b(short,n,desc=None):return next(m['instructions'] for m in w[PKG+short+'.class']['methods'] if m['name']==n and (desc is None or desc in m['descriptor']))
    def h(v,s):return [i for i in v if s in str(i.get('operand',''))]
    def off(v,s):return h(v,s)[0]['offset']
    def pop_after(v,s):
        ix=next(i for i,x in enumerate(v) if s in str(x.get('operand','')));assert v[ix+1]['opcode']=='0x57',s
    v=b(SW,'hurt','SandwormEntityPart;');assert h(v,'.isDirect(') and h(v,'.BYPASSES_INVULNERABILITY') and h(v,'.getDirectEntity(')
    assert off(v,'.reallyHurt(')<off(v,'.recentDamageF')<off(v,'.shootPoisonSpit(')
    assert any(i.get('operand')==25.0 for i in v) and any(i.get('operand')==60 for i in v)
    assert any(i['opcode']=='0x99' and 46<i['offset']<58 for i in v)
    v=b(SW,'isInvulnerableTo');assert all(h(v,s) for s in ['.FALL','.CACTUS','.POISON_DAMAGE','.LAVA']) and not h(v,'.isHiddenUnderground(') and not h(v,'.isDying(')
    v=b(SW,'applyUndergroundEffects');assert h(v,'.healAllSegments(') and h(v,'.removeFrost(') and not h(v,'.setHealth(') and not h(v,'.setTicksFrozen(')
    for n in ['readAdditionalSaveData','addAdditionalSaveData']:assert not h(b(SW,n),'.DATA_DAMAGED_SEGMENTS') and not h(b(SW,n),'.DATA_IS_HIDDEN')
    v=b(SW,'attackCollidingEntities','Ljava/util/List;');assert off(v,'.pushEntity(')<off(v,'.attackEntity(')<off(v,'.accept(');pop_after(v,'.attackEntity(')
    assert any(i['opcode']=='0x82' for i in b(SW,'pushCollidingEntities'))
    attacks=[m for m in w[PKG+SW+'.class']['methods'] if m['name'].startswith('lambda$static$') and h(m['instructions'],'.attackCollidingEntities(')];assert len(attacks)==5
    col='entity/SandColumnEntity';v=b(col,'damageEntity');assert off(v,'.isInvulnerable(')<off(v,'.push(')<off(v,'.isAlliedTo(')
    assert h(v,'.magic(') and h(v,'.indirectMagic(') and len(h(v,'.hurt('))==2 and h(v,'.doPostAttackEffects(')
    assert any(i.get('operand')==-2 for i in b(col,'tick')) and h(b(col,'spawnSandColumn'),'.MISS')
    spit='entity/projectile/PoisonSpitPrEntity'
    for n in ['onHitEntity','onHitBlock']:
        v=b(spit,n);assert off(v,'AbstractArrow.'+n+'(')<off(v,'.spawnPoisonAreaEntity(')
    v=b(spit,'onProjectileImpactEvent');assert h(v,'PartEntity.getParent(') and h(v,'.getOwner(') and h(v,'.setCanceled(')
    area='entity/PoisonAreaEntity';v=b(area,'tick');assert off(v,'.isAffectedByPotions(')<off(v,'.put(')<off(v,'.addEffect(');pop_after(v,'.addEffect(');assert not h(v,'.hurt(')
    assert not h(b(area,'addAdditionalSaveData'),'.victims')
    assert any(row['entry'].endswith('/SandwormGauntletItem.class') and 'PoisonSpitPrEntity.shoot(' in str(row['hits']) for row in c['rows'])
    def ref(cl,n):return next(m['instructions'] for m in rw['net/minecraft/'+cl+'.class']['methods'] if m['name']==n)
    v=ref('world/damagesource/DamageSource','isDirect');assert h(v,'.causingEntity') and h(v,'.directEntity') and any(i['opcode'] in ['0xa5','0xa6'] for i in v)
    v=ref('world/entity/Entity','isInvulnerableTo');assert h(v,'.invulnerableZ') and not h(v,'.isInvulnerable(') and h(v,'.isEntityInvulnerableTo(')
    v=ref('world/effect/PoisonMobEffect','applyEffectTick');assert off(v,'.getHealth(')<off(v,'.POISON_DAMAGE')<off(v,'.hurt(');pop_after(v,'.hurt(')
    v=ref('world/effect/PoisonMobEffect','shouldApplyEffectTickThisTick');assert any(i.get('operand')==25 for i in v) and any(i['opcode']=='0x7a' for i in v)
    table={x['id']:x['tags'] for x in p['profiles']};assert len(table)==5
    assert 'neoforge:is_poison' in table['neoforge:poison'] and 'minecraft:is_projectile' not in table['minecraft:indirect_magic']
    assert not any(t in tags for tags in table.values() for t in ['minecraft:bypasses_effects','minecraft:bypasses_resistance','minecraft:bypasses_enchantments','minecraft:bypasses_invulnerability','minecraft:bypasses_cooldown'])
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==10 and len(d['delivery_paths'])==23
    assert sum(m['stage_scaling_needed'] for m in d['mechanic_packages'])==4 and not d['remaining_subsection_native_ambiguities']
    preserved=preserve_section(d);assert preserved==dict(effects=543,sources=1303,paths=1303,comparisons=543,primitives=717)
    return dict(schema='tno.external_effects.bossesrise_sandworm_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),reference_witnesses=len(r['witnesses']),raw_reference_classes=len(raw['classes']),mechanic_packages=10,native_paths=23,numeric_stage_candidates=4,source_identity_and_hurt_return_order_verified=True,independent_controls_and_poison_verified=True,actual_equipment_producers_reserved=True,accepted_counts_preserved=preserved,sandworm_family_complete=True,whole_mod_complete=False,runtime_tests=0,**boundary_flags())
if __name__=='__main__':
    d=validate_sandworm();write_json(OUT/'bossesrise-r2i6-integrity.json',d);print(json.dumps(d,indent=2))
