from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_bossesrise_foundation import targets,KEY,PKG

CLASSES={'attachment/entity/RollAttachment':None,'network/DodgeRollMessage':None,'mixins/RollMixin':None,'mixins/ControlMixin':None,'init/BossesRiseKeyMappings$1':['setDown'],'init/BossesRiseAttributes':None,'init/BossesRiseDataAttachments':['<clinit>','lambda$static$1'],'configuration/ServerConfiguration':['<clinit>'],'BossesRise':['registerNetworking','addNetworkMessage'],'entity/boss/yeti/GlacialShoveEntity':['tick']}

def census():
    t=targets()[KEY];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(x for x in z.namelist() if x.endswith('.class')):
            raw=z.read(n);c=ClassFile(raw)
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if any(s in str(i.get('operand','')) for s in ['RollAttachment.startRoll(','RollAttachment.isInvulnerable(','RollAttachment.isRolling(','ServerConfiguration.ROLL_COOLDOWN_MORE','BossesRiseAttributes.ROLL_COUNT']) and i['opcode'] in ['0xb2','0xb6','0xb7','0xb8','0xb9']]
                if hits:rows.append(dict(entry=n,entry_sha256=byte_hash(raw),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits))
    return dict(jar_sha256=t['sha256'],scope='Installed roll activation, actual gate consumers and resource modifier caller index. Other equipment/GlacialShove payload semantics remain family work.',rows=rows)

def save():
    t=targets()[KEY];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in CLASSES.items():
            n=PKG+short+'.class';c=ClassFile(z.read(n));names=wanted or sorted({m['name'] for m in c.methods});names=sorted(set(names)|{m['name'] for m in c.methods if any(m['name'].startswith('lambda$'+v+'$') for v in names)})
            rows.append(dict(id='br:roll:'+short,mod_key=KEY,entry=n,methods=names))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Actual roll delivery, resource, admission, freeze/movement gates; partial equipment/Yeti references only.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/bossesrise-roll.json',s);write_json(OUT/'native-evidence/bossesrise-roll.json',collect(s));write_json(OUT/'bossesrise-roll-census.json',census())
    old=read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'];archives=[]
    for index,classes in [(0,{'net/minecraft/world/entity/LivingEntity.class':['hurt','addEffect','forceAddEffect']}),(1,{'net/neoforged/neoforge/common/CommonHooks.class':['onEntityIncomingDamage','canMobEffectBeApplied'],'net/neoforged/neoforge/event/EventHooks.class':['onProjectileImpact'],'net/neoforged/neoforge/event/entity/EntityEvent.class':['<init>','getEntity'],'net/neoforged/neoforge/event/entity/ProjectileImpactEvent.class':['<init>','getProjectile'],'net/neoforged/neoforge/event/entity/living/MobEffectEvent$Applicable.class':['<init>','setResult','getApplicationResult']})]:
        a=dict(old[index]);a.pop('semantic_review',None);a['classes']=classes;archives.append(a)
    r=dict(id='bossesrise-roll-244',scope='Exact NeoForge damage/effect dispatch and event identity. ProjectileImpactEvent subject is projectile, not hit target. No runtime execution.',archives=archives)
    write_json(OUT/'reference-specifications/bossesrise-roll-244.json',r);write_json(OUT/'reference-evidence/bossesrise-roll-244.json',reference_collect(r,source_aids=True))
    tool=Path('C:/Program Files/Java/jdk-21/bin/javap.exe');args=['-p','-v','-classpath',t['path'],PKG.replace('/','.')+'attachment.entity.RollAttachment',PKG.replace('/','.')+'network.DodgeRollMessage']
    p=OUT/'annotation-evidence/bossesrise-roll-javap.txt';p.write_text(subprocess.check_output([str(tool),*args],encoding='utf-8'),encoding='utf-8')
    write_json(p.with_suffix('.json'),dict(tool=str(tool),tool_sha256=sha256(tool),jar_sha256=t['sha256'],arguments=args,output_file=p.relative_to(OUT).as_posix(),output_sha256=sha256(p)))
    print('Roll evidence saved')

if __name__=='__main__':save()
