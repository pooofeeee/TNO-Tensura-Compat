from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_bomd_equipment import PKG
from assemble_bomd_equipment import CP,STEM,FACTS
from bomd_combat_common import preserve_section

def validate_equipment():
    e=read_json(OUT/'native-evidence/bomd-equipment.json');assert collect(read_json(OUT/'native-specifications/bomd-equipment.json'))==e and len(e['witnesses'])==27
    r=read_json(OUT/'reference-evidence/bomd-equipment-244.json');assert reference_collect(read_json(OUT/'reference-specifications/bomd-equipment-244.json'))==r
    v=read_json(OUT/'vanilla-evidence/bomd-equipment.json');assert prepare(read_json(OUT/'vanilla-specifications/bomd-equipment.json'))==v
    w={x['entry']:x for x in e['witnesses']+r['witnesses']}
    def b(short,name):return next(m['instructions'] for m in w[PKG+short+'.class']['methods'] if m['name']==name)
    def hits(ins,s):return [i for i in ins if s in str(i.get('operand',''))]
    def off(ins,s):return hits(ins,s)[0]['offset']
    p='item/custom/ChargedEnderPearlEntity'
    ins=b(p,'onHitEntity');assert off(ins,'.thrown(')<off(ins,'.hurt(') and any(int(i['opcode'],16)==11 for i in ins)
    ix=next(i for i,x in enumerate(ins) if '.hurt(' in str(x.get('operand','')));assert int(ins[ix+1]['opcode'],16)==87
    ins=b(p,'serverCollision');assert off(ins,'.teleportEntity(')<off(ins,'.applyMobEffects(')<off(ins,'.discard(')
    ins=b(p,'applyMobEffects');assert hits(ins,'DAMAGE_RESISTANCE') and hits(ins,'SLOW_FALLING') and hits(ins,'.knockback(') and not hits(ins,'.hurt(')
    ins=b('item/custom/ChargedEnderPearlItem','use');assert hits(ins,'.addCooldown(') and hits(ins,'.addFreshEntity(') and not hits(ins,'.shrink(')
    ins=b('item/BMDFoods','<clinit>');assert all(hits(ins,x) for x in ['REGENERATION','HEAL','DAMAGE_RESISTANCE','.alwaysEdible('])
    ins=b('item/custom/EarthdiveSpear','releaseUsing');assert off(ins,'.isCharged(')<off(ins,'.tryTeleport(')<off(ins,'.hurtAndBreak(') and not hits(ins,'.hurt(')
    ins=b('block/custom/MonolithBlock','getExplosionPower');assert hits(ins,'.getBlocksFromChunk(') and any(i.get('operand')==64 for i in ins) and any(abs(float(i.get('operand',0) or 0)-1.3)<.00001 for i in ins if isinstance(i.get('operand'),(int,float)))
    ins=b('block/custom/LevitationBlockEntity','tickFlight');assert all(hits(ins,x) for x in ['.mayfly','.flying','.isCreative(','.isSpectator(','ClientboundPlayerAbilitiesPacket']) and not hits(ins,'.addEffect(')
    ins=b('block/custom/VoidLilyBlock','<init>');assert hits(ins,'MobEffects.GLOWING') and any(int(i['opcode'],16)==11 for i in ins)
    for row in v['classes']:assert row
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==10 and len(d['delivery_paths'])==11 and len(d['review_required'])==2 and not d['remaining_subsection_native_ambiguities']
    assert all(set(p['labels'])<=set(DELIVERIES) for p in d['delivery_paths'])
    assert sum(m['stage_scaling_needed'] for m in d['mechanic_packages'])==3
    preserved=preserve_section(d);assert preserved==dict(effects=625,sources=1535,paths=1535,comparisons=625,primitives=827)
    # Every watched source and native effect reference is backed by installed instructions before promotion.
    keys=set()
    for f in (OUT/'native-evidence').glob('bomd-*.json'):
        for x in read_json(f)['witnesses']:
            keys|={(x['entry'],m['name'],m['descriptor']) for m in x.get('methods',[])}
    c=read_json(OUT/'bomd-source-census.json')
    for row in c['watched_methods']+c['native_effect_reference_methods']+c['custom_effect_registry_candidates']:
        assert (row['entry'],row['method'],row['descriptor']) in keys,row
    return dict(schema='tno.external_effects.bomd_equipment_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',native_witnesses=27,reference_witnesses=len(r['witnesses']),vanilla_classes=len(v['classes']),mechanic_packages=10,delivery_paths=11,numeric_scaling_points=3,review_required=2,watched_methods_backed=len(c['watched_methods']),native_effect_references_backed=len(c['native_effect_reference_methods']),accepted_counts_preserved=preserved,promoted_records=0,whole_mod_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_equipment();write_json(OUT/'bomd-r2j7-integrity.json',d);print(json.dumps(d,indent=2))
