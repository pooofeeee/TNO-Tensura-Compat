from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_eternalstarlight_foundation import ES,targets

CLASSES={}
for n in ['CrescentSpear','Greatsword','Hammer','Scythe','MoonringGreatsword','TentacleSpike','FlowglazeBow','UnrealiumCrossbow','BloodBow','GlaciteShield','FlowglazeShield']:
    CLASSES['common/item/combat/'+n+'Item']=None
for n in ['NeoScythe','NeoPetalScythe','NeoCrescentSpear']:CLASSES['neoforge/item/combat/'+n+'Item']=None
CLASSES.update({
 'common/mixin/PlayerMixin':['damageShield','disableShield','attackHurtEnemy','attackCheckHammerStrength','attackBeforeScytheSweepCheck','attackAfterScytheSweepCheck'],
 'common/mixin/LivingEntityMixin':['isBlocking','getKnockback','checkAutoSpinAttack','checkAutoSpinAttackTail','doCrescentSpearDamage'],
 'common/mixin/EntityMixin':['deflection','move'],
 'common/handler/ESCommonHandler':['onEntityTick','onModifyLivingHurtDamage','onPostLivingHurt','handleFlowglazeWeaponAttack','onCriticalHit','onShieldBlock'],
 'neoforge/event/CommonEvents':['onCriticalHit','onShieldBlock'],
 'common/entity/attack/TentacleSpike':None,
})

def census():
    t=targets()['eternalstarlight'];rows=[]
    needles=['CONCENTRATED_','CONCENTRATION_LEVEL','LAST_CONCENTRATED_','ESDataAttachments.MOVEMENT','LAST_MOVEMENT_UPDATE','CRESCENT_SPEAR_DASH','FLOWGLAZE_ARROW_EXTRA_BASE_DAMAGE','eternal_starlight:flowglaze','FLOWGLAZE_SHIELD','GLACITE_SHIELD','WARHAMMER_PENDANT','UNREALIUM_CROSSBOW']
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(x for x in z.namelist() if x.endswith('.class')):
            raw=z.read(n);c=ClassFile(raw)
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if any(s in str(i['operand']) for s in needles)]
                if hits:rows.append(dict(entry=n,sha256=byte_hash(raw),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits))
    return dict(jar_sha256=t['sha256'],scope='Whole JAR special-weapon marker, concentration, movement and shield state references; registrations/tooltips alone are not native combat paths.',rows=rows)

def save():
    t=targets()['eternalstarlight'];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in CLASSES.items():
            n=ES+short+'.class';c=ClassFile(z.read(n));names=wanted if wanted is not None else sorted({m['name'] for m in c.methods});names=sorted(set(names)|{m['name'] for m in c.methods if any(m['name'].startswith('lambda$'+v+'$') for v in names)})
            rows.append(dict(id='es:weapons:'+short,mod_key='eternalstarlight',entry=n,methods=names))
        for tag in ['flowglaze_weapons','greatswords','hammers','scythes']:
            n='data/eternal_starlight/tags/item/'+tag+'.json';rows.append(dict(id='es:weapons:data:'+tag,mod_key='eternalstarlight',entry=n))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Special melee, projectile weapon modifiers and shields. Armor deferred to next bounded section.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/eternalstarlight-special-weapons.json',s);write_json(OUT/'native-evidence/eternalstarlight-special-weapons.json',collect(s));write_json(OUT/'eternalstarlight-special-weapons-census.json',census())
    archives=[]
    for idx,classes in enumerate([
        {'net/minecraft/world/entity/player/Player.class':['attack','getWeaponItem','startAutoSpinAttack','doAutoAttackOnTouch','hurtCurrentlyUsedShield','disableShield'],
         'net/minecraft/world/entity/LivingEntity.class':['checkAutoSpinAttack','isBlocking','isDamageSourceBlocked','hurt'],
         'net/minecraft/world/entity/projectile/Projectile.class':['hitTargetOrDeflectSelf','deflect']},
        {'net/neoforged/neoforge/event/entity/living/LivingShieldBlockEvent.class':['*'],
         'net/neoforged/neoforge/event/entity/player/CriticalHitEvent.class':['*'],
         'net/neoforged/neoforge/common/CommonHooks.class':['fireCriticalHit','onDamageBlock']}
    ]):
        a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][idx]);a.pop('semantic_review',None);a['classes']=classes;archives.append(a)
    r=dict(id='eternalstarlight-special-weapons-244',scope='Exact installed loader attack locals, critical event timing, spin clearing order, shield admission and reflection owner routing.',archives=archives)
    write_json(OUT/'reference-specifications/eternalstarlight-special-weapons-244.json',r);write_json(OUT/'reference-evidence/eternalstarlight-special-weapons-244.json',reference_collect(r,source_aids=True))
    print('Special weapons witnesses saved')
if __name__=='__main__':save()
