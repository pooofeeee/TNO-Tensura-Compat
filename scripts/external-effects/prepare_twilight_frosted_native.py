"""Selected producer/registration evidence completing the R2f1 Frosted trace."""
from twilight_evidence import *
import tomllib

classes={
 'events/EntityEvents':['setup','onParryProjectile','<clinit>'],
 'events/ProgressionEvents':['setup'],
 'TwilightForestMod':['<init>','<clinit>'],
 'beanification/BeanContext':['init','initInternal','runAnnotationProcessor'],
 'beanification/processors/finalize/PostConstructAnnotationFinalizeBeanProcessor':['process'],
 'beanification/processors/gather/ComponentAnnotationGatherBeanProcessor':['process'],
 'beanification/processors/construct/ConstructBeanProcessor':['process'],
 'dispenser/TFDispenserBehaviors':['init'],
 'events/RegistrationEvents':['init'],
 'init/TFEnchantmentEffects':['*'],
 'util/landmarks/LandmarkUtil':['isProgressionEnforced'],
 'util/PlayerHelper':['doesPlayerHaveRequiredAdvancements','playerHasRequiredAdvancements'],
 'init/TFGameRules':['*'],
 'entity/projectile/TFThrowable':['*'],
 'entity/boss/AlphaYeti':['performRangedAttack','canRampage','registerGoals'],
 'item/YetiArmorItem':['<init>','canWalkOnPowderedSnow'],
 'init/TFItems':['<clinit>'],
 'init/TFEntities':['<clinit>'],
 'config/TFConfig':['<clinit>'],
}

if __name__=='__main__':
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest')
    with zipfile.ZipFile(target['path']) as z:
        # Select actual registry factories and setup lambdas, not unrelated item implementations.
        needles={'init/TFItems':['IceSwordItem','IceBowItem','IceBombItem','YetiArmorItem'],
                 'init/TFEntities':['IceArrow','IceBomb'],
                 'events/RegistrationEvents':['TFDispenserBehaviors.init'],
                 'config/TFConfig':['shieldParryTicks']}
        for short,terms in needles.items():
            c=ClassFile(z.read('twilightforest/'+short+'.class'))
            for m in c.methods:
                if any(any(term in str(i.get('operand')) for term in terms) for i in c.instructions(m.get('code',b''))):
                    if m['name'] not in classes[short]:classes[short].append(m['name'])
    resources=[
      'data/twilightforest/enchantment/chill_aura.json',
      'data/twilightforest/twilight/restrictions/glacier.json',
      'data/twilightforest/twilight/restrictions/snowy_forest.json',
      'data/minecraft/tags/entity_type/freeze_immune_entity_types.json',
      'data/minecraft/tags/entity_type/freeze_hurts_extra_types.json',
      'data/minecraft/tags/item/freeze_immune_wearables.json',
      'data/twilightforest/tags/entity_type/bosses.json',
      'data/twilightforest/loot_table/aurora_room.json',
    ]
    print('New native witnesses',native('twilight-frosted',classes,resources))
    config=MODS.parent/'config/twilightforest-common.toml'
    text=config.read_bytes().decode('utf-8-sig')
    write_json(OUT/'config-evidence/twilightforest-common.json',dict(baseline=BASELINE,path=str(config),sha256=sha256(config),text=text,values=tomllib.loads(text)))
