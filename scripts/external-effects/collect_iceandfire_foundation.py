"""R2g1 installed registry/source foundation; caller census is not semantic completion."""
from collections import defaultdict
from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from vanilla_reference import CLIENT

START='86b6e670819be918b2df9ddcd73bf81b729282fc'
CP='R2g1-native-source-foundation'
IAF='com/iafenvoy/iceandfire/'
COMPAT='tensura_iaf-neoforge-2.0.0.1'
FACTORY=IAF+'registry/IafDamageTypes'
FULL=['registry/IafDamageTypes','registry/IafDamageTypes$CustomEntityDamageSource','registry/IafDamageTypes$CustomIndirectEntityDamageSource','registry/IafStatusEffects','registry/IafDragonTypes','IceAndFire','neoforge/IceAndFireNeoForge','entity/FireDragonChargeEntity','entity/IceDragonChargeEntity','entity/LightningDragonChargeEntity']
LIMITED={'entity/util/dragon/IafDragonDestructionManager':['getDamageSource'], 'entity/DragonChargeEntity':['onHit','canHitMob','hurt'], 'entity/DragonBaseEntity':['getRidingPlayer','getControllingPassenger'], 'entity/GorgonEntity':['aiStep'], 'item/GorgonHeadItem':['releaseUsing'], 'item/ability/DamageBonusAbility':['active']}


def targets():
    inv=read_json(OUT/'jar-inventory.json')
    return {t['key']:t for t in inv['targets']+inv['compat_candidates']}


def caller_census():
    t=targets()['iceandfire'];assert sha256(t['path'])==t['sha256'];calls=[];status=[];classes=0
    with zipfile.ZipFile(t['path']) as jar:
        for entry in sorted(n for n in jar.namelist() if n.endswith('.class')):
            c=ClassFile(jar.read(entry));classes+=1
            for m in c.methods:
                body=list(c.instructions(m.get('code',b'')))
                hits=[i for i in body if isinstance(i.get('operand'),str) and i['opcode'] in ['0xb6','0xb7','0xb8','0xb9'] and i['operand'].startswith(FACTORY+'.') and '.<init>' not in i['operand'] and not entry.startswith(FACTORY)]
                if hits:calls.append(dict(entry=entry,entry_sha256=byte_hash(jar.read(entry)),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),calls=hits,delivery_review='PENDING_FAMILY_SEMANTICS'))
                hits=[i for i in body if isinstance(i.get('operand'),str) and i['opcode']=='0xb2' and i['operand'].startswith(IAF+'registry/IafStatusEffects.') and not entry.startswith(IAF+'registry/IafStatusEffects')]
                if hits:status.append(dict(entry=entry,method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),references=hits,delivery_review='PENDING_FAMILY_SEMANTICS'))
    return dict(schema='tno.external_effects.iaf_source_census.v1',baseline=BASELINE,jar_sha256=t['sha256'],parsed_classes=classes,factory_callers=calls,status_references=status,note='Every installed class parsed. Direct invocation/field-reference census only; indirect/dynamic/helper delivery and native eligibility remain family review work.')


def tag_census():
    t=targets()['iceandfire'];loader=next(a for a in read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'] if a['path'].endswith('universal.jar'))
    archives=[dict(path=str(CLIENT),sha256=sha256(CLIENT)),dict(path=loader['path'],sha256=loader['sha256']),dict(path=t['path'],sha256=t['sha256'])]
    assert archives[0]['sha256']=='499f6897d1837516680f3114072d8106e11c9adcd933fe5cf051b551089b0c99'
    tags={};resources=[];declarations=[]
    for a in archives:
        assert sha256(a['path'])==a['sha256']
        with zipfile.ZipFile(a['path']) as jar:
            for entry in sorted(jar.namelist()):
                if entry.startswith('data/') and '/tags/damage_type/' in entry and entry.endswith('.json'):
                    data=jar.read(entry);obj=json.loads(data);tag=entry.split('/')[1]+':'+entry.split('/tags/damage_type/')[1][:-5]
                    resources.append(dict(archive_sha256=a['sha256'],entry=entry,sha256=byte_hash(data),data=obj))
                    if obj.get('replace'):tags[tag]=[]
                    tags.setdefault(tag,[]).extend(obj.get('values',[]))
                elif a['path']==t['path'] and entry.startswith('data/iceandfire/damage_type/') and entry.endswith('.json'):
                    data=jar.read(entry);declarations.append(dict(id='iceandfire:'+Path(entry).stem,entry=entry,sha256=byte_hash(data),data=json.loads(data)))
    def members(tag,seen=()):
        if tag in seen:return set()
        result=set()
        for v in tags.get(tag,[]):
            v=v['id'] if isinstance(v,dict) else v
            result|=members(v[1:],seen+(tag,)) if v.startswith('#') else {v}
        return result
    for d in declarations:d['tags']=sorted(k for k in tags if d['id'] in members(k))
    return dict(schema='tno.external_effects.iaf_damage_tags.v1',baseline=BASELINE,archives=archives,declarations=declarations,tag_resources=resources,scope='Raw Minecraft1.21.1 plus exact installed NeoForge21.1.244 plus installed IceAndFireCE beta15 contributions. Additional mod/datapack mutations and runtime pack order are not inferred. JSON effects burning/freezing is not damage-tag membership.')


def save():
    ts=targets();specs=[]
    with zipfile.ZipFile(ts['iceandfire']['path']) as jar:
        for short in FULL+list(LIMITED):
            entry=IAF+short+'.class';c=ClassFile(jar.read(entry));names=sorted({m['name'] for m in c.methods}) if short in FULL else LIMITED[short]
            specs.append(dict(id='iaf:'+short,mod_key='iceandfire',entry=entry,methods=names))
        for entry in ['iceandfire.mixins.json','META-INF/neoforge.mods.toml']+[n for n in jar.namelist() if n.startswith('data/') and ('/damage_type/' in n)]:
            specs.append(dict(id='iaf:data:'+entry,mod_key='iceandfire',entry=entry))
    # Pin complete compat class bodies and registration config. Semantic coverage
    # is explicitly narrower than witness availability.
    with zipfile.ZipFile(ts[COMPAT]['path']) as jar:
        for entry in sorted(n for n in jar.namelist() if n.endswith('.class')):
            c=ClassFile(jar.read(entry));specs.append(dict(id='iafcompat:'+c.name,mod_key=COMPAT,entry=entry,methods=sorted({m['name'] for m in c.methods})))
        for entry in ['tensura_iaf.mixins.json','META-INF/neoforge.mods.toml']:
            specs.append(dict(id='iafcompat:data:'+entry,mod_key=COMPAT,entry=entry))
    spec=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='R2g1 source/registry foundation and explicit direct-compat witnesses. Family mechanics are pending; availability of a witness is not a completed semantic review.',evidence_specifications=specs)
    result=collect(spec);write_json(OUT/'native-specifications/iceandfire-foundation.json',spec);write_json(OUT/'native-evidence/iceandfire-foundation.json',result)
    write_json(OUT/'iceandfire-source-census.json',caller_census());write_json(OUT/'iceandfire-damage-tag-census.json',tag_census())
    # javap exposes annotation attributes not decoded by the existing ClassFile
    # reader. Pin its output separately; do not alter that accepted parser.
    with zipfile.ZipFile(ts[COMPAT]['path']) as jar:config=json.loads(jar.read('tensura_iaf.mixins.json'))
    javap=Path('C:/Program Files/Java/jdk-21/bin/javap.exe');names=[config['package']+'.'+s for s in config['mixins']]
    output=subprocess.check_output([str(javap),'-p','-v','-classpath',ts[COMPAT]['path'],*names],encoding='utf-8',errors='strict')
    path=OUT/'annotation-evidence/iceandfire-compat-javap.txt';path.parent.mkdir(exist_ok=True);path.write_text(output,encoding='utf-8')
    write_json(OUT/'annotation-evidence/iceandfire-compat-javap.json',dict(jar_sha256=ts[COMPAT]['sha256'],tool=str(javap),tool_sha256=sha256(javap),arguments=['-p','-v','-classpath',ts[COMPAT]['path'],*names],output_file=path.relative_to(OUT).as_posix(),output_sha256=sha256(path),scope='Native javap annotation/bytecode aid; registration/injection declarations do not certify successful runtime mixin application.'))
    print('R2g1 native source/registry witnesses saved:',len(result['witnesses']))


if __name__=='__main__':save()
