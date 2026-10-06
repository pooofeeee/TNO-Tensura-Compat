"""Bosses of Mass Destruction partial reviews; all accepted owner tables stay immutable."""
from historical_catalog_common import write_json, refresh_safe, preserve_section as preserve_historical_section
from catalog_common import *
import assemble_batch
from assemble_batch import refresh



KEY='bosses_of_mass_destruction'
VIEWS=[('effect-catalog.json','effects'),('effect-sources.json','sources'),('delivery-path-matrix.json','paths'),('vanilla-comparison.json','comparisons'),('behavior-primitives.json','primitives')]

def save_section(d,stem,title):
    if read_json(OUT/'mod-reviews'/str(KEY+'.json')).get('integrity_checkpoint'):
        raise RuntimeError('Completed canonical review is protected from historical Stage-routing publication.')
    d.update(baseline=BASELINE,mod_key=KEY,runtime_tests=0,whole_mod_complete=False,promoted_mechanics=0,promoted_paths=0,**boundary_flags())
    d['reference_files']=[dict(file=f,sha256=sha256(OUT/f)) for f in d.pop('references')]
    write_json(OUT/(stem+'.json'),d)
    p=OUT/'mod-reviews'/f'{KEY}.json'
    r=read_json(p) if p.exists() else dict(schema='tno.external_effects.mod_review.v1',baseline=BASELINE,mod_key=KEY,status='PARTIAL',semantic_discovery_complete=False,special_damage_discovery_complete=False,source_mapping_complete=False,delivery_mapping_complete=False,effects=[],paths=[],unresolved_native_ambiguities=None,remaining_native_ambiguities=None)
    r.update(checkpoint=d['checkpoint'],scope=d['scope'],notes_file=stem+'.json',exact_next_task=d['exact_next_task']);write_json(p,r);refresh_safe(d['checkpoint'])
    for f,_ in VIEWS:
        o=read_json(OUT/f);o.update(checkpoint=d['checkpoint'],unfinished_review=dict(mod_key=KEY,status='PARTIAL',promoted_records=0,notes_file=stem+'.json'));write_json(OUT/f,o)
    o=read_json(OUT/'research-decision.json');o.update(checkpoint=d['checkpoint'],next_task=d['exact_next_task'],latest_bomd_decision=d['status'],save_mode=False,save_reason=None);o['checkpoints'][d['previous_checkpoint']]=d['starting_sha'];o['checkpoints'][d['checkpoint']]='Self: exact SHA from commit/live verification.';write_json(OUT/'research-decision.json',o)
    lines=['# '+title,'',d['scope'],'','Static review only. Future runtime fixtures remain unexecuted; whole Bosses of Mass Destruction review is PARTIAL.','']
    for k,v in d['facts'].items():lines+=['## '+k.replace('_',' ').capitalize(),'',v,'']
    for m in d.get('mechanic_packages',[]):lines+=['- **'+m['name']+'**: '+', '.join(m['tno_categories'])+'. Stage: '+(m['single_scaling_point'] if m['stage_scaling_needed'] else m['stage_reason'])]
    lines+=['','[Machine evidence, packages and native paths]('+stem+'.json).','','Exact next task: '+d['exact_next_task'],'']
    (OUT/(stem+'-review.md')).write_text('\n'.join(lines),encoding='utf-8')
    main=ROOT/'docs/external-effects-catalog-research.md';s=main.read_text(encoding='utf-8');h='## '+title
    if h not in s:s+='\n'+h+'\n\n'+d['summary']+' [Evidence and resume point](benchmarks/external-effects-catalog/'+stem+'-review.md).\n'
    main.write_text(s,encoding='utf-8')

def preserve_section(d):
    return preserve_historical_section(d, KEY)
