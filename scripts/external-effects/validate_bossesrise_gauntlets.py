from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_bossesrise_gauntlets import census
from collect_bossesrise_foundation import PKG
from assemble_bossesrise_gauntlets import FACTS,CORRECTIONS,CP,STEM
from bossesrise_combat_common import preserve_section

def validate_gauntlets():
    e=read_json(OUT/'native-evidence/bossesrise-gauntlets.json');assert collect(read_json(OUT/'native-specifications/bossesrise-gauntlets.json'))==e
    r=read_json(OUT/'reference-evidence/bossesrise-gauntlets-244.json');assert reference_collect(read_json(OUT/'reference-specifications/bossesrise-gauntlets-244.json'))==r
    raw=read_json(OUT/'vanilla-evidence/bossesrise-gauntlets.json');assert prepare(read_json(OUT/'vanilla-specifications/bossesrise-gauntlets.json'))==raw
    c=read_json(OUT/'bossesrise-gauntlets-helper-census.json');assert census()==c
    assert all(row['entry']==PKG+'entity/projectile/PoisonSpitPrEntity.class' for row in c['rows'])
    w={x['entry']:x for x in e['witnesses']}
    def b(short,n):return next(m['instructions'] for m in w[PKG+short+'.class']['methods'] if m['name']==n)
    def h(v,s):return [i for i in v if s in str(i.get('operand',''))]
    def off(v,s):return h(v,s)[0]['offset']
    def pop_after(v,s):
        ix=next(i for i,x in enumerate(v) if s in str(x.get('operand','')));assert v[ix+1]['opcode']=='0x57',s
    ice='item/IceGauntletItem';sand='item/SandwormGauntletItem';a='attachment/entity/GauntletAttachment'
    assert h(b(ice,'<init>'),'ShieldItem.<init>') and h(b(ice,'use'),'ShieldItem.use(')
    v=b(ice,'hurtEnemy');assert h(v,'.setTicksFrozen(') and any(i.get('operand')==400 for i in v) and not h(v,'.hurt(') and not h(v,'.canFreeze(')
    v=b(ice,'releaseUsing');assert h(v,'.isSecondaryUseActive(') and h(v,'.isOnCooldown(') and off(v,'.MISS')<off(v,'.iceWave(')<off(v,'.addCooldown(')<off(v,'.hurtAndBreak(')
    v=b(a,'onJump');assert h(v,'.isUsingItem(') and h(v,'.isHoldingAnyShards(') and h(v,'.activeZ') and any(i.get('operand')==400 for i in v)
    v=b(a,'onFall');assert h(v,'.activeZ') and h(v,'.iceBurst(') and not h(v,'.getUseItem(') and not h(v,'.isOnCooldown(')
    hits=[m['instructions'] for m in w[PKG+a+'.class']['methods'] if m['name'].startswith('lambda$onFall$') and h(m['instructions'],'.hurt(')];assert len(hits)==1
    v=hits[0];assert off(v,'.freeze(')<off(v,'.hurt(')<off(v,'.setTicksFrozen(');pop_after(v,'.hurt(');assert any(i.get('operand')==10.0 for i in v) and not h(v,'.canFreeze(')
    v=b(a,'tick');assert h(v,'IceSpikeProjectileEntity.<init>') and h(v,'.setBaseDamage(') and h(v,'.setKnockback(') and h(v,'.lastShotTickJ')
    v=b(sand,'releaseUsingWithPoisonBarrage');assert any(i['opcode']=='0xbb' and str(i['operand']).endswith('/PoisonSpitPrEntity') for i in v)
    assert any(i['opcode']=='0xb6' and '.shoot(DDDFF)' in str(i['operand']) for i in v) and not any(i['opcode']=='0xb8' and 'PoisonSpitPrEntity.shoot(' in str(i['operand']) for i in v)
    assert any(i.get('operand')==6.0 for i in v) and not h(v,'.hurtAndBreak(') and not h(v,'.addCooldown(')
    v=b(sand,'onUseTickWithEarthquake');assert off(v,'.hurtAndBreak(')<off(v,'.spawnSandColumn(') and any(i.get('operand')==30 for i in v) and any(i.get('operand')==20 for i in v)
    v=b(sand,'onPoisonBarrageStart');assert any(i.get('operand')==.5 for i in v) and h(v,'.ADD_MULTIPLIED_BASE')
    assert all(not h(m['instructions'],'.hurt(') and not h(m['instructions'],'.setTicksFrozen(') for m in w[PKG+'network/IceGauntletMessage.class']['methods'])
    allref={x['entry']:x for x in r['witnesses']}
    shield=allref.get('net/minecraft/world/item/ShieldItem.class')
    if shield:sv=next(m['instructions'] for m in shield['methods'] if m['name']=='use')
    else:sv=next(m['instructions'] for cl in raw['classes'] if cl['class_name']=='net/minecraft/world/item/ShieldItem' for m in cl['methods'] if m['name']=='use')
    assert h(sv,'.startUsingItem(')
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and d['semantic_corrections']==CORRECTIONS
    assert len(d['mechanic_packages'])==12 and len(d['delivery_paths'])==18 and sum(m['stage_scaling_needed'] for m in d['mechanic_packages'])==9
    prior={m['id']:m for f in ['bossesrise-r2i5b-yeti-offense.json','bossesrise-r2i6-sandworm.json'] for m in read_json(OUT/f)['mechanic_packages']}
    reused=[m for m in d['mechanic_packages'] if m.get('extends_existing_package')];assert len(reused)==9
    for m in reused:
        for field in ['single_scaling_point','stage_scaling_needed','primary_classification','tno_categories']:assert m[field]==prior[m['id']][field]
    preserved=preserve_section(d);assert preserved==dict(effects=543,sources=1303,paths=1303,comparisons=543,primitives=717)
    return dict(schema='tno.external_effects.bossesrise_gauntlets_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),reference_witnesses=len(r['witnesses']),raw_reference_classes=len(raw['classes']),mechanic_packages=12,extends_existing_packages=9,new_packages=3,native_paths=18,numeric_stage_candidates=9,real_ShieldItem_use_verified=True,native_input_cost_and_hazard_owner_verified=True,additive_static_helper_correction_proven=True,protected_hazard_scaling_points_reused=True,accepted_counts_preserved=preserved,whole_mod_complete=False,runtime_tests=0,**boundary_flags())
if __name__=='__main__':
    d=validate_gauntlets();write_json(OUT/'bossesrise-r2i8a-integrity.json',d);print(json.dumps(d,indent=2))
