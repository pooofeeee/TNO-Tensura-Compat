"""Travellers storage/view controls, Emperor cloth and exact native ASM routes."""
from twilight_evidence import *
from vanilla_reference import MojangNames,CLIENT
from selected_reference import collect as reference_collect
BATCH='twilight-travellers-utility'
T='item/travellers_gear/'
FULL=[T+c for c in ['TravellersArmorBeltItem','TravellersArmorBeltItem$Tooltip','TravellersGogglesItem','TravellersGogglesItem$Tooltip','modifiers/display/ItemDisplayType']]+['components/item/ItemDisplayContents'+s for s in ['','$Mutable','$DisplaySlot']]+['network/'+c for c in ['SwapHotbarPacket','CycleMapSlotPacket','GogglesZoomPacket']]+['init/custom/ItemDisplays','asmhooks/ArmorHooks','util/ArmorUtil','item/recipe/EmperorsClothRecipe','item/recipe/NoTemplateSmithingRecipe','item/recipe/NoTemplateSmithingRecipe$Serializer','client/event/TravellersClientEvents','events/TravellersGearEvents','client/overlay/ItemDisplayOverlay','client/overlay/ItemDisplayOverlay$DisplayHolder','client/renderer/block/RedThreadRenderer','block/RedThreadBlock','block/entity/RedThreadBlockEntity','item/MoonDialItem','command/TravellersGearCommand','command/TravellersGearCommand$Context','init/TFKeyBinds']+['client/overlay/display/'+c for c in ['ItemDisplay','ItemDisplay$Bounds','ItemDisplay$DisplayPosition','SimpleTextDisplay','MapDisplay','CompassDisplay','ClockDisplay','ClockDisplay$TimeFrame','MoonDialDisplay']]
TRANSFORMERS=['ArmorVisibilityRenderingTransformer','CancelArmorRenderingTransformer','FixCapeUnrenderingTransformer','UpdateMapsInGogglesTransformer']
TOKENS=['EMPERORS_CLOTH','SWAP_HOTBAR','ITEM_DISPLAY','RED_THREAD_VISION','IS_USING_GOGGLES_ZOOM','ZOOM_ABILITY','getShroudedArmorPercentage','updateMapsInGoggles']

def scan_callers(target):
    hits=[]
    with zipfile.ZipFile(target['path']) as jar:
        for entry in jar.namelist():
            if not entry.startswith('twilightforest/') or not entry.endswith('.class'):continue
            b=jar.read(entry)
            if not any(s.encode() in b for s in TOKENS):continue
            c=ClassFile(b)
            for m in c.methods:
                for i in c.instructions(m.get('code',b'')):
                    if any(s in str(i['operand']) for s in TOKENS):hits.append(dict(entry=entry,class_sha256=byte_hash(b),method=m['name'],descriptor=m['descriptor'],instruction=i))
    return dict(jar_sha256=target['sha256'],scope='All TF instruction callers of Travellers storage/view/cloth controls; GUI/data/command producers are dispositioned separately from native combat callbacks.',needles=TOKENS,hits=hits)

def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest');res=read_json(WORK/'twilightforest/resources.json')
    selected=[p for p in res if p.startswith('data/') and any(k in p for k in ['emperors_cloth','belt_blacklisted','item_display','red_thread_vision','swap_hotbar','travellers_modifiers/zoom'])]
    classes={c:['*'] for c in FULL}
    classes.update({'asmhooks/MapHooks':['updateMapsInGoggles'],'events/MiscEvents':['setup','washOffCloth'],'util/TFItemStackUtils':['giveOrDrop'],'init/TFDataComponents':['*'],'init/TFDataAttachments':['*'],T+'TravellersArmorItem':['getArmorTexture','gogglesProperties','beltProperties'],'client/event/ClientGameEvents':['addCustomTooltips']})
    with zipfile.ZipFile(target['path']) as jar:
        # Base belt properties are declared on the belt subclass, already fully covered.
        classes[T+'TravellersArmorItem'].remove('beltProperties')
        for c,wanted in list(classes.items()):
            if wanted==['*']:continue
            available={m['name'] for m in ClassFile(jar.read('twilightforest/'+c+'.class')).methods}
            classes[c]=sorted(set(wanted)|{m for m in available if any(m.startswith('lambda$'+n+'$') for n in wanted)})
        for c,needles in [('init/TFRecipes',['EmperorsCloth','NoTemplateSmithing']),('init/TFItems',['EMPERORS_CLOTH','Travellers','MoonDial']),('events/RegistrationEvents',['SwapHotbarPacket','CycleMapSlotPacket','GogglesZoomPacket','ITEM_DISPLAY_TYPE']),('client/event/ClientRegistrationEvents',['ItemDisplayOverlay','RedThreadRenderer']),('command/TFCommand',['TravellersGearCommand'])]:
            cls=ClassFile(jar.read('twilightforest/'+c+'.class'));classes[c]=[m['name'] for m in cls.methods if m['name']=='<clinit>' or any(any(n in str(i['operand']) for n in needles) for i in cls.instructions(m.get('code',b'')))]
    print('native',native(BATCH,classes,selected),flush=True)
    raw={'net/minecraft/world/entity/LivingEntity':['getArmorCoverPercentage','getVisibilityPercent'],'net/minecraft/world/entity/ai/targeting/TargetingConditions':['test'],'net/minecraft/world/entity/player/Inventory':['getArmor','getItem','setItem','tick','contains'],'net/minecraft/world/item/ItemStack':['canFitInsideContainerItems','isSameItemSameComponents','overrideStackedOnOther','overrideOtherStackedOnMe'],'net/minecraft/world/item/MapItem':['inventoryTick','getUpdatePacket','update'],'net/minecraft/world/level/saveddata/maps/MapItemSavedData':['tickCarriedBy','mapMatcher'],'net/minecraft/client/renderer/entity/layers/CapeLayer':['render'],'net/minecraft/client/renderer/entity/layers/HumanoidArmorLayer':['renderArmorPiece'],'net/minecraft/client/renderer/entity/layers/ElytraLayer':['render'],'net/minecraft/client/renderer/blockentity/BlockEntityRenderer':['shouldRender','shouldRenderOffScreen','getViewDistance'],'net/minecraft/client/MouseHandler':['turnPlayer'],'net/minecraft/world/item/component/ItemContainerContents':['fromItems','getStackInSlot','getSlots','copyInto','<init>'],'net/minecraft/world/inventory/Slot':['safeInsert','allowModification'],'net/minecraft/world/inventory/SmithingMenu':['createResult','onTake']}
    names=MojangNames()
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c,ms in raw.items():
            cls=ClassFile(jar.read(names.named[c]+'.class'));available={names.member(cls.name,m['name'],m['descriptor']) for m in cls.methods}
            raw[c]=sorted({m for m in available if m in ms or any(m.startswith('lambda$'+n+'$') for n in ms)})
    loader={c+'.class':list(ms) for c,ms in raw.items()};template=read_json(OUT/'reference-specifications/vv-loader-244.json');a=next(a for a in template['archives'] if a['path'].endswith('client.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c in loader:
            if c not in jar.namelist():continue
            available={m['name'] for m in ClassFile(jar.read(c)).methods};wanted=raw[c[:-6]]+(['shouldRender'] if c.endswith('ElytraLayer.class') else [])+(['getSlots','getStackInSlot','validateSlotIndex'] if c.endswith('ItemContainerContents.class') else [])
            loader[c]=sorted({m for m in available if m in wanted or any(m.startswith('lambda$'+n+'$') for n in wanted if not n.startswith('lambda$'))})
    hooks={'net/neoforged/neoforge/client/event/CalculatePlayerTurnEvent.class':['*'],'net/neoforged/neoforge/client/event/ComputeFovModifierEvent.class':['*'],'net/neoforged/neoforge/client/ClientHooks.class':['getTurnPlayerValues','getFieldOfViewModifier'],'net/neoforged/neoforge/common/CommonHooks.class':['getEntityVisibilityMultiplier'],'net/neoforged/neoforge/common/extensions/IItemExtension.class':['canFitInsideContainerItems'],'net/neoforged/neoforge/common/extensions/IItemStackExtension.class':['canFitInsideContainerItems']}
    a=next(a for a in template['archives'] if a['path'].endswith('universal.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c,ms in hooks.items():
            available={m['name'] for m in ClassFile(jar.read(c)).methods}
            hooks[c]=sorted(available if ms==['*'] else {m for m in available if m in ms or any(m.startswith('lambda$'+n+'$') for n in ms)})
            assert hooks[c],(c,ms,available)
    print('references',references(BATCH,raw,loader,hooks),flush=True)
    nestedpath=WORK/'twilightforest/nested-tf-asm.jar'
    with zipfile.ZipFile(nestedpath) as jar:asmclasses={n:['*'] for n in jar.namelist() if n.endswith('.class') and n.rsplit('/',1)[-1][:-6] in TRANSFORMERS}
    assert len(asmclasses)==4
    spec=dict(id=BATCH+'-asm',scope='Four installed registered cloth/map transformers. Landmark locator ASM remains a separate unfinished map utility.',archives=[dict(path=str(nestedpath),sha256=sha256(nestedpath),classes=asmclasses,resources=[])])
    write_json(OUT/'reference-specifications'/f'{BATCH}-asm.json',spec);write_json(OUT/'reference-evidence'/f'{BATCH}-asm.json',reference_collect(spec,source_aids=True))
    write_json(OUT/'twilightforest-travellers-utility-caller-scan.json',scan_callers(target))

if __name__=='__main__':collect()
