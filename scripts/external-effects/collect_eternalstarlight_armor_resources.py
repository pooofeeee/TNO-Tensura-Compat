from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare,MojangNames,CLIENT
from collect_eternalstarlight_foundation import ES,targets

CLASSES={
 'common/registry/ESAttributes':None,'common/registry/ESFoods':None,
 'common/mixin/ItemStackMixin':['forEachModifier','inventoryTick'],
 'common/mixin/ItemMixin':['modifyFoodProperties'],
 'common/mixin/LivingEntityMixin':['eat'],
 'common/mixin/ProjectileMixin':['getMovementToShoot'],
 'common/util/ESAccessoryUtil':['getAccessories','getActiveAccessories','getActiveAccessoriesOnArmors','overrideEquipmentOnAccessory','overrideAccessoryOnEquipment'],
 'common/handler/ESCommonHandler':['<clinit>','onEntityTick','onPostLivingHurt','onLivingHeal','onLivingVisibility','onLivingDecreaseAirSupply','onVanillaGameEvent'],
 'neoforge/event/CommonEvents':['onLivingHeal','onLivingVisibility','onLivingBreathe','onVanillaGameEvent'],
 'neoforge/item/armor/NeoStarlitDiamondArmorItem':None,
}
for n in ['Unrealium','Deepsilver','ThermalSpringstone','Glacite','AirSac','Alchemist']:CLASSES['common/item/armor/'+n+'ArmorItem']=None

def census():
    t=targets()['eternalstarlight'];rows=[]
    needles=['ESAttributes.HEAL_MULTIPLIER','ESItems.FUNGUS_AMULET','ESItems.PEARL_NECKLACE','DEEPSILVER_ARMOR_CAN_REMOVE','onVanillaGameEvent(','onLivingDecreaseAirSupply(']
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(x for x in z.namelist() if x.endswith('.class')):
            raw=z.read(n);c=ClassFile(raw)
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if any(s in str(i['operand']) for s in needles)]
                if hits:rows.append(dict(entry=n,sha256=byte_hash(raw),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits))
    return dict(jar_sha256=t['sha256'],scope='Whole JAR heal/Fungus/Pearl and armor cleanse/air/vibration references; cosmetic refs are exclusions.',rows=rows)

def save():
    t=targets()['eternalstarlight'];rows=[];classes=dict(CLASSES)
    with zipfile.ZipFile(t['path']) as z:
        c=ClassFile(z.read(ES+'common/registry/ESItems.class'))
        classes['common/registry/ESItems']=[m['name'] for m in c.methods if any(i['opcode']=='0xbb' and str(i['operand']).endswith('/Accessory') for i in c.instructions(m.get('code',b'')))]
        assert len(classes['common/registry/ESItems'])==6
        for short,wanted in classes.items():
            n=ES+short+'.class';c=ClassFile(z.read(n));names=wanted if wanted is not None else sorted({m['name'] for m in c.methods});names=sorted(set(names)|{m['name'] for m in c.methods if any(m['name'].startswith('lambda$'+v+'$') for v in names)})
            rows.append(dict(id='es:armor:'+short,mod_key='eternalstarlight',entry=n,methods=names))
        tags=['mob_effect/deepsilver_armor_can_remove','item/thermal_springstone_weapons','item/glacite_weapons','item/malarite_weapons','item/pungency_fruit_weapons','item/consumable_when_wearing_fungus_amulet','item/mends_naturally','item/repaired_by_crescent_pendant']
        for tag in tags:
            n='data/eternal_starlight/tags/'+tag+'.json';rows.append(dict(id='es:armor:data:'+tag,mod_key='eternalstarlight',entry=n))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Armor defenses/attributes, native material Post controls, accessories/heal/air and consumable cleanse. Static only.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/eternalstarlight-armor-resources.json',s);write_json(OUT/'native-evidence/eternalstarlight-armor-resources.json',collect(s));write_json(OUT/'eternalstarlight-armor-resources-census.json',census())
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None);a['classes']={}
    wanted={'net/minecraft/world/entity/LivingEntity':['collectEquipmentChanges','removeEffect','removeEffectNoUpdate','heal'],'net/minecraft/world/item/ItemStack':['forEachModifier'],'net/minecraft/world/item/component/ItemAttributeModifiers':['forEach'],'net/minecraft/world/item/component/ItemAttributeModifiers$Builder':['add','build'],'net/minecraft/world/entity/ai/attributes/AttributeInstance':['addTransientModifier','removeModifier']}
    raw={}
    with zipfile.ZipFile(a['path']) as z:
        for k,v in wanted.items():
            if k+'.class' in z.namelist():
                c=ClassFile(z.read(k+'.class'));a['classes'][k+'.class']=v+[m['name'] for m in c.methods if any(m['name'].startswith('lambda$'+n+'$') for n in v)]
            else:raw[k]=v
    b=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][1]);b.pop('semantic_review',None);b['classes']={'net/neoforged/neoforge/common/CommonHooks.class':['computeModifiedAttributes'],'net/neoforged/neoforge/event/ItemAttributeModifierEvent.class':['*'],'net/neoforged/neoforge/event/entity/living/LivingBreatheEvent.class':['*'],'net/neoforged/neoforge/event/VanillaGameEvent.class':['*']}
    b['classes']['net/neoforged/neoforge/common/extensions/IItemStackExtension.class']=['getAttributeModifiers']
    r=dict(id='eternalstarlight-armor-resources-244',scope='Exact installed native equipment modifier application, removal/heal admission and air/vibration events.',archives=[a,b])
    write_json(OUT/'reference-specifications/eternalstarlight-armor-resources-244.json',r);write_json(OUT/'reference-evidence/eternalstarlight-armor-resources-244.json',reference_collect(r,source_aids=True))
    s=dict(classes=raw,resources=[]);write_json(OUT/'vanilla-specifications/eternalstarlight-armor-resources.json',s);write_json(OUT/'vanilla-evidence/eternalstarlight-armor-resources.json',prepare(s))
    write_json(OUT/'reference-routing/eternalstarlight-armor-resources.json',dict(archive=a['path'],sha256=a['sha256'],absent_entries=[k+'.class' for k in raw]))
    print('Armor/resource witnesses saved')
if __name__=='__main__':save()
