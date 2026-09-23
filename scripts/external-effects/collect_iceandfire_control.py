from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_iceandfire_foundation import IAF,COMPAT,targets
CLASSES=['item/ChainItem','data/component/ChainData','entity/ChainTieEntity','neoforge/IafAttachments','impl/neoforge/ComponentManagerImpl','item/DragonFluteItem','entity/PixieEntity','entity/PixieChargeEntity','entity/ai/PixieAIStealGoal','entity/ai/PixieAIPickupItemGoal','item/PixieWandItem','item/DragonFleshItem','item/CannoliItem','compat/delight/DelightFoodItem','event/ServerEvents']

def census():
    t=targets()['iceandfire'];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for s in CLASSES:
            entry=IAF+s+'.class';c=ClassFile(z.read(entry))
            for m in c.methods:
                h=[i for i in c.instructions(m.get('code',b'')) if any(n in str(i.get('operand','')) for n in ['.hurt(','.heal(','.addEffect(','.attachChain(','.removeChain(','.clearChains(','.setDeltaMovement(','.addFreshEntity(','.onHearFlute('])]
                if h:rows.append(dict(entry=entry,method=m['name'],descriptor=m['descriptor'],hits=h))
    return dict(jar_sha256=t['sha256'],rows=rows)

def save():
    ts=targets();rows=[]
    with zipfile.ZipFile(ts['iceandfire']['path']) as z:
        for s in CLASSES:
            rows.append(dict(id='iaf:control:'+s,mod_key='iceandfire',entry=IAF+s+'.class',methods=sorted({m['name'] for m in ClassFile(z.read(IAF+s+'.class')).methods})))
        c=ClassFile(z.read(IAF+'registry/IafItems.class'));names=['<clinit>']+[m['name'] for m in c.methods if any('MobEffects.' in str(i.get('operand','')) for i in c.instructions(m.get('code',b'')))]
        rows.append(dict(id='iaf:control:IafItems',mod_key='iceandfire',entry=IAF+'registry/IafItems.class',methods=names))
        for s in ['entity/DragonBaseEntity','entity/AmphithereEntity']:rows.append(dict(id='iaf:control:'+s,mod_key='iceandfire',entry=IAF+s+'.class',methods=['onHearFlute']))
    for key in ['iceandfire',COMPAT]:
        with zipfile.ZipFile(ts[key]['path']) as z:
            for n in sorted(z.namelist()):
                if n.endswith('.json') and '/tags/' in n and '/worldgen/' not in n and any(s in n for s in ['chain','pixie']):rows.append(dict(id=key+':control-data:'+n,mod_key=key,entry=n))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Chain/flute/Pixie/food and native lightning armor admission.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/iceandfire-control.json',s);write_json(OUT/'native-evidence/iceandfire-control.json',collect(s));write_json(OUT/'iceandfire-control-census.json',census())
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None)
    a['classes']={'net/minecraft/world/entity/projectile/AbstractHurtingProjectile.class':['tick','<init>'],'net/minecraft/world/entity/LivingEntity.class':['eat','addEatEffect']}
    with zipfile.ZipFile(a['path']) as z:assert 'net/minecraft/world/entity/decoration/BlockAttachedEntity.class' not in z.namelist()
    arch=MODS/'architectury-13.0.8-neoforge.jar'
    r=dict(id='iceandfire-control-244',scope='Native Pixie projectile impact, food status and actual Architectury IncomingDamage/Death event bridge.',archives=[a,dict(path=str(arch),sha256=sha256(arch),classes={'dev/architectury/event/forge/EventHandlerImplCommon.class':['event']})])
    write_json(OUT/'reference-specifications/iceandfire-control-244.json',r);write_json(OUT/'reference-evidence/iceandfire-control-244.json',reference_collect(r,source_aids=True))
    raw=dict(classes={'net/minecraft/world/entity/decoration/BlockAttachedEntity':['hurt','tick']},resources=[])
    write_json(OUT/'vanilla-specifications/iceandfire-control.json',raw);write_json(OUT/'vanilla-evidence/iceandfire-control.json',prepare(raw))
    write_json(OUT/'reference-routing/iceandfire-control.json',dict(archive=a['path'],sha256=a['sha256'],absent_entries=['net/minecraft/world/entity/decoration/BlockAttachedEntity.class']))
    javap=Path('C:/Program Files/Java/jdk-21/bin/javap.exe');args=['-p','-v','-classpath',str(arch)+';'+ts['iceandfire']['path'],'dev.architectury.event.forge.EventHandlerImplCommon','com.iafenvoy.iceandfire.neoforge.IafAttachments']
    text=subprocess.check_output([str(javap),*args],encoding='utf-8');p=OUT/'annotation-evidence/iceandfire-control-javap.txt';p.write_text(text,encoding='utf-8')
    write_json(OUT/'annotation-evidence/iceandfire-control-javap.json',dict(tool=str(javap),tool_sha256=sha256(javap),arguments=args,output_file=p.relative_to(OUT).as_posix(),output_sha256=sha256(p),scope='Actual SubscribeEvent signatures; runtime composition remains untested.'))
    print('Control/Pixie/food witnesses saved')
if __name__=='__main__':save()
