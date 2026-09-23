from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_bossesrise_foundation import targets,KEY,PKG

PROJECTILES=['SwordWaveEntity','SoulShockwaveEntity','RiftProjectileEntity','BigRiftProjectileEntity']
CLASSES={**{'entity/projectile/'+s:None for s in PROJECTILES},'entity/RiftEntity':None,'entity/monster/SoulSkeletonEntity':None,'entity/monster/SoulSkeletonEntity$1':None,'entity/monster/SoulKnightWitherSkeletonEntity':None,'entity/monster/SoulKnightWitherSkeletonEntity$1':None,'procedures/SoulSkeletonOnEntityTickUpdateProcedure':None,'procedures/SoulKnightWitherSkeletonOnEntityTickUpdateProcedure':None,'procedures/SoulSkeletonsEntityDiesProcedure':None,'procedures/UnderworldKnightOnEntityTickUpdateProcedure':None,'entity/boss/knight/UnderworldKnightEntity':['jumpSlash','getOutOfMe','registerGoals','chooseAttack','getAttackPatternPool'],'entity/boss/knight/UnderworldKnightEntity$2':None,'init/BossesRiseItems':['<clinit>']}

def census():
    t=targets()[KEY];rows=[]
    needles=['SoulShockwaveEntity.shoot(','.attackJumpspin1(','.attackCombo1(','.jumpSlash(']
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(x for x in z.namelist() if x.endswith('.class')):
            raw=z.read(n);c=ClassFile(raw)
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if (i['opcode']=='0xbb' and str(i.get('operand','')).startswith(PKG) and any(str(i.get('operand','')).endswith('/'+v) for v in PROJECTILES+['RiftEntity','SoulSkeletonEntity','SoulKnightWitherSkeletonEntity'])) or (i['opcode'] in ['0xb6','0xb7','0xb8','0xb9'] and any(s in str(i.get('operand','')) for s in needles))]
                if hits:rows.append(dict(entry=n,entry_sha256=byte_hash(raw),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits))
    return dict(jar_sha256=t['sha256'],scope='Whole-artifact concrete constructors and actual helper invocation census. Registry factories/method references are separately pinned; unused helper bodies are not delivered payloads.',rows=rows)

def source_tags():
    source=read_json(OUT/'bossesrise-damage-tags.json');table={}
    for r in source['resources']:
        n=r['entry'];tag=n.split('/')[1]+':'+n.split('/tags/damage_type/')[1][:-5];d=r['data']
        if d.get('replace'):table[tag]=[]
        table.setdefault(tag,[]).extend(d.get('values',[]))
    def members(tag,seen=()):
        if tag in seen:return set()
        result=set()
        for v in table.get(tag,[]):
            v=v['id'] if isinstance(v,dict) else v
            result|=members(v[1:],seen+(tag,)) if v.startswith('#') else {v}
        return result
    return dict(scope=source['scope'],reference_file='bossesrise-damage-tags.json',reference_sha256=sha256(OUT/'bossesrise-damage-tags.json'),profiles=[dict(id='minecraft:'+n,tags=sorted(tag for tag in table if 'minecraft:'+n in members(tag))) for n in ['arrow','indirect_magic','magic','mob_attack','in_wall','explosion','wither']])

def save():
    t=targets()[KEY];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in CLASSES.items():
            n=PKG+short+'.class';c=ClassFile(z.read(n));names=wanted or sorted({m['name'] for m in c.methods});names=sorted(set(names)|{m['name'] for m in c.methods if any(m['name'].startswith('lambda$'+v+'$') for v in names)})
            rows.append(dict(id='br:knight_offense:'+short,mod_key=KEY,entry=n,methods=names))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Knight native offensive payloads and independent arena mobs; reuse protected tick/phase/mark witnesses. Equipment SwordWave producer is pending equipment review.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/bossesrise-knight-offense.json',s);write_json(OUT/'native-evidence/bossesrise-knight-offense.json',collect(s));write_json(OUT/'bossesrise-knight-offense-census.json',census())
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None);a['classes']={}
    wanted={'net/minecraft/world/entity/projectile/Projectile':['tick','canHitEntity','hitTargetOrDeflectSelf','deflect','getOwner','addAdditionalSaveData','readAdditionalSaveData'],'net/minecraft/world/entity/projectile/AbstractArrow':['tick','onHitEntity','onHitBlock'],'net/minecraft/world/entity/Mob':['doHurtTarget'],'net/minecraft/world/entity/ai/goal/MeleeAttackGoal':['checkAndPerformAttack'],'net/minecraft/world/effect/WitherMobEffect':['applyEffectTick','shouldApplyEffectTickThisTick'],'net/minecraft/world/damagesource/DamageSources':['arrow','indirectMagic','magic','mobAttack','wither']}
    raw={}
    with zipfile.ZipFile(a['path']) as z:
        for k,v in wanted.items():
            if k+'.class' in z.namelist():
                c=ClassFile(z.read(k+'.class'));a['classes'][k+'.class']=v+[m['name'] for m in c.methods if any(m['name'].startswith('lambda$'+n+'$') for n in v)]
            else:raw[k]=v
    r=dict(id='bossesrise-knight-offense-244',scope='Actual installed projectile/arrow admission, native hit result and ordinary Mob melee; raw fallback only for absent classes.',archives=[a]);write_json(OUT/'reference-specifications/bossesrise-knight-offense-244.json',r);write_json(OUT/'reference-evidence/bossesrise-knight-offense-244.json',reference_collect(r,source_aids=True))
    s=dict(classes=raw,resources=['data/minecraft/damage_type/'+n+'.json' for n in ['arrow','indirect_magic','magic','mob_attack','in_wall','explosion','wither']]);write_json(OUT/'vanilla-specifications/bossesrise-knight-offense.json',s);write_json(OUT/'vanilla-evidence/bossesrise-knight-offense.json',prepare(s));write_json(OUT/'reference-routing/bossesrise-knight-offense.json',dict(archive=a['path'],sha256=a['sha256'],absent_entries=[k+'.class' for k in raw]))
    write_json(OUT/'bossesrise-knight-source-profiles.json',source_tags())
    print('Knight offense evidence saved')

if __name__=='__main__':save()
