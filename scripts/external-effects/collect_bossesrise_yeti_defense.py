from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_bossesrise_foundation import targets,KEY,PKG

YETI='entity/boss/yeti/YetiEntity'
CLASSES={YETI:['<init>','<clinit>','defineSynchedData','hurt','shouldCancelDeath','tick','baseTick','setState','isTimerDone','finalizeSpawn','assignIfPresent','createAttributes','addAdditionalSaveData','readAdditionalSaveData','isEnraged','isDead','canCollideWith','getDeltaMovement','checkFallDamage','registerGoals'],YETI+'$YetiEvents':None,YETI+'$YetiState':None,'configuration/ServerConfiguration':['<clinit>']}

def census():
    t=targets()[KEY];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(x for x in z.namelist() if x.endswith('.class')):
            raw=z.read(n);c=ClassFile(raw)
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if i['opcode'] in ['0xb2','0xb3','0xb6','0xb7','0xb8','0xb9'] and str(i.get('operand','')).startswith(PKG) and any(s in str(i.get('operand','')) for s in ['.DATA_DIE_ANIMTIME','.DATA_GROUNDSMASH_ANIMTIME','.DATA_HAS_USED_ULTIMATE','.DATA_IS_ENRAGED','.DATA_HIT_TICK','BossCancelDieProcedure.execute('])]
                if hits:rows.append(dict(entry=n,entry_sha256=byte_hash(raw),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits))
    return dict(jar_sha256=t['sha256'],scope='Whole native artifact Yeti phase/resource/hit markers and legacy death counter references; render-only reads do not establish extra admission.',rows=rows)

def save():
    rows=[];t=targets()[KEY]
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in CLASSES.items():
            n=PKG+short+'.class';c=ClassFile(z.read(n));names=wanted or sorted({m['name'] for m in c.methods});names=sorted(set(names)|{m['name'] for m in c.methods if any(m['name'].startswith('lambda$'+v+'$') for v in names)})
            rows.append(dict(id='br:yeti_defense:'+short,mod_key=KEY,entry=n,methods=names))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Yeti native defense/phase/death ordering; tick offensive witnesses retained for next section, not yet semantically accepted.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/bossesrise-yeti-defense.json',s);write_json(OUT/'native-evidence/bossesrise-yeti-defense.json',collect(s));write_json(OUT/'bossesrise-yeti-defense-census.json',census())
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None)
    a['classes']={'net/minecraft/world/entity/projectile/ThrownTrident.class':['<init>'],'net/minecraft/world/entity/LivingEntity.class':['canFreeze','hurt','die','getDamageAfterMagicAbsorb']}
    # ThrownTrident may be raw-only in this exact patched archive.
    raw={}
    with zipfile.ZipFile(a['path']) as z:
        for n in list(a['classes']):
            if n not in z.namelist():raw[n[:-6]]=a['classes'].pop(n)
    r=dict(id='bossesrise-yeti-defense-244',scope='Actual superclass Trident/arrow double modifier, native downstream hurt and freeze admission.',archives=[a]);write_json(OUT/'reference-specifications/bossesrise-yeti-defense-244.json',r);write_json(OUT/'reference-evidence/bossesrise-yeti-defense-244.json',reference_collect(r,source_aids=True))
    s=dict(classes=raw,resources=[]);write_json(OUT/'vanilla-specifications/bossesrise-yeti-defense.json',s);write_json(OUT/'vanilla-evidence/bossesrise-yeti-defense.json',prepare(s));write_json(OUT/'reference-routing/bossesrise-yeti-defense.json',dict(archive=a['path'],sha256=a['sha256'],absent_entries=[k+'.class' for k in raw]))
    print('Yeti defense pinned')

if __name__=='__main__':save()
