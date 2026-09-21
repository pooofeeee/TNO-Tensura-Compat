"""Incremental Minoshroom/Knight Phantom witnesses from the installed authority."""
from twilight_evidence import *


def collect():
    batch = 'twilight-minoshroom-knight'
    classes = {c: ['*'] for c in [
        'entity/boss/Minoshroom', 'entity/boss/KnightPhantom', 'entity/boss/KnightPhantom$Formation',
        'entity/monster/Minotaur', 'entity/ai/goal/GroundAttackGoal', 'entity/ai/goal/ChargeAttackGoal',
        'entity/ai/goal/PhantomWatchAndAttackGoal', 'entity/ai/goal/PhantomAttackStartGoal',
        'entity/ai/goal/PhantomThrowWeaponGoal', 'entity/ai/goal/PhantomUpdateFormationAndMoveGoal',
        'entity/ai/control/NoClipMoveControl', 'entity/projectile/ThrownWep', 'entity/projectile/TFThrowable',
        'item/MinotaurAxeItem', 'item/KnightmetalSwordItem', 'item/KnightmetalAxeItem',
        'item/KnightmetalPickItem', 'item/KnightmetalShieldItem', 'item/PhantomArmorItem',
        'entity/boss/BaseTFBoss', 'entity/EnforcedHomePoint', 'entity/ai/goal/AttemptToGoHomeGoal',
        'block/entity/spawner/MinoshroomSpawnerBlockEntity', 'block/entity/spawner/KnightPhantomSpawnerBlockEntity',
        'block/entity/spawner/BossSpawnerBlockEntity']}
    classes['util/entities/EntityUtil'] = ['properlyApplyCustomDamageSource', 'getKnockback', 'canDestroyBlock', 'killLavaAround']
    classes['events/ToolEvents'] = ['setup', 'doKnightmetalToolLogic', 'addExtraAxeChargingDamage']
    classes['entity/monster/Wraith'] = ['doHurtTarget']  # Alternate HAUNT caller only, not a Wraith review.
    classes['init/TFDamageTypes'] = ['getEntityDamageSource', 'getDamageSource', 'getIndirectEntityDamageSource']
    classes['util/TFToolMaterials'] = ['<clinit>']
    classes['init/TFItems'] = ['<clinit>']
    classes['init/TFArmorMaterials'] = ['<clinit>', 'lambda$static$18', 'lambda$static$19', 'lambda$static$20']
    inventory = read_json(OUT / 'jar-inventory.json')
    target = next(t for t in inventory['targets'] if t['key'] == 'twilightforest')
    with zipfile.ZipFile(target['path']) as jar:
        cls = ClassFile(jar.read('twilightforest/init/TFItems.class'))
        for m in cls.methods:
            ins = list(cls.instructions(m.get('code', b'')))
            if any(i['opcode'] == '0xbb' and any(n in str(i['operand']) for n in (
                    'MinotaurAxeItem', 'KnightmetalSwordItem', 'KnightmetalAxeItem',
                    'KnightmetalPickItem', 'KnightmetalShieldItem', 'PhantomArmorItem')) for i in ins):
                classes['init/TFItems'].append(m['name'])
    resources = read_json(WORK / 'twilightforest/resources.json')
    selected = [p for p, v in resources.items() if '/tags/entity_type/' in p and any(
        x in str(v) for x in ('twilightforest:minoshroom', 'twilightforest:knight_phantom', 'twilightforest:thrown_wep'))]
    print('native', native(batch, classes, selected))
    raw = {
        'net/minecraft/world/entity/monster/Monster': ['createMonsterAttributes'],
        'net/minecraft/world/entity/Mob': ['createMobAttributes', 'doHurtTarget', 'finalizeSpawn', 'populateDefaultEquipmentSlots', 'populateDefaultEquipmentEnchantments', 'enchantSpawnedWeapon', 'enchantSpawnedArmor', 'enchantSpawnedEquipment'],
        'net/minecraft/world/entity/LivingEntity': ['<clinit>', 'setSprinting', 'canDisableShield', 'blockUsingShield', 'blockedByShield', 'hurtCurrentlyUsedShield', 'hurtArmor', 'getArmorCoverPercentage', 'detectEquipmentUpdates', 'collectEquipmentChanges', 'handleEquipmentChanges', 'createLivingAttributes', 'getArmorValue', 'canBeAffected', 'isInvertedHealAndHarm'],
        'net/minecraft/world/entity/player/Player': ['blockUsingShield', 'disableShield', 'hurtCurrentlyUsedShield'],
        'net/minecraft/world/entity/ai/goal/MeleeAttackGoal': ['<init>', 'canUse', 'canContinueToUse', 'start', 'stop', 'tick', 'checkAndPerformAttack', 'resetAttackCooldown', 'getAttackInterval', 'canPerformAttack', 'requiresUpdateEveryTick'],
        'net/minecraft/world/item/DiggerItem': ['createAttributes', 'hurtEnemy', 'postHurtEnemy'],
        'net/minecraft/world/item/SwordItem': ['createAttributes', 'hurtEnemy', 'postHurtEnemy'],
        'net/minecraft/world/item/Tiers': ['<clinit>', 'getAttackDamageBonus'],
        'net/minecraft/world/item/ArmorItem': ['<init>'],
        'net/minecraft/world/entity/ai/attributes/Attributes': ['<clinit>'],
        'net/minecraft/world/entity/ai/attributes/AttributeInstance': ['calculateValue', 'save', 'load'],
        'net/minecraft/world/entity/projectile/Projectile': ['<init>', 'setOwner', 'getOwner', 'addAdditionalSaveData', 'readAdditionalSaveData', 'canHitEntity', 'onHit', 'onHitEntity', 'hitTargetOrDeflectSelf', 'deflect'],
        'net/minecraft/world/entity/projectile/ThrowableProjectile': ['<init>', 'tick'],
        'net/minecraft/world/entity/Entity': ['hurt', 'isAttackable', 'move', 'push', 'addAdditionalSaveData', 'readAdditionalSaveData'],
    }
    from vanilla_reference import MojangNames, CLIENT
    names = MojangNames()
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar = jar
        c = 'net/minecraft/world/entity/LivingEntity'
        cls = ClassFile(jar.read(names.named[c] + '.class'))
        raw[c] += [names.member(cls.name, m['name'], m['descriptor']) for m in cls.methods
                   if names.member(cls.name, m['name'], m['descriptor']).startswith('lambda$collectEquipmentChanges$')]
    loader = {c + '.class': list(ms) for c, ms in raw.items()}
    template = read_json(OUT / 'reference-specifications/vv-loader-244.json')
    with zipfile.ZipFile(next(a['path'] for a in template['archives'] if a['path'].endswith('client.jar'))) as jar:
        c = 'net/minecraft/world/entity/LivingEntity.class'
        loader[c] = [m for m in loader[c] if not m.startswith('lambda$')] + [
            m['name'] for m in ClassFile(jar.read(c)).methods if m['name'].startswith('lambda$collectEquipmentChanges$')]
    # canDisableShield is introduced by the installed extension; vanilla uses the AxeItem check.
    hooks = {'net/neoforged/neoforge/common/extensions/IItemExtension.class': ['canDisableShield'],
             'net/neoforged/neoforge/common/damagesource/DamageContainer.class': ['<init>', 'setNewDamage', 'getOriginalDamage', 'getNewDamage']}
    print('references', references(batch, raw, loader, hooks))


if __name__ == '__main__':
    collect()
