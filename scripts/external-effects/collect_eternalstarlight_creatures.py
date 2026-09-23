from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_eternalstarlight_foundation import ES,targets

CLASSES=['common/entity/living/'+n for n in [
 'monster/Gleech','monster/Gleech$1','monster/Creteor','monster/TinyCreteor','AethersentGolem',
 'npc/boarwarf/golem/AstralGolem','npc/boarwarf/golem/AstralGolemMaterial','npc/boarwarf/Boarwarf',
 'animal/Luminofish','animal/Luminaris','animal/ShadowSnail','monster/Stranghoul','monster/Stranghoul$EatGoal',
 'monster/NightfallSpider','monster/ThirstWalker','monster/Seeker','goal/ChargeAttackGoal','animal/AuroraDeer',
 'phase/BehaviorPhase','phase/MeleeAttackPhase','monster/ZombifiedRatlin','animal/TwilightGaze','animal/AuroraDeer$1','animal/AuroraDeer$2',
 'animal/Ent','animal/Ratlin','animal/Rookfish','animal/ShimmerLacewing','animal/Yeti','animal/YetiAi','GrimstoneGolem']]
CLASSES+=['common/entity/projectile/GleechEgg','common/item/combat/GleechEggItem','common/registry/ESEntities']

def census():
    t=targets()['eternalstarlight'];rows=[]
    needles=['Gleech.attachTo(', 'Creteor.explode(', 'TinyCreteor.explode(', 'AethersentGolem', 'ASTRAL_GOLEM_MATERIAL']
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(x for x in z.namelist() if x.endswith('.class')):
            raw=z.read(n);c=ClassFile(raw)
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if any(s in str(i['operand']) for s in needles)]
                if hits:rows.append(dict(entry=n,sha256=byte_hash(raw),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits))
    return dict(jar_sha256=t['sha256'],scope='Exact attachment, Creteor detonation and Golem material references; data/render hits are not extra deliveries.',rows=rows)

def save():
    t=targets()['eternalstarlight'];rows=[]
    selected={n:None for n in CLASSES};selected.update({'neoforge/platform/ESNeoPlatform':['isShield'],'common/handler/ESCommonSetupHandler':['commonSetup']})
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in selected.items():
            n=ES+short+'.class';c=ClassFile(z.read(n));names=wanted or sorted({m['name'] for m in c.methods});names=sorted(set(names)|{m['name'] for m in c.methods if any(m['name'].startswith('lambda$'+v+'$') for v in names)})
            rows.append(dict(id='es:creature:'+short,mod_key='eternalstarlight',entry=n,methods=names))
        for n in sorted(x for x in z.namelist() if x.endswith('.json') and (('/tags/entity_type/' in x and x.startswith('data/')) or '/astral_golem_material/' in x or x=='data/eternal_starlight/tags/item/stranghoul_vulnerable_to.json')):
            rows.append(dict(id='es:creature:data:'+n,mod_key='eternalstarlight',entry=n))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Remaining creature combat/admission; full class witnesses do not promote utility/render branches.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/eternalstarlight-creatures.json',s);write_json(OUT/'native-evidence/eternalstarlight-creatures.json',collect(s));write_json(OUT/'eternalstarlight-creatures-census.json',census())
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None);a['classes']={}
    wanted={'net/minecraft/world/entity/Entity':['startRiding','stopRiding','removeVehicle'], 'net/minecraft/world/entity/Mob':['doHurtTarget'], 'net/minecraft/world/entity/monster/Spider':['canBeAffected'], 'net/minecraft/world/entity/ai/goal/MeleeAttackGoal':['checkAndPerformAttack','canPerformAttack'], 'net/minecraft/world/entity/AreaEffectCloud':['<init>','tick'], 'net/minecraft/world/damagesource/DamageSources':['explosion','magic','mobAttack','thrown']}
    raw={}
    with zipfile.ZipFile(a['path']) as z:
        for k,v in wanted.items():
            if k+'.class' in z.namelist():
                c=ClassFile(z.read(k+'.class'));a['classes'][k+'.class']=v+[m['name'] for m in c.methods if any(m['name'].startswith('lambda$'+n+'$') for n in v)]
            else:raw[k]=v
    r=dict(id='eternalstarlight-creatures-244',scope='Native riding admission, ordinary Mob melee, Spider immunity and source attribution; raw fallback only where patched archive lacks class.',archives=[a])
    write_json(OUT/'reference-specifications/eternalstarlight-creatures-244.json',r);write_json(OUT/'reference-evidence/eternalstarlight-creatures-244.json',reference_collect(r,source_aids=True))
    s=dict(classes=raw,resources=[]);write_json(OUT/'vanilla-specifications/eternalstarlight-creatures.json',s);write_json(OUT/'vanilla-evidence/eternalstarlight-creatures.json',prepare(s));write_json(OUT/'reference-routing/eternalstarlight-creatures.json',dict(archive=a['path'],sha256=a['sha256'],absent_entries=[k+'.class' for k in raw]))
    print('Creature witnesses saved')
if __name__=='__main__':save()
