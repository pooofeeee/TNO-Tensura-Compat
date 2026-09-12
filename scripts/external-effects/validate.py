"""Validate research scope, pinned JARs and catalog referential integrity; no runtime."""
import argparse
from catalog_common import *

def validate():
    inventory=read_json(OUT/'jar-inventory.json')
    assert inventory['baseline']==BASELINE
    assert len(inventory['targets'])==23
    assert {(t['key'],t['filename']) for t in inventory['targets']}==set(TARGETS)
    for target in inventory['targets']+inventory['compat_candidates']:
        if target['status']=='UNAVAILABLE': continue
        assert Path(target['path']).name==target['filename']
        assert sha256(target['path'])==target['sha256'], 'Installed JAR changed: '+target['filename']
        with zipfile.ZipFile(target['path']) as jar:
            for meta in target['metadata']:
                assert byte_hash(jar.read(meta['entry']))==meta['sha256']
    decision=read_json(OUT/'research-decision.json')
    for key in boundary_flags(): assert decision[key] is False, key
    assert decision['baseline']==BASELINE
    files=['effect-catalog.json','effect-sources.json','delivery-path-matrix.json','vanilla-comparison.json','behavior-primitives.json']
    records={name:read_json(OUT/name) for name in files}
    for obj in records.values(): assert obj['baseline']==BASELINE
    catalog=records['effect-catalog.json']
    for ref in catalog['existing_tno_coverage']:
        assert ref['coverage']=='TENSURA_NATIVE_EXISTING_TNO_COVERAGE' and ref['repeat_research'] is False
        assert git('rev-parse',ref['revision']+':'+ref['path'])==ref['git_blob']
    ids=[e['id'] for e in catalog['effects']]
    assert len(ids)==len(set(ids)), 'Duplicate effect id'
    for effect in catalog['effects']:
        if effect.get('primary_classification') is not None:
            assert effect['primary_classification'] in CLASSIFICATIONS
        assert effect['mod_key'] in {key for key,_ in TARGETS if key!='tensura'}
    # All pre-existing files, including Phase 6 and the readiness assessment, are immutable here.
    allowed=('docs/external-effects-catalog-research.md','docs/benchmarks/external-effects-catalog/','scripts/external-effects/')
    for line in git('diff','--name-status',BASELINE).splitlines():
        status,path=line.split('\t',1)
        assert status=='A' and path.startswith(allowed), 'Out-of-scope change: '+line
    for path in git('ls-files','--others','--exclude-standard').splitlines():
        assert path.startswith(allowed), 'Out-of-scope untracked file: '+path
    git('diff','--check',BASELINE)
    if decision['status']=='COMPLETE':
        assert decision['decision']=='EXTERNAL_EFFECT_CATALOG_READY_FOR_OWNER_REVIEW'
        assert decision['effect_coverage_complete'] and decision['delivery_coverage_complete']
        assert all(obj['status']=='COMPLETE' for obj in records.values())
        assert all(e.get('inspection_status')=='VERIFIED' for e in catalog['effects'])
    return dict(schema='tno.external_effects.validation.v1',status='PASS',checkpoint=decision['checkpoint'],
        target_jars=len(inventory['targets']),available=inventory['inspected_inventory_count'],
        unavailable=inventory['unavailable_count'],compat_candidates=len(inventory['compat_candidates']),
        catalog_effects=len(ids),complete=decision['status']=='COMPLETE',**boundary_flags())

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--report',required=True); args=parser.parse_args()
    report=validate(); write_json(OUT/args.report,report); print(json.dumps(report,indent=2))
