"""Bosses of Mass Destruction installed-bytecode foundation; census hits are not reviewed payloads."""
from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from vanilla_reference import CLIENT

KEY='bosses_of_mass_destruction'
PKG='com/cerbon/bosses_of_mass_destruction/'
START='0d53681feca19379ce8047d0cdc2db7b18806516'
CP='R2j1-bomd-source-foundation'
STEM='bomd-r2j1-source-foundation'

def targets():
    i=read_json(OUT/'jar-inventory.json')
    return {t['key']:t for t in i['targets']+i['compat_candidates']}

def census():
    t=targets()[KEY];assert sha256(t['path'])==t['sha256']
    rows=[];classes=[];custom=[];effect_refs=[];effect_registry=[]
    watches=['.hurt(','.heal(','.setHealth(','.addEffect(','.removeEffect(','.setTicksFrozen(','.setRemainingFireTicks(','.igniteForSeconds(','.isInvulnerableTo(','.canBeAffected(','.explode(','.setCanceled(','.setAmount(','.setNewDamage(','.setResult(','.knockback(','.push(','.setDeltaMovement(','.doHurtTarget(','.doPostAttackEffects(','.actuallyHurt(','.shieldPiercing(']
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(n for n in z.namelist() if n.endswith('.class')):
            raw=z.read(n);c=ClassFile(raw)
            classes.append(dict(entry=n,entry_sha256=byte_hash(raw),superclass=c.super,interfaces=c.interfaces))
            for m in c.methods:
                ins=list(c.instructions(m.get('code',b'')))
                base=dict(entry=n,entry_sha256=byte_hash(raw),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')))
                hits=[x for x in ins if x['opcode'] in {'0xb6','0xb7','0xb8','0xb9'} and any(s in str(x.get('operand','')) for s in watches)]
                if hits:rows.append(dict(**base,hits=hits,semantic_status='PENDING_FAMILY_REVIEW'))
                hits=[x for x in ins if x['opcode']=='0xb2' and str(x.get('operand','')).startswith(PKG+'util/BMDUtils.SHIELD_PIERCING')]
                if hits and n!=PKG+'util/BMDUtils.class':custom.append(dict(**base,hits=hits,semantic_status='PENDING_FAMILY_REVIEW'))
                hits=[x for x in ins if x['opcode']=='0xb2' and str(x.get('operand','')).startswith('net/minecraft/world/effect/MobEffects.')]
                if hits:effect_refs.append(dict(**base,hits=hits,semantic_status='PENDING_FAMILY_REVIEW'))
                hits=[x for x in ins if any(s in str(x.get('operand','')) for s in ['Registries.MOB_EFFECT','BuiltInRegistries.MOB_EFFECT','world/effect/MobEffect.<init>'])]
                if hits:effect_registry.append(dict(**base,hits=hits))
    return dict(schema='tno.external_effects.bomd_census.v1',baseline=BASELINE,jar_sha256=t['sha256'],parsed_classes=len(classes),classes=classes,watched_methods=rows,custom_damage_key_methods=custom,native_effect_reference_methods=effect_refs,custom_effect_registry_candidates=effect_registry,scope='Entire installed artifact census. Candidates include support, datagen, client and ordinary utility; semantic interpretation remains bounded family work. No absence-of-combat conclusion from name matching.')

def tags():
    t=targets()[KEY];loader=next(a for a in read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'] if a['path'].endswith('universal.jar'))
    archives=[dict(path=str(CLIENT),sha256=sha256(CLIENT)),dict(path=loader['path'],sha256=loader['sha256']),dict(path=t['path'],sha256=t['sha256'])]
    table={};resources=[];declarations=[]
    for a in archives:
        assert sha256(a['path'])==a['sha256']
        with zipfile.ZipFile(a['path']) as z:
            for n in sorted(z.namelist()):
                if n.startswith('data/') and '/tags/damage_type/' in n and n.endswith('.json'):
                    raw=z.read(n);d=json.loads(raw);tag=n.split('/')[1]+':'+n.split('/tags/damage_type/')[1][:-5]
                    resources.append(dict(archive_sha256=a['sha256'],entry=n,sha256=byte_hash(raw),data=d))
                    if d.get('replace'):table[tag]=[]
                    table.setdefault(tag,[]).extend(d.get('values',[]))
                elif a['path']==t['path'] and n.startswith('data/'+KEY+'/damage_type/') and n.endswith('.json'):
                    raw=z.read(n);declarations.append(dict(id=KEY+':'+Path(n).stem,entry=n,sha256=byte_hash(raw),data=json.loads(raw)))
    def members(tag,seen=()):
        if tag in seen:return set()
        result=set()
        for v in table.get(tag,[]):
            v=v['id'] if isinstance(v,dict) else v
            result|=members(v[1:],seen+(tag,)) if v.startswith('#') else {v}
        return result
    for d in declarations:d['tags']=sorted(tag for tag in table if d['id'] in members(tag))
    return dict(schema='tno.external_effects.bomd_tags.v1',baseline=BASELINE,archives=archives,declarations=declarations,resources=resources,scope='Raw Minecraft1.21.1 + NeoForge21.1.244 + Bosses of Mass Destruction only. Other mods/datapacks and runtime tag load order are not certified.')

def compat_scan():
    ts=targets();i=read_json(OUT/'jar-inventory.json');rows=[]
    scopes=[(KEY,['tensura','l2hostility','l2complements','l2library'])]+[(k,[KEY,'bomd']) for k in ['tensura']+[x['key'] for x in i['compat_candidates']]]
    for key,needles in scopes:
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
    return dict(schema='tno.external_effects.bomd_direct_compat.v1',baseline=BASELINE,scope='Six-archive explicit-name scan only; generic damage/effect/event/tag/mixin interactions remain untested.',archives=rows)

CLASSES={
 'BossesOfMassDestruction':None,'neoforge/BossesOfMassDestructionNeo':None,
 'entity/custom/lich/VolleyAction':['performVolley','lambda$getMissileThrower$2'],
 'entity/custom/lich/VolleyRageAction':['performVolley','lambda$getMissileThrower$1'],
 'config/BMDConfig':None,'util/BMDUtils':['<clinit>','shieldPiercing'],
 'util/VanillaCopiesServer':['create'],'mixin/LivingEntityMixin':None,'mixin/ExplosionMixin':None,
 'projectile/SporeBallProjectile':None,'entity/custom/void_blossom/Spikes':None,
 'entity/custom/obsidilith/WaveAction':None,'entity/custom/obsidilith/BurstAction':None,'entity/custom/obsidilith/SpikeAction':None,
 'entity/util/BaseEntity':['hurt','canBeAffected'],'entity/util/EffectsImmunity':None,
 'neoforge/event/NeoEvents':None,'neoforge/event/BMDEventsNeo':None,
}

def installed_config():
    p=MODS.parent/'config/bosses_of_mass_destruction.json5'
    raw=p.read_bytes()
    return dict(schema='tno.external_effects.bomd_config.v1',path=str(p),sha256=byte_hash(raw),text=raw.decode('utf-8'),values=json.loads(raw),scope='Installed file snapshot only; not proof of loaded runtime values.')

def save():
    t=targets()[KEY];specs=[]
    with zipfile.ZipFile(t['path']) as z:
        for short,names in CLASSES.items():
            n=PKG+short+'.class';c=ClassFile(z.read(n));methods=names if names is not None else sorted({m['name'] for m in c.methods})
            specs.append(dict(id='bomd:foundation:'+short,mod_key=KEY,entry=n,methods=methods))
        resources=['META-INF/neoforge.mods.toml',KEY+'.mixins.json',KEY+'-common.mixins.json']+[n for n in sorted(z.namelist()) if n.startswith('data/') and ('/damage_type/' in n or '/tags/entity_type/' in n or '/tags/mob_effect/' in n)]
        for n in resources:specs.append(dict(id='bomd:foundation:data:'+n,mod_key=KEY,entry=n))
    spec=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Native key/source/registration/tag and admission-hook foundation; full payload/defense semantics pending.',evidence_specifications=specs)
    e=collect(spec);write_json(OUT/'native-specifications/bomd-foundation.json',spec);write_json(OUT/'native-evidence/bomd-foundation.json',e)
    write_json(OUT/'bomd-source-census.json',census());write_json(OUT/'bomd-damage-tags.json',tags());write_json(OUT/'bomd-direct-compat-census.json',compat_scan())
    tool=Path('C:/Program Files/Java/jdk-21/bin/javap.exe');names=[PKG.replace('/','.')+x.replace('/','.') for x in CLASSES if any(s in x for s in ['Mixin','Events','DestructionNeo'])]
    args=['-p','-v','-classpath',t['path'],*names];s=subprocess.check_output([str(tool),*args],encoding='utf-8');p=OUT/'annotation-evidence/bomd-foundation-javap.txt';p.write_text(s,encoding='utf-8')
    write_json(p.with_suffix('.json'),dict(tool=str(tool),tool_sha256=sha256(tool),jar_sha256=t['sha256'],arguments=args,output_file=p.relative_to(OUT).as_posix(),output_sha256=sha256(p),scope='Installed annotation declarations only; not proof of runtime dispatch or successful mixin application.'))
    write_json(OUT/'bomd-installed-config.json',installed_config())
    c=read_json(OUT/'bomd-source-census.json');print('Foundation witnesses',len(e['witnesses']),'classes',c['parsed_classes'],'watched',len(c['watched_methods']),'keys',len(c['custom_damage_key_methods']),'native effects',len(c['native_effect_reference_methods']))

if __name__=='__main__':save()
