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
    if (OUT/'discovery-scan.json').exists():
        from audit_discovery import audit
        assert audit()==read_json(OUT/'discovery-audit.json'), 'Discovery audit stale'
        from native_evidence import collect
        from assemble_native import assemble
        for path in (OUT/'native-findings').glob('*.json'):
            document=read_json(path)
            assert collect(document)==read_json(OUT/'native-evidence'/path.name), 'Native witness changed: '+path.name
            known={e['id'] for e in document['evidence_specifications']}
            for finding in document['findings']:
                assert set(finding['evidence_ids'])<=known
        assert catalog['effects']==assemble(), 'Catalog does not match native findings'
        compat_path=OUT/'compat-findings'/'antarchy-tensura-data.json'
        if compat_path.exists():
            compat=read_json(compat_path)
            target=next(t for t in inventory['compat_candidates'] if t['key']==compat['mod_key'])
            assert target['sha256']==compat['compat_jar_sha256']
            assert compat['definitions']==len(compat['entries'])
            with zipfile.ZipFile(target['path']) as jar:
                for entry in compat['entries']:
                    raw=jar.read(entry['entry'])
                    assert byte_hash(raw)==entry['sha256'] and json.loads(raw)==entry['data']
        parser=read_json(OUT/'parser-validation.json')
        assert parser['status']=='PASS' and parser['tests']==5 and not parser['failures'] and not parser['errors']
        notes=OUT/'partial-notes'/'cultofazazel.json'
        if notes.exists():
            assert collect(read_json(notes))==read_json(OUT/'native-evidence'/'cultofazazel-partial.json')
        for notes in (OUT/'partial-notes').glob('*-r2c*.json'):
            document=read_json(notes)
            assert collect(document)==read_json(OUT/'native-evidence'/notes.name)
            known={e['id'] for e in document['evidence_specifications']}
            for finding in document['findings']:
                assert set(finding.get('source_witness_ids',[]))<=known
        for config_path in (OUT/'config-evidence').glob('*.json'):
            import tomllib
            config=read_json(config_path)
            assert config['baseline']==BASELINE
            assert sha256(config['path'])==config['sha256'], 'Installed config changed: '+config['path']
            assert Path(config['path']).read_bytes().decode('utf-8-sig')==config['text']
            assert tomllib.loads(config['text'])==config['values']
        cult_continuation=OUT/'native-evidence/cultofazazel-r2c2.json'
        if cult_continuation.exists():
            witnesses=read_json(cult_continuation)['witnesses']
            config=next(w for w in witnesses if w['id']=='coa2-config')
            instructions=config['methods'][0]['instructions']
            builds=[i['offset'] for i in instructions if 'ModConfigSpec$Builder.build(' in str(i.get('operand'))]
            defines=[i['offset'] for i in instructions if 'ModConfigSpec$Builder.define' in str(i.get('operand'))]
            assert len(builds)==1 and defines and max(defines)<builds[0], 'Use actual bytecode initialization order'
        vanilla_spec=OUT/'vanilla-specifications'/'variants-prerequisites.json'
        if vanilla_spec.exists():
            from vanilla_reference import prepare
            raw=read_json(OUT/'vanilla-evidence'/'variants-prerequisites.json')
            assert prepare(read_json(vanilla_spec))==raw, 'Raw vanilla witness changed'
            poison=next(c for c in raw['classes'] if c['class_name'].endswith('/PoisonMobEffect'))
            tick=next(m for m in poison['methods'] if m['name']=='applyEffectTick')
            assert any(i['operand']=='net/minecraft/world/damagesource/DamageSources.magic()Lnet/minecraft/world/damagesource/DamageSource;' for i in tick['instructions'])
            loader=read_json(OUT/'instance-loader-reference.json')
            assert sha256(loader['manifest_path'])==loader['manifest_sha256']
            for artifact in loader['artifacts']: assert sha256(artifact['path'])==artifact['sha256']
        for spec_path in (OUT/'reference-specifications').glob('*.json'):
            from selected_reference import collect as collect_reference
            assert collect_reference(read_json(spec_path))==read_json(OUT/'reference-evidence'/spec_path.name)
        for spec_path in (OUT/'vanilla-specifications').glob('*.json'):
            assert prepare(read_json(spec_path))==read_json(OUT/'vanilla-evidence'/spec_path.name)
        reviews=[read_json(p) for p in (OUT/'mod-reviews').glob('*.json')]
        paths=records['delivery-path-matrix.json']['paths']
        assert len({p['id'] for p in paths})==len(paths)
        path_ids={p['id'] for p in paths}
        for review in reviews:
            assert review['baseline']==BASELINE
            if review['status']=='COMPLETE':
                assert all(review[k] for k in ('semantic_discovery_complete','special_damage_discovery_complete','source_mapping_complete','delivery_mapping_complete'))
                for e in review['effects']:
                    assert e['inspection_status']=='VERIFIED' and e['primary_classification'] in CLASSIFICATIONS
                    assert e['components'] and e['implementation'] and e['primary_test_source']
                    assert set(e['delivery_paths'])<=path_ids
            for p in review['paths']:
                assert set(p['labels'])<=set(DELIVERIES) and set(p['effect_ids'])<=set(ids)
        if reviews:
            ledger=read_json(OUT/'mod-completion-ledger.json')
            assert {t['mod_key'] for t in ledger['targets']}=={k for k,_ in TARGETS}
            assert len(ledger['targets'])==23
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
