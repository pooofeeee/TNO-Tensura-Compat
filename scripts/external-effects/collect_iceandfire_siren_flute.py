"""Siren Flute component path and exact native tick entry witnesses."""
from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_iceandfire_foundation import IAF,targets

FULL=['item/SirenFluteItem','util/attachment/NeedUpdateData','util/attachment/IafEntityAttachment','neoforge/IafAttachments']
LIMITED={'data/component/MiscData':['<init>','<clinit>','get','tick','setLoveTicks','getLoveTicks','createLoveParticles'], 'impl/ComponentManager':['getMiscData'],'impl/neoforge/ComponentManagerImpl':['getMiscData'],'entity/util/dragon/DragonUtils':['isAlive']}

def census():
    rows=[]
    with zipfile.ZipFile(targets()['iceandfire']['path']) as z:
        for entry in z.namelist():
            if not entry.endswith('.class'):continue
            c=ClassFile(z.read(entry))
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if any(x in str(i.get('operand')) for x in ['MiscData.loveTicks','MiscData.setLoveTicks(','MiscData.getLoveTicks(','MiscData.tick(','IafEntityAttachment.tick(','IafAttachments.MISC_DATA'])]
                if hits:rows.append(dict(entry=entry,method=m['name'],descriptor=m['descriptor'],hits=hits))
    return dict(schema='tno.external_effects.iaf_flute_callers.v1',jar_sha256=targets()['iceandfire']['sha256'],rows=rows)

def save():
    rows=[]
    with zipfile.ZipFile(targets()['iceandfire']['path']) as z:
        for short in FULL+list(LIMITED):
            c=ClassFile(z.read(IAF+short+'.class'));names=sorted({m['name'] for m in c.methods}) if short in FULL else list(LIMITED[short])
            if short=='data/component/MiscData':names += [m['name'] for m in c.methods if m['name'].startswith('lambda$static$')]
            rows.append(dict(id='iaf:siren-flute:'+short,mod_key='iceandfire',entry=IAF+short+'.class',methods=names))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Flute love timer/attachment path only; scepter/lunge/other attachments remain separate pending mechanics.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/iceandfire-siren-flute.json',s);write_json(OUT/'native-evidence/iceandfire-siren-flute.json',collect(s));write_json(OUT/'iceandfire-flute-callers.json',census())
    old=read_json(OUT/'reference-specifications/vv-loader-244.json');a=dict(old['archives'][1]);a.pop('semantic_review',None);a['classes']={'net/neoforged/neoforge/event/EventHooks.class':['fireEntityTickPost'],'net/neoforged/neoforge/attachment/AttachmentType$Builder.class':['serialize','sync','copyOnDeath','build']}
    client=dict(old['archives'][0]);client.pop('semantic_review',None);client['classes']={'net/minecraft/server/level/ServerLevel.class':['tickNonPassenger','tickPassenger'],'net/minecraft/client/multiplayer/ClientLevel.class':['tickNonPassenger','tickPassenger']}
    ref=dict(id='iceandfire-siren-flute-244',scope='Actual NeoForge Post event entry and attachment declarations; no full generic attachment-system review.',archives=[client,a])
    write_json(OUT/'reference-specifications/iceandfire-siren-flute-244.json',ref);write_json(OUT/'reference-evidence/iceandfire-siren-flute-244.json',reference_collect(ref,source_aids=True))
    javap=Path('C:/Program Files/Java/jdk-21/bin/javap.exe');t=targets()['iceandfire'];args=['-p','-v','-classpath',t['path'],'com.iafenvoy.iceandfire.neoforge.IafAttachments']
    output=subprocess.check_output([str(javap),*args],encoding='utf-8');p=OUT/'annotation-evidence/iceandfire-attachments-javap.txt';p.write_text(output,encoding='utf-8')
    write_json(OUT/'annotation-evidence/iceandfire-attachments-javap.json',dict(tool=str(javap),tool_sha256=sha256(javap),jar_sha256=t['sha256'],arguments=args,output_file=p.relative_to(OUT).as_posix(),output_sha256=sha256(p)))
    print('Flute native/reference witnesses saved')

if __name__=='__main__':save()
