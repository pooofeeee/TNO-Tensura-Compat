from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_bossesrise_foundation import targets,KEY,PKG
CLASSES={s:None for s in ['event/DragonArmorEvents','item/KnightSwordItem','item/PirateSaberItem','item/EnhancedShieldItem','item/DragonGuardShieldItem','item/AnimatedSwordItem','item/WarriorSwordItem','item/LargeSwordItem','item/DaggerItem','item/DragonShankItem']}
for s in ['item/DragonBonesItem','item/KnightItem']:CLASSES[s]=['<init>','getDefaultAttributeModifiers','createAttributes','createAttributesBuilder']
CLASSES['init/BossesRiseItems']=['<clinit>']

def helper_census():
    t=targets()[KEY];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(x for x in z.namelist() if x.endswith('.class')):
            data=z.read(n);c=ClassFile(data)
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if 'EnhancedShieldItem.createAttributes(' in str(i.get('operand',''))]
                if hits:rows.append(dict(entry=n,method=m['name'],entry_sha256=byte_hash(data),hits=hits))
    return dict(jar_sha256=t['sha256'],scope='Whole-JAR calls of unused EnhancedShieldItem roll-attribute builder.',rows=rows)

def save():
    t=targets()[KEY];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in CLASSES.items():
            n=PKG+short+'.class';c=ClassFile(z.read(n));names=wanted or sorted({m['name'] for m in c.methods})
            if short=='init/BossesRiseItems':names += [m['name'] for m in c.methods if any('DragonBonesItem.createAttributes(' in str(i.get('operand','')) for i in c.instructions(m.get('code',b'')))]
            rows.append(dict(id='br:equipment:'+short,mod_key=KEY,entry=n,methods=names))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Dragon armor native event hooks and remaining combat equipment delivery; cosmetic members retained only as bytecode exclusion evidence.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/bossesrise-equipment.json',s);write_json(OUT/'native-evidence/bossesrise-equipment.json',collect(s));write_json(OUT/'bossesrise-equipment-helper-census.json',helper_census())
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None);a['classes']={};raw={}
    wanted={'net/minecraft/world/level/Level':['explode'],'net/minecraft/server/level/ServerLevel':['explode'],'net/minecraft/world/level/Explosion':['explode','getDefaultDamageSource','getIndirectSourceEntityInternal'],'net/minecraft/world/level/EntityGetter':['getNearbyPlayers'],'net/minecraft/world/entity/ai/targeting/TargetingConditions':['<clinit>','test'],'net/minecraft/world/item/ArmorItem':['getDefaultAttributeModifiers'],'net/minecraft/world/item/ItemStack':['forEachModifier'],'net/minecraft/world/entity/LivingEntity':['actuallyHurt','addEffect','canBeAffected'],'net/minecraft/world/entity/player/Player':['actuallyHurt']}
    with zipfile.ZipFile(a['path']) as z:
        for k,v in wanted.items():
            if k+'.class' in z.namelist():a['classes'][k+'.class']=v
            else:raw[k]=v
    u=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][1]);u.pop('semantic_review',None);u['classes']={'net/neoforged/neoforge/common/extensions/IItemStackExtension.class':['getAttributeModifiers'],'net/neoforged/neoforge/common/extensions/IItemExtension.class':['getDefaultAttributeModifiers']}
    r=dict(id='bossesrise-equipment-244',scope='Native Post event admission, double explosion lifecycle, target filters and default equipment attributes.',archives=[a,u]);write_json(OUT/'reference-specifications/bossesrise-equipment-244.json',r);write_json(OUT/'reference-evidence/bossesrise-equipment-244.json',reference_collect(r,source_aids=True))
    s=dict(classes=raw,resources=[]);write_json(OUT/'vanilla-specifications/bossesrise-equipment.json',s);write_json(OUT/'vanilla-evidence/bossesrise-equipment.json',prepare(s));write_json(OUT/'reference-routing/bossesrise-equipment.json',dict(archive=a['path'],sha256=a['sha256'],absent_entries=[k+'.class' for k in raw]));print('Equipment native/reference evidence pinned')
if __name__=='__main__':save()
