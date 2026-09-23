"""ES partial sections: preserve accepted catalog rows until whole-mod promotion."""
from catalog_common import *
from assemble_batch import refresh

VIEWS=[('effect-catalog.json','effects'),('effect-sources.json','sources'),('delivery-path-matrix.json','paths'),('vanilla-comparison.json','comparisons'),('behavior-primitives.json','primitives')]

def save_section(d,stem,title):
    d.update(baseline=BASELINE,runtime_tests=0,whole_eternalstarlight_complete=False,promoted_mechanics=0,promoted_paths=0,**boundary_flags())
    d['reference_files']=[dict(file=f,sha256=sha256(OUT/f)) for f in d.pop('references')]
    write_json(OUT/(stem+'.json'),d)
    r=read_json(OUT/'mod-reviews/eternalstarlight.json');r.update(checkpoint=d['checkpoint'],scope=d['scope'],notes_file=stem+'.json',exact_next_task=d['exact_next_task']);write_json(OUT/'mod-reviews/eternalstarlight.json',r);refresh(d['checkpoint'])
    for f,_ in VIEWS:
        o=read_json(OUT/f);o.update(checkpoint=d['checkpoint'],unfinished_review=dict(mod_key='eternalstarlight',status='PARTIAL',promoted_records=0,notes_file=stem+'.json'));write_json(OUT/f,o)
    o=read_json(OUT/'research-decision.json');o.update(checkpoint=d['checkpoint'],next_task=d['exact_next_task'],latest_eternalstarlight_subsection_decision=d['status'],save_mode=False,save_reason=None);o['checkpoints'][d['previous_checkpoint']]=d['starting_sha'];o['checkpoints'][d['checkpoint']]='Self: exact SHA from commit/live verification.';write_json(OUT/'research-decision.json',o)
    lines=['# '+title,'',d['scope'],'','Static subsection complete. Runtime fixtures remain unexecuted; no Stage or production implementation.','']
    for k,v in d['facts'].items():lines+=['## '+k.replace('_',' ').capitalize(),'',v,'']
    lines+=['## TNO integration decisions','']
    for m in d['mechanic_packages']:lines+=['- **'+m['name']+'**: '+', '.join(m['tno_categories'])+'. Stage: '+(m['single_scaling_point'] if m['stage_scaling_needed'] else 'no additional multiplier; '+m['stage_reason'])]
    lines+=['','[Machine-readable packages, delivery paths and future fixtures]('+stem+'.json). Exact archive/method witnesses and targeted semantic assertions are reproducible. No whole-mod completion claim.','','Exact next task: '+d['exact_next_task'],'']
    (OUT/(stem+'-review.md')).write_text('\n'.join(lines),encoding='utf-8')
    main=ROOT/'docs/external-effects-catalog-research.md';s=main.read_text(encoding='utf-8');heading='## '+title
    if heading not in s:s+='\n'+heading+'\n\n'+d['summary']+' [Evidence, decisions and resume point](benchmarks/external-effects-catalog/'+stem+'-review.md).\n'
    main.write_text(s,encoding='utf-8')

def preserve_section(d):
    for r in d['reference_files']:assert sha256(OUT/r['file'])==r['sha256'],r['file']
    ids={p['id'] for p in d['delivery_paths']};assert len(ids)==len(d['delivery_paths'])
    for m in d['mechanic_packages']:
        assert m['primary_classification'] in CLASSIFICATIONS
        assert set(m['tno_categories'])<={'NUMERIC_SCALABLE','BINARY','COMPOSITE','VANILLA_ROUTED','CUSTOM_ROUTED','ADMISSION_GATED','NO_STAGE_VALUE'}
        assert bool(m['single_scaling_point'])==m['stage_scaling_needed'] and set(m['delivery_paths'])<=ids
    preserved={}
    for f,key in VIEWS:
        old=json.loads(git('show',d['starting_sha']+':docs/benchmarks/external-effects-catalog/'+f))[key]
        current=read_json(OUT/f)[key];assert [r for r in current if r['mod_key'] in {x['mod_key'] for x in old}]==old;preserved[key]=len(old)
    mutable={'docs/external-effects-catalog-research.md','scripts/external-effects/validate.py'}|{'docs/benchmarks/external-effects-catalog/'+n for n in [f for f,_ in VIEWS]+['mod-completion-ledger.json','research-decision.json','mod-reviews/eternalstarlight.json']}
    for line in git('diff','--name-status',d['starting_sha']).splitlines():
        status,path=line.split('\t',1);assert status=='A' or (status=='M' and path in mutable),line
    allowed=('docs/external-effects-catalog-research.md','docs/benchmarks/external-effects-catalog/','scripts/external-effects/')
    for line in git('diff','--name-status',BASELINE).splitlines():
        status,path=line.split('\t',1);assert status=='A' and path.startswith(allowed),line
    for path in git('ls-files','--others','--exclude-standard').splitlines():assert path.startswith(allowed),path
    assert all(not d[k] for k in boundary_flags()) and d['runtime_tests']==0
    git('diff','--check',BASELINE)
    return preserved
