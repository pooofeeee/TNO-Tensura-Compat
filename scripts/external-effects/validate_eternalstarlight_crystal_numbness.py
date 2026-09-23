"""Reproduce exact witnesses and check high-impact status/debt ordering claims."""
from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_eternalstarlight_crystal_numbness import attachment_census
from collect_eternalstarlight_foundation import ES
from assemble_eternalstarlight_crystal_numbness import CP,STEM,FACTS
from eternalstarlight_combat_common import preserve_section

def validate_crystal_numbness():
    e=read_json(OUT/'native-evidence/eternalstarlight-crystal-numbness.json');assert collect(read_json(OUT/'native-specifications/eternalstarlight-crystal-numbness.json'))==e
    r=read_json(OUT/'reference-evidence/eternalstarlight-crystal-numbness-244.json');assert reference_collect(read_json(OUT/'reference-specifications/eternalstarlight-crystal-numbness-244.json'))==r
    assert prepare(read_json(OUT/'vanilla-specifications/eternalstarlight-crystal-numbness.json'))==read_json(OUT/'vanilla-evidence/eternalstarlight-crystal-numbness.json')
    routing=read_json(OUT/'reference-routing/eternalstarlight-crystal-numbness.json');assert sha256(routing['archive'])==routing['sha256']
    with zipfile.ZipFile(routing['archive']) as z:assert not(set(routing['absent_entries'])&set(z.namelist()))
    c=read_json(OUT/'eternalstarlight-status-attachment-census.json');assert attachment_census()==c
    assert {x['method'] for x in c['rows'] if any('NUMBNESS_DAMAGE' in str(i['operand']) for i in x['hits'])}=={'<clinit>','onModifyLivingActualHurtDamage','tickEffects'}
    w={x['entry']:x for x in e['witnesses']+r['witnesses']}
    def body(entry,method):return next(m['instructions'] for m in w[entry+'.class']['methods'] if m['name']==method)
    def hit(b,s):return [i for i in b if s in str(i.get('operand',''))]
    def pos(b,s):return hit(b,s)[0]['offset']
    def after(b,s):return b[b.index(hit(b,s)[0])+1]
    dot=body(ES+'common/effect/CrystalInfectionEffect','applyEffectTick');assert after(dot,'.hurt(')['opcode']=='0x57' and dot[-2]['operand']==1
    interval=body(ES+'common/effect/CrystalInfectionEffect','shouldApplyEffectTickThisTick');assert interval[1]['operand']==35 and interval[2]['opcode']=='0x70'
    cluster=body(ES+'common/entity/attack/CrystalCluster','tick');assert pos(cluster,'.discard(')<pos(cluster,'.shouldHarm(')<pos(cluster,'.hurt(')<pos(cluster,'.addEffect(')
    assert after(cluster,'.hurt(')['opcode']=='0x99' and cluster[cluster.index(hit(cluster,'.hurt(')[0])-1]['operand']==4.0
    assert not hit(cluster,'hasLineOfSight')
    bonus=body(ES+'common/item/combat/CrystalGreatswordItem','getAttackDamageBonus');assert hit(bonus,'0.25') and hit(bonus,'0.15000000596046448')
    melee=body(ES+'common/item/combat/CrystalGreatswordItem','postHurtEnemy');assert hit(melee,'.removeEffect(') and hit(melee,'.addEffect(') and not hit(melee,'.hurt(')
    pre=body(ES+'common/handler/ESCommonHandler','onModifyLivingActualHurtDamage');assert pos(pre,'BYPASSES_CRESCENT_PENDANT')<pos(pre,'NUMBNESS_DAMAGE')<pos(pre,'.setData(')<pos(pre,'BYPASSES_INVULNERABILITY')<pos(pre,'Math.max(')
    assert {i['operand'] for i in pre if i['opcode'] in ['0x12','0x13']}=={.75,.25}
    release=body(ES+'common/mixin/LivingEntityMixin','tickEffects');assert pos(release,'.hasEffect(')<pos(release,'.hurt(')<pos(release,'.setData(') and after(release,'.hurt(')['opcode']=='0x57'
    tick=body('net/minecraft/world/entity/LivingEntity','tickEffects');assert pos(tick,'.effectsDirty')<pos(tick,'.updateGlowingStatus(')
    window=[i for i in tick if pos(tick,'.effectsDirty')<i['offset']<pos(tick,'.updateGlowingStatus(')];assert hit(window,'.isClientSide') and sum(i['opcode'] in ['0x99','0x9a'] for i in window)>=2
    for cl in ['LivingEntity','player/Player']:
        damage=body('net/minecraft/world/entity/'+cl,'actuallyHurt');assert pos(damage,'getDamageAfterMagicAbsorb(')<pos(damage,'onLivingDamagePre(')<pos(damage,'Reduction.ABSORPTION')<pos(damage,'onLivingDamagePost(')
    magic=body('net/minecraft/world/entity/LivingEntity','getDamageAfterMagicAbsorb');assert pos(magic,'BYPASSES_RESISTANCE')<pos(magic,'BYPASSES_ENCHANTMENTS')
    for cl in ['AbstractArrow','FireworkRocketEntity']:
        b=body('net/minecraft/world/entity/projectile/'+cl,'tick' if cl=='AbstractArrow' else 'onHit');assert hit(b,'onProjectileImpact(')
    a=read_json(OUT/'annotation-evidence/eternalstarlight-crystal-numbness-javap.json');assert sha256(a['tool'])==a['tool_sha256'] and sha256(OUT/a['output_file'])==a['output_sha256']
    annotations=(OUT/a['output_file']).read_text(encoding='utf-8');assert 'target="Lnet/minecraft/world/entity/LivingEntity;updateGlowingStatus()V"' in annotations and 'AFTER' in annotations and 'BootstrapMethods:' in annotations
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==8 and len(d['delivery_paths'])==12
    debt=next(m for m in d['mechanic_packages'] if m['id']=='es:numbness_debt');assert not debt['stage_scaling_needed'] and 'must not scale again' in debt['stage_reason']
    assert all(v in (OUT/(STEM+'-review.md')).read_text(encoding='utf-8') for v in FACTS.values())
    preserved=preserve_section(d)
    return dict(schema='tno.external_effects.es_crystal_numbness_integrity.v1',checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),loader_witnesses=len(r['witnesses']),reviewed_packages=8,reviewed_paths=12,damage_types_reviewed=2,semantic_amount_and_order_checks='PASS',accepted_counts_preserved=preserved,promoted_records=0,whole_eternalstarlight_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_crystal_numbness();write_json(OUT/'eternalstarlight-r2h2a-integrity.json',d);print(json.dumps(d,indent=2))
