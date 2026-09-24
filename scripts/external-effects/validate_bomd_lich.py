from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_bomd_lich import source_tags,PKG
from assemble_bomd_lich import CP,STEM,FACTS
from bomd_combat_common import preserve_section

def validate_lich():
    e=read_json(OUT/'native-evidence/bomd-lich.json');assert collect(read_json(OUT/'native-specifications/bomd-lich.json'))==e and len(e['witnesses'])==27
    r=read_json(OUT/'reference-evidence/bomd-lich-244.json');assert reference_collect(read_json(OUT/'reference-specifications/bomd-lich-244.json'))==r and len(r['witnesses'])==9
    v=read_json(OUT/'vanilla-evidence/bomd-lich.json');assert prepare(read_json(OUT/'vanilla-specifications/bomd-lich.json'))==v and len(v['classes'])==5
    t=read_json(OUT/'bomd-lich-source-tags.json');assert source_tags()==t
    assert 'minecraft:is_projectile' in t['types']['minecraft:thrown'] and 'minecraft:is_explosion' in t['types']['minecraft:player_explosion']
    assert all(not any(s in tag for s in ['bypasses_armor','bypasses_shield','bypasses_resistance']) for n,tags in t['types'].items() if n!='minecraft:generic_kill' for tag in tags)
    w={x['entry']:x for x in e['witnesses']+r['witnesses']};raw={x['class_name']:x for x in v['classes']}
    def body(path,name):return next(m['instructions'] for m in w[path+'.class']['methods'] if m['name']==name)
    def b(short,name):return body(PKG+short,name)
    def vb(path,name):return next(m['instructions'] for m in raw[path]['methods'] if m['name']==name)
    def hits(ins,s):return [i for i in ins if s in str(i.get('operand',''))]
    def off(ins,s):return hits(ins,s)[0]['offset']
    lich=w[PKG+'entity/custom/lich/LichEntity.class'];assert not {'hurt','isInvulnerableTo','canBeAffected'}&{m['name'] for m in lich['methods']}
    ins=b('projectile/MagicMissileProjectile','entityHit');assert off(ins,'.thrown(')<off(ins,'.hurt(')<off(ins,'Consumer.accept(')<off(ins,'.discard(')
    hi=next(i for i,x in enumerate(ins) if '.hurt(' in str(x.get('operand','')));assert ins[hi+1]['opcode']=='0x57'
    assert hits(ins,'ATTACK_DAMAGE') and not hits(ins,'.doPostAttackEffects(')
    for short in ['VolleyAction','VolleyRageAction']:
        methods=w[PKG+'entity/custom/lich/'+short+'.class']['methods'];assert any(hits(m['instructions'],'.addEffect(Lnet/minecraft/world/effect/MobEffectInstance;)Z') for m in methods)
        assert any(hits(m['instructions'],'mobEffectDuration') and hits(m['instructions'],'mobEffectAmplifier') for m in methods)
    ins=b('projectile/comet/CometProjectile','hurt');assert off(ins,'.onImpact(')<off(ins,'.hurt(')
    ins=b('projectile/comet/CometProjectile','onImpact');assert off(ins,'.impacted')<off(ins,'.getOwner(')<off(ins,'Consumer.accept(')<off(ins,'.discard(')
    assert not hits(ins,'isClientSide') and not hits(ins,'.hurt(')
    for short in ['CometAction','CometRageAction']:
        methods=w[PKG+'entity/custom/lich/'+short+'.class']['methods'];expl=[m for m in methods if hits(m['instructions'],'.explode(')];assert len(expl)==1
        assert hits(expl[0]['instructions'],'ExplosionInteraction.MOB') and hits(expl[0]['instructions'],'explosionStrength')
    ins=b('entity/spawn/SimpleMobSpawner','spawn');assert off(ins,'.setPos(')<off(ins,'.finalizeSpawn(')<off(ins,'.addFreshEntityWithPassengers(') and hits(ins,'MOB_SUMMONED')
    ins=b('entity/custom/lich/MinionAction','<clinit>');assert any('Attributes:' in str(i.get('operand','')) and 'Health:14,Size:2' in str(i.get('operand','')) for i in ins)
    ins=body('net/minecraft/world/entity/LivingEntity','readAdditionalSaveData');assert any(i.get('operand')=='attributes' for i in ins) and not any(i.get('operand')=='Attributes' for i in ins)
    ins=vb('net/minecraft/world/entity/monster/Phantom','finalizeSpawn');assert hits(ins,'.setPhantomSize(')
    ix=next(i for i,x in enumerate(ins) if '.setPhantomSize(' in str(x.get('operand','')));assert int(ins[ix-1]['opcode'],16)==3
    ins=vb('net/minecraft/world/entity/monster/Phantom','updatePhantomSizeInfo');assert hits(ins,'ATTACK_DAMAGE') and any(i.get('operand')==6 for i in ins)
    ins=vb('net/minecraft/world/entity/monster/Phantom$PhantomSweepAttackGoal','tick');assert hits(ins,'.doHurtTarget(')
    ins=body('net/minecraft/world/entity/Mob','doHurtTarget');assert off(ins,'.modifyDamage(')<off(ins,'.hurt(')<off(ins,'.doPostAttackEffects(')
    tele=w[PKG+'entity/custom/lich/TeleportAction.class']['methods'];assert any(hits(m['instructions'],'.teleportTo(') for m in tele) and not any(hits(m['instructions'],'.setInvulnerable(') for m in tele)
    ins=b('entity/custom/lich/LichEntity','die');assert off(ins,'.getEntitiesOfClass(')<off(ins,'.die(')
    ins=body('net/minecraft/world/entity/LivingEntity','kill');assert hits(ins,'.genericKill(') and hits(ins,'.hurt(')
    ins=body('net/minecraft/world/level/Explosion','explode');assert off(ins,'.getEntities(')<off(ins,'.onExplosionDetonate(')<off(ins,'.hurt(')<off(ins,'.getExplosionKnockback(')
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==9 and len(d['delivery_paths'])==16 and len(d['review_required'])==2
    assert not d['remaining_subsection_native_ambiguities'] and sum(m['stage_scaling_needed'] for m in d['mechanic_packages'])==3
    preserved=preserve_section(d);assert preserved==dict(effects=625,sources=1535,paths=1535,comparisons=625,primitives=827)
    return dict(schema='tno.external_effects.bomd_lich_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',native_witnesses=27,reference_witnesses=9,vanilla_classes=5,mechanic_packages=9,delivery_paths=16,numeric_scaling_points=3,review_required=2,accepted_counts_preserved=preserved,promoted_records=0,whole_mod_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_lich();write_json(OUT/'bomd-r2j3-integrity.json',d);print(json.dumps(d,indent=2))
