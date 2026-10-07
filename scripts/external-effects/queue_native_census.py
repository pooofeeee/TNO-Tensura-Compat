"""Compact routing of an existing finite queue; no semantic or coverage inference."""
import argparse
from collections import Counter, defaultdict
from pathlib import Path

from catalog_common import OUT, read_json, write_json, sha256
from reconcile_native_census import reconcile, method_key
from collect_combat_census import decode_sites


def call_frontier(census, ordinals, field_index=None):
    """Group repeated structural questions without interpreting their meaning.

    Every site keeps its exact caller, opcode, offset and resolved symbol.
    Bootstrap handles stay separate from invocations; neither proves that a
    callback actually executes. Native inheritance resolves declarations only.
    """
    ordinals=sorted(set(ordinals))
    assert all(isinstance(n,int) and 0<=n<len(census['methods']) for n in ordinals)
    classes={c['name']:c for c in census['classes']}
    native={method_key(m):n for n,m in enumerate(census['methods'])}
    boot={(b['entry'],b['index']):b for b in census.get('registration_bootstraps',[])}
    calls=defaultdict(list);writes=defaultdict(list);callbacks=defaultdict(list)
    fields={method_key(m):m for m in field_index['methods']} if field_index else {}
    if field_index:
        assert field_index['jar_sha256']==census['jar_sha256'] and field_index['mod_key']==census['mod_key']
        if field_index.get('owner_scope')=='ALL_FIELD_OWNERS':
            selected={method_key(m):m for m in field_index['selection']}
            for n in ordinals:
                m=census['methods'][n];key=method_key(m)
                assert key in selected and selected[key]['code_sha256']==m['code_sha256'], \
                    'Incomplete selected field proof'
    for n in ordinals:
        m=census['methods'][n]
        for site in decode_sites(census,m,'calls'):
            symbol=site['operand'];row=dict(caller_ordinal=n,offset=site['offset'],opcode=site['opcode'])
            calls[symbol].append(row)
            if site['opcode']=='0xba':
                import re
                number=int(re.match(r'bootstrap#(\d+):',symbol).group(1))
                b=boot.get((m['entry'],number))
                assert b,'Missing exact bootstrap'
                callbacks[b['handle']].append(dict(row,bootstrap_index=number,arguments=b['arguments']))
        key=method_key(m)
        sites=(decode_sites(field_index,fields[key],'field_sites') if key in fields else []) if field_index else decode_sites(census,m,'hits')
        for site in sites:
            if site['opcode'] in ('0xb3','0xb5'):
                writes[site['operand']].append(dict(caller_ordinal=n,offset=site['offset'],opcode=site['opcode']))
    def declaration(symbol):
        import re
        match=re.fullmatch(r'(.+)\.([^.(]+)(\(.*)',symbol)
        if not match:return None
        owner,name,desc=match.groups();seen=set()
        while owner in classes and owner not in seen:
            seen.add(owner);key=(owner+'.class',name,desc)
            if key in native:return native[key]
            owner=classes[owner]['superclass']
        return None
    return dict(schema='tno.external_effects.finite_call_frontier.v1',mod_key=census['mod_key'],
        jar_sha256=census['jar_sha256'],scope='Exact finite structural site grouping only; no reachability, semantic classification, exclusion or coverage inferred.',
        selected_ordinals=ordinals,
        field_site_basis=('ALL_SELECTED_FIELD_OWNERS' if field_index.get('owner_scope')=='ALL_FIELD_OWNERS'
                          else 'MOD_OWNED_FIELD_INDEX') if field_index else 'CENSUS_COMBAT_FILTERED_HITS',
        calls=[dict(symbol=s,native_declaration_ordinal=declaration(s),sites=rows) for s,rows in sorted(calls.items())],
        field_writes=[dict(symbol=s,sites=rows) for s,rows in sorted(writes.items())],
        bootstrap_handles=[dict(handle=s,sites=rows) for s,rows in sorted(callbacks.items())],
        summary=dict(selected_methods=len(ordinals),unique_calls=len(calls),unique_written_fields=len(writes),bootstrap_handles=len(callbacks)))


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


def generate(key, output, contract_index=None, frontier=None):
    census_path=OUT/f'{key}-combat-census.json'
    review_path=OUT/'mod-reviews'/f'{key}.json'
    census=read_json(census_path);review=read_json(review_path)
    result=build(review,census)
    result['input_hashes']=dict(census=sha256(census_path),canonical_review=sha256(review_path))
    write_json(output,result)
    if contract_index:
        index,_=reconcile(review,census);write_json(contract_index,index)
    if frontier:
        field_file=OUT/f'{key}-native-field-use-index.json'
        write_json(frontier,call_frontier(census,[n for g in result['groups'] for n in g['method_ordinals']],read_json(field_file) if field_file.exists() else None))
    return result['summary']


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mod_key');p.add_argument('--output',type=Path,required=True)
    p.add_argument('--contract-index',type=Path)
    p.add_argument('--frontier',type=Path)
    a=p.parse_args();print(generate(a.mod_key,a.output,a.contract_index,a.frontier))
