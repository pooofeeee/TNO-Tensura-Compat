"""Index exact existing contracts against a finite census; never infer exclusions.

Capture alone does not establish coverage. Only methods explicitly cited by a
canonical contract, its referenced shared equivalence/kernel registry, or a
structured reviewed exclusion enter this index. Exclusions retain their own
provenance and do not create semantic records. Every remaining method stays
pending, including bridges, accessors and methods without a combat-keyword hit.
"""
import argparse
from collections import Counter, defaultdict
from pathlib import Path

from catalog_common import OUT, read_json, write_json, sha256


def method_key(method):
    return (method['entry'], method.get('method', method.get('name')),
            method['descriptor'])


def reconcile(review, census, read=read_json, root=OUT):
    native = {method_key(m): m for m in census['methods']}
    assert len(native) == len(census['methods']), 'Duplicate census method'
    classes = {c['entry']: c for c in census['classes']}
    packets = {}
    covered = defaultdict(lambda: dict(record_ids=set(), proofs=[]))

    def packet(filename):
        if filename not in packets:
            packets[filename] = read(root / filename)
        return packets[filename]

    def add(key, digest, record_ids, proof):
        assert key in native, ('Proof not in census', key)
        assert digest == native[key]['code_sha256'], ('Method hash mismatch', key)
        item = covered[key]
        item['record_ids'].update(record_ids)
        if proof not in item['proofs']:
            item['proofs'].append(proof)

    def witness(filename, entry=None, witness_id=None):
        matches = [w for w in packet(filename)['witnesses']
                   if (entry is None or w['entry'] == entry)
                   and (witness_id is None or w['id'] == witness_id)]
        assert len(matches) == 1, ('Missing/ambiguous witness', filename, entry, witness_id)
        value = matches[0]
        assert value['jar_sha256'] == census['jar_sha256']
        assert value['entry_sha256'] == classes[value['entry']]['entry_sha256']
        return value

    shared = defaultdict(set)
    context_equivalences = {}
    forwarding_files=set()
    def cite(p, record_ids, metadata):
        filename = p.get('evidence_file', '')
        entry = p.get('entry')
        if not filename.startswith('native-evidence/') or entry not in classes or not p.get('methods'):
            return
        w = witness(filename, entry=entry, witness_id=p.get('witness_id'))
        for name in p['methods']:
            matches = [m for m in w['methods'] if m['name'] == name]
            assert matches, ('Cited method missing', filename, entry, name)
            for m in matches:
                add((entry, name, m['descriptor']), m['code_sha256'], record_ids,
                    dict(metadata, evidence_file=filename, witness_id=w['id']))

    for row in review['effects']:
        for p in row.get('implementation', []) + row.get('shared_contracts', []):
            cite(p, [row['id']], dict(kind='CANONICAL_CONTRACT'))
        for field in ('shared_native_method_equivalence', 'shared_kernel_registry_file'):
            if row.get(field):
                shared[row[field]].add(row['id'])

    for filename in sorted(set(review.get('reviewed_batches', []))):
        batch = packet(filename)
        assert batch['schema'] == 'tno.external_effects.reviewed_combat_batch.v1'
        assert batch['mod_key'] == census['mod_key']
        if batch.get('native_forwarding_registry_file'):
            forwarding_files.add(batch['native_forwarding_registry_file'])
        for context in batch.get('native_context_equivalences', []):
            assert context.get('file') and context.get('reason'), 'Unreviewed context equivalence'
            filename = context['file']
            assert filename not in context_equivalences, 'Repeated context equivalence'
            context_equivalences[filename] = context['reason']
            shared[filename]  # Context proof grants no semantic record identity.
        if batch.get('native_uncalled_registry_file'):
            from native_uncalled import validate_batch as validate_uncalled_batch
            validate_uncalled_batch(batch,census,packet)
        exclusions = batch.get('exclusions', [])
        # Legacy prose or unscoped name lists cannot close native methods.
        if not isinstance(exclusions, list):
            continue
        for exclusion in exclusions:
            if not isinstance(exclusion, dict) or not all(exclusion.get(k)
                    for k in ('entry', 'reason', 'implementation')):
                continue
            assert exclusion['entry'] in classes, ('Excluded entry missing', filename, exclusion['entry'])
            for p in exclusion['implementation']:
                cite(p, [], dict(kind='REVIEWED_EXCLUSION', reviewed_batch=filename,
                     excluded_entry=exclusion['entry'], reason=exclusion['reason'],
                     disposition=exclusion.get('disposition', 'REVIEWED_EXCLUSION')))

    for filename, record_ids in sorted(shared.items()):
        document = packet(filename)
        schema = document['schema']
        if schema == 'tno.external_effects.native_method_equivalence.v1':
            assert document['jar_sha256'] == census['jar_sha256']
            template = document['template']
            w = witness(template['evidence_file'], witness_id=template['witness_id'])
            template_methods = {(m['name'], m['descriptor']): m for m in w['methods']}
            for row in document['rows']:
                key = method_key(row)
                assert row['entry_sha256'] == classes[key[0]]['entry_sha256']
                assert classes[key[0]]['superclass'] == w['superclass']
                assert row['status'] == 'EXACT_RESOLVED_INSTRUCTIONS_EXCEPT_SELF_OWNER'
                assert template_methods[key[1:]]['code_sha256'] == row['template_code_sha256']
                if filename in context_equivalences:
                    assert not template_methods[key[1:]].get('instruction_offset_ranges'), 'Partial context template'
                add(key, row['code_sha256'], record_ids,
                    dict(kind='REVIEWED_EXCLUSION' if filename in context_equivalences else 'SHARED_NATIVE_METHOD',
                         registry_file=filename, evidence_file=template['evidence_file'], witness_id=w['id'],
                         **(dict(disposition='EXACT_REVIEWED_TEMPLATE_CONTEXT', reason=context_equivalences[filename])
                            if filename in context_equivalences else {})))
        elif schema == 'tno.external_effects.native_producer_kernel_registry.v1':
            assert document['mod_key'] == census['mod_key']
            for row in document['rows']:
                for field in ('factory', 'constructor', 'knockback', 'piercing'):
                    p = row[field]
                    w = witness(p['evidence_file'], entry=p['entry'], witness_id=p['witness_id'])
                    matches = [m for m in w['methods'] if (m['name'], m['descriptor']) ==
                               (p['method'], p['descriptor'])]
                    assert len(matches) == 1 and matches[0]['code_sha256'] == p['code_sha256']
                    add(method_key(p), p['code_sha256'], record_ids,
                        dict(kind='SHARED_NATIVE_KERNEL', registry_file=filename,
                             evidence_file=p['evidence_file'], witness_id=w['id']))
        else:
            raise AssertionError(('Unsupported shared registry', filename, schema))

    from native_forwarding import validate as validate_forwarding
    for filename in sorted(forwarding_files):
        registry=packet(filename)
        rows=validate_forwarding(registry,census,covered,
             field_index=packet(registry['field_index_file']) if registry.get('field_index_file') else None)
        for row in rows:
            key=method_key(row)
            target=row.get('target')
            records=covered[method_key(target)]['record_ids'] if target else []
            add(key,row['code_sha256'],records,dict(kind='REVIEWED_EXCLUSION',
                registry_file=filename,disposition=row['kind'],
                reason='Exact pinned context body; no independent native payload. Bridge targets require prior exact coverage.'))

    pending = [m for m in census['methods'] if method_key(m) not in covered]
    rows = []
    for key, value in sorted(covered.items()):
        rows.append(dict(entry=key[0], method=key[1], descriptor=key[2],
                         code_sha256=native[key]['code_sha256'],
                         record_ids=sorted(value['record_ids']),
                         proofs=sorted(value['proofs'], key=lambda p: tuple(sorted(p.items())))))
    contracts = sum(any(p['kind'] != 'REVIEWED_EXCLUSION' for p in r['proofs']) for r in rows)
    return dict(schema='tno.external_effects.exact_native_contract_index.v1',
                mod_key=census['mod_key'], jar_sha256=census['jar_sha256'],
                whole_mod_complete=False,
                scope='Exact canonical/shared references and explicitly cited reviewed exclusions only. A method reference does not prove every branch closed. Pending context, bridge and accessor methods remain undispositioned; no new semantics, reachability or whole-mod closure inferred.',
                summary=dict(total_census_methods=len(native), exact_contract_methods=contracts,
                             explicit_exclusion_methods=len(rows)-contracts,
                             exact_dispositioned_methods=len(rows),
                             pending_methods=len(pending),
                             pending_by_census_role=dict(sorted(Counter(m['disposition'] for m in pending).items())),
                             pending_by_package=dict(sorted(Counter(m['entry'].rsplit('/', 1)[0] for m in pending).items()))),
                methods=rows), pending


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mod_key')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--pending-output', type=Path)
    args = parser.parse_args()
    census_file = OUT / f'{args.mod_key}-combat-census.json'
    review_file = OUT / 'mod-reviews' / f'{args.mod_key}.json'
    index, pending = reconcile(read_json(review_file), read_json(census_file))
    index['input_hashes'] = dict(census=sha256(census_file), canonical_review=sha256(review_file))
    write_json(args.output, index)
    if args.pending_output:
        write_json(args.pending_output, dict(mod_key=args.mod_key, methods=pending))
    print(index['summary'])
