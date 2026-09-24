"""Final Bosses Rise promotion integrity; all protected native contracts remain immutable."""
from catalog_common import *
from complete_bossesrise import build,fact_text,KEY,CP,START,STEMS
VIEWS=[('effect-catalog.json','effects'),('effect-sources.json','sources'),('delivery-path-matrix.json','paths'),('vanilla-comparison.json','comparisons'),('behavior-primitives.json','primitives')]

def validate_final():
    r,m,f,c=build()
    for name,obj in [('mod-reviews/'+KEY+'.json',r),('bossesrise-final-promotion-map.json',m),('bossesrise-future-runtime-fixtures.json',f),('bossesrise-total-source-coverage.json',c)]:assert read_json(OUT/name)==obj,name
    assert r['status']=='COMPLETE' and r['decision']=='BOSSES_RISE_COMBAT_SEMANTIC_REVIEW_COMPLETE'
    assert not r['unresolved_native_ambiguities'] and r['review_required'] and f['review_required']==r['review_required']
    assert m['counts']==dict(input_packages=115,native_cases=232,final_mechanics=82,final_deliveries=232,aliased_input_packages=18,delivery_extensions=19,excluded_combat_cases=0)
    ids={x['id'] for x in r['effects']};pids={x['id'] for x in r['paths']};assert len(ids)==82 and len(pids)==232
    assert {x['path_id'] for x in f['fixtures']}==pids and all(x['runtime_status']=='NOT_RUN' for x in f['fixtures'])
    cache={}
    def checkref(ref):
        file=ref['evidence_file']
        if file not in cache:cache[file]={w['id']:w for w in read_json(OUT/file)['witnesses']}
        w=cache[file][ref['witness_id']];assert w['entry']==ref['entry'] and set(ref['methods'])<={x['name'] for x in w['methods']}
    assert len(c['watched_methods'])==157 and len(c['native_effect_reference_methods'])==18 and c['custom_damage_key_method_count']==6
    for row in c['watched_methods']+c['native_effect_reference_methods']:
        assert row['semantic_sections'] and row['implementation']
        for ref in row['implementation']:checkref(ref)
    assert len(c['custom_damage_types'])==2 and c['actual_custom_hurt_producers']==2
    for t in c['custom_damage_types']:
        assert t['disposition']=='USED' and t['requested_amount_formula'] and t['direct_entity'] and t['causing_entity'] and t['hurt_return_dependencies_and_secondary_callbacks']
        assert set(t['mechanic_ids'])<=ids and t['delivery_paths'] and set(t['delivery_paths'])<=pids
        assert len([x for x in t['callers'] if x['kind']=='ACTUAL_NATIVE_HURT_PRODUCER'])==1
    smash=next(t for t in c['custom_damage_types'] if t['id'].endswith(':kraken_tentacle_smash'))
    assert smash['direct_entity']=='KrakenTentacleEntity' and 'normally Kraken' in smash['causing_entity']
    witness=next(w for w in read_json(OUT/'native-evidence/bossesrise-kraken-offense.json')['witnesses'] if w['entry'].endswith('/KrakenTentacleEntity.class'))
    instructions=next(m['instructions'] for m in witness['methods'] if m['name']=='attackEntityWithSlam')
    native_owner=next(i['offset'] for i in instructions if '.getOwner(' in str(i.get('operand','')))
    native_source=next(i['offset'] for i in instructions if 'DamageSources.source(' in str(i.get('operand','')))
    assert native_owner<native_source and 'Lnet/minecraft/world/entity/Entity;Lnet/minecraft/world/entity/Entity;' in str(next(i['operand'] for i in instructions if i['offset']==native_source))
    for e in r['effects']:
        assert e['inspection_status']=='VERIFIED' and e['primary_classification'] in CLASSIFICATIONS and e['components'] and e['implementation'] and e['delivery_paths']
        assert e['stage_scaling_needed']==bool(e['single_scaling_point'])
        for ref in e['implementation']:checkref(ref)
        for ref in e['fact_references']:assert fact_text(ref['file'],ref['key']) in e['actual_behavior']
        assert not any('Gauntlet uses a genuine static shoot helper' in s for s in e['actual_behavior'])
    byid={e['id']:e for e in r['effects']}
    for p in r['paths']:
        assert set(p['labels'])<=set(DELIVERIES) and p['effect_ids'] and set(p['effect_ids'])<=ids
        assert all(p['id'] in byid[e]['delivery_paths'] for e in p['effect_ids'])
    assert 'br:equipment:boots_start_cancel' in byid['br:native_explosion_hp']['delivery_paths']
    assert 'br:equipment:chest_arrow' in byid['br:native_arrow_hp']['delivery_paths']
    assert 'br:equipment:sword_wave' in byid['br:sword_wave']['delivery_paths']
    assert 'br:equipment:saber_rook' in byid['br:native_timed_melee']['delivery_paths']
    assert not byid['br:roll_resource']['stage_scaling_needed'] and not byid['br:shared_death']['stage_scaling_needed']
    assert byid['br:kraken_trident_hit']['single_scaling_point']!=byid['br:kraken_trident_area']['single_scaling_point']
    preserved={};totals={}
    for name,key in VIEWS:
        old=json.loads(git('show',START+':docs/benchmarks/external-effects-catalog/'+name))[key];now=read_json(OUT/name)[key]
        assert [x for x in now if x['mod_key'] in {o['mod_key'] for o in old}]==old
        preserved[key]=len(old);totals[key]=len(now);br=[x for x in now if x['mod_key']==KEY]
        if key=='effects':assert br==r['effects']
        elif key=='paths':assert br==r['paths']
        elif key=='sources':
            assert {x['path_id'] for x in br}==pids
            for x,p in zip(br,r['paths']):assert x['effect_ids']==p['effect_ids'] and x['implementation']==p['implementation']
        elif key=='comparisons':assert {x['effect_id'] for x in br}==ids
        else:
            assert len(br)==sum(len(e['components']) for e in r['effects'])
            for e in r['effects']:
                for x,part in zip([v for v in br if v['effect_id']==e['id']],e['components']):assert all(x[k]==v for k,v in part.items())
    assert preserved==dict(effects=543,sources=1303,paths=1303,comparisons=543,primitives=717)
    assert next(t for t in read_json(OUT/'mod-completion-ledger.json')['targets'] if t['mod_key']==KEY)['state']=='COMPLETE'
    mutable={'docs/external-effects-catalog-research.md','scripts/external-effects/validate.py'}|{'docs/benchmarks/external-effects-catalog/'+n for n in [n for n,_ in VIEWS]+['mod-reviews/'+KEY+'.json','mod-completion-ledger.json','research-decision.json']}
    for line in git('diff','--name-status',START).splitlines():
        status,path=line.split('\t',1);assert status=='A' or (status=='M' and path in mutable),line
    for line in git('diff','--name-status',BASELINE).splitlines():
        status,path=line.split('\t',1);assert status=='A' and path.startswith(('docs/external-effects-catalog-research.md','docs/benchmarks/external-effects-catalog/','scripts/external-effects/')),line
    assert all(not r[k] and not f[k] for k in boundary_flags()) and r['runtime_tests']==0 and f['runtime_tests']==0
    git('diff','--check',BASELINE)
    return dict(schema='tno.external_effects.bossesrise_final_integrity.v1',baseline=BASELINE,checkpoint=CP,starting_sha=START,status='PASS',counts=m['counts'],custom_damage_types=2,actual_custom_hurt_producers=2,watched_methods=157,native_effect_references=18,accepted_counts_preserved=preserved,current_view_counts=totals,remaining_native_ambiguities=0,future_integration_review_items=len(r['review_required']),whole_bossesrise_complete=True,runtime_tests=0,**boundary_flags())
if __name__=='__main__':
    d=validate_final();write_json(OUT/'bossesrise-final-integrity.json',d);print(json.dumps(d,indent=2))
