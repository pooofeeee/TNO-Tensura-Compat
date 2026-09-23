from collections import defaultdict
from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from collect_bossesrise_foundation import targets,KEY,PKG,census

AI=['entity/monster/SoulSkeletonEntity$1','entity/monster/SoulKnightWitherSkeletonEntity$1','entity/boss/dragon/guardians/DragonGuardSwordEntity$1','entity/boss/dragon/guardians/FlamingSkeletonGuardSwordEntity$1','entity/boss/dragon/guardians/FlamingSkeletonGuardFireballEntity$1']
EXTRA=['entity/boss/yeti/FrozenSkeletonEntity','entity/decoration/PileOfBonesEntity','procedures/PileOfBonesEntityIsHurtProcedure','procedures/PileOfBonesOnEntityTickUpdateProcedure','entity/decoration/AnchorEntity','entity/decoration/CageEntity','entity/decoration/CratePileEntity','event/StructureDestructionEvents','mixins/server/WitherBossMixin','mixins/server/WardenMixin','mixins/server/EndDragonFightMixin','entity/OwnableByAllEntity','entity/OwnableByAllEntity$OwnerHurtByTargetGoal','entity/OwnableByAllEntity$OwnerHurtTargetGoal','entity/OwnableByAllEntity$DoNotAttackOwnerGoal']

def specification():
    covered=set();prior=[]
    for f in sorted((OUT/'native-evidence').glob('bossesrise-*.json')):
        if f.name=='bossesrise-closure.json':continue
        prior.append(dict(file='native-evidence/'+f.name,sha256=sha256(f)))
        for w in read_json(f)['witnesses']:
            covered|={(w['entry'],m['name'],m['descriptor']) for m in w.get('methods',[])}
    t=targets()[KEY];wanted=defaultdict(set);gaps=[]
    c=read_json(OUT/'bossesrise-source-census.json')
    for row in c['watched_methods']:
        if (row['entry'],row['method'],row['descriptor']) not in covered:wanted[row['entry']].add(row['method']);gaps.append(row)
    with zipfile.ZipFile(t['path']) as z:
        for short in AI+EXTRA:
            n=PKG+short+'.class';cl=ClassFile(z.read(n));wanted[n]|={m['name'] for m in cl.methods}
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Final watched-method witnesses, native melee admission and short noncombat exclusions; no new native payloads.',evidence_specifications=[dict(id='br:closure:'+n.removeprefix(PKG),mod_key=KEY,entry=n,methods=sorted(names)) for n,names in sorted(wanted.items())])
    return s,dict(schema='tno.external_effects.bossesrise_closure_census.v1',baseline=BASELINE,jar_sha256=t['sha256'],parsed_classes=c['parsed_classes'],watched_methods=c['watched_methods'],previous_evidence=prior,newly_witnessed_methods=gaps,scope='Original whole-JAR candidate scan plus explicit anonymous AI/inherited/entity/event semantics. Witness coverage is not by itself semantic acceptance.')

def save():
    s,c=specification();write_json(OUT/'native-specifications/bossesrise-closure.json',s);write_json(OUT/'native-evidence/bossesrise-closure.json',collect(s));write_json(OUT/'bossesrise-combat-closure-census.json',c);print('Closure evidence pinned:',len(c['newly_witnessed_methods']),'new watched methods')
if __name__=='__main__':save()
