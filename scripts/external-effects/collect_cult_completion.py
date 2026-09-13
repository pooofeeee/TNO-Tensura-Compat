"""Pin the remaining reviewed Cult classes/resources and relevant conditional compat hooks."""
from catalog_common import *
from classfile import ClassFile
from native_evidence import collect

def build():
    inv=read_json(OUT/'jar-inventory.json');targets={t['key']:t for t in inv['targets']+inv['compat_candidates']}
    names=['NetherExp','NetherExp$ModEvents','effect/ManipulationEffect','effect/ZoneEffect','client/ClientEffectEvents','client/ClientZoneAmbientEvents','client/ClientFogHandler',
     'event/MansionCheckHandler','network/ModMessages','network/FogSyncS2CPacket','network/ClientPayloadHandler','event/AzazelAltarEvent','event/GildedGolemSpawnEvent',
     'item/CrimsonArrowItem','item/CrimsonHoneyBottleItem','item/ManipulatorStickItem','item/AzazelTrophyItem','item/crafting/CrimsonArrowRecipe',
     'entity/PiglinPrisonerEntity','entity/VillagerPrisonerEntity','entity/DoctorEntity','entity/BlacksmithEntity','entity/TraderEntity','entity/GhastlyEntity',
     'entity/GhastlyBuildNestGoal','entity/GhastlyPollinateGoal','entity/GhastlyEnterHiveGoal','entity/ManipulatorEntity','entity/BelieverEntity',
     'block/GrandDoorBlock','block/GrandDoorPartBlock','block/TraphiveBlock','block/EntranceBlock','block/CrimsonWebBlock','block/VoidNetherMidBlock','block/VoidNetherCornerBlock','block/VoidNetherMidCornerBlock',
     'block/entity/GrandDoorBlockEntity','block/entity/TraphiveBlockEntity','block/entity/GhastlyNestBlockEntity','block/GhastlyNestBlock','block/entity/NetherSpawnerBlockEntity',
     'block/StatueStandBlock','block/BlackstoneAxonBlock','block/BlackstonePlantBlock','block/entity/EyeBlockEntity','block/entity/PointedBlackstoneBlockEntity']
    specs=[]
    with zipfile.ZipFile(targets['cultofazazel']['path']) as jar:
        for name in names:
            entry='com/benji/netherman/'+name+'.class';c=ClassFile(jar.read(entry))
            specs.append(dict(id='coa3-'+name,mod_key='cultofazazel',entry=entry,methods=list(dict.fromkeys(m['name'] for m in c.methods))))
        for entry in jar.namelist():
            if entry.startswith('data/') and entry.endswith('.json'):
                specs.append(dict(id='coa3-resource-'+entry,mod_key='cultofazazel',entry=entry))
    key='rarcompat-1.21-0.9.7';prefix='it/hurts/octostudios/rarcompat/'
    chosen=['items/bracelet/WitheredBraceletItem','items/charm/AntidoteVesselItem','items/charm/ObsidianSkullItem',
     'items/feet/KittySlippersItem','items/necklace/CrossNecklaceItem','items/hands/PowerGloveItem','items/hands/VampiricGloveItem',
     'items/charm/ChorusTotemItem','items/UmbrellaItem','items/necklace/ThornPendantItem','items/necklace/ShockPendantItem',
     'mixin/LivingEntityMixin','mixin/MobMixin','items/hat/CowboyHatItem']
    with zipfile.ZipFile(targets[key]['path']) as jar:
        for entry in jar.namelist():
            if entry.endswith('.class') and any(entry==prefix+n+'.class' or entry.startswith(prefix+n+'$') for n in chosen):
                c=ClassFile(jar.read(entry));specs.append(dict(id='coa3-compat-'+entry,mod_key=key,entry=entry,methods=list(dict.fromkeys(m['name'] for m in c.methods))))
    spec=dict(schema='tno.external_effects.native_spec.v1',baseline=BASELINE,mod_key='cultofazazel',evidence_specifications=specs)
    write_json(OUT/'native-specifications/cult-completion.json',spec)
    result=collect(spec);write_json(OUT/'native-evidence/cult-completion.json',result)
    print(len(specs),'witnesses, of which',sum(x['entry'].endswith('.class') for x in specs),'classes')

if __name__=='__main__': build()
