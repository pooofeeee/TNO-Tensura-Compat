"""Pin Friends & Foes native code and exact vanilla/installed-loader comparisons. Static only."""
from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from vanilla_reference import prepare
from selected_reference import collect as reference

PREFIX='com/faboslav/friendsandfoes/'

def main():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='friendsandfoes')
    assert sha256(target['path'])==target['sha256']
    specs=[]
    with zipfile.ZipFile(target['path']) as jar:
        for entry in sorted(jar.namelist()):
            short=entry.removeprefix(PREFIX)
            if entry.endswith('.class') and entry.startswith(PREFIX):
                cls=ClassFile(jar.read(entry))
                specs.append(dict(id='faf:'+short.removesuffix('.class'),mod_key='friendsandfoes',entry=entry,methods=sorted({m['name'] for m in cls.methods})))
            elif (entry.startswith('data/') and entry.endswith('.json')) or entry.endswith('mixins.json') or 'wildfire' in entry and entry.endswith('.json') and 'animation' in entry:
                specs.append(dict(id='faf:'+entry,mod_key='friendsandfoes',entry=entry))
    native=dict(schema='tno.external_effects.native_spec.v1',baseline=BASELINE,evidence_specifications=specs)
    write_json(OUT/'native-specifications/friendsandfoes.json',native)
    write_json(OUT/'native-evidence/friendsandfoes.json',collect(native))
    config=MODS.parent/'config/friendsandfoes.json'
    write_json(OUT/'friendsandfoes-config-snapshot.json',dict(path=str(config),sha256=sha256(config),data=read_json(config),authority='Installed file snapshot, not a runtime assertion. Wildfire is disabled; do not change configuration in this research.'))
    classes={
        'net/minecraft/world/entity/projectile/SmallFireball':['onHitEntity','onHitBlock','onHit','hurt'],
        'net/minecraft/world/entity/projectile/Snowball':['onHitEntity'],
        'net/minecraft/world/entity/monster/Blaze$BlazeAttackGoal':['tick'],
        'net/minecraft/world/entity/monster/SpellcasterIllager$SpellcasterUseSpellGoal':['canUse','start','tick','getCastWarmupTime'],
        'net/minecraft/world/entity/monster/Illusioner$IllusionerBlindnessSpellGoal':['canUse','start','performSpellCasting','getCastingTime','getCastingInterval'],
        'net/minecraft/world/entity/monster/Illusioner$IllusionerMirrorSpellGoal':['performSpellCasting','getCastingTime','getCastingInterval'],
        'net/minecraft/world/entity/animal/horse/SkeletonTrapGoal':['canUse','tick','createHorse','createSkeleton'],
        'net/minecraft/world/entity/animal/IronGolem':['mobInteract'],
        'net/minecraft/world/entity/animal/Wolf':['applyTamingSideEffects','mobInteract'],
        'net/minecraft/world/entity/animal/allay/Allay':['aiStep'],
        'net/minecraft/world/entity/ai/behavior/Behavior':['tryStart','tickOrStop'],
        'net/minecraft/world/entity/ai/behavior/CountDownCooldownTicks':['tick'],
        'net/minecraft/world/entity/ai/goal/TemptGoal':['<init>','shouldFollow','canUse','canContinueToUse','start','stop','tick'],
        'net/minecraft/world/entity/Entity':['thunderHit','isInvulnerableTo','setTicksFrozen','getTicksRequiredToFreeze','isFullyFrozen','canFreeze'],
        'net/minecraft/world/damagesource/DamageSources':['fireball','mobAttack','thrown','lightningBolt','magic'],
        'net/minecraft/world/entity/LightningBolt':['tick'],
        'net/minecraft/world/item/SuspiciousStewItem':['finishUsingItem'],
        'net/minecraft/world/inventory/GrindstoneMenu$4':['getExperienceFromItem','getExperienceAmount'],
    }
    # Raw method spellings are validated, not inferred from later source versions.
    spec=dict(classes=classes,resources=['data/minecraft/damage_type/'+n+'.json' for n in ['mob_attack','fireball','unattributed_fireball','magic','lightning_bolt','freeze','on_fire']])
    write_json(OUT/'vanilla-specifications/friendsandfoes.json',spec)
    write_json(OUT/'vanilla-evidence/friendsandfoes.json',prepare(spec))
    old=read_json(OUT/'reference-specifications/cult-loader-244.json');archives=[]
    for a in old['archives']:
        if a['path'].endswith('-client.jar'):
            with zipfile.ZipFile(a['path']) as jar:entries=set(jar.namelist())
            wanted={k+'.class':v for k,v in classes.items() if k+'.class' in entries}
            archives.append(dict(path=a['path'],sha256=a['sha256'],classes=wanted))
    spec=dict(id='friends-loader-244',scope='Exact installed NeoForge21.1.244 overrides for Friends & Foes comparisons.',archives=archives)
    write_json(OUT/'reference-specifications/friends-loader-244.json',spec)
    write_json(OUT/'reference-evidence/friends-loader-244.json',reference(spec,True))
    print('Friends & Foes native witnesses',len(specs),'vanilla classes',len(classes))

if __name__=='__main__':main()
