"""Shared independent validation after the historical promotion builders retire."""
import hashlib
import json
import subprocess

from catalog_common import OUT, ROOT, read_json
from audit_catalog_integrity import audit_review, EvidenceIndex


def digest(row):
    return hashlib.sha256(json.dumps(row,sort_keys=True,ensure_ascii=False).encode()).hexdigest()


def validate_mod(mod_key):
    review=read_json(OUT/'mod-reviews'/str(mod_key+'.json'))
    result=audit_review(review,EvidenceIndex())
    target=next(t for t in read_json(OUT/'mod-completion-ledger.json')['targets'] if t['mod_key']==mod_key)
    assert review['status']==target['state']=='COMPLETE'
    assert result['semantic_records']==target['semantic_effect_count']
    assert result['numeric_candidate_entries']==target['numeric_candidate_count']
    return result


def validate_external_dependency_contracts(review, census, dependency=None):
    """Require pinned bodies and reciprocal native callers for resolved dependencies."""
    import tomllib
    from reconcile_native_census import method_key
    from collect_combat_census import decode_sites
    dep=dependency or read_json(OUT/review['external_dependency_obligations_file'])
    assert dep['mod_key']==review['mod_key'] and dep['native_jar_sha256']==census['jar_sha256']
    artifact=dep['artifact']
    assert artifact['status']=='AVAILABLE_VERIFIED' and artifact['installed_identity_confirmed_by_owner']
    inventory=read_json(OUT/'jar-inventory.json')
    pin=next(p for p in inventory.get('dependency_artifacts',[]) if p['key']==artifact['mod_id'])
    assert pin['sha256']==artifact['sha256'] and pin['version']==artifact['exact_installed_version']
    assert pin['filename']==artifact['filename'] and pin['size_bytes']==artifact['size_bytes']
    evidence=EvidenceIndex()
    packet=evidence.read(dep['evidence_file'])
    assert packet['witnesses'] and all(w['jar_sha256']==pin['sha256'] for w in packet['witnesses'])
    metadata=next(w for w in packet['witnesses'] if w['entry']==artifact['metadata_entry'])
    mods=tomllib.loads(metadata['text'])['mods']
    assert any(m['modId']==artifact['mod_id'] and m['version']==pin['version'] for m in mods)
    native={method_key(m):m for m in census['methods']}
    rows={e['id']:e for e in review['effects']}
    ids={o['id'] for o in dep['obligations']}
    assert len(ids)==len(dep['obligations']) and ids and dep['status']=='COMPLETE'
    traced=set()
    for o in dep['obligations']:
        assert o['status']=='RESOLVED_PINNED' and o['reason'] and o['contract']['actual_behavior']
        assert o['evidence'] and o['native_boundary_calls'] and o['affected_mechanic_ids']
        for proof in o['evidence']:
            _,w=evidence.witness(proof,dict(id=o['id']))
            assert w['jar_sha256']==pin['sha256']
            traced.add(w['entry'])
        for rid in o['affected_mechanic_ids']:
            row=rows[rid];ref=row['external_dependency_contracts']
            assert ref['file']==review['external_dependency_obligations_file']
            assert o['id'] in ref['ids'] and set(ref['ids']) <= ids
            assert ref['pin_sha256']==pin['sha256'] and not row['unresolved_ambiguities']
        for call in o['native_boundary_calls']:
            for site in call['sites']:
                method=native[method_key(site)]
                assert any(i['offset']==site['offset'] and i['operand']==call['symbol']
                           for i in decode_sites(census,method,'calls')), 'Unproven external caller'
    # Every captured dependency entry is relevant to a named obligation or its pin.
    assert {w['entry'] for w in packet['witnesses']} <= traced | {artifact['metadata_entry']}
    return dict(status='PASS',resolved_dependency_groups=len(ids),pin_sha256=pin['sha256'])


def validate_native_scope_closure(mod_key):
    """Validate a finite native closure independently of its saved totals.

    A dependency-blocked PARTIAL mod can finish its native scope; this never
    promotes it to COMPLETE or proves the external implementation.
    """
    from reconcile_native_census import reconcile,method_key
    from collect_combat_census import decode_sites
    review=read_json(OUT/'mod-reviews'/f'{mod_key}.json')
    census=read_json(OUT/f'{mod_key}-combat-census.json')
    summary=audit_review(review,EvidenceIndex())
    index,pending=reconcile(review,census)
    assert not pending, 'Unresolved finite native methods'
    target=next(t for t in read_json(OUT/'mod-completion-ledger.json')['targets'] if t['mod_key']==mod_key)
    assert review['status']==target['state']
    for field,key in [('semantic_effect_count','semantic_records'),
                      ('numeric_candidate_count','numeric_candidate_entries'),
                      ('classification_counts','classification_counts')]:
        assert target[field]==summary[key], ('stale canonical totals',field)
    assert target['pending_native_method_count']==target['pending_semantic_method_count']==0
    note=read_json(OUT/review['native_closure_file'])
    assert note['canonical_summary']==summary
    assert note['finite_census']['dispositions']==index['summary']
    assert note['native_jar_sha256']==census['jar_sha256']
    assert note['independent_native_status']=='COMPLETE'
    native={method_key(m):m for m in census['methods']}
    dependency_count=0
    if review['status']=='PARTIAL':
        dep=read_json(OUT/review['external_dependency_obligations_file'])
        assert dep['mod_key']==mod_key and dep['native_jar_sha256']==census['jar_sha256']
        assert dep['artifact']['status']=='UNAVAILABLE' and dep['artifact']['sha256'] is None
        obligations=dep['obligations'];dependency_count=len(obligations)
        assert obligations and len({o['id'] for o in obligations})==dependency_count
        for o in obligations:
            assert o['status']=='BLOCKED_EXACT_ARTIFACT_UNAVAILABLE' and o['reason']
            assert o['native_boundary_calls'] and o['affected_mechanic_ids']
            assert set(o['affected_mechanic_ids']) <= {e['id'] for e in review['effects']}
            for call in o['native_boundary_calls']:
                assert call['sites']
                for site in call['sites']:
                    m=native[method_key(site)]
                    assert any(i['offset']==site['offset'] and i['operand']==call['symbol']
                               for i in decode_sites(census,m,'calls')), 'Unproven external boundary'
        assert note['blocked_dependency_groups']==target['blocked_external_dependency_count']==dependency_count
        assert review['unresolved_native_ambiguities']==review['remaining_native_ambiguities']==dependency_count
        assert not review['external_dependency_complete']
    else:
        assert review['status']=='COMPLETE' and review['external_dependency_complete']
        if review.get('external_dependency_obligations_file'):
            result=validate_external_dependency_contracts(review,census)
            assert note['resolved_dependency_groups']==target['resolved_external_dependency_count']==result['resolved_dependency_groups']
            assert note['blocked_dependency_groups']==target['blocked_external_dependency_count']==0
            assert review['unresolved_native_ambiguities']==review['remaining_native_ambiguities']==0
            assert all(not e.get('unresolved_ambiguities') for e in review['effects'])
    return dict(summary,native_dispositions=index['summary'],
                blocked_dependency_groups=dependency_count)


def validate_cataclysm_repairs():
    report=read_json(OUT/'catalog-integrity-repairs.json')
    review=read_json(OUT/'mod-reviews/cataclysm.json')
    path=(OUT/'mod-reviews/cataclysm.json').relative_to(ROOT).as_posix()
    before=json.loads(subprocess.check_output(['git','show',report['starting_sha']+':'+path],cwd=ROOT))
    old={r['id']:r for r in before['effects']};current={r['id']:r for r in review['effects']}
    declared={r['original_id']:r for r in report['canonical_record_changes']['cataclysm']}
    aliases={a['original_id']:a['canonical_ids'] for a in review['semantic_aliases']}
    excluded={c.get('original_id') for c in review['native_context_records']}
    for rid,row in old.items():
        if rid in current and row==current[rid]:
            continue
        change=declared[rid]
        assert change['before_sha256']==digest(row)
        if rid in current:
            assert change['after_sha256']==digest(current[rid])
        else:
            assert rid in aliases or rid in excluded
            assert change['after_sha256'] is None
    assert subprocess.check_output(['git','rev-parse','codex/production-continuation'],cwd=ROOT,text=True).strip()==report['protected_production_sha']
    # All existing native bytecode remains independently locked; mutable
    # canonical records are repaired explicitly rather than blindly frozen.
    for item in report['protected_native_files']:
        assert hashlib.sha256((OUT/item['file']).read_bytes()).hexdigest()==item['sha256']
    return validate_mod('cataclysm')
