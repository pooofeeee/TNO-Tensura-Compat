"""R2f8c complete native SPIKED paths, chain control and Destruction payload."""
from twilight_evidence import *
from vanilla_reference import MojangNames,CLIENT
BATCH='twilight-chain'
FULL=['entity/monster/BlockChainGoblin','entity/monster/BlockChainGoblin$MultipartGenericsAreDumb','entity/SpikeBlock','entity/ai/goal/ThrowSpikeBlockGoal','entity/ai/goal/AvoidAnyEntityGoal','entity/ai/goal/AvoidAnyEntityGoal$1','entity/projectile/ChainBlock','entity/projectile/ChainBlock$1','item/ChainBlockItem','enchantment/SmashBlocksEffect','components/entity/SmashBlocksEnchantmentAttachment']

def scan_callers(target):
    needles=['TFDamageTypes.SPIKEDLnet/minecraft/resources/ResourceKey;','TFDataAttachments.SMASH_BLOCKS','SmashBlocksEnchantmentAttachment.setBlocksSmashed','entity/projectile/ChainBlock.<init>']
    hits=[]
    with zipfile.ZipFile(target['path']) as jar:
        for entry in jar.namelist():
            if not entry.startswith('twilightforest/') or not entry.endswith('.class'):continue
            b=jar.read(entry)
            if not any(x.encode() in b for x in ['SPIKED','SMASH_BLOCKS','setBlocksSmashed','entity/projectile/ChainBlock']):continue
            c=ClassFile(b)
            for m in c.methods:
                for i in c.instructions(m.get('code',b'')):
                    if any(n in str(i['operand']) for n in needles):hits.append(dict(entry=entry,class_sha256=byte_hash(b),method=m['name'],descriptor=m['descriptor'],instruction=i))
    return dict(jar_sha256=target['sha256'],scope='All installed TF classes; SPIKED, smash attachment accesses/setters and ChainBlock constructors only.',needles=needles,hits=hits)

def scan_vanilla_callers():
    names=MojangNames();hits=[]
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar;owner=names.named['net/minecraft/world/item/enchantment/EnchantmentHelper'];c=ClassFile(jar.read(owner+'.class'))
        targets=[owner+'.'+m['name']+m['descriptor'] for m in c.methods if names.member(c.name,m['name'],m['descriptor'])=='onHitBlock']
        for entry in jar.namelist():
            if not entry.endswith('.class'):continue
            b=jar.read(entry)
            if owner.encode() not in b:continue
            c=ClassFile(b)
            for m in c.methods:
                for i in c.instructions(m.get('code',b'')):
                    if i['operand'] in targets:hits.append(dict(entry=entry,class_name=names.obfuscated.get(c.name,c.name),class_sha256=byte_hash(b),method=names.member(c.name,m['name'],m['descriptor']),descriptor=m['descriptor'],offset=i['offset']))
    return dict(client_sha256=sha256(CLIENT),scope='All raw Minecraft1.21.1 class instructions; exact EnchantmentHelper.onHitBlock callers. Exact loader comparison of legitimate mining and projectile paths separately pinned.',hits=hits)

def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest')
    resources=read_json(WORK/'twilightforest/resources.json')
    selected=[p for p,v in resources.items() if (p.endswith('/destruction.json') and '/enchantment/' in p) or ('/tags/' in p and (any(x in str(v) for x in ['chain_block','block_and_chain','blockchain_goblin']) or any(x in p for x in ['block_and_chain','incorrect_for_wooden_tool','incorrect_for_stone_tool','incorrect_for_iron_tool'])))]
    todo=['twilightforest:mineable_with_block_and_chain','twilightforest:block_and_chain_never_breaks']+['minecraft:incorrect_for_'+x+'_tool' for x in ['wooden','stone','iron']]
    seen=set();raw_resources=[]
    with zipfile.ZipFile(CLIENT) as jar:
        while todo:
            tag=todo.pop()
            if tag in seen:continue
            seen.add(tag);ns,name=tag.split(':',1);p='data/'+ns+'/tags/block/'+name+'.json'
            contributions=[]
            if p in jar.namelist():raw_resources.append(p);contributions.append(json.loads(jar.read(p)))
            if p in resources:selected.append(p);contributions.append(resources[p]['data'])
            assert contributions,p
            for contribution in contributions:
                for value in contribution['values']:
                    value=value['id'] if isinstance(value,dict) else value
                    if value.startswith('#'):todo.append(value[1:])
    resource_spec=dict(classes={},resources=sorted(set(raw_resources)))
    write_json(OUT/'vanilla-specifications/twilight-chain-tools.json',resource_spec)
    write_json(OUT/'vanilla-evidence/twilight-chain-tools.json',prepare(resource_spec))
    selected=sorted(set(selected))
    classes={c:['*'] for c in FULL}
    with zipfile.ZipFile(target['path']) as jar:
        for short,needle in [('init/TFItems','ChainBlockItem'),('init/TFDataComponents','UUIDUtil'),('init/TFDataAttachments','SmashBlocksEnchantmentAttachment'),('init/TFEnchantmentEffects','SmashBlocksEffect')]:
            c=ClassFile(jar.read('twilightforest/'+short+'.class'))
            classes[short]=['<clinit>']+[m['name'] for m in c.methods if any(needle in str(i['operand']) for i in c.instructions(m.get('code',b'')))]
    print('native',native(BATCH,classes,selected))
    raw={'net/minecraft/world/entity/player/Player':['disableShield'],
         'net/minecraft/server/level/ServerPlayerGameMode':['handleBlockBreakAction'],
         'net/minecraft/world/entity/LivingEntity':['isBlocking','onEquippedItemBroken','broadcastBreakEvent','stopUsingItem'],
         'net/minecraft/world/item/ItemStack':['hurtAndBreak','isCorrectToolForDrops','mineBlock'],
         'net/minecraft/world/item/Item':['getDefaultAttributeModifiers','hurtEnemy','postHurtEnemy','mineBlock'],
         'net/minecraft/world/item/enchantment/EnchantmentHelper':['onHitBlock','modifyDamage'],
         'net/minecraft/world/item/enchantment/Enchantment':['onHitBlock','blockHitContext'],
         'net/minecraft/world/item/Tier':['createToolProperties'],
         'net/minecraft/world/item/Tiers':['<clinit>','getIncorrectBlocksForDrops','createToolProperties'],
         'net/minecraft/world/level/Level':['destroyBlock'],
         'net/minecraft/world/entity/projectile/Projectile':['shoot','shootFromRotation','canHitEntity','addAdditionalSaveData','readAdditionalSaveData'],
         'net/minecraft/world/entity/projectile/ThrowableProjectile':['tick','getDefaultGravity'],
         'net/minecraft/world/entity/Entity':['push','isPushable','canBeHitByProjectile']}
    names=MojangNames()
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c,ms in raw.items():
            cls=ClassFile(jar.read(names.named[c]+'.class'));available={names.member(cls.name,m['name'],m['descriptor']) for m in cls.methods}
            raw[c]=[m for m in ms if m in available]
            if c.endswith('EnchantmentHelper') or c.endswith('/Enchantment'):
                raw[c]+=[names.member(cls.name,m['name'],m['descriptor']) for m in cls.methods if names.member(cls.name,m['name'],m['descriptor']).startswith('lambda$onHitBlock')]
    loader={c+'.class':list(ms) for c,ms in raw.items()}
    print('references',references(BATCH,raw,loader,{'net/neoforged/neoforge/common/extensions/IItemExtension.class':['canPerformAction'],'net/neoforged/neoforge/common/extensions/IItemStackExtension.class':['canPerformAction']}))
    write_json(OUT/'twilightforest-chain-caller-scan.json',scan_callers(target))
    write_json(OUT/'twilightforest-chain-vanilla-caller-scan.json',scan_vanilla_callers())

if __name__=='__main__':collect()
