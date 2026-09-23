from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_eternalstarlight_foundation import ES,targets

CLASSES={
 'common/entity/living/boss/gatekeeper/TheGatekeeper':None,
 'common/entity/living/goal/GatekeeperTargetGoal':None,
 'common/entity/living/goal/MoveToTargetGoal':None,
 'common/entity/living/boss/creeper/SolarCreeper':None,
 'common/entity/living/boss/creeper/SolarCreeperIntroPhase':None,
 'common/entity/projectile/GatekeeperFireball':None,
 'common/entity/living/phase/BehaviorPhase':None,
 'common/handler/ESCommonHandler':['onModifyLivingHurtDamage','onAllowLivingDeath'],
 'common/config/ESConfig$MobsConfig':['<init>'],
 'common/item/combat/GreatswordItem':None,
 'common/item/combat/HammerItem':None,
 'common/item/combat/GlisteringBowItem':None,
}

def census():
    t=targets()['eternalstarlight'];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(x for x in z.namelist() if x.endswith('.class')):
            raw=z.read(n);c=ClassFile(raw)
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if (i['opcode']=='0xbb' and str(i['operand']).endswith('/GatekeeperFireball')) or ('SolarCreeper' in str(i['operand']) or 'ESEntities.SOLAR_CREEPER' in str(i['operand']))]
                if hits:rows.append(dict(entry=n,sha256=byte_hash(raw),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits))
    return dict(jar_sha256=t['sha256'],scope='Whole JAR GatekeeperFireball producers and Solar Creeper references; registry/render/data rows are exclusions, not assumed attacks.',rows=rows)

def save():
    t=targets()['eternalstarlight'];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for n in z.namelist():
            if n.startswith(ES+'common/entity/living/boss/gatekeeper/') and n.endswith('.class'):CLASSES[n[len(ES):-6]]=None
        for short,wanted in CLASSES.items():
            n=ES+short+'.class';c=ClassFile(z.read(n));names=wanted if wanted is not None else sorted({m['name'] for m in c.methods});names=sorted(set(names)|{m['name'] for m in c.methods if any(m['name'].startswith('lambda$'+v+'$') for v in names)})
            rows.append(dict(id='es:gatekeeper:'+short,mod_key='eternalstarlight',entry=n,methods=names))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Gatekeeper native damage admission, attacks, heal/reset/teleport and Solar Creeper actual goals; static only.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/eternalstarlight-gatekeeper.json',s);write_json(OUT/'native-evidence/eternalstarlight-gatekeeper.json',collect(s));write_json(OUT/'eternalstarlight-gatekeeper-census.json',census())
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None);a['classes']={}
    wanted={'net/minecraft/world/entity/Mob':['doHurtTarget'],'net/minecraft/world/entity/monster/Monster':['getProjectile'],'net/minecraft/world/entity/projectile/ProjectileUtil':['getMobArrow'],'net/minecraft/world/entity/projectile/AbstractArrow':['setBaseDamageFromMob'],'net/minecraft/world/entity/projectile/AbstractHurtingProjectile':['tick'],'net/minecraft/world/entity/projectile/Fireball':['<init>'],'net/minecraft/world/damagesource/DamageSource':['isDirect'],'net/minecraft/world/damagesource/DamageSources':['fireball','explosion']}
    raw={}
    with zipfile.ZipFile(a['path']) as z:
        for k,v in wanted.items():
            if k+'.class' in z.namelist():a['classes'][k+'.class']=v
            else:raw[k]=v
    r=dict(id='eternalstarlight-gatekeeper-244',scope='Actual Mob melee and arrow setup, native fireball collision/source and direct predicate; no inferred Mace Player callback.',archives=[a])
    write_json(OUT/'reference-specifications/eternalstarlight-gatekeeper-244.json',r);write_json(OUT/'reference-evidence/eternalstarlight-gatekeeper-244.json',reference_collect(r,source_aids=True))
    s=dict(classes=raw,resources=[]);write_json(OUT/'vanilla-specifications/eternalstarlight-gatekeeper.json',s);write_json(OUT/'vanilla-evidence/eternalstarlight-gatekeeper.json',prepare(s))
    write_json(OUT/'reference-routing/eternalstarlight-gatekeeper.json',dict(archive=a['path'],sha256=a['sha256'],absent_entries=[k+'.class' for k in raw]))
    config=MODS.parent/'config/eternal_starlight.json';v=read_json(config).get('mobsConfig',{});write_json(OUT/'eternalstarlight-gatekeeper-config-snapshot.json',dict(path=str(config),sha256=sha256(config),values={k:v.get(k) for k in ['theGatekeeper','solarCreeper']},scope='File snapshot, not runtime loaded-value claim.'))
    print('Gatekeeper/Solar witnesses saved')
if __name__=='__main__':save()
