"""Remaining nine-effect family semantics and native delivery, bounded to combat."""
from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare,CLIENT,MojangNames
from collect_eternalstarlight_foundation import ES,targets

CLASSES={
 'common/effect/StarfireEffect':None,'common/effect/DreamCatcherEffect':None,'common/effect/StickyEffect':None,'common/effect/OblivionEffect':None,
 'common/handler/ESCommonHandler':['onPostLivingHurt','onLivingDeath','onLivingVisibility','onLivingChangeTarget','onEntityTick','onClientToServerSimpleAction'],
 'common/mixin/LivingEntityMixin':['onClimbable','createLivingAttributes'],
 'common/mixin/EntityMixin':['isStateClimbable','isInWall'],
 'common/mixin/BlockStateBaseMixin':['getCollisionShape'],
 'common/mixin/TntBlockMixin':['explode'],
 'common/mixin/client/MinecraftMixin':['getHitResultType'],
 'common/network/SimpleActionPacket':['handle'],
 'common/item/combat/WhipItem':['use','performSwingAttack','hurtEnemy','postHurtEnemy'],
 'common/item/combat/CandlashItem':['doPostHurtEffects','createWhip'],
 'common/item/combat/ColdsnapItem':['doPostHurtEffects','createWhip'],
 'common/entity/attack/Whip':['<init>','tick','hurt','getPlayerOwner','getWeaponItem'],
 'common/entity/attack/Candlash':['getLifespan','getWhipRange'],
 'common/entity/attack/Coldsnap':['getLifespan','getWhipRange','isCloudSpawned','setCloudSpawned'],
 'common/entity/projectile/AmaramberArrow':['<init>','doPostHurtEffects','readAdditionalSaveData','addAdditionalSaveData'],
 'common/item/combat/AmaramberArrowItem':['createArrow','asProjectile'],
 'common/item/combat/StarfireItem':['use','asProjectile'],
 'common/item/combat/StarfireCrossbowItem':['createProjectile'],
 'common/entity/projectile/ThrownStarfire':['onHit','onHitBlock'],
 'common/block/TorreyaCampfireBlock':['useItemOn','getTicker'],
 'common/block/entity/TorreyaCampfireBlockEntity':['serverTick'],
 'common/entity/projectile/PermafrostSpit':['onHit','onHitEntity'],
 'common/entity/living/boss/golem/PermafrostSneezePhase':['canStart','tick'],
 'common/entity/attack/PermafrostCloud':['tick','hurt','getDimensions','setSmall','readAdditionalSaveData','addAdditionalSaveData'],
 'common/entity/misc/TearBomb':['<init>','explode'],
 'common/entity/misc/TearBombMinecart':['explode'],
 'common/block/TearBombBlock':['wasExploded'],
 'common/item/misc/TearBombMinecartItem':['<init>','useOn'],
 'common/item/misc/TearBombMinecartItem$1':['execute'],
 'common/entity/projectile/ThrownSpear':['onHitEntity','getItemDamage'],
 'common/entity/projectile/ThrownPungencyFruitSpear':['getDamageScale','doPostHurtEffects'],
 'common/item/combat/PungencyFruitSpearItem':['createSpear','asProjectile'],
 'common/item/combat/SpearItem':['releaseUsing'],
 'common/entity/living/monster/Stranghoul':['canBeAffected'],
 'common/entity/living/boss/monstrosity/LunarMonstrosity':['hurt','addEffect'],
 'common/registry/ESAttributes':None,
 'common/config/ESConfig':['<init>','load'],
 'common/client/handler/ESClientHandler':['onClientTick','onRenderBlockOverlay','renderDreamCatcher'],
 'common/handler/ESCommonSetupHandler':['commonSetup'],
 'neoforge/event/CommonEvents':['onLivingVisibility','onLivingChangeTarget','onLivingTick'],
}
RESOURCES=['data/eternal_starlight/enchantment/tearing.json','data/eternal_starlight/tags/entity_type/teary_immune.json','data/eternal_starlight/tags/block/unaffected_by_oblivion.json','data/eternal_starlight/tags/item/starfire_weapons.json','data/eternal_starlight/tags/item/whips.json','data/eternal_starlight/tags/entity_type/lunar_monstrosity_allies.json']

def config_snapshot():
    p=MODS.parent/'config/eternal_starlight.json'
    return dict(path=str(p),sha256=sha256(p),mobMaxTearyTicks=read_json(p).get('mobMaxTearyTicks'),scope='File snapshot only, not certification of loaded runtime configuration.') if p.exists() else dict(path=str(p),exists=False,scope='Native default remains200; no loaded configuration claim.')

def data_census():
    t=targets()['eternalstarlight'];rows=[];ids={'eternal_starlight:'+s for s in ['crystal_infection','dream_catcher','sticky','flammable','brittle','numbness','teary','starfire','oblivion']}
    def strings(x):
        if isinstance(x,str):yield x
        elif isinstance(x,list):
            for y in x:yield from strings(y)
        elif isinstance(x,dict):
            for y in x.values():yield from strings(y)
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(z.namelist()):
            if not n.startswith('data/') or not n.endswith('.json'):continue
            raw=z.read(n);hits=sorted(set(strings(json.loads(raw)))&ids)
            if hits:rows.append(dict(entry=n,sha256=byte_hash(raw),exact_ids=hits,disposition='STATUS_DELIVERY' if '/enchantment/tearing.json' in n else 'DAMAGE_TAG_FOUNDATION' if '/tags/damage_type/' in n else 'ACQUISITION_OR_ITEM_ID_NOT_STATUS_CALLBACK'))
    return dict(jar_sha256=t['sha256'],scope='Exact JSON value equality, not prefix matching item names; only Tearing is an additional data-defined status delivery.',rows=rows)

def save():
    t=targets()['eternalstarlight'];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in CLASSES.items():
            entry=ES+short+'.class';c=ClassFile(z.read(entry));names=wanted if wanted is not None else sorted({m['name'] for m in c.methods})
            rows.append(dict(id='es:status_control:'+short,mod_key='eternalstarlight',entry=entry,methods=names))
        for short,needles in [('common/registry/ESItems',['ESMobEffects.DREAM_CATCHER'])]:
            entry=ES+short+'.class';c=ClassFile(z.read(entry));names=[m['name'] for m in c.methods if any(any(s in str(i.get('operand','')) for s in needles) for i in c.instructions(m.get('code',b'')))]
            rows.append(dict(id='es:status_control:'+short,mod_key='eternalstarlight',entry=entry,methods=names))
        for n in RESOURCES:rows.append(dict(id='es:status_control:data:'+n,mod_key='eternalstarlight',entry=n))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Seven remaining status/control effects, native delivery callbacks and associated freeze/whip/Tear Bomb damage. Other shared-method branches remain later work.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/eternalstarlight-status-control.json',s);write_json(OUT/'native-evidence/eternalstarlight-status-control.json',collect(s))
    write_json(OUT/'eternalstarlight-status-config-snapshot.json',config_snapshot());write_json(OUT/'eternalstarlight-status-data-census.json',data_census())
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None)
    wanted={
      'net/minecraft/world/entity/AreaEffectCloud':['<init>','tick','addEffect'],
      'net/minecraft/world/entity/vehicle/MinecartTNT':['*'],
      'net/minecraft/world/entity/item/PrimedTnt':['tick'],
      'net/minecraft/world/level/block/TntBlock':['*'],
      'net/minecraft/world/item/enchantment/effects/ApplyMobEffect':['apply'],
      'net/minecraft/world/item/enchantment/EnchantmentHelper':['doPostAttackEffectsWithItemSource'],
      'net/minecraft/world/entity/projectile/ThrowableProjectile':['tick'],
      'net/minecraft/world/entity/LivingEntity':['canFreeze','baseTick','aiStep','getVisibilityPercent'],
      'net/minecraft/world/entity/Entity':['igniteForSeconds','igniteForTicks','baseTick','canFreeze'],
    }
    raw={};a['classes']={}
    with zipfile.ZipFile(a['path']) as z:
        for k,v in wanted.items():
            if k+'.class' in z.namelist():a['classes'][k+'.class']=v
            else:raw[k]=v
    names=MojangNames()
    with zipfile.ZipFile(CLIENT) as z:
        names.jar=z
        for k,v in raw.items():
            if v==['*']:
                c=ClassFile(z.read(names.named[k]+'.class'));raw[k]=sorted({names.member(c.name,m['name'],m['descriptor']) for m in c.methods})
    u=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][1]);u.pop('semantic_review',None)
    u['classes']={'net/neoforged/neoforge/event/entity/living/LivingEvent$LivingVisibilityEvent.class':['modifyVisibility','getVisibilityModifier']}
    r=dict(id='eternalstarlight-status-control-244',scope='Exact native AEC, projectile, TNT, enchantment effect and tag-gated fire/freeze/visibility delivery; only absent classes use raw fallback.',archives=[a,u])
    write_json(OUT/'reference-specifications/eternalstarlight-status-control-244.json',r);write_json(OUT/'reference-evidence/eternalstarlight-status-control-244.json',reference_collect(r,source_aids=True))
    s=dict(classes=raw,resources=[]);write_json(OUT/'vanilla-specifications/eternalstarlight-status-control.json',s);write_json(OUT/'vanilla-evidence/eternalstarlight-status-control.json',prepare(s))
    write_json(OUT/'reference-routing/eternalstarlight-status-control.json',dict(archive=a['path'],sha256=a['sha256'],absent_entries=[k+'.class' for k in raw]))
    javap=Path('C:/Program Files/Java/jdk-21/bin/javap.exe');args=['-p','-v','-classpath',t['path'],*[ES.replace('/','.')+x for x in ['common.mixin.LivingEntityMixin','common.mixin.EntityMixin','common.mixin.BlockStateBaseMixin','common.mixin.TntBlockMixin','common.mixin.client.MinecraftMixin','neoforge.event.CommonEvents']]]
    text=subprocess.check_output([str(javap),*args],encoding='utf-8');p=OUT/'annotation-evidence/eternalstarlight-status-control-javap.txt';p.write_text(text,encoding='utf-8')
    write_json(OUT/'annotation-evidence/eternalstarlight-status-control-javap.json',dict(tool=str(javap),tool_sha256=sha256(javap),jar_sha256=t['sha256'],arguments=args,output_file=p.relative_to(OUT).as_posix(),output_sha256=sha256(p),scope='Mixin targets and event subscriptions, not successful runtime application proof.'))
    print('Status/control evidence saved')
if __name__=='__main__':save()
