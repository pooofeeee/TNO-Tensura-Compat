from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_bomd_blossom import PKG,source_tags
from assemble_bomd_blossom import CP,STEM,FACTS
from bomd_combat_common import preserve_section

def validate_blossom():
    e=read_json(OUT/'native-evidence/bomd-blossom.json');assert collect(read_json(OUT/'native-specifications/bomd-blossom.json'))==e and len(e['witnesses'])==21
    r=read_json(OUT/'reference-evidence/bomd-blossom-244.json');assert reference_collect(read_json(OUT/'reference-specifications/bomd-blossom-244.json'))==r
    v=read_json(OUT/'vanilla-evidence/bomd-blossom.json');assert prepare(read_json(OUT/'vanilla-specifications/bomd-blossom.json'))==v
    assert source_tags()==read_json(OUT/'bomd-blossom-source-tags.json')
    w={x['entry']:x for x in e['witnesses']+r['witnesses']}
    def b(short,name):return next(m['instructions'] for m in w[PKG+short+'.class']['methods'] if m['name']==name)
    def hits(ins,s):return [i for i in ins if s in str(i.get('operand',''))]
    def off(ins,s):return hits(ins,s)[0]['offset']
    def ignored(ins,s):
        ix=next(i for i,x in enumerate(ins) if s in str(x.get('operand','')));assert int(ins[ix+1]['opcode'],16)==0x57
    base='entity/custom/void_blossom/'
    assert [int(i['opcode'],16) for i in b(base+'hitbox/VoidBlossomCompoundHitbox','shouldDamage')]==[4,172]
    ins=b(base+'hitbox/VoidBlossomCompoundHitbox','afterDamage');assert off(ins,'.nextDamagedPart')<off(ins,'IS_PROJECTILE')<off(ins,'.thorns(')<off(ins,'.hurt(');ignored(ins,'.hurt(')
    assert hits(b(base+'hitbox/NetworkedHitboxManager','setNextDamagedPart'),'Map.get(')
    ins=b(base+'VoidBlossomSpikeTick','tick');assert hits(ins,'.distanceToSqr(') and hits(ins,'.thorns(') and not hits(ins,'.isAlive(');ignored(ins,'.hurt(')
    ins=b(base+'Spikes','damageEntity');assert off(ins,'.getAttributeValue(')<off(ins,'.shieldPiercing(')<off(ins,'.hurt(');ignored(ins,'.hurt(')
    ins=b('projectile/SporeBallProjectile','entityHit');assert hits(ins,'.thrown(') and not any(hits(ins,s) for s in ['.onImpact(','.discard(','.addEffect(']);ignored(ins,'.hurt(')
    assert hits(b('projectile/SporeBallProjectile','onHitBlock'),'.onImpact(')
    ins=b('projectile/SporeBallProjectile','onImpact');assert off(ins,'.impacted')<off(ins,'.doExplosion(')
    area=next(m['instructions'] for m in w[PKG+'projectile/SporeBallProjectile.class']['methods'] if hits(m['instructions'],'MobEffects.POISON'))
    assert off(area,'.getAttributeValue(')<off(area,'.getOwner(')<off(area,'.shieldPiercing(')<off(area,'.hurt(')<off(area,'.addEffect(');ignored(area,'.hurt(')
    assert not any(hits(m['instructions'],'Level.explode(') for m in w[PKG+'projectile/SporeBallProjectile.class']['methods'])
    ins=b('projectile/PetalBladeProjectile','entityHit');assert off(ins,'.thrown(')<off(ins,'.hurt(')<off(ins,'Consumer.accept(')<off(ins,'.discard(');ignored(ins,'.hurt(')
    ins=b(base+'BladeAction','lambda$perform$5');assert hits(ins,'MathUtils.lineCallback(') if ins else False
    assert any(hits(m['instructions'],'LichUtils.cappedHeal(') and any(i.get('operand')==10.0 for i in m['instructions']) for m in w[PKG+'block/custom/VoidBlossomBlock.class']['methods'])
    ins=b(base+'LightBlockRemover','tick');assert hits(ins,'.deathTime') and hits(ins,'.remove(') and not hits(ins,'.explode(')
    poison=next(m['instructions'] for m in w['net/minecraft/world/effect/PoisonMobEffect.class']['methods'] if m['name']=='applyEffectTick')
    assert off(poison,'.getHealth(')<off(poison,'POISON_DAMAGE')<off(poison,'.hurt(') and hits(poison,'DamageTypes.MAGIC')
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==8 and len(d['delivery_paths'])==15 and len(d['review_required'])==1 and not d['remaining_subsection_native_ambiguities']
    assert sum(m['stage_scaling_needed'] for m in d['mechanic_packages'])==5
    preserved=preserve_section(d);assert preserved==dict(effects=625,sources=1535,paths=1535,comparisons=625,primitives=827)
    return dict(schema='tno.external_effects.bomd_blossom_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',native_witnesses=21,reference_witnesses=len(r['witnesses']),vanilla_classes=len(v['classes']),mechanic_packages=8,delivery_paths=15,numeric_scaling_points=5,review_required=1,accepted_counts_preserved=preserved,promoted_records=0,whole_mod_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_blossom();write_json(OUT/'bomd-r2j6-integrity.json',d);print(json.dumps(d,indent=2))
