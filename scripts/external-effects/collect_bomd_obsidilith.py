from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_bomd_foundation import targets,KEY,PKG

CLASSES={**{'entity/custom/obsidilith/'+n:None for n in ['ObsidilithEntity','ShieldDamageHandler','PillarAction','ObsidilithMoveLogic','BurstAction','WaveAction','SpikeAction','AnvilAction','RiftBurst','ObsidilithUtils']},'block/custom/ObsidilithRuneBlock':None,'block/BMDBlocks':['<clinit>'],'packet/BMDPackets':['registerPackets'],'packet/custom/SendDeltaMovementS2CPacket':None,'util/BMDUtils':['findGroundBelow'],'capability/util/BMDCapabilities':['getPlayerPositions'],'neoforge/platform/NeoCapabilityHelper':['getPlayerPositions'],'neoforge/attachment/BMDAttachments':None,'neoforge/event/NeoEvents':['onPlayerTick']}

def save():
    t=targets()[KEY];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in CLASSES.items():
            n=PKG+short+'.class';c=ClassFile(z.read(n));names=wanted or sorted({m['name'] for m in c.methods})
            if short=='block/BMDBlocks':names+=sorted(m['name'] for m in c.methods if m['name'].startswith('lambda$static$'))
            rows.append(dict(id='bomd:obsidilith:'+short,mod_key=KEY,entry=n,methods=names))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Obsidilith native rune shield, rift damage/control and anvil/death explosions; ordinary utility/cosmetics excluded semantically.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/bomd-obsidilith.json',s);write_json(OUT/'native-evidence/bomd-obsidilith.json',collect(s))
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None);a['classes']={'net/minecraft/world/entity/Entity.class':['baseTick','setRemainingFireTicks'],'net/minecraft/world/entity/LivingEntity.class':['knockback']}
    dep=MODS/'CerbonsAPI-NeoForge-1.21-1.3.0.jar';prefix='com/cerbon/cerbons_api/'
    b=dict(path=str(dep),sha256=sha256(dep),classes={prefix+n+'.class':names for n,names in {'api/general/event/Event':['*'],'api/static_utilities/CapabilityUtils':['getLevelEventScheduler'],'neoforge/platform/NeoForgeCapabilityHelper':['getLevelEventScheduler'],'neoforge/attachment/saved_data/LevelEventScheduler':['*'],'neoforge/event/NeoForgeEvents':['onLevelTick'],'api/static_utilities/MathUtils':['buildBlockCircle','unNormedDirection'],'api/network/Dispatcher':['sendToClient']}.items()})
    r=dict(id='bomd-obsidilith-244',scope='Installed world scheduler delivery/event predicate, block-circle geometry, native five-tick fire and knockback semantics.',archives=[a,b]);write_json(OUT/'reference-specifications/bomd-obsidilith-244.json',r);write_json(OUT/'reference-evidence/bomd-obsidilith-244.json',reference_collect(r,source_aids=True))
    tool=Path('C:/Program Files/Java/jdk-21/bin/javap.exe');args=['-p','-v','-classpath',str(dep),'com.cerbon.cerbons_api.neoforge.event.NeoForgeEvents'];s=subprocess.check_output([str(tool),*args],encoding='utf-8');p=OUT/'annotation-evidence/bomd-world-scheduler-javap.txt';p.write_text(s,encoding='utf-8')
    write_json(p.with_suffix('.json'),dict(tool=str(tool),tool_sha256=sha256(tool),jar_sha256=sha256(dep),arguments=args,output_file=p.relative_to(OUT).as_posix(),output_sha256=sha256(p),scope='Native SubscribeEvent declaration only; runtime dispatch not executed.'))
    print('Obsidilith witnesses',len(rows))

if __name__=='__main__':save()
