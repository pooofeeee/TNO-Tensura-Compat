from catalog_common import *
from native_evidence import collect
from collect_bossesrise_closure import specification,AI,PKG
from assemble_bossesrise_closure import FACTS,CP,STEM
from bossesrise_combat_common import preserve_section

def validate_closure():
    s,c=specification();assert read_json(OUT/'native-specifications/bossesrise-closure.json')==s and read_json(OUT/'bossesrise-combat-closure-census.json')==c
    e=read_json(OUT/'native-evidence/bossesrise-closure.json');assert collect(s)==e
    assert c['parsed_classes']==802 and len(c['watched_methods'])==157 and len(c['newly_witnessed_methods'])==16
    w={x['entry']:x for x in e['witnesses']}
    def b(short,n):return next(m['instructions'] for m in w[PKG+short+'.class']['methods'] if m['name']==n)
    def h(v,s):return [i for i in v if s in str(i.get('operand',''))]
    for a in AI:
        v=b(a,'canPerformAttack');assert h(v,'.isTimeToAttack(') and h(v,'.distanceToSqr(') and h(v,'.hasLineOfSight(')
    v=b('event/StructureDestructionEvents','onExplosion');assert h(v,'.getAffectedBlocks(') and not h(v,'.getAffectedEntities(')
    v=b('procedures/PileOfBonesEntityIsHurtProcedure','execute');assert h(v,'FallingBlockEntity.fall(') and not h(v,'.setHurtsEntities(') and not h(v,'.hurt(')
    for a in ['entity/decoration/AnchorEntity','entity/decoration/CageEntity','entity/decoration/CratePileEntity','entity/boss/yeti/FrozenSkeletonEntity']:
        assert not h(b(a,'hurt'),'.hurt(')
    seen=set()
    for f in sorted((OUT/'native-evidence').glob('bossesrise-*.json')):
        for x in read_json(f)['witnesses']:seen|={(x['entry'],m['name'],m['descriptor']) for m in x.get('methods',[])}
    for row in c['watched_methods']:assert (row['entry'],row['method'],row['descriptor']) in seen,row
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and not d['mechanic_packages'] and not d['delivery_paths'] and d['whole_combat_semantics_closed']
    preserved=preserve_section(d);assert preserved==dict(effects=543,sources=1303,paths=1303,comparisons=543,primitives=717)
    return dict(schema='tno.external_effects.bossesrise_closure_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',parsed_classes=802,watched_methods=157,new_method_witnesses=16,anonymous_AI_melee_confirmed=5,exclusions_verified=True,semantic_closure_complete=True,accepted_counts_preserved=preserved,whole_mod_complete=False,promotion_pending=True,runtime_tests=0,**boundary_flags())
if __name__=='__main__':
    d=validate_closure();write_json(OUT/'bossesrise-r2i9a-integrity.json',d);print(json.dumps(d,indent=2))
