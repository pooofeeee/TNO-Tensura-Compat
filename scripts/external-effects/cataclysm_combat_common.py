"""Cataclysm partial reviews; all accepted owner tables stay immutable."""
from catalog_common import *
import assemble_batch
from assemble_batch import refresh

def write_json(path,obj):
    import time
    from catalog_common import write_json as write_once
    for attempt in range(5):
        try:return write_once(path,obj)
        except OSError as error:
            if error.errno!=22 or attempt==4:raise
            time.sleep(.1)

def refresh_safe(checkpoint):
    prior=assemble_batch.write_json
    assemble_batch.write_json=write_json
    try:refresh(checkpoint)
    finally:assemble_batch.write_json=prior

KEY='cataclysm'
VIEWS=[('effect-catalog.json','effects'),('effect-sources.json','sources'),('delivery-path-matrix.json','paths'),('vanilla-comparison.json','comparisons'),('behavior-primitives.json','primitives')]

def save_section(d,stem,title):
    d.update(baseline=BASELINE,mod_key=KEY,runtime_tests=0,whole_mod_complete=False,promoted_mechanics=0,promoted_paths=0,**boundary_flags())
    d['reference_files']=[dict(file=f,sha256=sha256(OUT/f)) for f in d.pop('references')]
    write_json(OUT/(stem+'.json'),d)
    p=OUT/'mod-reviews'/f'{KEY}.json'
    r=read_json(p) if p.exists() else dict(schema='tno.external_effects.mod_review.v1',baseline=BASELINE,mod_key=KEY,status='PARTIAL',semantic_discovery_complete=False,special_damage_discovery_complete=False,source_mapping_complete=False,delivery_mapping_complete=False,effects=[],paths=[],unresolved_native_ambiguities=None,remaining_native_ambiguities=None)
    r.update(checkpoint=d['checkpoint'],scope=d['scope'],notes_file=stem+'.json',exact_next_task=d['exact_next_task']);write_json(p,r);refresh_safe(d['checkpoint'])
    for f,_ in VIEWS:
        o=read_json(OUT/f);o.update(checkpoint=d['checkpoint'],unfinished_review=dict(mod_key=KEY,status='PARTIAL',promoted_records=0,notes_file=stem+'.json'));write_json(OUT/f,o)
    o=read_json(OUT/'research-decision.json');o.update(checkpoint=d['checkpoint'],next_task=d['exact_next_task'],latest_cataclysm_decision=d['status'],save_mode=False,save_reason=None);o['checkpoints'][d['previous_checkpoint']]=d['starting_sha'];o['checkpoints'][d['checkpoint']]='Self: exact SHA from commit/live verification.';write_json(OUT/'research-decision.json',o)
    lines=['# '+title,'',d['scope'],'','Static review only. Future runtime fixtures remain unexecuted; whole Cataclysm review is PARTIAL.','']
    for k,v in d['facts'].items():lines+=['## '+k.replace('_',' ').capitalize(),'',v,'']
    for m in d.get('mechanic_packages',[]):lines+=['- **'+m['name']+'**: '+', '.join(m['tno_categories'])+'. Stage: '+(m['single_scaling_point'] if m['stage_scaling_needed'] else m['stage_reason'])]
    lines+=['','[Machine evidence, packages and native paths]('+stem+'.json).','','Exact next task: '+d['exact_next_task'],'']
    (OUT/(stem+'-review.md')).write_text('\n'.join(lines),encoding='utf-8')
    main=ROOT/'docs/external-effects-catalog-research.md';s=main.read_text(encoding='utf-8');h='## '+title
    if h not in s:s+='\n'+h+'\n\n'+d['summary']+' [Evidence and resume point](benchmarks/external-effects-catalog/'+stem+'-review.md).\n'
    main.write_text(s,encoding='utf-8')

def preserve_section(d):
    for r in d['reference_files']:assert sha256(OUT/r['file'])==r['sha256'],r['file']
    paths=d.get('delivery_paths',[]);ids={p['id'] for p in paths};assert len(ids)==len(paths)
    for m in d.get('mechanic_packages',[]):
        assert m['primary_classification'] in CLASSIFICATIONS
        assert set(m['tno_categories'])<={'NUMERIC_SCALABLE','BINARY','COMPOSITE','VANILLA_ROUTED','CUSTOM_ROUTED','ADMISSION_GATED','NO_STAGE_VALUE'}
        assert bool(m['single_scaling_point'])==m['stage_scaling_needed'] and set(m['delivery_paths'])<=ids
    preserved={}
    for f,key in VIEWS:
        old=json.loads(git('show',d['starting_sha']+':docs/benchmarks/external-effects-catalog/'+f))[key];now=read_json(OUT/f)[key]
        assert [r for r in now if r['mod_key'] in {x['mod_key'] for x in old}]==old;preserved[key]=len(old)
    mutable={'docs/external-effects-catalog-research.md','scripts/external-effects/validate.py'}|{'docs/benchmarks/external-effects-catalog/'+n for n in [f for f,_ in VIEWS]+['mod-completion-ledger.json','research-decision.json','mod-reviews/'+KEY+'.json']}
    for line in git('diff','--name-status',d['starting_sha']).splitlines():
        status,path=line.split('\t',1);assert status=='A' or (status=='M' and path in mutable),line
    allowed=('docs/external-effects-catalog-research.md','docs/benchmarks/external-effects-catalog/','scripts/external-effects/')
    for line in git('diff','--name-status',BASELINE).splitlines():
        status,path=line.split('\t',1);assert status=='A' and path.startswith(allowed),line
    for path in git('ls-files','--others','--exclude-standard').splitlines():assert path.startswith(allowed),path
    assert not any(d[k] for k in boundary_flags()) and d['runtime_tests']==0
    git('diff','--check',BASELINE)
    return preserved
