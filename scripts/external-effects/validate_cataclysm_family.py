"""Focused structural, native-boundary and protection checks for one family checkpoint."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess

from catalog_common import ROOT, OUT, read_json
from collect_cataclysm_family import collect

CLASSIFICATIONS = {'VANILLA_DIRECT', 'VANILLA_EQUIVALENT', 'VANILLA_LIKE_EXTENDED',
                   'VANILLA_COMPOSITE', 'CUSTOM_DAMAGE', 'CUSTOM_STATUS', 'CUSTOM_CONTROL',
                   'CUSTOM_RESOURCE', 'BINARY_MECHANIC'}


def at_start(note, path):
    return subprocess.check_output(['git', 'show', note['starting_sha'] + ':' +
        path.relative_to(ROOT).as_posix()], cwd=ROOT)


def records(note):
    review = read_json(OUT / 'mod-reviews/cataclysm.json')
    by_id = {r['id']: r for r in review['effects']}
    assert len(by_id) == len(review['effects'])
    return review, [by_id[key] for key in note['mechanic_ids']]


def validate_records(note):
    review, rows = records(note)
    assert note['status'] == 'PARTIAL' and review['status'] == 'PARTIAL'
    assert len(set(note['mechanic_ids'])) == len(rows) == note['mechanics_closed']
    paths = {p['id']: p for p in review['paths']}
    assert len(paths) == len(review['paths'])
    for row in rows:
        assert row['review_checkpoint'] == note['checkpoint']
        assert row['primary_classification'] in CLASSIFICATIONS
        for field in ['actual_behavior', 'source_actor', 'hurt_return_dependency', 'primary_test_source', 'delivery_paths', 'implementation']:
            assert row[field], (row['id'], field)
        assert row['inspection_status'] == 'STATIC_REVIEWED' and not row['unresolved_ambiguities']
        for path in row['delivery_paths']:
            assert row['id'] in paths[path]['effect_ids'] and paths[path]['status'] == 'VERIFIED'
        observations = {(o['primitive'], o['parameter']): o for o in row['numeric_observations']}
        assert len(observations) == len(row['numeric_observations'])
        seen = set()
        for candidate in row['scalable_parameter_candidates']:
            assert candidate['parameters']
            for parameter in candidate['parameters']:
                key = (candidate['primitive'], parameter)
                assert key not in seen and key in observations
                seen.add(key)
                observation = observations[key]
                assert any(c['primitive'] == key[0] and
                           parameter in (set(c['numerical_parameters']) | set(c.get('parameter_formulas', {})))
                           for c in row['components'])
                assert candidate['native_value'] == observation['native_value']
                assert candidate['native_formula'] == observation['native_formula']
                assert candidate['units'] == observation['units']
                assert candidate['native_boundary'] == observation['boundary']
        for proof in row['implementation']:
            evidence = read_json(OUT / proof['evidence_file'])
            # Reference archives identify the artifact, then the exact class entry;
            # native archives identify each class witness separately.
            if proof.get('evidence_format') == 'VANILLA_COMPARISON':
                assert evidence['version'] == '1.21.1'
                witness = next(w for w in evidence['classes']
                               if w['class_name'] == proof['witness_id']
                               and w['raw_entry'] == proof['entry'])
                assert witness['raw_entry'] == proof['entry']
            else:
                witness = next(w for w in evidence['witnesses']
                               if w.get('id', evidence.get('id')) == proof['witness_id']
                               and w['entry'] == proof['entry'])
                assert witness['entry'] == proof['entry']
            assert set(proof['methods']) <= {m['name'] for m in witness['methods']}
    assert dict(sorted(Counter(r['primary_classification'] for r in rows).items())) == note['classification_counts']
    assert sum(len(c['parameters']) for r in rows for c in r['scalable_parameter_candidates']) == note['candidate_numeric_parameter_count']
    assert note['unresolved_ambiguities'] == []
    for expected in note.get('semantic_expectations', []):
        row = next(r for r in rows if r['id'] == expected['id'])
        for key, value in expected['fields'].items():
            assert row[key] == value, (row['id'], key)


def validate_boundaries(note):
    evidence = read_json(OUT / note['evidence_file'])
    for check in note['native_boundary_assertions']:
        witness = next(w for w in evidence['witnesses'] if w['entry'] == check['entry'])
        method = next(m for m in witness['methods'] if m['name'] == check['method'] and
                      ('descriptor' not in check or m['descriptor'] == check['descriptor']))
        for expected in check.get('instructions', []):
            actual = next(i for i in method['instructions'] if i['offset'] == expected['offset'])
            assert all(actual.get(k) == v for k, v in expected.items()), (check, expected, actual)
        text = json.dumps(method['instructions'])
        for term in check.get('contains', []):
            assert term in text, (check, term)
        for term in check.get('excludes', []):
            assert term not in text, (check, term)
    for check in note.get('declared_method_checks', []):
        witness = next(w for w in evidence['witnesses'] if w['entry'] == check['entry'])
        assert set(check.get('absent', [])).isdisjoint(witness['declared_method_names'])
    for check in note.get('bootstrap_assertions', []):
        witness = next(w for w in evidence['witnesses'] if w['entry'] == check['entry'])
        bootstrap = next(b for b in witness['registration_bootstraps'] if b['index'] == check['index'])
        assert bootstrap['arguments'] == check['arguments']
    if note.get('evidence_mode') == 'LOCKED_REUSE':
        assert note['new_class_witnesses'] == 0
        assert any(ref['file'] == note['evidence_file'] and ref['usage'] == 'LOCKED_REUSED'
                   for ref in note['reference_files'])
    else:
        assert len(evidence['witnesses']) == note['new_class_witnesses']


def validate_protection(note):
    review, rows = records(note)
    original = json.loads(at_start(note, OUT / 'mod-reviews/cataclysm.json'))
    current = {r['id']: r for r in review['effects']}
    current_paths = {r['id']: r for r in review['paths']}
    assert all(current[r['id']] == r for r in original['effects'])
    assert all(current_paths[r['id']] == r for r in original['paths'])
    assert original['checkpoint'] == note['previous_checkpoint']
    for ref in note['reference_files']:
        path = OUT / ref['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == ref['sha256']
        if ref['usage'] == 'LOCKED_REUSED':
            assert path.read_bytes() == at_start(note, path)
        else:
            assert ref['usage'] == 'NEW_SCOPED'
    assert subprocess.check_output(['git', 'rev-parse', 'codex/production-continuation'], cwd=ROOT).decode().strip() == note['protected_production_sha']
    if review['checkpoint'] == note['checkpoint']:
        ledger = read_json(OUT / 'mod-completion-ledger.json')
        target = next(t for t in ledger['targets'] if t['mod_key'] == 'cataclysm')
        assert target['state'] == 'PARTIAL' and ledger['checkpoint'] == note['checkpoint']
        assert target['exact_next_task'] == review['exact_next_task'] == note['exact_next_task']
        before = json.loads(at_start(note, OUT / 'mod-completion-ledger.json'))
        assert [t for t in ledger['targets'] if t['mod_key'] != 'cataclysm'] == [t for t in before['targets'] if t['mod_key'] != 'cataclysm']
        changed = subprocess.check_output(['git', 'diff', '--name-only', note['starting_sha']], cwd=ROOT).decode().splitlines()
        assert set(changed) <= set(note['intended_files']), changed


def validate_reproduction(note, jar):
    if note.get('evidence_mode') == 'LOCKED_REUSE':
        # Reproduce only the selected methods from existing witnesses. Do not
        # regenerate a completed evidence domain or duplicate it in a new file.
        import zipfile
        from classfile import ClassFile
        from collect_cataclysm_ignited_revenant_offense import instructions

        target = next(t for t in read_json(OUT / 'jar-inventory.json')['targets']
                      if t['key'] == 'cataclysm')
        with Path(jar).open('rb') as stream:
            assert hashlib.file_digest(stream, 'sha256').hexdigest() == target['sha256']
        assert Path(jar).stat().st_size == target['size_bytes']
        evidence = read_json(OUT / note['evidence_file'])
        assert note['reproduction_methods']
        with zipfile.ZipFile(jar) as archive:
            for selected in note['reproduction_methods']:
                witness = next(w for w in evidence['witnesses']
                               if w['entry'] == selected['entry'])
                raw = archive.read(witness['entry'])
                assert witness['jar_sha256'] == target['sha256']
                assert hashlib.sha256(raw).hexdigest() == witness['entry_sha256']
                cls = ClassFile(raw)
                for name in selected['methods']:
                    stored = [m for m in witness['methods'] if m['name'] == name]
                    assert stored, (witness['entry'], name)
                    for method in stored:
                        native = next(m for m in cls.methods if m['name'] == name
                                      and m['descriptor'] == method['descriptor'])
                        code = native.get('code', b'')
                        assert hashlib.sha256(code).hexdigest() == method['code_sha256']
                        body = instructions(cls, code)
                        ranges = method.get('instruction_offset_ranges')
                        if ranges:
                            body = [i for i in body if any(a <= i['offset'] <= b
                                                          for a, b in ranges)]
                        # Older witnesses predate decoded branch/local metadata;
                        # the exact code hash above still protects those bytes.
                        stored_body = method['instructions']
                        assert len(body) == len(stored_body)
                        assert all(all(actual.get(k) == v for k, v in stored.items())
                                   for actual, stored in zip(body, stored_body))
        return
    assert collect(read_json(OUT / note['specification_file']), jar) == read_json(OUT / note['evidence_file'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('checkpoint', type=Path)
    parser.add_argument('--jar', type=Path)
    args = parser.parse_args()
    note = read_json(args.checkpoint)
    validate_records(note)
    validate_boundaries(note)
    validate_protection(note)
    if args.jar:
        validate_reproduction(note, args.jar)
    print(f'{note["checkpoint"]}: {note["mechanics_closed"]} records, {note["candidate_numeric_parameter_count"]} numeric candidates; focused validation PASS')
