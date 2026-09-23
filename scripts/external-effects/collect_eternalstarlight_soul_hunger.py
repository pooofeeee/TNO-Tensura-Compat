from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_eternalstarlight_foundation import ES,targets

CLASSES={
 'common/entity/projectile/ChainOfSouls':None,
 'common/item/combat/ChainOfSoulsItem':['use','shoot','retrieve'],
 'common/item/combat/DaggerOfHungerItem':['<init>','<clinit>','postHurtEnemy','inventoryTick'],
 'common/item/combat/DaggerOfHungerItem$1':None,
 'common/item/combat/ESItemTiers':['<init>','<clinit>','getAttackDamageBonus'],
 'common/item/combat/DualWieldingSwordItem':['use','pick','filterHitResult'],
 'common/entity/projectile/VoraciousArrow':['<init>','doPostHurtEffects','readAdditionalSaveData','addAdditionalSaveData'],
 'common/item/combat/VoraciousArrowItem':['createArrow','asProjectile'],
 'common/mixin/PlayerMixin':['aiStep','getWeaponItem','useOffhandWeapon','useOffhandAttackStrengthTimer','resetOffhandAttackStrengthTimer'],
 'common/handler/ESCommonHandler':['onLivingHeal','onModifyPostAttackInvulnerabilityTicks'],
 'neoforge/event/CommonEvents':['onLivingHeal'],
 'common/config/ESConfig$ItemsConfig':['<init>'],
 'common/config/ESConfig$ItemsConfig$ChainOfSoulsConfig':None,
 'common/util/ESTags$EntityTypes':['<clinit>'],
}
def census():
    t=targets()['eternalstarlight'];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(x for x in z.namelist() if x.endswith('.class')):
            raw=z.read(n);c=ClassFile(raw)
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if (i['opcode']=='0xbb' and str(i['operand']).endswith('/ChainOfSouls')) or (i['opcode']=='0xb2' and any(s in str(i['operand']) for s in ['ESDamageTypes.SOUL_ABSORB','ESDamageTypes.DAGGER_OF_HUNGER','ESDataComponents.HUNGER_LEVEL','ESDataAttachments.OFFHAND_ATTACK']))]
                if hits:rows.append(dict(entry=n,sha256=byte_hash(raw),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits))
    return dict(jar_sha256=t['sha256'],scope='Whole ES-JAR Chain producer, soul/hunger source and Dagger hunger/offhand state references.',rows=rows)
def save():
    t=targets()['eternalstarlight'];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in CLASSES.items():
            n=ES+short+'.class';c=ClassFile(z.read(n));names=wanted if wanted is not None else sorted({m['name'] for m in c.methods});names=sorted(set(names)|{m['name'] for m in c.methods if any(m['name'].startswith('lambda$'+v+'$') for v in names)})
            rows.append(dict(id='es:soul_hunger:'+short,mod_key='eternalstarlight',entry=n,methods=names))
        n='data/eternal_starlight/tags/entity_type/chan_of_souls_cannot_pull.json';rows.append(dict(id='es:soul_hunger:data:'+n,mod_key='eternalstarlight',entry=n))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Chain native soul absorption/healing/control, Dagger hunger and dual-wield/Voracious delivery; no runtime.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/eternalstarlight-soul-hunger.json',s);write_json(OUT/'native-evidence/eternalstarlight-soul-hunger.json',collect(s));write_json(OUT/'eternalstarlight-soul-hunger-census.json',census())
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None);a['classes']={}
    wanted={'net/minecraft/world/entity/LivingEntity':['heal'],'net/minecraft/world/entity/player/Player':['causeFoodExhaustion'],'net/minecraft/world/food/FoodData':['eat','add'],'net/minecraft/world/food/FoodConstants':['saturationByModifier'],'net/minecraft/world/effect/HungerMobEffect':['applyEffectTick','shouldApplyEffectTickThisTick'],'net/minecraft/world/entity/projectile/ProjectileUtil':['getHitResultOnMoveVector','getHitResult','getEntityHitResult'],'net/minecraft/world/entity/projectile/Projectile':['onHit','onHitEntity','onHitBlock']}
    raw={}
    with zipfile.ZipFile(a['path']) as z:
        for k,v in wanted.items():
            if k+'.class' in z.namelist():a['classes'][k+'.class']=v+(['deflect'] if k.endswith('/Projectile') else [])
            else:raw[k]=v
    r=dict(id='eternalstarlight-soul-hunger-244',scope='Native heal hook, food/Hunger and Chain custom projectile collision path; raw fallback only for absent patched classes.',archives=[a])
    write_json(OUT/'reference-specifications/eternalstarlight-soul-hunger-244.json',r);write_json(OUT/'reference-evidence/eternalstarlight-soul-hunger-244.json',reference_collect(r,source_aids=True))
    s=dict(classes=raw,resources=[]);write_json(OUT/'vanilla-specifications/eternalstarlight-soul-hunger.json',s);write_json(OUT/'vanilla-evidence/eternalstarlight-soul-hunger.json',prepare(s))
    write_json(OUT/'reference-routing/eternalstarlight-soul-hunger.json',dict(archive=a['path'],sha256=a['sha256'],absent_entries=[k+'.class' for k in raw]))
    config=MODS.parent/'config/eternal_starlight.json';write_json(OUT/'eternalstarlight-soul-config-snapshot.json',dict(path=str(config),sha256=sha256(config),itemsConfig=read_json(config).get('itemsConfig',{}).get('chainOfSouls'),scope='File snapshot, not proof of loaded runtime values.'))
    print('Soul/hunger witnesses saved')
if __name__=='__main__':save()
