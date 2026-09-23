from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_eternalstarlight_foundation import ES,targets
CLASSES={
 'common/block/AbyssalFireBlock':['entityInside'],
 'common/block/AmaramberFireBlock':['entityInside'],
 'common/block/LunarisCactusBlock':['entityInside'],
 'common/block/CrinoaBaleBlock':['fallOn'],
 'common/block/YetiFurBlock':['fallOn','updateEntityAfterFallOn','bounceUp'],
 'common/block/IcicleBlock':['fallOn','tick','spawnFallingStalactite','onProjectileHit','getSuitableState','canSurvive'],
 'common/block/Stellagmite':['step','<clinit>'],
 'common/block/entity/GolemSteelJetBlockEntity':['tick'],
 'common/block/WeatheringGolemSteelJetBlock':['getTicker'],
 'common/handler/ESCommonHandler':['onEntityTick','onPostLivingHurt'],
 'common/handler/ESCommonSetupHandler':['commonSetup'],
 'common/mixin/EntityFlagsPredicateMixin':['isOnFire'],
 'common/entity/projectile/AetherstrikeRocketEntity':None,
 'common/item/misc/AetherstrikeRocketItem':None,
}
for n in ['StellagmiteBlock','StellagmiteSlabBlock','StellagmiteStairBlock','StellagmiteWallBlock']:CLASSES['common/block/'+n]=['stepOn']
for n in ['Freeze','IgniteAbyssalFire','PushTowardsEntity']:CLASSES['common/enchantment/effect/'+n]=None

def census():
    t=targets()['eternalstarlight'];rows=[]
    needles=['ABYSSAL_FIRE_TICKS','/AetherstrikeRocketEntity','ESBiomes.THE_ABYSS','IGNITE_ABYSSAL_FIRE','PUSH_TOWARDS_ENTITY']
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(x for x in z.namelist() if x.endswith('.class')):
            raw=z.read(n);c=ClassFile(raw)
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if any(s in str(i['operand']) for s in needles)]
                if hits:rows.append(dict(entry=n,sha256=byte_hash(raw),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits))
    return dict(jar_sha256=t['sha256'],scope='Whole JAR Abyssal fire state, Rocket constructors and Abyss biome combat/resource references.',rows=rows)

def save():
    t=targets()['eternalstarlight'];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in CLASSES.items():
            n=ES+short+'.class';c=ClassFile(z.read(n));names=wanted if wanted is not None else sorted({m['name'] for m in c.methods});names=sorted(set(names)|{m['name'] for m in c.methods if any(m['name'].startswith('lambda$'+v+'$') for v in names)})
            rows.append(dict(id='es:hazard:'+short,mod_key='eternalstarlight',entry=n,methods=names))
        data=sorted(n for n in z.namelist() if n.endswith('.json') and (n.startswith('data/eternal_starlight/enchantment/') or '/tags/item/enchantable/' in n or n=='data/eternal_starlight/tags/entity_type/abyssal_fire_immune.json'))
        for n in data:rows.append(dict(id='es:hazard:data:'+n,mod_key='eternalstarlight',entry=n))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Native hazards, control enchantments and genuine Rocket weather path; no worldgen/utility archaeology.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/eternalstarlight-hazards.json',s);write_json(OUT/'native-evidence/eternalstarlight-hazards.json',collect(s));write_json(OUT/'eternalstarlight-hazards-census.json',census())
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None);a['classes']={}
    wanted={'net/minecraft/world/entity/item/FallingBlockEntity':['causeFallDamage','setHurtsEntities'],'net/minecraft/world/item/enchantment/EnchantmentHelper':['doPostAttackEffects','doPostAttackEffectsWithItemSource'],'net/minecraft/world/item/enchantment/Enchantment':['doPostAttack'],'net/minecraft/world/item/enchantment/Enchantment$1':['<clinit>'],'net/minecraft/world/item/enchantment/effects/ApplyMobEffect':['apply']}
    raw={}
    with zipfile.ZipFile(a['path']) as z:
        for k,v in wanted.items():
            if k+'.class' in z.namelist():
                c=ClassFile(z.read(k+'.class'));a['classes'][k+'.class']=v+[m['name'] for m in c.methods if any(m['name'].startswith('lambda$'+n+'$') for n in v)]
            else:raw[k]=v
    r=dict(id='eternalstarlight-hazards-244',scope='Installed falling block admission/source and native enchantment victim/attacker routing. Raw fallback only absent classes.',archives=[a])
    write_json(OUT/'reference-specifications/eternalstarlight-hazards-244.json',r);write_json(OUT/'reference-evidence/eternalstarlight-hazards-244.json',reference_collect(r,source_aids=True))
    s=dict(classes=raw,resources=[]);write_json(OUT/'vanilla-specifications/eternalstarlight-hazards.json',s);write_json(OUT/'vanilla-evidence/eternalstarlight-hazards.json',prepare(s));write_json(OUT/'reference-routing/eternalstarlight-hazards.json',dict(archive=a['path'],sha256=a['sha256'],absent_entries=[k+'.class' for k in raw]))
    print('Hazards witnesses saved')
if __name__=='__main__':save()
