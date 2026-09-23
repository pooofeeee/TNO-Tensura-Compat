from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from collect_eternalstarlight_foundation import ES,targets

CLASSES={
 'common/item/armor/AlchemistArmorItem':None,
 'common/entity/projectile/ThioquartzShard':None,
 'common/entity/projectile/ThioquartzArrow':None,
 'common/item/combat/ThioquartzArrowItem':None,
 'common/entity/projectile/ThrownShatteredBlade':None,
 'common/item/combat/ShatteredSwordItem':None,
 'common/entity/living/goal/LonestarSkeletonShootBladeGoal':None,
 'common/entity/living/monster/LonestarSkeleton':['<init>','createAttributes','populateDefaultEquipmentSlots','onSwitchWeapon','reassessWeaponGoal','readAdditionalSaveData','setItemSlot'],
 'common/entity/projectile/WiltedPetal':None,
 'common/item/combat/WiltedCrossbowItem':['createProjectile','shootProjectile'],
 'common/handler/ESCommonHandler':['onEntityTick','onPostLivingHurt'],
 'common/block/fluid/EtherFluid':['armorModifier','<clinit>'],
 'common/mixin/EntityMixin':['checkInsideBlocks'],
 'common/util/ESAccessoryUtil':['getActiveAccessoriesOnArmors','getActiveAccessories','getAccessories'],
 'neoforge/registry/ESFluidTypes':None,
 'neoforge/registry/ESFluidTypes$1':None,
}
def census():
    t=targets()['eternalstarlight'];rows=[]
    needles=['ESDamageTypes.ETHER','ESDamageTypes.SHATTERED_BLADE','ESDamageTypes.WILT','ESDataAttachments.IN_ETHER','ETHER_RESISTANCE','eternal_starlight:wilted','ShatteredSwordItem.hasBlade(','ESItems.THIOQUARTZ_ARROW']
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(x for x in z.namelist() if x.endswith('.class')):
            raw=z.read(n);c=ClassFile(raw)
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if (i['opcode']=='0xbb' and any(str(i['operand']).endswith('/'+s) for s in ['ThioquartzShard','ThioquartzArrow','ThrownShatteredBlade','WiltedPetal'])) or any(s in str(i['operand']) for s in needles)]
                if hits:rows.append(dict(entry=n,sha256=byte_hash(raw),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits))
    return dict(jar_sha256=t['sha256'],scope='Whole JAR Ether counter/source/resistance, Shattered Blade and Wilt actual source and producer references.',rows=rows)
def save():
    t=targets()['eternalstarlight'];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in CLASSES.items():
            n=ES+short+'.class';c=ClassFile(z.read(n));names=wanted if wanted is not None else sorted({m['name'] for m in c.methods});names=sorted(set(names)|{m['name'] for m in c.methods if any(m['name'].startswith('lambda$'+v+'$') for v in names)})
            rows.append(dict(id='es:ebw:'+short,mod_key='eternalstarlight',entry=n,methods=names))
        n='data/eternal_starlight/tags/fluid/ether.json';rows.append(dict(id='es:ebw:data:'+n,mod_key='eternalstarlight',entry=n))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Remaining three ES custom damage types, Ether armor resource and distinct native deliveries. Static only.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/eternalstarlight-ether-blade-wilt.json',s);write_json(OUT/'native-evidence/eternalstarlight-ether-blade-wilt.json',collect(s));write_json(OUT/'eternalstarlight-ether-blade-wilt-census.json',census())
    print('Ether/blade/wilt witnesses saved')
if __name__=='__main__':save()
