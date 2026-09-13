"""Pin only the final focused comparison gaps; never rerun broad discovery."""
from catalog_common import *
from vanilla_reference import prepare
from selected_reference import collect
from classfile import ClassFile
from native_evidence import collect as collect_native

if __name__=='__main__':
    raw=dict(classes={
        'net/minecraft/world/level/block/state/BlockBehaviour$Properties':['<init>','noOcclusion','noCollission'],
        'net/minecraft/world/level/block/WebBlock':['entityInside'],
        'net/minecraft/world/entity/LivingEntity':['getArmorCoverPercentage'],
    },resources=[])
    write_json(OUT/'vanilla-specifications/cult-final.json',raw)
    write_json(OUT/'vanilla-evidence/cult-final.json',prepare(raw))
    loader=read_json(OUT/'reference-specifications/vv-loader-244.json')
    requests={
        'client':{'net/minecraft/world/entity/LivingEntity.class':['removeEffectsCuredBy','getArmorCoverPercentage']},
        'universal':{
            'net/neoforged/neoforge/common/extensions/IMobEffectExtension.class':['fillEffectCures'],
            'net/neoforged/neoforge/common/EffectCures.class':['<clinit>'],
            'net/neoforged/neoforge/common/CommonHooks.class':['onLivingDeath','getEntityVisibilityMultiplier'],
            'net/neoforged/neoforge/event/EventHooks.class':['onEffectRemoved'],
        }}
    archives=[]
    for a in loader['archives']:
        kind='client' if a['path'].endswith('-client.jar') else 'universal'
        archives.append(dict(path=a['path'],sha256=a['sha256'],classes=requests[kind]))
    spec=dict(id='cult-final-244',scope='Focused remaining Cult comparisons; installed NeoForge21.1.244 only.',archives=archives)
    write_json(OUT/'reference-specifications/cult-final-244.json',spec)
    write_json(OUT/'reference-evidence/cult-final-244.json',collect(spec,source_aids=True))
    inv=read_json(OUT/'jar-inventory.json')
    cult=next(t for t in inv['targets'] if t['key']=='cultofazazel')
    entries=['entity/GuardianEntity','entity/StatueEntity','block/entity/StatueStandBlockEntity',
        'block/entity/VoidNetherCornerBlockEntity','block/entity/VoidNetherMidBlockEntity','block/entity/VoidNetherMidCornerBlockEntity',
        'client/ClientActionDelegate','item/CrimsonHoneyBottleItem']
    specs=[]
    with zipfile.ZipFile(cult['path']) as jar:
        for name in entries:
            entry='com/benji/netherman/'+name+'.class'; cls=ClassFile(jar.read(entry))
            specs.append(dict(id='coa4-'+name,mod_key='cultofazazel',entry=entry,methods=list(dict.fromkeys(m['name'] for m in cls.methods))))
    ns=dict(schema='tno.external_effects.native_spec.v1',baseline=BASELINE,mod_key='cultofazazel',evidence_specifications=specs)
    write_json(OUT/'native-specifications/cult-final.json',ns)
    write_json(OUT/'native-evidence/cult-final.json',collect_native(ns))
    print('Final Cult comparison gaps pinned')
