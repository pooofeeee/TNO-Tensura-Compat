"""Compact routing of an existing finite queue; no semantic or coverage inference."""
import argparse
from collections import Counter, defaultdict
from pathlib import Path

from catalog_common import OUT, read_json, write_json, sha256
from reconcile_native_census import reconcile, method_key
from collect_combat_census import decode_sites


def build(review, census):
    index, pending = reconcile(review, census)
    ordinals = {method_key(m): n for n, m in enumerate(census['methods'])}
    classes = {c['entry']: c for c in census['classes']}
    groups = defaultdict(list)
    hints = defaultdict(list)
    consumers = Counter()
    for method in pending:
        ordinal = ordinals[method_key(method)]
        package = method['entry'].rsplit('/', 1)[0]
        parent = classes[method['entry']]['superclass']
        groups[(package, parent)].append(ordinal)
        if method['code_bytes']:
            # Raw bytecode hashes can collide across differing constant pools.
            # These groups only route exact resolved-instruction comparisons.
            hints[(method['descriptor'], method['code_sha256'])].append(ordinal)
        for site in decode_sites(census, method, 'calls'):
            operand = site['operand']
            for marker in ('.hurt(', '.addEffect(', '.setDeltaMovement(', '.heal(',
                           '.setTarget(', '.addFreshEntity(',
                           '.addFreshEntityWithPassengers(', '.explode('):
                if marker in operand:
                    consumers[marker] += 1
    return dict(
        schema='tno.external_effects.finite_unresolved_queue.v1',
        mod_key=census['mod_key'], jar_sha256=census['jar_sha256'],
        scope='Exact pending census ordinals grouped for review. Routing and raw hash hints '
              'grant no coverage, classification, reachability or exclusions.',
        summary=dict(total_methods=census['total_methods'],
            dispositioned_methods=index['summary']['exact_dispositioned_methods'],
            remaining_methods=len(pending),
            pending_by_census_role=dict(sorted(Counter(m['disposition'] for m in pending).items())),
            direct_native_call_sites=dict(sorted(consumers.items())),
            groups=len(groups)),
        groups=[dict(package=package, superclass=parent, method_ordinals=sorted(rows))
                for (package, parent), rows in sorted(groups.items())],
        raw_code_hash_comparison_hints=[dict(descriptor=descriptor, code_sha256=digest,
            method_ordinals=sorted(rows), coverage_proven=False)
            for (descriptor, digest), rows in sorted(hints.items()) if len(rows)>1])


def generate(key, output, contract_index=None):
    census_path=OUT/f'{key}-combat-census.json'
    review_path=OUT/'mod-reviews'/f'{key}.json'
    census=read_json(census_path);review=read_json(review_path)
    result=build(review,census)
    result['input_hashes']=dict(census=sha256(census_path),canonical_review=sha256(review_path))
    write_json(output,result)
    if contract_index:
        index,_=reconcile(review,census);write_json(contract_index,index)
    return result['summary']


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mod_key');p.add_argument('--output',type=Path,required=True)
    p.add_argument('--contract-index',type=Path)
    a=p.parse_args();print(generate(a.mod_key,a.output,a.contract_index))
