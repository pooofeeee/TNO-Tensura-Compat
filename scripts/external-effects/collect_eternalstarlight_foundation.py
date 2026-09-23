"""Bounded Eternal Starlight source foundation; census membership is not semantic completion."""
from collections import defaultdict
from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from vanilla_reference import CLIENT

START='74492a5c2ec72051e8c0d142e16542a795aa5029'
CP='R2h1-eternalstarlight-source-foundation'
ES='cn/leolezury/eternalstarlight/'
FACTORY=ES+'common/data/ESDamageTypes'
EFFECTS=ES+'common/registry/ESMobEffects'
EVENTS=['onIncomingDamage','onPreLivingHurt','onPostLivingHurt','onLivingHeal','onLivingDeath','onLivingChangeTarget','onLivingBreathe','onLivingTick','onCriticalHit','onShieldBlock','onProjectileImpact']

def targets():
    inv=read_json(OUT/'jar-inventory.json');return {t['key']:t for t in inv['targets']+inv['compat_candidates']}

def census():
    t=targets()['eternalstarlight'];assert sha256(t['path'])==t['sha256'];calls=[];statuses=[];uses=[];classes=0
    with zipfile.ZipFile(t['path']) as jar:
        for entry in sorted(n for n in jar.namelist() if n.endswith('.class')):
            raw=jar.read(entry);c=ClassFile(raw);classes+=1
            for m in c.methods:
                body=list(c.instructions(m.get('code',b'')))
                for kind,prefix,opcodes,out in [('damage_factory',FACTORY+'.get',{'0xb8'},calls),('damage_key',FACTORY+'.',{'0xb2'},uses),('effect_field',EFFECTS+'.',{'0xb2'},statuses)]:
                    if entry in {FACTORY+'.class',EFFECTS+'.class'}:continue
                    hits=[i for i in body if i['opcode'] in opcodes and str(i.get('operand','')).startswith(prefix)]
                    if hits:out.append(dict(entry=entry,entry_sha256=byte_hash(raw),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits,kind=kind,semantic_status='PENDING_FAMILY_REVIEW'))
    return dict(schema='tno.external_effects.es_source_census.v1',baseline=BASELINE,jar_sha256=t['sha256'],parsed_classes=classes,factory_callers=calls,damage_key_references=uses,status_references=statuses,note='Direct installed bytecode invocation/field-reference census. Datagen/client/registry entries are not automatically legitimate combat deliveries. Helpers and native admission remain family work.')

def tags():
    t=targets()['eternalstarlight'];loader=next(a for a in read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'] if a['path'].endswith('universal.jar'))
    archives=[dict(path=str(CLIENT),sha256=sha256(CLIENT)),dict(path=loader['path'],sha256=loader['sha256']),dict(path=t['path'],sha256=t['sha256'])]
    table={};resources=[];declarations=[]
    for a in archives:
        assert sha256(a['path'])==a['sha256']
        with zipfile.ZipFile(a['path']) as jar:
            for entry in sorted(jar.namelist()):
                if entry.startswith('data/') and '/tags/damage_type/' in entry and entry.endswith('.json'):
                    raw=jar.read(entry);d=json.loads(raw);tag=entry.split('/')[1]+':'+entry.split('/tags/damage_type/')[1][:-5]
                    resources.append(dict(archive_sha256=a['sha256'],entry=entry,sha256=byte_hash(raw),data=d))
                    if d.get('replace'):table[tag]=[]
                    table.setdefault(tag,[]).extend(d.get('values',[]))
                elif a['path']==t['path'] and entry.startswith('data/eternal_starlight/damage_type/') and entry.endswith('.json'):
                    raw=jar.read(entry);declarations.append(dict(id='eternal_starlight:'+Path(entry).stem,entry=entry,sha256=byte_hash(raw),data=json.loads(raw)))
    def members(tag,seen=()):
        if tag in seen:return set()
        result=set()
        for v in table.get(tag,[]):
            v=v['id'] if isinstance(v,dict) else v
            result|=members(v[1:],seen+(tag,)) if v.startswith('#') else {v}
        return result
    for d in declarations:d['tags']=sorted(tag for tag in table if d['id'] in members(tag))
    return dict(schema='tno.external_effects.es_damage_tags.v1',baseline=BASELINE,archives=archives,declarations=declarations,resources=resources,scope='Raw Minecraft1.21.1, exact NeoForge21.1.244 and installed Eternal Starlight contributions only; not whole-pack runtime tag order. DamageEffects display feedback does not imply an elemental damage tag.')

def compat_scan():
    ts=targets();inv=read_json(OUT/'jar-inventory.json');rows=[]
    scopes=[('eternalstarlight',['tensura','l2hostility','l2complements','l2library'])]+[(k,['eternal_starlight','eternalstarlight','cn/leolezury/eternalstarlight']) for k in ['tensura']+[x['key'] for x in inv['compat_candidates']]]
    for key,needles in scopes:
        t=ts[key];assert sha256(t['path'])==t['sha256'];hits=[];classes=0;resource_count=0
        with zipfile.ZipFile(t['path']) as jar:
            for entry in sorted(jar.namelist()):
                if entry.endswith('.class'):
                    raw=jar.read(entry);c=ClassFile(raw);classes+=1
                    matched=sorted({x[1] for x in c.cp if x and x[0]==1 and any(n in x[1].lower() for n in needles)})
                elif entry.endswith(('.json','.toml','.cfg','.properties','.mcmeta')):
                    raw=jar.read(entry);resource_count+=1;text=raw.decode('utf-8',errors='replace').lower();matched=[n for n in needles if n in text]
                else:continue
                if matched:hits.append(dict(entry=entry,entry_sha256=byte_hash(raw),matches=matched))
        rows.append(dict(mod_key=key,jar_sha256=t['sha256'],needles=needles,parsed_classes=classes,scanned_text_resources=resource_count,hits=hits))
    return dict(schema='tno.external_effects.es_direct_compat_census.v1',baseline=BASELINE,scope='Explicit-name constant-pool and text-resource scan of ES, installed Tensura and the four inventoried compat candidates only. Generic event/mixin/skill interactions and other installed mods are not negative-certified.',archives=rows)

def save():
    t=targets()['eternalstarlight'];specs=[]
    classes={'common/data/ESDamageTypes':None,'common/registry/ESMobEffects':None,'common/EternalStarlight':['init','id'],'neoforge/ESNeoEntrypoint':['<init>'],'common/platform/registry/RegistrationProvider':['get'],'common/platform/ESPlatform':['<clinit>','lambda$static$0'],'neoforge/platform/ESNeoPlatform':['createRegistrationProvider'],'neoforge/platform/ESNeoPlatform$NeoForgeRegistrationProvider':None,'neoforge/event/CommonEvents':EVENTS}
    with zipfile.ZipFile(t['path']) as jar:
        for short,names in classes.items():
            entry=ES+short+'.class';c=ClassFile(jar.read(entry));methods=names if names is not None else sorted({m['name'] for m in c.methods})
            specs.append(dict(id='es:foundation:'+short,mod_key='eternalstarlight',entry=entry,methods=methods))
        resources=['META-INF/neoforge.mods.toml','eternal_starlight.mixins.json','eternal_starlight-common.mixins.json','META-INF/services/cn.leolezury.eternalstarlight.common.platform.ESPlatform']
        resources+=sorted(n for n in jar.namelist() if n.startswith('data/') and ('/damage_type/' in n or '/tags/mob_effect/' in n))
        for entry in resources:specs.append(dict(id='es:foundation:data:'+entry,mod_key='eternalstarlight',entry=entry))
    spec=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Source factory, actual registry/loader dispatch and data foundation; payload semantics remain pending.',evidence_specifications=specs)
    e=collect(spec);write_json(OUT/'native-specifications/eternalstarlight-foundation.json',spec);write_json(OUT/'native-evidence/eternalstarlight-foundation.json',e)
    write_json(OUT/'eternalstarlight-source-census.json',census());write_json(OUT/'eternalstarlight-damage-tags.json',tags());write_json(OUT/'eternalstarlight-direct-compat-census.json',compat_scan())
    tool=Path('C:/Program Files/Java/jdk-21/bin/javap.exe');names=[ES.replace('/','.')+'neoforge.event.CommonEvents',ES.replace('/','.')+'neoforge.ESNeoEntrypoint',EFFECTS.replace('/','.')]
    args=['-p','-v','-classpath',t['path'],*names];text=subprocess.check_output([str(tool),*args],encoding='utf-8')
    path=OUT/'annotation-evidence/eternalstarlight-foundation-javap.txt';path.write_text(text,encoding='utf-8')
    write_json(OUT/'annotation-evidence/eternalstarlight-foundation-javap.json',dict(tool=str(tool),tool_sha256=sha256(tool),jar_sha256=t['sha256'],arguments=args,output_file=path.relative_to(OUT).as_posix(),output_sha256=sha256(path),scope='Declaration evidence, not successful runtime mixin/event application certification.'))
    print('Saved foundation witnesses:',len(e['witnesses']))

if __name__=='__main__':save()
