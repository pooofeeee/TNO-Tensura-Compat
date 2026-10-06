"""Reduce verified factory kernels to explicit, independently reviewed owners.

Captured evidence or matching bodies cannot close an owning producer scope.
"""
from collections import Counter, defaultdict

from catalog_common import OUT, read_json, write_json


def update(mod_key):
    registry_file = f'{mod_key}-projectile-producer-kernel-registry.json'
    registry = read_json(OUT/registry_file)
    review = read_json(OUT/'mod-reviews'/f'{mod_key}.json')
    closed = defaultdict(list)
    for filename in review.get('reviewed_batches', []):
        batch = read_json(OUT/filename)
        for entry in batch.get('producer_closed_entries', []):
            assert any(p['entry']==entry for r in batch['effects'] for p in r['implementation'])
            assert all(any(old['id']==r['id'] for old in review['effects']) for r in batch['effects'])
            closed[entry].append(dict(kind='EXPLICIT_REVIEWED_SOURCE_HELPER', file=filename))
    event_file = f'{mod_key}-event-review-queue.json'
    if (OUT/event_file).exists():
        for root in read_json(OUT/event_file)['roots']:
            if root['disposition'].startswith('CLOSED_'):
                closed[root['entry']].append(dict(kind='REUSED_LOCKED_EVENT_CONTRIBUTIONS',
                    file=event_file, method=root['method'], disposition=root['disposition']))
    owners = defaultdict(list)
    for row in registry['rows']:
        entry = row['factory']['entry'].split('$',1)[0]+'.class'
        owners[entry].append(row['factory']['entry'])
    rows = [dict(entry=entry, factory_entries=sorted(factories),
                 disposition='CLOSED_REUSED_SOURCE_SCOPE' if entry in closed else 'PENDING_OWNING_SOURCE_SEMANTICS',
                 closure_proofs=closed.get(entry, [])) for entry,factories in sorted(owners.items())]
    result = dict(schema='tno.external_effects.native_arrow_producer_queue.v1', mod_key=mod_key,
        checkpoint=review['checkpoint'], finite_census_file=registry['finite_census_file'],
        finite_census_sha256=registry['finite_census_sha256'], kernel_registry_file=registry_file,
        summary=dict(owning_roots=len(rows), factories=sum(len(r['factory_entries']) for r in rows),
            counts_by_disposition=dict(sorted(Counter(r['disposition'] for r in rows).items())),
            pending_factories=sum(len(r['factory_entries']) for r in rows if r['disposition'].startswith('PENDING_'))),
        owners=rows, whole_mod_complete=False, exact_next_task=review['exact_next_task'],
        note='Closure applies only to the exact source helper/event contributions. Other callbacks, source actors, items, setup, registry and encounter scopes remain the finite mod census; identical anonymous carrier bodies do not close them.')
    write_json(OUT/f'{mod_key}-projectile-producer-review-queue.json',result)
    return result['summary']


if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mod_key')
    print(update(parser.parse_args().mod_key))
