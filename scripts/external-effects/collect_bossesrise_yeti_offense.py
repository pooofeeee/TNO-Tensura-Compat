from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_bossesrise_foundation import targets,KEY,PKG
from collect_bossesrise_yeti_defense import YETI

ENTITIES=['IceSpikeEntity','IceSpikeClusterEntity','IceSpikeProjectileEntity','GlacialShoveEntity','FrozenSkeletonEntity']
CLASSES={**{'entity/boss/yeti/'+s:None for s in ENTITIES},YETI:['chooseAttack','doAttack','<clinit>'],'attachment/entity/GauntletAttachment':['iceBurst','delayedBurst','iceWave','getNewShardIndex'],'item/IceGauntletItem':['placeProper'],'entity/boss/yeti/goals/YetiChaseGoal':['tick','canUse','canContinueToUse']}

def census():
    t=targets()[KEY];rows=[]
    needles=['GauntletAttachment.iceBurst(', 'GauntletAttachment.delayedBurst(', 'GauntletAttachment.iceWave(', 'IceSpikeProjectileEntity.shoot(','.getEvil(']
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(x for x in z.namelist() if x.endswith('.class')):
            raw=z.read(n);c=ClassFile(raw)
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if (i['opcode']=='0xbb' and str(i.get('operand','')).startswith(PKG) and any(str(i.get('operand','')).endswith('/'+s) for s in ENTITIES)) or (i['opcode'] in ['0xb6','0xb7','0xb8','0xb9'] and str(i.get('operand','')).startswith(PKG) and any(s in str(i.get('operand','')) for s in needles))]
                if hits:rows.append(dict(entry=n,entry_sha256=byte_hash(raw),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits))
    return dict(jar_sha256=t['sha256'],scope='Actual Yeti ice/shove/helper producers; player gauntlet paths explicitly reserved for equipment section, no unused helper delivery inferred.',rows=rows)

def profiles():
    source=read_json(OUT/'bossesrise-damage-tags.json');table={}
    for r in source['resources']:
        n=r['entry'];tag=n.split('/')[1]+':'+n.split('/tags/damage_type/')[1][:-5];d=r['data']
        if d.get('replace'):table[tag]=[]
        table.setdefault(tag,[]).extend(d.get('values',[]))
    def members(tag,seen=()):
        if tag in seen:return set()
        out=set()
        for v in table.get(tag,[]):
            v=v['id'] if isinstance(v,dict) else v
            out|=members(v[1:],seen+(tag,)) if v.startswith('#') else {v}
        return out
    return dict(scope=source['scope'],reference_file='bossesrise-damage-tags.json',reference_sha256=sha256(OUT/'bossesrise-damage-tags.json'),profiles=[dict(id='minecraft:'+s,tags=sorted(t for t in table if 'minecraft:'+s in members(t))) for s in ['mob_attack','indirect_magic','freeze']])

def save():
    t=targets()[KEY];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in CLASSES.items():
            n=PKG+short+'.class';c=ClassFile(z.read(n));names=wanted or sorted({m['name'] for m in c.methods});names=sorted(set(names)|{m['name'] for m in c.methods if any(m['name'].startswith('lambda$'+v+'$') for v in names)})
            rows.append(dict(id='br:yeti_offense:'+short,mod_key=KEY,entry=n,methods=names))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Yeti ice/outgoing helper semantics; use protected R2i5a tick dispatch witness. Frozen Skeleton inspected for short noncombat disposition.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/bossesrise-yeti-offense.json',s);write_json(OUT/'native-evidence/bossesrise-yeti-offense.json',collect(s));write_json(OUT/'bossesrise-yeti-offense-census.json',census());write_json(OUT/'bossesrise-yeti-source-profiles.json',profiles())
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None);a['classes']={}
    wanted={'net/minecraft/world/entity/player/Player':['aiStep','touch'],'net/minecraft/world/entity/LivingEntity':['aiStep','canFreeze','tryAddFrost','removeFrost','hurt'],'net/minecraft/world/entity/Entity':['canFreeze','setTicksFrozen','getTicksRequiredToFreeze','getPercentFrozen','isFullyFrozen'],'net/minecraft/world/damagesource/DamageSources':['freeze','indirectMagic']};raw={}
    with zipfile.ZipFile(a['path']) as z:
        for k,v in wanted.items():
            if k+'.class' in z.namelist():a['classes'][k+'.class']=v
            else:raw[k]=v
    r=dict(id='bossesrise-yeti-offense-244',scope='Exact playerTouch dispatcher, frost counter/speed/tick and direct freezing damage admission. Projectile collision reused from Knight native-reference checkpoint.',archives=[a]);write_json(OUT/'reference-specifications/bossesrise-yeti-offense-244.json',r);write_json(OUT/'reference-evidence/bossesrise-yeti-offense-244.json',reference_collect(r,source_aids=True))
    s=dict(classes=raw,resources=['data/minecraft/damage_type/freeze.json']);write_json(OUT/'vanilla-specifications/bossesrise-yeti-offense.json',s);write_json(OUT/'vanilla-evidence/bossesrise-yeti-offense.json',prepare(s));write_json(OUT/'reference-routing/bossesrise-yeti-offense.json',dict(archive=a['path'],sha256=a['sha256'],absent_entries=[k+'.class' for k in raw]))
    print('Yeti offense pinned')
if __name__=='__main__':save()
