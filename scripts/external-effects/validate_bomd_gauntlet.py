from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_bomd_gauntlet import PKG
from assemble_bomd_gauntlet import CP,STEM,FACTS
from bomd_combat_common import preserve_section

def validate_gauntlet():
    e=read_json(OUT/'native-evidence/bomd-gauntlet.json');assert collect(read_json(OUT/'native-specifications/bomd-gauntlet.json'))==e and len(e['witnesses'])==16
    r=read_json(OUT/'reference-evidence/bomd-gauntlet-244.json');assert reference_collect(read_json(OUT/'reference-specifications/bomd-gauntlet-244.json'))==r and len(r['witnesses'])==16
    v=read_json(OUT/'vanilla-evidence/bomd-gauntlet.json');assert prepare(read_json(OUT/'vanilla-specifications/bomd-gauntlet.json'))==v and len(v['classes'])==3
    w={x['entry']:x for x in e['witnesses']+r['witnesses']}
    def body(path,name):return next(m['instructions'] for m in w[path+'.class']['methods'] if m['name']==name)
    def b(short,name):return body(PKG+short,name)
    def hits(ins,s):return [i for i in ins if s in str(i.get('operand',''))]
    def off(ins,s):return hits(ins,s)[0]['offset']
    base='entity/custom/gauntlet/'
    ins=b(base+'GauntletHitboxes','shouldDamage');assert all(hits(ins,s) for s in ['nextDamagedPart','disableHitboxesForCompatibility','BYPASSES_INVULNERABILITY','IS_EXPLOSION','IS_PROJECTILE','IS_FIRE','.getSourcePosition(','.knockback('])
    assert any(i.get('operand')=='eye' for i in ins) and not hits(ins,'.hurt(')
    assert off(ins,'.nextDamagedPart')<off(ins,'.disableHitboxesForCompatibility')
    ins=b(base+'GauntletHitboxes','<init>');assert any(i.get('operand')=='bettercombat' for i in ins) and any(i.get('operand')=='epicfight' for i in ins)
    ins=b(base+'GauntletGoalHandler','afterDamage');assert hits(ins,'.isAggroed') and hits(ins,'.addGoals(')
    for method in ['toTag','fromTag']:assert any(i.get('operand')=='isAggroed' for i in b(base+'GauntletGoalHandler',method))
    for short in ['PunchAction','SwirlPunchAction']:
        ins=b(base+short,'testEntityImpact');assert off(ins,'.doHurtTarget(')<off(ins,'.addDeltaMovement(')
        ix=next(i for i,x in enumerate(ins) if '.doHurtTarget(' in str(x.get('operand','')));assert int(ins[ix+1]['opcode'],16)==0x57
        ins=b(base+short,'testBlockPhysicalImpact');assert hits(ins,'.previousSpeed') and hits(ins,'.explode(')
    ins=b(base+'LaserAction','applyLaserToEntities');assert off(ins,'.addTransientModifier(')<off(ins,'.doHurtTarget(')<off(ins,'.removeModifier(') and hits(ins,'ADD_MULTIPLIED_BASE') and any(i.get('operand')==-.25 for i in ins)
    ins=b(base+'LaserAction','perform');assert hits(ins,'Vec3.ZERO') and hits(ins,'EventSeries')
    ins=b('util/VanillaCopiesServer','destroyBlocks');assert hits(ins,'Blocks.FIRE') and hits(ins,'RULE_MOBGRIEFING') and hits(ins,'WITHER_IMMUNE')
    assert any(hits(m['instructions'],'MobEffects.BLINDNESS') and hits(m['instructions'],'.addEffect(') for m in w[PKG+base+'BlindnessAction.class']['methods'])
    assert not any(hits(m['instructions'],'.addEffect(') for m in w[PKG+'packet/custom/BlindnessS2CPacket.class']['methods'])
    ins=b(base+'ServerGauntletDeathHandler','tick');assert hits(ins,'.deathTime') and off(ins,'.explode(')<off(ins,'.spawnAncientDebrisOnDeath')<off(ins,'.remove(')
    assert any(int(i['opcode'],16)==1 for i in ins) and any(i.get('operand')==4.0 for i in ins)
    api='com/cerbon/cerbons_api/'
    ins=body(api+'mixin/multipart_entities/ProjectileMixin','onCollision');assert off(ins,'.raycast(')<off(ins,'.setNextDamagedPart(')
    ins=body(api+'mixin/multipart_entities/client/MultiplayerGameModeMixin','attackHook');assert off(ins,'.raycast(')<off(ins,'.sendToServer(')<off(ins,'.setNextDamagedPart(')<off(ins,'.attack(')
    ins=body(api+'packet/custom/MultipartEntityInteractionC2SPacket','setNextDamagedPart');assert off(ins,'.setNextDamagedPart(')<off(ins,'.attack(')
    ins=body(api+'api/general/event/EventSeries','shouldRemoveEvent');assert hits(ins,'.shouldRemoveEvent(') and hits(ins,'Iterator.next(')
    ins=body('net/minecraft/world/level/Explosion','finalizeExplosion');assert hits(ins,'BaseFireBlock.getState(')
    ins=body('net/minecraft/world/level/block/BaseFireBlock','entityInside');assert off(ins,'.igniteForSeconds(')<off(ins,'.inFire(')<off(ins,'.hurt(')
    a=read_json(OUT/'annotation-evidence/bomd-multipart-javap.json');assert sha256(a['tool'])==a['tool_sha256'] and sha256(OUT/a['output_file'])==a['output_sha256']
    text=(OUT/a['output_file']).read_text(encoding='utf-8');assert 'onHit(Lnet/minecraft/world/phys/HitResult;)V' in text and 'attack(Lnet/minecraft/world/entity/player/Player;Lnet/minecraft/world/entity/Entity;)V' in text and 'HEAD' in text
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==9 and len(d['delivery_paths'])==18 and len(d['review_required'])==2 and not d['remaining_subsection_native_ambiguities']
    assert sum(m['stage_scaling_needed'] for m in d['mechanic_packages'])==4
    preserved=preserve_section(d);assert preserved==dict(effects=625,sources=1535,paths=1535,comparisons=625,primitives=827)
    return dict(schema='tno.external_effects.bomd_gauntlet_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',native_witnesses=16,reference_witnesses=16,vanilla_classes=3,mechanic_packages=9,delivery_paths=18,numeric_scaling_points=4,review_required=2,accepted_counts_preserved=preserved,promoted_records=0,whole_mod_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_gauntlet();write_json(OUT/'bomd-r2j5-integrity.json',d);print(json.dumps(d,indent=2))
