"""Dragon body combat, defense and actual healing/resource callers."""
from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_iceandfire_foundation import IAF,targets
from vanilla_reference import prepare

METHODS={
 'entity/DragonBaseEntity':['<init>','registerGoals','bakeAttributes','setConfigurableAttributes','updateAttributes','calculateArmorModifier','getAgeInDays','growDragon','setHunger','getHunger','updatePreyInMouth','positionRider','hurt','doHurtTarget','roar','isOwnersPet','isDirectPathBetweenPoints','updateRider','mobInteract','interactAt','tickDeath','die','kill','updateScale','containerChanged','readAdditionalSaveData','addAdditionalSaveData','checkFallDamage','isMobDead','isSleeping','setModelDead','isModelDead','getItemBySlot','isPlayingAttackAnimation','finalizeSpawn','canAddPassenger','setInSittingPose','travel','isAggressive','attack'],
 'entity/FireDragonEntity':['<init>','doHurtTarget','shouldTarget'],
 'entity/IceDragonEntity':['<init>','doHurtTarget','shouldTarget'],
 'entity/LightningDragonEntity':['<init>','doHurtTarget','shouldTarget','isInvulnerableTo'],
 'entity/util/dragon/IafDragonLogic':['attackTarget','updateDragonAttack','updateDragonServer'],
 'entity/ai/DragonAIAttackMeleeGoal':['*'],
 'entity/ai/DragonAITargetGoal':['*'],
 'entity/ai/DragonAITargetNonTamedGoal':['*'],
 'entity/ai/DragonAITargetItemsGoal':['*'],
 'entity/util/dragon/DragonUtils':['riderLookingAtEntity','hasSameOwner','isAnimaniaMob','canHostilesTarget','canTameDragonAttack'],
 'entity/MultipartPartEntity':['hurt','isInvulnerableTo','getParent'],
 'entity/DragonPartEntity':['<init>','collideWithNearbyEntities'],
 'network/ServerNetworkHelper':['registerReceivers'],
 'registry/IafEntities':['<clinit>','build'],
}

def census():
    t=targets()['iceandfire'];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for entry in sorted(n for n in z.namelist() if n.endswith('.class')):
            if not any(x in entry for x in ['Dragon','Multipart','ServerNetworkHelper']):continue
            c=ClassFile(z.read(entry))
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if any(x in str(i.get('operand','')) for x in ['.hurt(','.heal(','.setHealth(','.addEffect(','.setHunger(','.roar(','.attackTarget('])]
                if hits:rows.append(dict(entry=entry,method=m['name'],descriptor=m['descriptor'],hits=hits))
    return dict(schema='tno.external_effects.iaf_dragon_combat_census.v1',jar_sha256=t['sha256'],rows=rows,scope='Dragon/Multipart native class-name scope primitive locator; all rows require explicit disposition, not a whole-mod completion proof.')

def save():
    rows=[]
    with zipfile.ZipFile(targets()['iceandfire']['path']) as z:
        for short,wanted in METHODS.items():
            c=ClassFile(z.read(IAF+short+'.class'))
            if short=='network/ServerNetworkHelper':
                names={m['name'] for m in c.methods};wanted=[n for n in names if n=='registerReceivers' or n.startswith('lambda$')]
            methods=sorted({m['name'] for m in c.methods}) if wanted==['*'] else sorted(set(wanted+[m['name'] for m in c.methods if m['name'].startswith('lambda$')]))
            rows.append(dict(id='iaf:dragon-combat:'+short,mod_key='iceandfire',entry=IAF+short+'.class',methods=methods))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Shared dragon combat only; registry/network/interaction witness availability does not mark unrelated systems reviewed.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/iceandfire-dragon-combat.json',s);write_json(OUT/'native-evidence/iceandfire-dragon-combat.json',collect(s));write_json(OUT/'iceandfire-dragon-combat-census.json',census())
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None)
    a['classes']={'net/minecraft/world/entity/LivingEntity.class':['heal','setHealth'], 'net/minecraft/world/entity/Entity.class':['startRiding','canRide','couldAcceptPassenger','stopRiding','removeVehicle']}
    with zipfile.ZipFile(a['path']) as z:assert 'net/minecraft/world/damagesource/DamageSources.class' not in z.namelist()
    raw=dict(classes={'net/minecraft/world/damagesource/DamageSources':['mobAttack','indirectMagic']},resources=[])
    write_json(OUT/'vanilla-specifications/iceandfire-dragon-combat.json',raw);write_json(OUT/'vanilla-evidence/iceandfire-dragon-combat.json',prepare(raw))
    write_json(OUT/'reference-routing/iceandfire-dragon-combat.json',dict(archive=a['path'],sha256=a['sha256'],absent_entries=['net/minecraft/world/damagesource/DamageSources.class'],authority='Raw Minecraft1.21.1 for DamageSources class absent from exact patched archive.'))
    uranus=MODS/'uranus-2.4-1.21.1-neoforge.jar'
    ref=dict(id='iceandfire-dragon-combat-244',scope='Heal versus setHealth, native mount admission, source identity and exact Uranus food-point helper only.',archives=[a,dict(path=str(uranus),sha256=sha256(uranus),classes={'com/iafenvoy/uranus/object/item/FoodUtils.class':['getFoodPoints']})])
    write_json(OUT/'reference-specifications/iceandfire-dragon-combat-244.json',ref);write_json(OUT/'reference-evidence/iceandfire-dragon-combat-244.json',reference_collect(ref,source_aids=True))
    print('Dragon body/resource witnesses saved')

if __name__=='__main__':save()
