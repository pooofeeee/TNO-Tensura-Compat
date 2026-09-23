from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_bossesrise_foundation import targets,KEY,PKG

BASE_METHODS=['<init>','defineSynchedData','addAdditionalSaveData','readAdditionalSaveData','tick','maybeCancelDeath','shouldCancelDeath','die','forEachNearbyEntity','forEachNearbyPlayer','attackEntity','meleeAttack','getLookOffset','getSourceEntity']
CLASSES={'entity/boss/AbstractBossEntity':BASE_METHODS+['onDamageTaken','setState','doAttack'],'entity/boss/AbstractStateBossEntity':BASE_METHODS+['actuallyHurt','cancelDeath','simulatePlayerKill'],'entity/boss/part/AbstractEntityPart':None,'entity/OwnableByAllEntity':None,'entity/OwnableByAllEntity$DoNotAttackOwnerGoal':None,'entity/OwnableByAllEntity$OwnerHurtByTargetGoal':None,'entity/OwnableByAllEntity$OwnerHurtTargetGoal':None,'util/SpatialUtil':['pushEntity'],'network/PlayerPushMessage':['handleData','registerMessage'],'network/PlayerPushMessage$ClientHandler':['handle'],'procedures/BossCancelDieProcedure':['execute'],'procedures/AbstractBossOnEntityTickUpdateProcedure':['onDying','onSpawn'],'procedures/BossCancelDie2Procedure':['onEntityAttacked','execute']}

def census():
    t=targets()[KEY];rows=[]
    needles=['.attackEntity(','.meleeAttack(','.simulatePlayerKill(','.onDying(','.onSpawn(','.shouldCancelDeath(','.cancelDeath(','.onDamageTaken(','.maybeCancelDeath(','.pushEntity(']
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(x for x in z.namelist() if x.endswith('.class')):
            raw=z.read(n);c=ClassFile(raw)
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if i['opcode'] in ['0xb6','0xb7','0xb8','0xb9'] and str(i.get('operand','')).startswith(PKG) and any(s in str(i.get('operand','')) for s in needles)]
                if hits:rows.append(dict(entry=n,entry_sha256=byte_hash(raw),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits,semantic_disposition='Shared helper reviewed here; concrete caller timing/geometry/payload pending its family unless already reviewed.'))
    return dict(jar_sha256=t['sha256'],scope='Actual shared attack/death/motion callback callers, not automatically complete boss deliveries.',rows=rows)

def save():
    t=targets()[KEY];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in CLASSES.items():
            n=PKG+short+'.class';c=ClassFile(z.read(n));names=wanted or sorted({m['name'] for m in c.methods});names=sorted(set(names)|{m['name'] for m in c.methods if any(m['name'].startswith('lambda$'+v+'$') for v in names)})
            rows.append(dict(id='br:shared:'+short,mod_key=KEY,entry=n,methods=names))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Shared attack/death/part/ownership/motion helpers. Concrete boss states and payload variants remain family work.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/bossesrise-shared.json',s);write_json(OUT/'native-evidence/bossesrise-shared.json',collect(s));write_json(OUT/'bossesrise-shared-census.json',census())
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None);a['classes']={'net/minecraft/world/entity/LivingEntity.class':['hurt','actuallyHurt'],'net/minecraft/world/entity/Entity.class':['push']}
    r=dict(id='bossesrise-shared-244',scope='Installed native death callback ordering and raw additive Entity.push (not LivingEntity.knockback).',archives=[a]);write_json(OUT/'reference-specifications/bossesrise-shared-244.json',r);write_json(OUT/'reference-evidence/bossesrise-shared-244.json',reference_collect(r,source_aids=True))
    print('Shared witnesses',len(rows),'caller methods',len(census()['rows']))

if __name__=='__main__':save()
