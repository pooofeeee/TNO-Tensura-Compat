from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_cataclysm_foundation import targets,KEY,PKG

BOSSES=['entity/AnimationMonster/BossMonsters/LLibrary_Boss_Monster','entity/InternalAnimationMonster/IABossMonsters/IABoss_monster']
CLASSES=BOSSES+['entity/AnimationMonster/LLibrary_Monster','entity/InternalAnimationMonster/Internal_Animation_Monster','entity/etc/Animation_Monsters','entity/etc/IHomeEntity']

def inheritance():
    t=targets()[KEY];classes={};rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for n in z.namelist():
            if n.endswith('.class') and n.startswith(PKG+'entity/'):classes[n[:-6]]=ClassFile(z.read(n))
        def root(n):
            if n in {PKG+s for s in BOSSES}:return n
            return root(classes[n].super) if n in classes and classes[n].super in classes else None
        for n,c in sorted(classes.items()):
            b=root(n)
            if b:rows.append(dict(entry=n+'.class',shared_base=b+'.class',overrides=[dict(method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b''))) for m in c.methods if m['name'] in ['hurt','canBeAffected','isInvulnerableTo','DamageCap','DpsCap','RangeLimit','NatureRegen','HealCooldown','Retry','PlayerCounter','ReturnToHome']],semantic_status='SHARED_BASE_REVIEWED_CONCRETE_OVERRIDES_PENDING' if n!=b else 'SHARED_BASE_REVIEWED'))
    return dict(schema='tno.external_effects.cataclysm_boss_inheritance.v1',baseline=BASELINE,jar_sha256=t['sha256'],classes=rows,scope='Actual native hierarchy and local method overrides only; concrete phase/cap/defense values remain family review.')

def tag_members():
    table={}
    for r in read_json(OUT/'cataclysm-damage-tags.json')['resources']:
        n=r['entry'];k=n.split('/')[1]+':'+n.split('/tags/damage_type/')[1][:-5];d=r['data']
        if d.get('replace'):table[k]=[]
        table.setdefault(k,[]).extend(d.get('values',[]))
    def walk(k,seen=()):
        if k in seen:return set()
        out=set()
        for v in table.get(k,[]):
            v=v['id'] if isinstance(v,dict) else v;out|=walk(v[1:],seen+(k,)) if v.startswith('#') else {v}
        return out
    w=next(w for w in read_json(OUT/'native-evidence/cataclysm-foundation.json')['witnesses'] if w['entry']=='data/cataclysm/tags/mob_effect/effective_for_bosses.json')
    return dict(scope='Pinned vanilla/NeoForge/Cataclysm damage closure and Cataclysm shipped effect whitelist; other pack contributions unmeasured.',damage_tags={k:sorted(walk(k)) for k in ['cataclysm:bypasses_hurt_time','cataclysm:block_self_regen']},effect_whitelist=w['data'])

def save():
    rows=[];t=targets()[KEY]
    with zipfile.ZipFile(t['path']) as z:
        for short in CLASSES:
            n=PKG+short+'.class';c=ClassFile(z.read(n));names=sorted({m['name'] for m in c.methods})
            if short=='entity/etc/Animation_Monsters':names=['<init>','setConfigattribute','calculateRange','die','onDeathUpdate','deathtimer','onDeathAIUpdate','AfterDefeatBoss']
            rows.append(dict(id='cataclysm:shared:'+short,mod_key=KEY,entry=n,methods=names))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Shared boss hurt caps/range/bucket, native regen, effect filter, home/life/death lifecycle; concrete boss special gates deferred.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/cataclysm-shared.json',s);write_json(OUT/'native-evidence/cataclysm-shared.json',collect(s));write_json(OUT/'cataclysm-boss-inheritance.json',inheritance());write_json(OUT/'cataclysm-shared-tags.json',tag_members())
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None);a['classes']={'net/minecraft/world/entity/LivingEntity.class':['hurt','addEffect','canBeAffected','heal'],'net/minecraft/world/entity/Entity.class':['isInvulnerableTo']}
    r=dict(id='cataclysm-shared-244',scope='Native underlying hurt/effect/heal/invulnerability admission; source-specific gates remain in Cataclysm.',archives=[a]);write_json(OUT/'reference-specifications/cataclysm-shared-244.json',r);write_json(OUT/'reference-evidence/cataclysm-shared-244.json',reference_collect(r,source_aids=True));print('Shared witnesses',len(rows))

if __name__=='__main__':save()
