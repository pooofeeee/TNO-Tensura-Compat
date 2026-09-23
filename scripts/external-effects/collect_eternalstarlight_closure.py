import re
from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_eternalstarlight_foundation import ES,targets

WATCH=re.compile(r'\.(hurt|heal|setHealth|kill|addEffect|removeEffect|removeAllEffects|forceAddEffect|setAbsorptionAmount|setTicksFrozen|igniteForSeconds|igniteForTicks|setRemainingFireTicks|explode|doHurtTarget|canBeAffected|isInvulnerableTo|isDamageSourceBlocked|isAlliedTo|startRiding|setTarget|knockback|push|setDeltaMovement|addDeltaMovement|teleportTo|randomTeleport|causeFallDamage)\(')
OVERRIDES={'hurt','doHurtTarget','canBeAffected','isInvulnerableTo','isAlliedTo','wantsToAttack','causeFallDamage','checkFallDamage','getKnockback','isBlocking','entityInside','stepOn','fallOn','onHitEntity','onHitBlock'}
EXTRA=['common/block/entity/AbstractDuskLightBlockEntity','common/block/entity/AbstractDuskLightBlockEntity$1','common/block/entity/DuskEmitterBlockEntity','common/block/entity/DuskLightBlockEntity','common/block/DuskEmitterBlock','common/block/DuskLightBlock','common/block/ReinforcedDuskLightBlock','common/block/entity/AlloyFurnaceBlockEntity','common/block/AlloyFurnaceBlock','common/block/ThermalSpringstoneBlock','common/block/LunarisCactusGelBlock','common/item/misc/EthericEyeItem','common/entity/living/monster/Stranghoul$HirerHurtTargetGoal','common/entity/living/monster/Stranghoul$HirerHurtByTargetGoal','common/handler/ESCommonSetupHandler$2','common/item/misc/GalacticQuiverItem','common/entity/living/animal/StarfireBird']

def census():
    t=targets()['eternalstarlight'];rows=[];inventory=[]
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(x for x in z.namelist() if x.endswith('.class')):
            raw=z.read(n);c=ClassFile(raw);inventory.append(dict(entry=n,sha256=byte_hash(raw),super_class=c.super))
            if '/client/' in n or '/data/provider/' in n:continue
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if WATCH.search(str(i.get('operand',''))) and i['opcode'] in ('0xb6','0xb7','0xb8','0xb9')]
                if hits or m['name'] in OVERRIDES:rows.append(dict(entry=n,entry_sha256=byte_hash(raw),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits))
    return dict(schema='tno.external_effects.es_closure_census.v1',jar_sha256=t['sha256'],class_count=len(inventory),class_inventory=inventory,watched_methods=rows,scope='Whole installed class inventory plus server/common combat calls and admission overrides; explicit semantic disposition required, never infer semantics from scan membership alone.')

def save():
    t=targets()['eternalstarlight'];seen=set()
    for f in (OUT/'native-evidence').glob('eternalstarlight-*.json'):
        if f.name=='eternalstarlight-closure.json':continue
        for w in read_json(f)['witnesses']:
            for m in w.get('methods',[]):seen.add((w['entry'],m['name'],m['descriptor']))
    c=census();chosen={ES+n+'.class':None for n in EXTRA}
    for row in c['watched_methods']:
        if (row['entry'],row['method'],row['descriptor']) not in seen:
            if row['entry'] not in chosen:chosen[row['entry']]=[]
            if chosen[row['entry']] is not None:chosen[row['entry']].append(row['method'])
    rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for n in z.namelist():
            if n.endswith('.class') and '/mixin/' in n and '/client/' not in n:chosen[n]=None
        for n in [ES+'common/registry/ESBlocks.class',ES+'common/registry/ESItems.class']:
            cls=ClassFile(z.read(n));chosen[n]=[m['name'] for m in cls.methods if any(any(s in str(i['operand']) for s in ['MagmaBlock.<init>','FlintAndSteelItem.<init>','TorreyaCampfireBlock.<init>','LunarisCactusGelBlock.<init>']) for i in cls.instructions(m.get('code',b'')))]
        for n,wanted in sorted(chosen.items()):
            cls=ClassFile(z.read(n));names=sorted(set(wanted if wanted is not None else [m['name'] for m in cls.methods]));names+=sorted({m['name'] for m in cls.methods if any(m['name'].startswith('lambda$'+v+'$') for v in names)}-set(names))
            rows.append(dict(id='es:closure:'+n,mod_key='eternalstarlight',entry=n,methods=names))
        for n in sorted(x for x in z.namelist() if x.endswith('.json') and '/tags/' in x and any(v in x for v in ['dusk_light','mends_naturally','repaired_by_crescent','stranghoul_'])):
            rows.append(dict(id='es:closure:data:'+n,mod_key='eternalstarlight',entry=n))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Final native combat-call gaps, remaining mixins and inherited hazards; utility branches excluded explicitly in review.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/eternalstarlight-closure.json',s);write_json(OUT/'native-evidence/eternalstarlight-closure.json',collect(s));write_json(OUT/'eternalstarlight-combat-closure-census.json',c)
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None);a['classes']={};raw={}
    wanted={'net/minecraft/world/level/block/MagmaBlock':['stepOn'],'net/minecraft/world/level/block/CampfireBlock':['entityInside'],'net/minecraft/world/level/block/SlimeBlock':['fallOn','updateEntityAfterFallOn','bounceUp','stepOn'],'net/minecraft/world/level/block/BubbleColumnBlock':['entityInside'],'net/minecraft/world/entity/Entity':['baseTick','setRemainingFireTicks'],'net/minecraft/world/entity/projectile/AbstractArrow':['doKnockback'],'net/minecraft/world/item/FlintAndSteelItem':['useOn']}
    with zipfile.ZipFile(a['path']) as z:
        for k,v in wanted.items():
            if k+'.class' in z.namelist():
                cls=ClassFile(z.read(k+'.class'));a['classes'][k+'.class']=v+[m['name'] for m in cls.methods if any(m['name'].startswith('lambda$'+n+'$') for n in v)]
            else:raw[k]=v
    r=dict(id='eternalstarlight-closure-244',scope='Inherited native hazards/fire and separate arrow knockback contribution; raw fallback only absent classes.',archives=[a])
    write_json(OUT/'reference-specifications/eternalstarlight-closure-244.json',r);write_json(OUT/'reference-evidence/eternalstarlight-closure-244.json',reference_collect(r,source_aids=True))
    s=dict(classes=raw,resources=[]);write_json(OUT/'vanilla-specifications/eternalstarlight-closure.json',s);write_json(OUT/'vanilla-evidence/eternalstarlight-closure.json',prepare(s));write_json(OUT/'reference-routing/eternalstarlight-closure.json',dict(archive=a['path'],sha256=a['sha256'],absent_entries=[k+'.class' for k in raw]))
    print('Closure witnesses saved',len(c['watched_methods']))
if __name__=='__main__':save()
