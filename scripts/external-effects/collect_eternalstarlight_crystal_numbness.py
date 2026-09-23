"""Exact native status/debt witnesses; no game or production execution."""
from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_eternalstarlight_foundation import ES, targets

CLASSES={
 'common/effect/CrystalInfectionEffect':None,
 'common/entity/attack/CrystalCluster':None,
 'common/item/combat/CrystalGreatswordItem':['postHurtEnemy','getAttackDamageBonus'],
 'common/item/combat/CrystalCrossbowItem':['createProjectile','shootProjectile'],
 'common/block/DesertFlowerBlock':['<init>'],
 'common/handler/ESCommonHandler':['onAllowLivingHurt','onModifyLivingActualHurtDamage','onModifyLivingHurtDamage','onProjectileImpact'],
 'common/mixin/LivingEntityMixin':['tickEffects','eat'],
 'common/util/ESEntityUtil':['shouldHarm'],
 'common/util/ESAccessoryUtil':['getActiveAccessoriesOnArmors','getActiveAccessories','getAccessories'],
 'common/platform/EntityDataAttachment':['setData'],
 'common/platform/ESPlatform':['registerDataAttachment'],
 'neoforge/platform/ESNeoPlatform':['registerDataAttachment'],
 'neoforge/platform/ESNeoPlatform$1':None,
 'common/registry/ESDataAttachments':None,
 'common/registry/ESFoods':None,
}

def attachment_census():
    t=targets()['eternalstarlight'];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for entry in sorted(n for n in z.namelist() if n.endswith('.class')):
            raw=z.read(entry);c=ClassFile(raw)
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if any('ESDataAttachments.'+s in str(i.get('operand','')) for s in ['NUMBNESS_DAMAGE','TEARY_TICKS','ARROW_TYPE'])]
                if hits:rows.append(dict(entry=entry,entry_sha256=byte_hash(raw),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits))
    return dict(jar_sha256=t['sha256'],scope='All installed ES class method field accesses to debt, Teary budget and arrow identity; reflective/external modifications not negative-certified.',rows=rows)

def save():
    t=targets()['eternalstarlight'];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in CLASSES.items():
            entry=ES+short+'.class';c=ClassFile(z.read(entry));names=wanted if wanted is not None else sorted({m['name'] for m in c.methods})
            rows.append(dict(id='es:crystal_numbness:'+short,mod_key='eternalstarlight',entry=entry,methods=names))
        for short,needles in [('common/registry/ESBlocks',['ESMobEffects.CRYSTAL_INFECTION']),('common/registry/ESItems',['CrystalGreatswordItem','CrystalCrossbowItem','ESFoods.SILVER_PUNGENCY_FRUIT'])]:
            entry=ES+short+'.class';c=ClassFile(z.read(entry));names=['<clinit>']+[m['name'] for m in c.methods if m['name']!='<clinit>' and any(any(s in str(i.get('operand','')) for s in needles) for i in c.instructions(m.get('code',b'')))]
            rows.append(dict(id='es:crystal_numbness:'+short,mod_key='eternalstarlight',entry=entry,methods=names))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Crystal Infection, Numbness and shared admission. Other branches in shared methods remain later family work.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/eternalstarlight-crystal-numbness.json',s);write_json(OUT/'native-evidence/eternalstarlight-crystal-numbness.json',collect(s))
    write_json(OUT/'eternalstarlight-status-attachment-census.json',attachment_census())
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None)
    wanted={
      'net/minecraft/world/entity/LivingEntity':['tickEffects','actuallyHurt','getDamageAfterArmorAbsorb','getDamageAfterMagicAbsorb','addEffect','canBeAffected','removeEffect','removeAllEffects','removeEffectsCuredBy','onEffectRemoved','onEffectAdded','onEffectUpdated','eat','addEatEffect'],
      'net/minecraft/world/effect/MobEffect':['addAttributeModifiers','removeAttributeModifiers'],
      'net/minecraft/world/effect/MobEffect$AttributeTemplate':['create'],
      'net/minecraft/world/effect/MobEffectInstance':['tick','update'],
      'net/minecraft/world/entity/player/Player':['attack','actuallyHurt'],
      'net/minecraft/world/item/ItemStack':['postHurtEnemy','hurtEnemy'],
      'net/minecraft/world/item/SwordItem':['hurtEnemy','postHurtEnemy'],
      'net/minecraft/world/item/CrossbowItem':['createProjectile'],
      'net/minecraft/world/entity/projectile/AbstractArrow':['tick','onHitEntity'],
      'net/minecraft/world/entity/projectile/FireworkRocketEntity':['tick','onHit','onHitEntity','dealExplosionDamage'],
      'net/minecraft/world/level/block/FlowerBlock':['<init>','makeEffectList','getSuspiciousEffects'],
      'net/minecraft/world/item/SuspiciousStewItem':['finishUsingItem'],
      'net/minecraft/world/item/component/SuspiciousStewEffects$Entry':['createEffectInstance'],
    }
    raw={};a['classes']={}
    with zipfile.ZipFile(a['path']) as z:
        for k,v in wanted.items():
            if k+'.class' in z.namelist():a['classes'][k+'.class']=v
            else:raw[k]=v
    u=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][1]);u.pop('semantic_review',None)
    u['classes']={'net/neoforged/neoforge/common/CommonHooks.class':['onLivingDamagePre','onLivingDamagePost','canMobEffectBeApplied'],'net/neoforged/neoforge/event/entity/living/LivingDamageEvent$Pre.class':['getNewDamage','setNewDamage'],'net/neoforged/neoforge/event/entity/living/LivingDamageEvent$Post.class':['<init>','getNewDamage']}
    r=dict(id='eternalstarlight-crystal-numbness-244',scope='Exact loader effect application/tick, damage debt event position, legitimate item/projectile delivery; raw fallback only for absent patched entries.',archives=[a,u])
    write_json(OUT/'reference-specifications/eternalstarlight-crystal-numbness-244.json',r);write_json(OUT/'reference-evidence/eternalstarlight-crystal-numbness-244.json',reference_collect(r,source_aids=True))
    s=dict(classes=raw,resources=[]);write_json(OUT/'vanilla-specifications/eternalstarlight-crystal-numbness.json',s);write_json(OUT/'vanilla-evidence/eternalstarlight-crystal-numbness.json',prepare(s))
    write_json(OUT/'reference-routing/eternalstarlight-crystal-numbness.json',dict(archive=a['path'],sha256=a['sha256'],absent_entries=[k+'.class' for k in raw]))
    javap=Path('C:/Program Files/Java/jdk-21/bin/javap.exe');args=['-p','-v','-classpath',t['path'],*[ES.replace('/','.')+x for x in ['common.mixin.LivingEntityMixin','common.registry.ESBlocks','common.registry.ESItems','common.registry.ESFoods']]]
    output=subprocess.check_output([str(javap),*args],encoding='utf-8')
    # Keep full mixin declarations but only relevant registry bootstrap lines, not
    # thousands of unrelated cosmetic/block/item registrations in tracked evidence.
    lines=output.splitlines();keep=set();end=next(i for i,l in enumerate(lines) if 'public class '+ES.replace('/','.')+'common.registry.ESBlocks' in l)
    keep.update(range(end))
    for row in rows:
        if '/registry/' not in row['entry']:continue
        simple=Path(row['entry']).stem
        names=[n for n in row['methods'] if n.startswith('lambda$')]
        for i,l in enumerate(lines):
            if any(simple+'.'+n+':' in l for n in names):keep.update(range(max(0,i-4),min(len(lines),i+5)))
    excerpt='Reproducible javap excerpts; original one-based line numbers. Registry code is separately pinned.\n'+'\n'.join((str(i+1)+': '+lines[i]).rstrip() for i in sorted(keep))+'\n'
    p=OUT/'annotation-evidence/eternalstarlight-crystal-numbness-javap.txt';p.write_text(excerpt,encoding='utf-8')
    write_json(OUT/'annotation-evidence/eternalstarlight-crystal-numbness-javap.json',dict(tool=str(javap),tool_sha256=sha256(javap),jar_sha256=t['sha256'],arguments=args,full_output_sha256=byte_hash(output.encode('utf-8')),output_file=p.relative_to(OUT).as_posix(),output_sha256=sha256(p),scope='Mixin target/order and selected registry lambda wiring; not runtime application proof.'))
    print('Crystal/Numbness evidence saved')

if __name__=='__main__':save()
