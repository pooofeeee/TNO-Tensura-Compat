from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_iceandfire_foundation import IAF,targets
CLASSES=['entity/GhostEntity','entity/ai/GhostAIChargeGoal','entity/GhostSwordEntity','item/ability/SummonGhostSwordAbility','item/tool/GhostSwordItem','mixin/LivingEntityMixin','item/block/entity/GhostChestBlockEntity','entity/TrollEntity','item/tool/TrollWeaponItem','item/armor/TrollArmorItem','event/ServerEvents','IceAndFire']
def census():
    t=targets()['iceandfire'];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        entries=z.namelist();myrmex=[n for n in entries if 'myrmex' in n.lower()]
        for entry in sorted(n for n in entries if n.endswith('.class')):
            if not any(s in entry for s in ['Ghost','Troll','ServerEvents','LivingEntityMixin']):continue
            c=ClassFile(z.read(entry))
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if any(s in str(i.get('operand','')) for s in ['.hurt(','.heal(','.addEffect(','.explode(','.doHurtTarget(','.remove(','.isInvulnerableTo(','.SUMMON_GHOST_SWORD'])]
                if hits:rows.append(dict(entry=entry,method=m['name'],descriptor=m['descriptor'],hits=hits))
        classes=[n for n in entries if n.endswith('.class')];myrmex_constants=[n for n in classes if b'myrmex' in z.read(n).lower()]
    return dict(jar_sha256=t['sha256'],rows=rows,myrmex_named_entries=myrmex,myrmex_class_constants=myrmex_constants,scope='Ghost/Troll primitive callers, installed whole-JAR Myrmex name and class-constant absence check.')
def save():
    with zipfile.ZipFile(targets()['iceandfire']['path']) as z:
        rows=[]
        for s in CLASSES:
            names=sorted({m['name'] for m in ClassFile(z.read(IAF+s+'.class')).methods})
            if s=='event/ServerEvents':names=['onEntityDamage']
            rows.append(dict(id='iaf:ghost-troll:'+s,mod_key='iceandfire',entry=IAF+s+'.class',methods=names))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Ghost/Troll combat and related special gear only.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/iceandfire-ghost-troll.json',s);write_json(OUT/'native-evidence/iceandfire-ghost-troll.json',collect(s));write_json(OUT/'iceandfire-ghost-troll-census.json',census())
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None);a['classes']={'net/minecraft/world/entity/projectile/AbstractArrow.class':['<init>','tick','canHitEntity','findHitEntity','doPostHurtEffects'],'net/minecraft/world/entity/Mob.class':['doHurtTarget'],'net/minecraft/world/entity/player/Player.class':['actuallyHurt']}
    uranus=MODS/'uranus-2.4-1.21.1-neoforge.jar'
    a['classes']['net/minecraft/world/entity/player/Player.class'].append('attack')
    u=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][1]);u.pop('semantic_review',None);u['classes']={'net/neoforged/neoforge/common/extensions/IItemExtension.class':['onEntitySwing']}
    r=dict(id='iceandfire-ghost-troll-244',scope='Inherited Ghost arrow/mob hit and real Uranus armor damage callback only.',archives=[a,u,dict(path=str(uranus),sha256=sha256(uranus),classes={'com/iafenvoy/uranus/event/LivingEntityEvents.class':['*'],'com/iafenvoy/uranus/mixin/LivingEntityMixin.class':['*'],'com/iafenvoy/uranus/mixin/PlayerEntityMixin.class':['*']})])
    write_json(OUT/'reference-specifications/iceandfire-ghost-troll-244.json',r);write_json(OUT/'reference-evidence/iceandfire-ghost-troll-244.json',reference_collect(r,source_aids=True))
    with zipfile.ZipFile(a['path']) as z:assert 'net/minecraft/world/effect/RegenerationMobEffect.class' not in z.namelist()
    raw=dict(classes={'net/minecraft/world/effect/RegenerationMobEffect':['applyEffectTick','shouldApplyEffectTickThisTick']},resources=[])
    write_json(OUT/'vanilla-specifications/iceandfire-ghost-troll.json',raw);write_json(OUT/'vanilla-evidence/iceandfire-ghost-troll.json',prepare(raw))
    write_json(OUT/'reference-routing/iceandfire-ghost-troll.json',dict(archive=a['path'],sha256=a['sha256'],absent_entries=['net/minecraft/world/effect/RegenerationMobEffect.class']))
    javap=Path('C:/Program Files/Java/jdk-21/bin/javap.exe');args=['-p','-v','-classpath',str(uranus)+';'+targets()['iceandfire']['path'],'com.iafenvoy.uranus.mixin.PlayerEntityMixin','com.iafenvoy.iceandfire.mixin.LivingEntityMixin']
    output=subprocess.check_output([str(javap),*args],encoding='utf-8');p=OUT/'annotation-evidence/iceandfire-ghost-troll-javap.txt';p.write_text(output,encoding='utf-8')
    write_json(OUT/'annotation-evidence/iceandfire-ghost-troll-javap.json',dict(tool=str(javap),tool_sha256=sha256(javap),arguments=args,output_file=p.relative_to(OUT).as_posix(),output_sha256=sha256(p),scope='Static injection declarations, not successful runtime composition proof.'))
    print('Ghost/Troll witnesses saved')
if __name__=='__main__':save()
