"""Pin Royal-only native code and exact 1.21.1 comparison inputs; never run Minecraft."""
from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from vanilla_reference import prepare, CLIENT
from selected_reference import collect as reference

PREFIX='com/mongoose/royalvariations/'

def main():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='royalvariations')
    assert sha256(target['path'])==target['sha256']
    specs=[]
    with zipfile.ZipFile(target['path']) as jar:
        for entry in sorted(jar.namelist()):
            short=entry.removeprefix(PREFIX)
            keep=short.startswith(('common/','utils/','mixin/','compat/','config/')) or short in ['RoyalVariations.class','client/events/ClientEvents.class','init/RVDataComponents.class','init/SidedInit.class']
            if entry.endswith('.class') and keep:
                c=ClassFile(jar.read(entry))
                specs.append(dict(id='rv:'+short.removesuffix('.class'),mod_key='royalvariations',entry=entry,methods=sorted({m['name'] for m in c.methods})))
            elif (entry.startswith('data/') and entry.endswith('.json')) or entry.endswith('mixins.json'):
                specs.append(dict(id='rv:'+entry,mod_key='royalvariations',entry=entry))
    native=dict(schema='tno.external_effects.native_spec.v1',baseline=BASELINE,evidence_specifications=specs)
    write_json(OUT/'native-specifications/royalvariations.json',native)
    write_json(OUT/'native-evidence/royalvariations.json',collect(native))
    classes={
        'net/minecraft/world/entity/ai/attributes/AttributeInstance':['calculateValue'],
        'net/minecraft/world/entity/ai/attributes/RangedAttribute':['sanitizeValue'],
        'net/minecraft/world/entity/ai/attributes/Attributes':['<clinit>'],
        'net/minecraft/world/entity/monster/EnderMan':['hurt','hurtWithCleanWater','setTarget','teleport','teleportTowards'],
        'net/minecraft/world/entity/monster/Creeper':['explodeCreeper','spawnLingeringCloud','causeFallDamage','thunderHit'],
        'net/minecraft/world/entity/monster/Zombie':['killedEntity'],
        'net/minecraft/world/entity/projectile/ThrownEnderpearl':['onHit','onHitEntity'],
        'net/minecraft/world/entity/projectile/AbstractArrow':['onHitEntity','doKnockback'],
        'net/minecraft/world/level/Explosion':['explode','getSeenPercent','getIndirectSourceEntity'],
        'net/minecraft/world/entity/AreaEffectCloud':['tick','<init>'],
        'net/minecraft/world/entity/ai/goal/target/NearestAttackableTargetGoal':['canUse','start','findTarget'],
        'net/minecraft/world/entity/ai/goal/target/TargetGoal':['canContinueToUse'],
        'net/minecraft/world/entity/ai/targeting/TargetingConditions':['test'],
        'net/minecraft/world/damagesource/DamageSources':['arrow','thrown','indirectMagic','explosion'],
        'net/minecraft/world/entity/LivingEntity':['isDamageSourceBlocked','hurt','getDamageAfterArmorAbsorb','getDamageAfterMagicAbsorb'],
    }
    with zipfile.ZipFile(CLIENT) as jar:
        resources=[n for n in sorted(jar.namelist()) if n.startswith('data/minecraft/tags/damage_type/') and n.endswith('.json')]
        resources += ['data/minecraft/damage_type/'+n+'.json' for n in ['arrow','thrown','indirect_magic','explosion','player_explosion']]
        resources += ['data/minecraft/enchantment/power.json','data/minecraft/tags/entity_type/undead.json']
    spec=dict(classes=classes,resources=resources)
    write_json(OUT/'vanilla-specifications/royalvariations.json',spec)
    write_json(OUT/'vanilla-evidence/royalvariations.json',prepare(spec))
    old=read_json(OUT/'reference-specifications/cult-loader-244.json')
    archives=[]
    for a in old['archives']:
        if a['path'].endswith('-client.jar'):
            with zipfile.ZipFile(a['path']) as jar:
                entries=set(jar.namelist())
                wanted={k+'.class':v for k,v in classes.items() if k+'.class' in entries}
            archives.append(dict(path=a['path'],sha256=a['sha256'],classes=wanted))
    spec=dict(id='royal-loader-244',scope='Exact installed NeoForge21.1.244 overrides for Royal vanilla comparisons.',archives=archives)
    write_json(OUT/'reference-specifications/royal-loader-244.json',spec)
    write_json(OUT/'reference-evidence/royal-loader-244.json',reference(spec,True))
    print('Royal native witnesses',len(specs),'vanilla classes',len(classes))

if __name__=='__main__':main()
