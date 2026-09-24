from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_bomd_obsidilith import PKG
from assemble_bomd_obsidilith import CP,STEM,FACTS
from bomd_combat_common import preserve_section

def validate_obsidilith():
    e=read_json(OUT/'native-evidence/bomd-obsidilith.json');assert collect(read_json(OUT/'native-specifications/bomd-obsidilith.json'))==e and len(e['witnesses'])==19
    r=read_json(OUT/'reference-evidence/bomd-obsidilith-244.json');assert reference_collect(read_json(OUT/'reference-specifications/bomd-obsidilith-244.json'))==r and len(r['witnesses'])==9
    w={x['entry']:x for x in e['witnesses']+r['witnesses']}
    def body(path,name):return next(m['instructions'] for m in w[path+'.class']['methods'] if m['name']==name)
    def b(short,name):return body(PKG+short,name)
    def hits(ins,s):return [i for i in ins if s in str(i.get('operand',''))]
    def off(ins,s):return hits(ins,s)[0]['offset']
    base='entity/custom/obsidilith/'
    ins=b(base+'ShieldDamageHandler','shouldDamage');assert hits(ins,'BYPASSES_INVULNERABILITY') and hits(ins,'IS_PROJECTILE') and hits(ins,'.getEntity(') and hits(ins,'.knockback(')
    assert not any(hits(ins,s) for s in ['.hurt(','.setHealth(','.remove(','.clear('])
    ins=b(base+'ObsidilithEntity','serverTick');assert off(ins,'.removeIf(')<off(ins,'.isEmpty(')<off(ins,'.set(')
    methods=w[PKG+base+'ObsidilithEntity.class']['methods'];assert any(hits(m['instructions'],'OBSIDILITH_RUNE') and hits(m['instructions'],'.closerThan(') for m in methods)
    ins=b('block/custom/ObsidilithRuneBlock','onPlace');assert hits(ins,'.scheduleTick(') and any(i.get('operand')==10 for i in ins)
    ins=b('block/custom/ObsidilithRuneBlock','linkToEntities');assert hits(ins,'.getEntitiesOfClass(')
    for method in ['load','saveWithoutId']:assert any(i.get('operand')=='activePillars' for i in b(base+'ObsidilithEntity',method))
    ins=b(base+'ObsidilithEntity','getArmorValue');assert hits(ins,'.getTarget(') and any(i.get('operand')==24 for i in ins)
    for short in ['BurstAction','WaveAction','SpikeAction']:
        ins=b(base+short,'damageEntity');assert hits(ins,'ATTACK_DAMAGE') and off(ins,'.shieldPiercing(')<off(ins,'.hurt(')
        ix=next(i for i,x in enumerate(ins) if '.hurt(' in str(x.get('operand','')));assert int(ins[ix+1]['opcode'],16)==0x57
    ins=b(base+'BurstAction','damageEntity');assert off(ins,'.sendToClient(')<off(ins,'.hurt(') and any(i.get('operand')==1.3 for i in ins)
    ins=b(base+'WaveAction','damageEntity');assert off(ins,'.sendToClient(')<off(ins,'.setRemainingFireTicks(')<off(ins,'.hurt(') and any(i.get('operand')==5 for i in ins)
    ins=b(base+'SpikeAction','damageEntity');assert off(ins,'.hurt(')<off(ins,'.addEffect(') and hits(ins,'MOVEMENT_SLOWDOWN') and any(i.get('operand')==120 for i in ins)
    ins=b('packet/custom/SendDeltaMovementS2CPacket','handle');assert hits(ins,'Side.SERVER') and hits(ins,'.execute(')
    assert any(hits(m['instructions'],'.setDeltaMovement(') for m in w[PKG+'packet/custom/SendDeltaMovementS2CPacket.class']['methods'])
    api='com/cerbon/cerbons_api/'
    ins=body(api+'api/general/event/Event','shouldDoEvent');assert hits(ins,'.condition') and not hits(ins,'.shouldCancel')
    ins=body(api+'neoforge/event/NeoForgeEvents','onLevelTick');assert off(ins,'.get(')<off(ins,'.updateEvents(')
    ins=body(api+'neoforge/attachment/saved_data/LevelEventScheduler','save');assert not hits(ins,'.put')
    ins=body('net/minecraft/world/entity/Entity','baseTick');assert hits(ins,'.onFire(') and hits(ins,'.hurt(') and any(i.get('operand')==20 for i in ins)
    ins=body('net/minecraft/world/entity/LivingEntity','knockback');assert hits(ins,'.onLivingKnockBack(') and hits(ins,'KNOCKBACK_RESISTANCE')
    ins=b(base+'ObsidilithUtils','onDeath');assert hits(ins,'.explode(') and any(i.get('operand')==2.0 for i in ins)
    assert any(hits(m['instructions'],'.explode(') and hits(m['instructions'],'.explosionPower') for m in w[PKG+base+'AnvilAction.class']['methods'])
    a=read_json(OUT/'annotation-evidence/bomd-world-scheduler-javap.json');assert sha256(a['tool'])==a['tool_sha256'] and sha256(OUT/a['output_file'])==a['output_sha256']
    text=(OUT/a['output_file']).read_text(encoding='utf-8');assert 'SubscribeEvent' in text and 'LevelTickEvent$Post' in text
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==9 and len(d['delivery_paths'])==13 and not d['remaining_subsection_native_ambiguities']
    assert sum(m['stage_scaling_needed'] for m in d['mechanic_packages'])==2
    preserved=preserve_section(d);assert preserved==dict(effects=625,sources=1535,paths=1535,comparisons=625,primitives=827)
    return dict(schema='tno.external_effects.bomd_obsidilith_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',native_witnesses=19,reference_witnesses=9,mechanic_packages=9,delivery_paths=13,numeric_scaling_points=2,accepted_counts_preserved=preserved,promoted_records=0,whole_mod_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_obsidilith();write_json(OUT/'bomd-r2j4-integrity.json',d);print(json.dumps(d,indent=2))
