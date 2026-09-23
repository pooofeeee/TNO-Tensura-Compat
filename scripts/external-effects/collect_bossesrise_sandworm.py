from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_bossesrise_foundation import targets,KEY,PKG

SW='entity/boss/sandworm/SandwormEntity'
CLASSES={s:None for s in [SW,SW+'Part','entity/projectile/PoisonSpitPrEntity','entity/PoisonAreaEntity','entity/SandColumnEntity','entity/boss/part/AbstractEntityPart','entity/boss/part/AbstractGeoEntityPart','state/StateController','state/StateSequence','state/ActiveState','state/LambdaState','state/LambdaState$LambdaStateBuilder','state/StateGoal']}
CLASSES.update({'init/BossesRiseEntities':['<clinit>'],'configuration/ServerConfiguration':['<clinit>']})

def census():
    t=targets()[KEY];rows=[]
    needles=['PoisonSpitPrEntity.shoot(', 'SandColumnEntity.spawnSandColumn(', 'SandwormEntity.shootPoisonSpit(']
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(x for x in z.namelist() if x.endswith('.class')):
            raw=z.read(n);c=ClassFile(raw)
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if (i['opcode']=='0xbb' and str(i.get('operand','')) in [PKG+'entity/projectile/PoisonSpitPrEntity',PKG+'entity/PoisonAreaEntity',PKG+'entity/SandColumnEntity']) or (i['opcode'] in ['0xb6','0xb7','0xb8','0xb9'] and any(s in str(i.get('operand','')) for s in needles))]
                if hits:rows.append(dict(entry=n,entry_sha256=byte_hash(raw),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits))
    return dict(jar_sha256=t['sha256'],scope='Whole installed mod producer census for Sandworm spit and column families; unused convenience methods are not inferred as delivered paths.',rows=rows)

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
    return dict(scope=source['scope'],reference_file='bossesrise-damage-tags.json',reference_sha256=sha256(OUT/'bossesrise-damage-tags.json'),profiles=[dict(id=s,tags=sorted(t for t in table if s in members(t))) for s in ['minecraft:mob_attack','minecraft:arrow','minecraft:magic','minecraft:indirect_magic','neoforge:poison']])

def save():
    t=targets()[KEY];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in CLASSES.items():
            n=PKG+short+'.class';c=ClassFile(z.read(n));names=wanted or sorted({m['name'] for m in c.methods});names=sorted(set(names)|{m['name'] for m in c.methods if any(m['name'].startswith('lambda$'+v+'$') for v in names)})
            rows.append(dict(id='br:sandworm:'+short,mod_key=KEY,entry=n,methods=names))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Sandworm multipart admission, native state attacks, spit, poison area and sand column. Cosmetic code carries no promoted mechanics.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/bossesrise-sandworm.json',s);write_json(OUT/'native-evidence/bossesrise-sandworm.json',collect(s));write_json(OUT/'bossesrise-sandworm-census.json',census());write_json(OUT/'bossesrise-sandworm-source-profiles.json',profiles())
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None);a['classes']={};raw={}
    wanted={'net/minecraft/world/entity/Entity':['isInvulnerableTo'],'net/minecraft/world/entity/LivingEntity':['canBeAffected','isAffectedByPotions','removeFrost'],'net/minecraft/world/effect/PoisonMobEffect':['applyEffectTick','shouldApplyEffectTickThisTick'],'net/minecraft/world/damagesource/DamageSource':['isDirect'],'net/minecraft/world/damagesource/DamageSources':['arrow','magic','indirectMagic']}
    with zipfile.ZipFile(a['path']) as z:
        for k,v in wanted.items():
            if k+'.class' in z.namelist():a['classes'][k+'.class']=v
            else:raw[k]=v
    r=dict(id='bossesrise-sandworm-244',scope='Exact native Poison, admission, frost modifier and source identity dependencies; arrow damage pipeline reuses protected Knight reference.',archives=[a]);write_json(OUT/'reference-specifications/bossesrise-sandworm-244.json',r);write_json(OUT/'reference-evidence/bossesrise-sandworm-244.json',reference_collect(r,source_aids=True))
    s=dict(classes=raw,resources=[]);write_json(OUT/'vanilla-specifications/bossesrise-sandworm.json',s);write_json(OUT/'vanilla-evidence/bossesrise-sandworm.json',prepare(s));write_json(OUT/'reference-routing/bossesrise-sandworm.json',dict(archive=a['path'],sha256=a['sha256'],absent_entries=[k+'.class' for k in raw]))
    print('Sandworm native evidence pinned')
if __name__=='__main__':save()
