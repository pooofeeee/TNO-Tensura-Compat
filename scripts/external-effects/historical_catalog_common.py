"""Shared historical research helpers; repaired canonical state takes precedence."""
from catalog_common import *
import assemble_batch
from assemble_batch import refresh
VIEWS=[('effect-catalog.json','effects'),('effect-sources.json','sources'),('delivery-path-matrix.json','paths'),('vanilla-comparison.json','comparisons'),('behavior-primitives.json','primitives')]

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

def preserve_section(d, KEY):
    if read_json(OUT/'mod-reviews'/str(KEY+'.json')).get('integrity_checkpoint'):
        from validate_current_integrity import validate_mod
        return validate_mod(KEY)
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
