"""Finish the saved multiplayer evidence; reuse protected raw/loader witnesses."""
from twilight_evidence import *
from vanilla_reference import MojangNames,CLIENT
from validate_twilight_multiplayer_read_ahead import census,FOLDER

BATCH='twilight-multiplayer'
FULL=['components/entity/MultiplayerInclusivityAttachment','config/TFConfig$MultiplayerFightAdjuster','loot/MultiplayerBasedNumberProvider','loot/MultiplayerBasedAdditionLootFunction','loot/MultiplayerBasedAdditionLootFunction$Builder','loot/LootingEnchantNumberProvider','advancements/HurtBossTrigger','advancements/HurtBossTrigger$TriggerInstance']


def collect():
    saved=read_json(FOLDER/'manifest.json')
    for row in saved['files']:assert sha256(FOLDER/row['file'])==row['sha256']
    scan=census();assert scan==read_json(FOLDER/'multiplayer-census-preview.json')
    classes={c:['*'] for c in FULL}
    classes.update({'events/EntityEvents':['setup','adjustEntityHealthInMultiplayerFights','getHealthBasedOnDifficulty','addQualifiedGroupPlayerIfNeeded','grantGroupAdvancementIfNeeded'],
      'events/EntityEvents$1':['*'],'config/TFConfig':['<clinit>','rebakeCommonOptions'],'config/TFCommonConfig':['<init>'],
      'init/TFDataAttachments':['<clinit>'],'init/TFLoot':['<clinit>'],'init/TFAdvancements':['<clinit>'],
      'block/entity/spawner/BossSpawnerBlockEntity':['tick','spawnMyBoss','initializeCreature','makeMyCreature'],
      'block/entity/spawner/LichSpawnerBlockEntity':['spawnMyBoss'],'block/entity/spawner/KnightPhantomSpawnerBlockEntity':['spawnMyBoss'],
      'entity/boss/Naga':['finalizeSpawn'],'entity/boss/Lich':['finalizeSpawn'],'entity/boss/Minoshroom':['finalizeSpawn'],'entity/monster/Minotaur':['finalizeSpawn']})
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest')
    with zipfile.ZipFile(target['path']) as jar:
        for c,ms in list(classes.items()):
            if ms==['*']:continue
            available={m['name'] for m in ClassFile(jar.read('twilightforest/'+c+'.class')).methods}
            assert set(ms)<=available,(c,set(ms)-available)
            # Static registration lambda names are lambda$static, not lambda$<clinit>.
            classes[c]=sorted(set(ms)|{m for m in available if any(m.startswith('lambda$'+('static' if n=='<clinit>' else n)+'$') for n in ms)})
    print('native',native(BATCH,classes,[r['entry'] for r in scan['resources']]),flush=True)
    raw=read_json(FOLDER/'multiplayer-native-preview-spec.json')['classes']
    raw['net/minecraft/util/Mth']=['nextInt','nextFloat','clamp','floor']
    raw['net/minecraft/world/entity/ai/attributes/AttributeMap']=['save','load']
    raw['net/minecraft/world/entity/EntityType']=['create','spawn']
    names=MojangNames()
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c,ms in list(raw.items()):
            cl=ClassFile(jar.read(names.named[c]+'.class'));av={names.member(cl.name,m['name'],m['descriptor']) for m in cl.methods}
            raw[c]=sorted(m for m in av if m in ms or any(m.startswith('lambda$'+n+'$') for n in ms));assert raw[c],c
    loader={c+'.class':ms for c,ms in raw.items()}
    template=read_json(OUT/'reference-specifications/vv-loader-244.json');a=next(a for a in template['archives'] if a['path'].endswith('client.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c in loader:
            if c not in jar.namelist():continue
            av={m['name'] for m in ClassFile(jar.read(c)).methods};loader[c]=sorted(m for m in av if m in raw[c[:-6]] or any(m.startswith('lambda$'+n+'$') for n in raw[c[:-6]]))
    hooks={'net/neoforged/neoforge/event/EventHooks.class':['finalizeMobSpawn','finalizeMobSpawnSpawner'],
      'net/neoforged/neoforge/common/CommonHooks.class':['onLivingDamagePost','onLivingDeath'],
      'net/neoforged/neoforge/event/entity/living/FinalizeSpawnEvent.class':['<init>','setSpawnCancelled','isSpawnCancelled'],
      'net/neoforged/neoforge/event/entity/living/LivingDamageEvent$Post.class':['<init>','getSource','getNewDamage','getOriginalDamage']}
    print('references',references(BATCH,raw,loader,hooks),flush=True)
    write_json(OUT/'twilightforest-multiplayer-caller-scan.json',scan)
    routing=[]
    def walk(value,path):
        if isinstance(value,dict):
            if value.get('type','').startswith('twilightforest:multiplayer') or value.get('function','').startswith('twilightforest:multiplayer') or value.get('trigger')=='twilightforest:hurt_boss':routing.append(dict(json_pointer=path,consumer=value))
            for k,v in value.items():walk(v,path+'/'+str(k))
        elif isinstance(value,list):
            for i,v in enumerate(value):walk(v,path+'/'+str(i))
    for r in scan['resources']:walk(r.get('data'),r['entry'])
    write_json(OUT/'twilightforest-multiplayer-resource-routing.json',dict(scope='Exact installed consumer JSON subtrees; acquisition/progression disposition, not independent combat packages.',routes=routing))


if __name__=='__main__':collect()
