from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_bomd_shared import census,PKG
from assemble_bomd_shared import CP,STEM,FACTS
from bomd_combat_common import preserve_section

def validate_shared():
    e=read_json(OUT/'native-evidence/bomd-shared.json');assert collect(read_json(OUT/'native-specifications/bomd-shared.json'))==e and len(e['witnesses'])==19
    r=read_json(OUT/'reference-evidence/bomd-shared-244.json');assert reference_collect(read_json(OUT/'reference-specifications/bomd-shared-244.json'))==r and len(r['witnesses'])==11
    c=read_json(OUT/'bomd-shared-census.json');assert census()==c and len(c['rows'])==13
    w={x['entry']:x for x in e['witnesses']+r['witnesses']}
    def body(path,name):return next(m['instructions'] for m in w[path+'.class']['methods'] if m['name']==name)
    def b(short,name):return body(PKG+short,name)
    def hits(ins,s):return [i for i in ins if s in str(i.get('operand',''))]
    def offset(ins,s):return hits(ins,s)[0]['offset']
    ins=b('entity/util/BaseEntity','hurt');assert offset(ins,'.beforeDamage(')<offset(ins,'.shouldDamage(')<offset(ins,'.hurt(')<offset(ins,'.afterDamage(')
    assert len(hits(ins,'isClientSide()'))==2
    ins=b('entity/util/BaseEntity','tick');assert len(hits(ins,'.updateEvents('))==2 and offset(ins,'.updateEvents(')<offset(ins,'PathfinderMob.tick(')<hits(ins,'.updateEvents(')[1]['offset']
    constructors=[x for x in c['rows'] if hits(x['hits'],'EffectsImmunity.<init>')];assert {x['entry'] for x in constructors}=={PKG+'entity/custom/'+n+'/'+cl+'.class' for n,cl in [('gauntlet','GauntletEntity'),('obsidilith','ObsidilithEntity')]}
    for row in constructors:
        ins=body(row['entry'][:-6],'<init>');assert hits(ins,'MobEffects.POISON') and hits(ins,'MobEffects.WITHER') and len(hits(ins,'Holder.value()'))>=2
    ins=b('entity/util/EffectsImmunity','canBeAffected');assert offset(ins,'getEffect()Lnet/minecraft/core/Holder;')<offset(ins,'List.contains(') and not hits(ins,'.value(')
    ins=body('net/minecraft/core/Holder$Reference','equals');assert any(i['opcode']=='0xc1' and i.get('operand')=='net/minecraft/core/Holder' for i in ins)
    ins=body('classes/java/util/Arrays$ArrayList','indexOf');assert hits(ins,'Object.equals(')
    ins=body('net/neoforged/neoforge/event/entity/living/MobEffectEvent$Applicable','getApplicationResult');assert hits(ins,'Result.APPLY') and hits(ins,'Result.DEFAULT') and hits(ins,'.canBeAffected(')
    ins=body('net/neoforged/neoforge/common/CommonHooks','canMobEffectBeApplied')
    # Overloads are both pinned; inspect the event-posting one.
    methods=w['net/neoforged/neoforge/common/CommonHooks.class']['methods'];assert any(hits(m['instructions'],'.post(') and hits(m['instructions'],'.getApplicationResult(') for m in methods)
    ins=b('entity/damage/DamageMemory','afterDamage');assert hits(ins,'.getEntity(') and hits(ins,'HistoricalData.add(') and any(i.get('operand')==4.0 for i in ins)
    ins=b('entity/damage/StagedDamageHandler','afterDamage');assert len(hits(ins,'.roundedStep('))==2 and hits(ins,'Runnable.run(') and not any(i['opcode']=='0x15' and i.get('operand')==4 for i in ins)
    ins=b('entity/custom/lich/LichUtils','cappedHeal');assert offset(ins,'.roundedStep(')<offset(ins,'Mth.clamp(')<offset(ins,'Consumer.accept(') and not hits(ins,'.setHealth(')
    ins=b('entity/custom/void_blossom/CappedHeal','tick');assert offset(ins,'.getTarget(')<offset(ins,'.cappedHeal(')
    ins=b('entity/ai/TargetSwitcher','trySwitchTarget');assert hits(ins,'.nextInt(') and hits(ins,'.setTarget(')
    ins=b('entity/ai/TargetSwitcher','filterTargetableEntities');assert hits(ins,'.hasLineOfSight(') and hits(ins,'FOLLOW_RANGE') and hits(ins,'.canAttack(')
    api='com/cerbon/cerbons_api/'
    ins=body(api+'api/general/event/EventScheduler','updateEvents');assert offset(ins,'.addAll(')<offset(ins,'.clear(')<offset(ins,'.shouldDoEvent(')<offset(ins,'.doEvent(')<offset(ins,'.removeIf(')
    ins=body(api+'api/general/event/TimedEvent','shouldDoEvent');assert hits(ins,'.age') and hits(ins,'.delay') and hits(ins,'Supplier.get(')
    ins=body(api+'api/general/event/TimedEvent','shouldRemoveEvent');assert hits(ins,'.duration') and hits(ins,'Supplier.get(')
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==6 and len(d['delivery_paths'])==13 and len(d['review_required'])==1
    assert not d['remaining_subsection_native_ambiguities'] and sum(x['stage_scaling_needed'] for x in d['mechanic_packages'])==1
    preserved=preserve_section(d);assert preserved==dict(effects=625,sources=1535,paths=1535,comparisons=625,primitives=827)
    return dict(schema='tno.external_effects.bomd_shared_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',native_witnesses=19,reference_witnesses=11,caller_methods=13,mechanic_packages=6,delivery_paths=13,numeric_scaling_points=1,review_required=1,accepted_counts_preserved=preserved,promoted_records=0,whole_mod_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_shared();write_json(OUT/'bomd-r2j2-integrity.json',d);print(json.dumps(d,indent=2))
