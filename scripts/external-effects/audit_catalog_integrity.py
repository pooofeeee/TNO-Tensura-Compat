"""Independent canonical/evidence integrity checks; never rebuild semantic claims."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import subprocess

from catalog_common import ROOT, OUT, BASELINE, read_json, write_json

CLASSIFICATIONS = {'VANILLA_DIRECT', 'VANILLA_EQUIVALENT', 'VANILLA_LIKE_EXTENDED',
    'VANILLA_COMPOSITE', 'CUSTOM_DAMAGE', 'CUSTOM_STATUS', 'CUSTOM_CONTROL',
    'CUSTOM_RESOURCE', 'BINARY_MECHANIC'}
POLICY_KEYS = {'stage_scaling_needed', 'single_scaling_point', 'stage_reason', 'tno_categories'}
SOURCE_KEYS = {'source_variants', 'source_variant_contracts'}


def audit_source_censuses(index):
    """Compare existing deterministic hit indexes to exact native instructions.

    Six data-generation declaration boundaries have no gameplay method witness;
    they are explicitly accounted for by typed provider/bootstrap context and
    the already-reviewed compiled resource declarations, not counted as combat.
    """
    sources = [
        ('iceandfire', ['factory_callers','status_references']),
        ('eternalstarlight', ['factory_callers','damage_key_references','status_references']),
        ('bossesrise', ['watched_methods','custom_damage_key_methods','native_effect_reference_methods']),
        ('bomd', ['watched_methods','custom_damage_key_methods','native_effect_reference_methods']),
        ('twilightforest-global', ['records']),
    ]
    methods=defaultdict(list)
    for path in sorted((index.root/'native-evidence').glob('*.json')):
        file=path.relative_to(index.root).as_posix()
        for witness in index.read(file).get('witnesses', []):
            for method in witness.get('methods', []):
                methods[(witness.get('entry'),method['name'],method.get('descriptor'))].append((file,witness,method))
    exclusions=read_json(index.root/'catalog-integrity-repairs.json').get('declaration_census_contexts', [])
    contexts={(r['entry'],r['method'],r['descriptor']):r for r in exclusions}
    result={}
    for prefix,groups in sources:
        census=index.read(prefix+'-source-census.json');proved=excluded=0
        for group in groups:
            for row in census.get(group, []):
                key=row['entry'],row['method'],row['descriptor']
                hits=row.get('hits',row.get('calls',row.get('references', [])))
                matched=[]
                for file,witness,method in methods[key]:
                    if row.get('code_sha256') and row['code_sha256']!=method.get('code_sha256'):
                        continue
                    body={(i['offset'],str(i.get('operand'))) for i in method.get('instructions', [])}
                    if all((h['offset'],str(h.get('operand'))) in body for h in hits):
                        matched.append(file)
                if matched:
                    proved+=1
                    continue
                context=contexts.get(key)
                assert context, ('unreconciled completed census boundary',prefix,key)
                assert context['disposition']=='DECLARATION_RESOURCE_CONTEXT'
                assert context['code_sha256']==row['code_sha256']
                assert context['typed_context'] and context['resource_review_files']
                for file in context['resource_review_files']:
                    index.read(file)
                excluded+=1
        result[prefix]=dict(exact_native_hit_rows=proved,declaration_resource_context_rows=excluded)
    return result


def forbidden_policy_paths(value, path=''):
    paths = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key in POLICY_KEYS:
                paths.append(path+'/'+key)
            paths.extend(forbidden_policy_paths(item, path+'/'+key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            paths.extend(forbidden_policy_paths(item, path+'/'+str(index)))
    return paths


class EvidenceIndex:
    def __init__(self, root=OUT):
        self.root, self.files = root, {}
        self.methods = defaultdict(set)
        self.file_hashes = {}

    def read(self, file):
        if file not in self.files:
            raw = (self.root/file).read_bytes()
            self.files[file] = json.loads(raw.decode('utf-8-sig'))
            self.file_hashes[file] = hashlib.sha256(raw).hexdigest()
        return self.files[file]

    def witness(self, proof, context):
        file = proof.get('evidence_file')
        if not file:
            matches = []
            for ref in context.get('reference_evidence', []):
                for witness in self.read(ref).get('witnesses', []):
                    if witness.get('entry') == proof['entry']:
                        matches.append((ref, witness))
            assert len(matches) == 1, ('unqualified reference', context['id'], proof)
            file, witness = matches[0]
        else:
            data = self.read(file)
            witnesses = data.get('witnesses', data.get('classes', []))
            matches = [w for w in witnesses if w.get('entry', w.get('raw_entry')) == proof['entry']]
            assert len(matches) == 1, ('missing/ambiguous witness', context['id'], proof)
            witness = matches[0]
            actual_id = witness.get('id', data.get('id', witness.get('class_name')))
            assert proof.get('witness_id', actual_id) == actual_id, ('wrong witness ID', proof)
        assert set(proof.get('methods', [])) <= {m['name'] for m in witness.get('methods', [])}
        for method in witness.get('methods', []):
            if method['name'] not in proof.get('methods', []):
                continue
            digest = method.get('code_sha256')
            descriptor = method.get('descriptor', method.get('raw_descriptor', method.get('obfuscated_descriptor')))
            if digest:
                assert len(digest) == 64
                if method.get('code_hex'):
                    assert hashlib.sha256(bytes.fromhex(method['code_hex'])).hexdigest() == digest
                if descriptor:
                    self.methods[(proof['entry'], method['name'], descriptor)].add(digest)
        return file, witness


def audit_review(review, index):
    rows, paths = review['effects'], review['paths']
    ids, by_path = {r['id'] for r in rows}, {p['id']: p for p in paths}
    assert len(ids) == len(rows), 'duplicate semantic ID'
    assert len(by_path) == len(paths), 'duplicate delivery ID'
    fingerprints = defaultdict(list)
    candidate_count = 0
    for row in rows:
        assert row['mod_key'] == review['mod_key']
        assert row['primary_classification'] in CLASSIFICATIONS
        assert row.get('actual_behavior') and row.get('implementation') and row.get('delivery_paths')
        assert row.get('components'), ('missing primitive/context', row['id'])
        assert not forbidden_policy_paths(row), ('policy mixed into native research', row['id'])
        for path in row['delivery_paths']:
            assert path in by_path and row['id'] in by_path[path]['effect_ids'], ('broken reciprocal path', row['id'], path)
        for proof in row['implementation']:
            index.witness(proof, row)
        for fact in row.get('fact_references', []):
            assert fact['key'] in index.read(fact['file'])['facts']
        for component in row['components']:
            assert component.get('primitive')
            assert not SOURCE_KEYS & set(component.get('numerical_parameters', {})), ('references treated as numeric', row['id'])
            assert component['primitive'] != 'UNSCALED_NATIVE_COMPANIONS'
        seen = set()
        for candidate in row.get('scalable_parameter_candidates', []):
            if not isinstance(candidate, dict):
                # Older completed schemas explicitly retain unscoped names;
                # they are not guessed into component/consumer mappings.
                candidate_count += 1
                continue
            for parameter in candidate['parameters']:
                key = candidate['primitive'], parameter
                assert key not in seen, ('duplicate parameter within mechanic', row['id'], key)
                seen.add(key)
                matches = [c for c in row['components'] if c['primitive'] == key[0]
                    and parameter in (set(c.get('numerical_parameters', {}))
                        | set(c.get('component_numerical_parameters', {}))
                        | set(c.get('parameter_formulas', {})))]
                assert len(matches) == 1, ('candidate detached from component', row['id'], key)
                if 'native_value' in candidate and parameter in matches[0].get('numerical_parameters', {}):
                    assert candidate['native_value'] == matches[0]['numerical_parameters'][parameter]
                candidate_count += 1
        # Actor/registry distinctions are part of identity; identical primitives
        # alone do not justify deduplicating separate combat mechanics.
        signature = json.dumps({k:row.get(k) for k in ['actual_behavior', 'components',
            'binary_parameters', 'source_actor', 'registry_ids']}, sort_keys=True)
        fingerprints[signature].append(row['id'])
    assert not [v for v in fingerprints.values() if len(v) > 1], 'exact duplicate semantic records'
    for path in paths:
        assert path['effect_ids'] and set(path['effect_ids']) <= ids
        assert all(path['id'] in next(r for r in rows if r['id'] == rid)['delivery_paths'] for rid in path['effect_ids'])
    for alias in review.get('semantic_aliases', []):
        assert alias['original_id'] not in ids and set(alias['canonical_ids']) <= ids
        assert alias['reason'] and alias['native_evidence']
        for proof in alias['native_evidence']:
            index.witness(proof,dict(id=alias['original_id']))
    for context in review.get('native_context_records', []):
        native = context.get('native_context')
        if native:
            assert not forbidden_policy_paths(native)
            for proof in native.get('implementation', []):
                index.witness(proof,native)
    for row in rows:
        for alias in row.get('non_independent_parameters', []):
            assert alias['independent_runtime_parameter'] is False
            assert alias['existing_parameters'] and alias['reason']
            assert alias['parameter'] not in row.get('scalable_parameter_candidates', [])
            for proof in alias['implementation']:
                _,witness=index.witness(proof,row)
                for name,digest in proof.get('method_code_sha256',{}).items():
                    assert next(m for m in witness['methods'] if m['name']==name)['code_sha256']==digest
        if row['id']=='es:native_wither_tick':
            # Independent source fact, not the historical promotion builder:
            # exact vanilla callback is anonymous wither1, POP hurt result.
            proof=next(p for p in row['implementation'] if p.get('evidence_format')=='VANILLA_COMPARISON')
            _,witness=index.witness(proof,row)
            body=next(m for m in witness['methods'] if m['name']=='applyEffectTick')['instructions']
            hit=next(i for i,x in enumerate(body) if '.hurt(' in str(x['operand']))
            assert body[hit-1]['operand']==1.0 and body[hit+1]['opcode']=='0x57'
            assert any('.wither()' in str(x['operand']) for x in body)
            assert row['primary_classification']=='VANILLA_DIRECT'
            assert row['components'][0]['numerical_parameters']['requested_damage']==1
    return dict(status='PASS', semantic_records=len(rows), delivery_paths=len(paths),
        numeric_candidate_entries=candidate_count,
        classification_counts=dict(sorted(Counter(r['primary_classification'] for r in rows).items())),
        native_context_records=len(review.get('native_context_records', [])),
        semantic_aliases=len(review.get('semantic_aliases', [])))


def audit_catalog():
    index = EvidenceIndex()
    ledger = read_json(OUT/'mod-completion-ledger.json')
    summaries = {}
    for target in ledger['targets']:
        path = OUT/'mod-reviews'/str(target['mod_key']+'.json')
        if not path.exists():
            if target['mod_key'] == 'tensura':
                refs = read_json(OUT/'effect-catalog.json')['existing_tno_coverage']
                assert len(refs) == 6
                for ref in refs:
                    assert ref['repeat_research'] is False
                    blob = subprocess.check_output(['git','rev-parse',ref['revision']+':'+ref['path']],cwd=ROOT,text=True).strip()
                    assert blob == ref['git_blob']
                summaries['tensura'] = dict(status='PASS_REFERENCE_ONLY', protected_references=6)
            else:
                assert target['state'] == 'UNSTARTED'
            continue
        review = read_json(path)
        summary = audit_review(review, index)
        assert target['state'] == review['status']
        assert target['semantic_effect_count'] == summary['semantic_records']
        if 'numeric_candidate_count' in target:
            assert target['numeric_candidate_count'] == summary['numeric_candidate_entries']
        summaries[target['mod_key']] = summary
    assert not {key:values for key,values in index.methods.items() if len(values) > 1}, 'conflicting hashes for exact method identity'
    source_coverage=audit_source_censuses(index)
    cat=read_json(OUT/'mod-reviews/cataclysm.json')
    accounted={r['id'] for r in cat['effects']} | {r['original_id'] for r in cat['semantic_aliases']}
    accounted |= {r.get('original_id') for r in cat['native_context_records']}
    packages_checked=0
    for file in sorted(OUT.glob('cataclysm-r2k*-*.json')):
        note=read_json(file)
        packages=note.get('mechanic_packages', [])
        if not isinstance(packages,list):
            continue
        for package in packages:
            assert package['id'] in accounted, ('locked package omitted from canonical catalog',file.name,package['id'])
            packages_checked+=1
    canonical = sorted((row for file in (OUT/'mod-reviews').glob('*.json')
                        for row in read_json(file)['effects']), key=lambda r:(r['mod_key'],r['id']))
    assert read_json(OUT/'effect-catalog.json')['effects'] == canonical, 'stale canonical catalog projection'
    return dict(schema='tno.external_effects.catalog_integrity.v1', status='PASS', baseline=BASELINE,
        mods=summaries, exact_method_identities=len(index.methods), source_census_checks=source_coverage,
        cataclysm_checkpoint_packages_accounted=packages_checked,
        evidence_files=[dict(file=f,sha256=h) for f,h in sorted(index.file_hashes.items())],
        semantic_records=len(canonical),
        numeric_candidate_entries=sum(s.get('numeric_candidate_entries',0) for s in summaries.values()),
        classification_counts=dict(sorted(Counter(r['primary_classification'] for r in canonical).items())),
        completed_mods_audited=sum(t['state']=='COMPLETE' for t in ledger['targets']),
        runtime_tests='NOT_RUN', production_changed=False, stage_policy_decided=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = audit_catalog()
    if args.output:
        write_json(args.output,result)
    print(json.dumps({k:v for k,v in result.items() if k!='evidence_files'},sort_keys=True))
