"""Installed Cataclysm source foundation; census rows remain unreviewed candidates."""
from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from vanilla_reference import CLIENT
from collect_bomd_foundation import targets

KEY='cataclysm'
PKG='com/github/L_Ender/cataclysm/'
START='bbd92263f0534929416b2ccfad969c472a1c7607'
CP='R2k1-cataclysm-source-foundation'
STEM='cataclysm-r2k1-source-foundation'

def census():
    t=targets()[KEY];assert sha256(t['path'])==t['sha256'];classes=[];watched=[];keys=[];effects=[];factories=[];tagreads=[]
    watches=['.hurt(','.heal(','.setHealth(','.addEffect(','.removeEffect(','.setTicksFrozen(','.setRemainingFireTicks(','.igniteForSeconds(','.isInvulnerableTo(','.canBeAffected(','.explode(','.setCanceled(','.setAmount(','.setNewDamage(','.setResult(','.knockback(','.push(','.setDeltaMovement(','.addDeltaMovement(','.doHurtTarget(','.doPostAttackEffects(','.actuallyHurt(','.teleportTo(','.randomTeleport(','.setAbsorptionAmount(']
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(n for n in z.namelist() if n.endswith('.class')):
            raw=z.read(n);c=ClassFile(raw);classes.append(dict(entry=n,entry_sha256=byte_hash(raw),superclass=c.super,interfaces=c.interfaces))
            for m in c.methods:
                ins=list(c.instructions(m.get('code',b'')));base=dict(entry=n,entry_sha256=byte_hash(raw),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),semantic_status='PENDING_FAMILY_REVIEW')
                hits=[i for i in ins if i['opcode'] in ['0xb6','0xb7','0xb8','0xb9'] and any(s in str(i.get('operand','')) for s in watches)]
                if hits:watched.append(dict(**base,hits=hits))
                hits=[i for i in ins if i['opcode']=='0xb2' and str(i.get('operand','')).startswith(PKG+'util/CMDamageTypes.')]
                if hits:keys.append(dict(**base,hits=hits))
                hits=[i for i in ins if i['opcode']=='0xb8' and str(i.get('operand','')).startswith(PKG+'util/CMDamageTypes.')]
                if hits:factories.append(dict(**base,hits=hits))
                hits=[i for i in ins if i['opcode']=='0xb2' and any(str(i.get('operand','')).startswith(p) for p in [PKG+'init/ModEffect.','net/minecraft/world/effect/MobEffects.'])]
                if hits:effects.append(dict(**base,hits=hits))
                hits=[i for i in ins if i['opcode']=='0xb2' and any(s in str(i.get('operand','')) for s in ['ModTag.BYPASSES_HURT_TIME','ModTag.BLOCK_SELF_REGEN','ModTag.EFFECTIVE_FOR_BOSSES'])]
                if hits:tagreads.append(dict(**base,hits=hits))
    return dict(schema='tno.external_effects.cataclysm_census.v1',baseline=BASELINE,jar_sha256=t['sha256'],parsed_classes=len(classes),classes=classes,watched_methods=watched,custom_damage_key_methods=keys,custom_source_factory_methods=factories,effect_reference_methods=effects,boss_tag_reader_methods=tagreads,scope='Whole1310-class instruction census; candidates include helpers, client, data and ordinary utility. No mechanic completion/absence inference from counts.')

def registries():
    t=targets()[KEY]
    with zipfile.ZipFile(t['path']) as z:
        result={}
        for short,descriptor,label in [('util/CMDamageTypes','Lnet/minecraft/resources/ResourceKey;','damage_keys'),('init/ModEffect','Lnet/neoforged/neoforge/registries/DeferredHolder;','mob_effects')]:
            n=PKG+short+'.class';c=ClassFile(z.read(n));m=next(m for m in c.methods if m['name']=='<clinit>');rows=[];last=None
            for i in c.instructions(m['code']):
                if i['opcode'] in ['0x12','0x13'] and isinstance(i.get('operand'),str):last=i['operand']
                if i['opcode']=='0xb3' and str(i.get('operand','')).startswith(PKG+short+'.') and str(i['operand']).endswith(descriptor):
                    field=i['operand'].split('.')[-1].removesuffix(descriptor);rows.append(dict(field=field,id=KEY+':'+last,putstatic_offset=i['offset']))
            result[label]=rows
        return dict(schema='tno.external_effects.cataclysm_registries.v1',baseline=BASELINE,jar_sha256=t['sha256'],**result)

def tags():
    t=targets()[KEY];loader=next(a for a in read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'] if a['path'].endswith('universal.jar'))
    archives=[dict(path=str(CLIENT),sha256=sha256(CLIENT)),dict(path=loader['path'],sha256=loader['sha256']),dict(path=t['path'],sha256=t['sha256'])];table={};resources=[];decl=[]
    for a in archives:
        assert sha256(a['path'])==a['sha256']
        with zipfile.ZipFile(a['path']) as z:
            for n in sorted(z.namelist()):
                if n.startswith('data/') and '/tags/damage_type/' in n and n.endswith('.json'):
                    raw=z.read(n);d=json.loads(raw);tag=n.split('/')[1]+':'+n.split('/tags/damage_type/')[1][:-5];resources.append(dict(archive_sha256=a['sha256'],entry=n,sha256=byte_hash(raw),data=d))
                    if d.get('replace'):table[tag]=[]
                    table.setdefault(tag,[]).extend(d.get('values',[]))
                elif a['path']==t['path'] and n.startswith('data/'+KEY+'/damage_type/') and n.endswith('.json'):
                    raw=z.read(n);decl.append(dict(id=KEY+':'+Path(n).stem,entry=n,sha256=byte_hash(raw),data=json.loads(raw)))
    def members(tag,seen=()):
        if tag in seen:return set()
        out=set()
        for v in table.get(tag,[]):
            v=v['id'] if isinstance(v,dict) else v;out|=members(v[1:],seen+(tag,)) if v.startswith('#') else {v}
        return out
    for d in decl:d['tags']=sorted(k for k in table if d['id'] in members(k));d['disposition']='PENDING_CALLER_SEMANTICS'
    return dict(schema='tno.external_effects.cataclysm_damage_tags.v1',baseline=BASELINE,archives=archives,declarations=decl,code_keys_without_bundled_json=[r['id'] for r in registries()['damage_keys'] if r['id'] not in {d['id'] for d in decl}],resources=resources,scope='Raw Minecraft1.21.1 + NeoForge21.1.244 + Cataclysm only; external datapacks/mod tag contributions and loaded registry remain unmeasured.')

def compat_scan():
    ts=targets();i=read_json(OUT/'jar-inventory.json');rows=[]
    for key,needles in [(KEY,['tensura','l2hostility','l2complements','l2library'])]+[(k,[KEY]) for k in ['tensura']+[v['key'] for v in i['compat_candidates']]]:
        t=ts[key];assert sha256(t['path'])==t['sha256'];hits=[];nc=0;nr=0
        with zipfile.ZipFile(t['path']) as z:
            for n in sorted(z.namelist()):
                if n.endswith('.class'):
                    raw=z.read(n);c=ClassFile(raw);nc+=1;matches=sorted({x[1] for x in c.cp if x and x[0]==1 and any(s in x[1].lower() for s in needles)})
                elif n.endswith(('.json','.toml','.cfg','.properties','.mcmeta')):
                    raw=z.read(n);nr+=1;s=raw.decode('utf-8',errors='replace').lower();matches=[v for v in needles if v in s]
                else:continue
                if matches:hits.append(dict(entry=n,entry_sha256=byte_hash(raw),matches=matches))
        rows.append(dict(mod_key=key,jar_sha256=t['sha256'],needles=needles,parsed_classes=nc,scanned_text_resources=nr,hits=hits))
    return dict(schema='tno.external_effects.cataclysm_direct_compat.v1',baseline=BASELINE,scope='Six-archive explicit-name scan only, not proof of generic event/attribute/trait compatibility.',archives=rows)

CLASSES=['Cataclysm','init/ModEffect','init/ModAttribute','init/ModTag','util/CMDamageTypes','util/EntityExcludedDamageSource','event/ServerEventHandler','mixin/LivingEntityMixin','mixin/FoodDataMixin','mixin/ItemMixin','config/ConfigHolder','config/CMCommonConfig','config/CommonConfig','entity/InternalAnimationMonster/IABossMonsters/IABoss_monster','entity/AnimationMonster/BossMonsters/LLibrary_Boss_Monster']

def save():
    t=targets()[KEY];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for short in CLASSES:
            n=PKG+short+'.class';c=ClassFile(z.read(n));rows.append(dict(id='cataclysm:foundation:'+short,mod_key=KEY,entry=n,methods=sorted({m['name'] for m in c.methods})))
        for n in ['META-INF/neoforge.mods.toml','cataclysm.mixins.json']+[n for n in sorted(z.namelist()) if n.startswith('data/') and n.endswith('.json') and any(v in n for v in ['/damage_type/','/tags/entity_type/','/tags/mob_effect/'])]:rows.append(dict(id='cataclysm:foundation:data:'+n,mod_key=KEY,entry=n))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Cataclysm registry, source identity, shared hooks and config foundation; payload/admission and legitimate delivery review pending.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/cataclysm-foundation.json',s);write_json(OUT/'native-evidence/cataclysm-foundation.json',collect(s));write_json(OUT/'cataclysm-source-census.json',census());write_json(OUT/'cataclysm-native-registries.json',registries());write_json(OUT/'cataclysm-damage-tags.json',tags());write_json(OUT/'cataclysm-direct-compat-census.json',compat_scan())
    import tomllib
    p=MODS.parent/'config/cataclysm-common.toml';raw=p.read_bytes();write_json(OUT/'cataclysm-installed-common-config.json',dict(schema='tno.external_effects.cataclysm_config.v1',baseline=BASELINE,path=str(p),sha256=byte_hash(raw),text=raw.decode('utf-8-sig'),values=tomllib.loads(raw.decode('utf-8-sig')),scope='Registered COMMON config file snapshot, not proof of currently baked runtime values. Legacy cataclysm.toml and backup not substituted.'))
    tool=Path('C:/Program Files/Java/jdk-21/bin/javap.exe');names=[PKG.replace('/','.')+n.replace('/','.') for n in ['Cataclysm','event/ServerEventHandler','init/ModAttribute','mixin/LivingEntityMixin','mixin/FoodDataMixin','mixin/ItemMixin']];args=['-p','-v','-classpath',t['path'],*names];s=subprocess.check_output([str(tool),*args],encoding='utf-8');p=OUT/'annotation-evidence/cataclysm-foundation-javap.txt';p.write_text(s,encoding='utf-8');write_json(p.with_suffix('.json'),dict(tool=str(tool),tool_sha256=sha256(tool),jar_sha256=t['sha256'],arguments=args,output_file=p.relative_to(OUT).as_posix(),output_sha256=sha256(p),scope='Native annotation declarations; runtime dispatch/mixin application not executed.'))
    c=read_json(OUT/'cataclysm-source-census.json');print(json.dumps(dict(witnesses=len(rows),classes=c['parsed_classes'],watched=len(c['watched_methods']),key_methods=len(c['custom_damage_key_methods']),factory_methods=len(c['custom_source_factory_methods']),effect_methods=len(c['effect_reference_methods']),tag_methods=len(c['boss_tag_reader_methods'])),indent=2))

if __name__=='__main__':save()
