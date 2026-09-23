"""Reproduce Flute dispatch, persistence declarations and native Siren attacks."""
from catalog_common import *
from native_evidence import collect
from selected_reference import collect as collect_reference
from collect_iceandfire_foundation import IAF
from collect_iceandfire_siren_flute import census
from assemble_iceandfire_siren_flute import START,CP,FACTS

def validate_siren_flute():
    n='iceandfire-siren-flute';s=read_json(OUT/'native-specifications'/f'{n}.json');e=read_json(OUT/'native-evidence'/f'{n}.json');assert collect(s)==e
    c=read_json(OUT/'iceandfire-flute-callers.json');assert census()==c
    refs=read_json(OUT/'reference-evidence'/f'{n}-244.json');assert collect_reference(read_json(OUT/'reference-specifications'/f'{n}-244.json'))==refs
    w={r['entry']:r for r in e['witnesses']}
    def body(short,name):return next(m['instructions'] for m in w[IAF+short+'.class']['methods'] if m['name']==name)
    def hits(b,n):return [i for i in b if n in str(i.get('operand'))]
    use=body('item/SirenFluteItem','use');assert hits(use,'setLoveTicks(') and not hits(use,'.addEffect(') and not hits(use,'.hurt(')
    assert hits(use,'setLoveTicks(')[0]['offset']<hits(use,'.hurtAndBreak(')[0]['offset']
    assert any(i['operand']==200 for i in use) and any(i['operand']==900 for i in use)
    misc=body('data/component/MiscData','tick');assert hits(misc,'.recomputePath(') and hits(misc,'.setTarget(') and hits(misc,'.setAggressive(')
    assert not hits(misc,'.hurt(') and not hits(misc,'.setNoAi(') and not hits(misc,'.addEffect(')
    post=body('neoforge/IafAttachments','onLivingTick');assert hits(post,'IafAttachments.MISC_DATA')
    dispatch=body('neoforge/IafAttachments','tickAndSync');assert hits(dispatch,'IafEntityAttachment.tick(')[0]['offset']<hits(dispatch,'.isDirty(')[0]['offset']<hits(dispatch,'.syncData(')[0]['offset']
    for cls in ['ServerLevel','ClientLevel']:
        r=next(r for r in refs['witnesses'] if r['entry'].endswith('/'+cls+'.class'))
        non=next(m['instructions'] for m in r['methods'] if m['name']=='tickNonPassenger');passenger=next(m['instructions'] for m in r['methods'] if m['name']=='tickPassenger')
        assert hits(non,'.tick(')[0]['offset']<hits(non,'fireEntityTickPost(')[0]['offset']
        assert hits(passenger,'.rideTick(') and not hits(passenger,'fireEntityTickPost(')
    a=read_json(OUT/'annotation-evidence/iceandfire-attachments-javap.json');assert sha256(a['tool'])==a['tool_sha256'] and sha256(OUT/a['output_file'])==a['output_sha256']
    text=(OUT/a['output_file']).read_text(encoding='utf-8');assert 'EventBusSubscriber' in text and 'SubscribeEvent' in text and 'EntityTickEvent$Post' in text
    siren=next(r for r in read_json(OUT/'native-evidence/iceandfire-siren.json')['witnesses'] if r['entry'].endswith('/SirenEntity.class'))
    attack=next(m['instructions'] for m in siren['methods'] if m['name']=='doHurtTarget');assert not hits(attack,'.hurt(') and not hits(attack,'Mob.doHurtTarget(')
    step=next(m['instructions'] for m in siren['methods'] if m['name']=='aiStep');hurts=hits(step,'.hurt(');assert len(hurts)==2
    for i in hurts:assert step[step.index(i)+1]['opcode']=='0x57'
    assert len(hits(step,'.mobAttack('))==2 and hurts[1]['offset']<hits(step,'.setDeltaMovement(')[0]['offset']
    # Native X pull term actually reads old Z before computing the later Y/Z terms.
    after=step[step.index(hurts[1])+1:];component=next(i for i in after if str(i.get('operand','')).startswith('net/minecraft/world/phys/Vec3.') and i['opcode']=='0xb4');assert component['operand'].endswith('.zD')
    d=read_json(OUT/'iceandfire-r2g3b-siren-flute-attacks.json');assert d['facts']==FACTS and len(d['delivery_paths'])==4 and len(d['unexecuted_future_fixtures'])==10
    for p in d['reference_files']:assert sha256(OUT/p['file'])==p['sha256']
    preserved={}
    for name,key in [('effect-catalog.json','effects'),('effect-sources.json','sources'),('delivery-path-matrix.json','paths'),('vanilla-comparison.json','comparisons'),('behavior-primitives.json','primitives')]:
        assert read_json(OUT/name)[key]==json.loads(git('show',START+':docs/benchmarks/external-effects-catalog/'+name))[key];preserved[key]=len(read_json(OUT/name)[key])
    mutable={'docs/external-effects-catalog-research.md','scripts/external-effects/validate.py'}|{'docs/benchmarks/external-effects-catalog/'+n for n in ['effect-catalog.json','effect-sources.json','delivery-path-matrix.json','vanilla-comparison.json','behavior-primitives.json','mod-completion-ledger.json','research-decision.json','mod-reviews/iceandfire.json']}
    for line in git('diff','--name-status',START).splitlines():
        status,path=line.split('\t',1);assert status=='A' or (status=='M' and path in mutable),line
    for line in git('diff','--name-status',BASELINE).splitlines():
        status,path=line.split('\t',1);assert status=='A' and path.startswith(('docs/external-effects-catalog-research.md','docs/benchmarks/external-effects-catalog/','scripts/external-effects/')),line
    assert all(not d[k] for k in boundary_flags());git('diff','--check',BASELINE)
    return dict(schema='tno.external_effects.iaf_siren_flute_integrity.v1',checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),exact_loader_witnesses=len(refs['witnesses']),caller_methods=len(c['rows']),reviewed_packages=3,delivery_paths=4,unexecuted_fixtures=10,post_vs_passenger_distinction_proven=True,pull_hurt_independence_proven=True,accepted_counts_preserved=preserved,promoted_iceandfire_records=0,whole_iceandfire_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_siren_flute();write_json(OUT/'iceandfire-r2g3b-integrity.json',d);print(json.dumps(d,indent=2))
