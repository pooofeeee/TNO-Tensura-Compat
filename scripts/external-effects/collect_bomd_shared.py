from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_bomd_foundation import targets,KEY,PKG

CLASSES={
 'entity/util/BaseEntity':['<init>','hurt','canBeAffected','tick','tickDeath'],
 'entity/util/EntityStats':None,'entity/util/EntityAdapter':['isAlive'],
 'entity/util/EffectsImmunity':None,'entity/damage/CompositeDamageHandler':None,
 'entity/damage/DamageMemory':None,'entity/damage/DamageMemory$DamageHistory':None,
 'entity/damage/DamagedAttackerNotSeen':None,'entity/damage/StagedDamageHandler':None,
 'entity/ai/TargetSwitcher':None,'entity/custom/void_blossom/CappedHeal':None,
 'entity/custom/lich/LichUtils':['cappedHeal','<clinit>'],
 'entity/custom/lich/LichMoveLogic':['<init>','beforeDamage','afterDamage'],
 'entity/custom/obsidilith/ObsidilithMoveLogic':['<init>','beforeDamage','afterDamage'],
 'entity/custom/obsidilith/ObsidilithUtils':['<clinit>'],
 'entity/custom/lich/LichEntity':['<init>'],
 'entity/custom/obsidilith/ObsidilithEntity':['<init>'],
 'entity/custom/gauntlet/GauntletEntity':['<init>'],
 'entity/custom/void_blossom/VoidBlossomEntity':['<init>','<clinit>'],
}

def census():
    t=targets()[KEY];rows=[]
    needles=['EffectsImmunity.<init>','StagedDamageHandler.<init>','CompositeDamageHandler.<init>','DamageMemory.<init>','DamagedAttackerNotSeen.<init>','CappedHeal.<init>','.cappedHeal(','.trySwitchTarget(']
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(x for x in z.namelist() if x.endswith('.class')):
            raw=z.read(n);c=ClassFile(raw)
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if i['opcode'] in ['0xb6','0xb7','0xb8','0xb9'] and str(i.get('operand','')).startswith(PKG) and any(s in str(i.get('operand','')) for s in needles)]
                if hits:rows.append(dict(entry=n,entry_sha256=byte_hash(raw),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits))
    return dict(jar_sha256=t['sha256'],scope='Whole-artifact native constructor/helper caller census. Concrete boss attack geometry and timing remain separate family work.',rows=rows)

def save():
    t=targets()[KEY];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in CLASSES.items():
            n=PKG+short+'.class';c=ClassFile(z.read(n));names=wanted or sorted({m['name'] for m in c.methods});names=sorted(set(names)|{m['name'] for m in c.methods if any(m['name'].startswith('lambda$'+v+'$') for v in names)})
            rows.append(dict(id='bomd:shared:'+short,mod_key=KEY,entry=n,methods=names))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Shared native admission/damage memory/phase transitions/healing and actual boss installation sites.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/bomd-shared.json',s);write_json(OUT/'native-evidence/bomd-shared.json',collect(s));write_json(OUT/'bomd-shared-census.json',census())
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None)
    a['classes']={'net/minecraft/core/Holder$Reference.class':['*'],'net/minecraft/core/Holder$Direct.class':['*'],'net/minecraft/world/effect/MobEffectInstance.class':['getEffect'],'net/minecraft/world/entity/LivingEntity.class':['addEffect','canBeAffected','heal']}
    neo=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][1]);neo.pop('semantic_review',None)
    neo['classes']={'net/neoforged/neoforge/common/CommonHooks.class':['canMobEffectBeApplied'],'net/neoforged/neoforge/event/entity/living/MobEffectEvent$Applicable.class':['getApplicationResult']}
    dep=MODS/'CerbonsAPI-NeoForge-1.21-1.3.0.jar'
    prefix='com/cerbon/cerbons_api/'
    b=dict(path=str(dep),sha256=sha256(dep),classes={prefix+n+'.class':v for n,v in {'api/general/event/EventScheduler':['*'],'api/general/event/TimedEvent':['*'],'api/general/data/HistoricalData':['*'],'api/static_utilities/MathUtils':['roundedStep']}.items()})
    # Pin Java List implementation used by Arrays.asList: contains delegates indexOf and compares the argument to each element.
    j=Path('C:/Program Files/Java/jdk-21/jmods/java.base.jmod')
    c=dict(path=str(j),sha256=sha256(j),classes={'classes/java/util/Arrays$ArrayList.class':['contains','indexOf']})
    r=dict(id='bomd-shared-244',scope='Pinned native Holder/effect admission, installed CerbonsAPI scheduling/rounding/history, and JDK list comparison. Static semantics, not runtime pack certification.',archives=[a,neo,b,c])
    write_json(OUT/'reference-specifications/bomd-shared-244.json',r);write_json(OUT/'reference-evidence/bomd-shared-244.json',reference_collect(r,source_aids=True))
    print('Shared witnesses',len(rows),'caller methods',len(census()['rows']))

if __name__=='__main__':save()
