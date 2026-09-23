"""Validate native Gorgon ordering/admission witnesses and prior checkpoint preservation."""
from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_iceandfire_foundation import IAF
from collect_iceandfire_gorgon import census
from assemble_iceandfire_gorgon import START,CP,FACTS

def validate_gorgon():
    e=read_json(OUT/'native-evidence/iceandfire-gorgon.json');assert collect(read_json(OUT/'native-specifications/iceandfire-gorgon.json'))==e
    c=read_json(OUT/'iceandfire-gorgon-census.json');assert census()==c and c['parsed_classes']==726
    r=read_json(OUT/'reference-evidence/iceandfire-gorgon-244.json');assert reference_collect(read_json(OUT/'reference-specifications/iceandfire-gorgon-244.json'))==r
    def body(doc,ending,name):return next(m['instructions'] for w in doc['witnesses'] if w['entry'].endswith(ending+'.class') for m in w.get('methods',[]) if m['name']==name)
    def hits(b,n):return [i for i in b if n in str(i.get('operand',''))]
    gaze=body(e,'entity/GorgonEntity','aiStep');head=body(e,'item/GorgonHeadItem','releaseUsing')
    assert hits(gaze,'.buildStatueEntity(')[0]['offset']<hits(gaze,'.addFreshEntity(')[0]['offset']<hits(gaze,'.hurt(')[0]['offset']
    assert gaze[gaze.index(hits(gaze,'.hurt(')[0])+1]['opcode']=='0x57'
    assert hits(head,'.hurt(')[0]['offset']<hits(head,'.buildStatueEntity(')[0]['offset']<hits(head,'.shrink(')[0]['offset']
    assert head[head.index(hits(head,'.hurt(')[0])+1]['opcode']=='0x36'
    assert gaze[gaze.index(hits(gaze,'.causeGorgonDamage(')[0])-1]['opcode']=='0x2a'
    assert head[head.index(hits(head,'.causeGorgonDamage(')[0])-1]['opcode']=='0x19'
    for b in [head,gaze]:assert any(i.get('operand')==2147483648.0 for i in b)
    assert not hits(head,'.isBlindfolded(')
    # Entity-ray AABB.clip is legitimate; no world/LOS clip belongs to Head.
    assert not hits(head,'Level.clip(') and not hits(head,'.hasLineOfSight(')
    melee=body(e,'entity/GorgonEntity','doHurtTarget');assert hits(melee,'.addEffect(')[0]['offset']<hits(melee,'.doHurtTarget(')[0]['offset']
    assert not hits(melee,'.isBlindfolded(')
    statue=body(e,'entity/StoneStatueEntity','hurt');assert hits(statue,'.remove(')[0]['offset']<hits(statue,'LivingEntity.hurt(')[0]['offset']
    invul=body(r,'entity/Entity','isInvulnerableTo');assert hits(invul,'.invulnerableZ') and not hits(invul,'.isInvulnerable(')
    assert len([row for row in c['rows'] if any('GorgonEntity.isTargetBlocked(' in str(i) for i in row['hits'])])==1
    assert not [row for row in c['rows'] if any('getBlockInTargetsViewGorgon(' in str(i) for i in row['hits'])]
    d=read_json(OUT/'iceandfire-r2g4-gorgon.json');assert d['facts']==FACTS and len(d['mechanic_packages'])==4 and len(d['delivery_paths'])==11
    allowed_categories={'NUMERIC_SCALABLE','BINARY','COMPOSITE','VANILLA_ROUTED','CUSTOM_ROUTED','ADMISSION_GATED','NO_STAGE_VALUE'}
    for p in d['mechanic_packages']:
        assert p['primary_classification'] in CLASSIFICATIONS and set(p['tno_categories'])<=allowed_categories
        assert bool(p['single_scaling_point'])==p['stage_scaling_needed']
    for f in d['reference_files']:assert sha256(OUT/f['file'])==f['sha256']
    preserved={}
    for name,key in [('effect-catalog.json','effects'),('effect-sources.json','sources'),('delivery-path-matrix.json','paths'),('vanilla-comparison.json','comparisons'),('behavior-primitives.json','primitives')]:
        assert read_json(OUT/name)[key]==json.loads(git('show',START+':docs/benchmarks/external-effects-catalog/'+name))[key];preserved[key]=len(read_json(OUT/name)[key])
    mutable={'docs/external-effects-catalog-research.md','scripts/external-effects/validate.py'}|{'docs/benchmarks/external-effects-catalog/'+n for n in ['effect-catalog.json','effect-sources.json','delivery-path-matrix.json','vanilla-comparison.json','behavior-primitives.json','mod-completion-ledger.json','research-decision.json','mod-reviews/iceandfire.json']}
    for line in git('diff','--name-status',START).splitlines():
        status,path=line.split('\t',1);assert status=='A' or (status=='M' and path in mutable),line
    for line in git('diff','--name-status',BASELINE).splitlines():
        status,path=line.split('\t',1);assert status=='A' and path.startswith(('docs/external-effects-catalog-research.md','docs/benchmarks/external-effects-catalog/','scripts/external-effects/')),line
    assert not d['review_required'] and not d['remaining_subsection_native_ambiguities'] and all(not d[k] for k in boundary_flags())
    git('diff','--check',BASELINE)
    return dict(schema='tno.external_effects.iaf_gorgon_integrity.v1',checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),reference_witnesses=len(r['witnesses']),caller_methods=len(c['rows']),reviewed_packages=4,delivery_paths=11,future_fixtures=len(d['unexecuted_future_fixtures']),ordering_source_and_hurt_return_checks='PASS',accepted_counts_preserved=preserved,prior_evidence_unchanged=True,whole_iceandfire_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_gorgon();write_json(OUT/'iceandfire-r2g4-integrity.json',d);print(json.dumps(d,indent=2))
