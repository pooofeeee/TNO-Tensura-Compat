from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_bomd_foundation import targets,KEY,PKG

CLASSES={**{'entity/custom/gauntlet/'+n:None for n in ['GauntletEntity','GauntletHitboxes','GauntletGoalHandler','GauntletMoveLogic','GauntletAttacks','PunchAction','SwirlPunchAction','LaserAction','BlindnessAction','ServerGauntletDeathHandler','GauntletClientEnergyShieldHandler','GauntletBlindnessIndicatorParticles']},'packet/custom/ChangeHitboxS2CPacket':None,'packet/custom/BlindnessS2CPacket':None,'util/BMDUtils':['findEntitiesInLine'],'util/VanillaCopiesServer':['destroyBlocks']}

def save():
    t=targets()[KEY];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in CLASSES.items():
            n=PKG+short+'.class';c=ClassFile(z.read(n));names=wanted or sorted({m['name'] for m in c.methods})
            if short=='util/BMDUtils':names+=sorted(m['name'] for m in c.methods if m['name'].startswith('lambda$findEntitiesInLine$'))
            rows.append(dict(id='bomd:gauntlet:'+short,mod_key=KEY,entry=n,methods=names))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Gauntlet concrete hitbox admission, native combat callbacks and equipment-independent source/delivery paths.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/bomd-gauntlet.json',s);write_json(OUT/'native-evidence/bomd-gauntlet.json',collect(s))
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None);a['classes']={'net/minecraft/world/entity/Entity.class':['addDeltaMovement','baseTick'],'net/minecraft/world/damagesource/DamageSource.class':['getSourcePosition'],'net/minecraft/world/level/block/BaseFireBlock.class':['entityInside','getState'],'net/minecraft/world/level/block/FireBlock.class':['<init>'],'net/minecraft/world/level/Explosion.class':['finalizeExplosion']}
    dep=MODS/'CerbonsAPI-NeoForge-1.21-1.3.0.jar';prefix='com/cerbon/cerbons_api/'
    names=['api/general/event/EventSeries','mixin/multipart_entities/ProjectileMixin','mixin/multipart_entities/client/MultiplayerGameModeMixin','packet/custom/MultipartEntityInteractionC2SPacket','api/multipart_entities/entity/MultipartAwareEntity','api/multipart_entities/entity/EntityBounds','api/multipart_entities/util/CompoundOrientedBox','api/multipart_entities/util/OrientedBox']
    b=dict(path=str(dep),sha256=sha256(dep),classes={prefix+n+'.class':['*'] for n in names})
    with zipfile.ZipFile(dep) as z:
        b['resources']=[n for n in z.namelist() if n.endswith('.mixins.json')]+['META-INF/services/com.cerbon.cerbons_api.platform.services.ICapabilityHelper']
    r=dict(id='bomd-gauntlet-244',scope='Native CerbonsAPI incoming part delivery and EventSeries, source-position and raw motion references.',archives=[a,b]);write_json(OUT/'reference-specifications/bomd-gauntlet-244.json',r);write_json(OUT/'reference-evidence/bomd-gauntlet-244.json',reference_collect(r,source_aids=True))
    tool=Path('C:/Program Files/Java/jdk-21/bin/javap.exe');args=['-p','-v','-classpath',str(dep),*[prefix.replace('/','.')+n.replace('/','.') for n in names if '/mixin/' in '/'+n]];s=subprocess.check_output([str(tool),*args],encoding='utf-8');p=OUT/'annotation-evidence/bomd-multipart-javap.txt';p.write_text(s,encoding='utf-8')
    write_json(p.with_suffix('.json'),dict(tool=str(tool),tool_sha256=sha256(tool),jar_sha256=sha256(dep),arguments=args,output_file=p.relative_to(OUT).as_posix(),output_sha256=sha256(p),scope='Installed multipart mixin annotation declarations only; runtime application not executed.'))
    v=dict(classes={'net/minecraft/world/level/block/SoulFireBlock':['<init>'],'net/minecraft/world/entity/ai/targeting/TargetingConditions':['test'],'net/minecraft/world/level/EntityGetter':['getNearbyPlayers']},resources=['data/minecraft/damage_type/explosion.json','data/minecraft/damage_type/on_fire.json','data/minecraft/damage_type/in_fire.json'])
    write_json(OUT/'vanilla-specifications/bomd-gauntlet.json',v);write_json(OUT/'vanilla-evidence/bomd-gauntlet.json',prepare(v))
    print('Gauntlet witnesses',len(rows))

if __name__=='__main__':save()
