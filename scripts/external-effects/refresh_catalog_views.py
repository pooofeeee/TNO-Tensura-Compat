"""Project canonical reviews into catalog views; no semantic inference or Stage policy."""
from copy import deepcopy
from collections import Counter
from catalog_common import OUT, read_json, write_json

VIEWS = [('effect-catalog.json','effects'),('effect-sources.json','sources'),
         ('delivery-path-matrix.json','paths'),('vanilla-comparison.json','comparisons'),
         ('behavior-primitives.json','primitives')]


def project(reviews):
    rows = sorted((row for review in reviews for row in review['effects']),key=lambda r:(r['mod_key'],r['id']))
    paths = sorted((path for review in reviews for path in review['paths']),key=lambda p:(p['mod_key'],p['id']))
    return dict(effects=rows, paths=paths,
        sources=[dict(id='source:'+p['id'],path_id=p['id'],effect_ids=p['effect_ids'],
                      mod_key=p['mod_key'],primary_test_source=p.get('primary_source'),
                      setup=p.get('setup'),implementation=p.get('implementation',[])) for p in paths],
        comparisons=[dict(effect_id=r['id'],mod_key=r['mod_key'],
            primary_classification=r['primary_classification'],
            closest_vanilla=r.get('closest_vanilla_equivalent'),
            similarities=r.get('vanilla_similarities'),differences=r.get('vanilla_differences'),
            components=r['components']) for r in rows],
        primitives=[dict(deepcopy(c),id=r['id']+':component:'+str(i),effect_id=r['id'],
            mod_key=r['mod_key'],status=r['inspection_status']) for r in rows for i,c in enumerate(r['components'])])


def refresh():
    reviews=[read_json(p) for p in sorted((OUT/'mod-reviews').glob('*.json'))]
    ledger=read_json(OUT/'mod-completion-ledger.json')
    by_mod={r['mod_key']:r for r in reviews}
    for target in ledger['targets']:
        if target['mod_key'] not in by_mod:
            continue
        review=by_mod[target['mod_key']]
        target['semantic_effect_count']=len(review['effects'])
        target['numeric_candidate_count']=sum(len(c['parameters']) if isinstance(c,dict) else 1
            for r in review['effects'] for c in r.get('scalable_parameter_candidates', []))
        target['classification_counts']=dict(sorted(Counter(r['primary_classification'] for r in review['effects']).items()))
    write_json(OUT/'mod-completion-ledger.json',ledger)
    cat=by_mod['cataclysm'];target=next(t for t in ledger['targets'] if t['mod_key']=='cataclysm')
    if cat['checkpoint']=='R2k34-catalog-integrity-and-cataclysm-closure':
        audit=read_json(OUT/'cataclysm-coverage-audit.json')
        audit['summary'].update(total_canonical_semantic_records=target['semantic_effect_count'],
            total_canonical_numeric_candidates=target['numeric_candidate_count'],
            classification_counts=target['classification_counts'])
        write_json(OUT/'cataclysm-coverage-audit.json',audit)
        summary=read_json(OUT/'cataclysm-classification-summary.json')
        summary.update(semantic_mechanics=target['semantic_effect_count'],numeric_candidate_count=target['numeric_candidate_count'],
            classification_counts=target['classification_counts'],
            classification_groups={
                'Vanilla':sum(r['primary_classification'] in ['VANILLA_DIRECT','VANILLA_EQUIVALENT'] for r in cat['effects']),
                'Vanilla_like_Mixed':sum(r['primary_classification'] in ['VANILLA_LIKE_EXTENDED','VANILLA_COMPOSITE'] for r in cat['effects']),
                'Custom':sum(r['primary_classification'].startswith('CUSTOM_') for r in cat['effects']),
                'Binary_Special':sum(r['primary_classification']=='BINARY_MECHANIC' for r in cat['effects'])},
            primitive_family_counts=dict(sorted(Counter(c['primitive'] for r in cat['effects'] for c in r['components']).items())))
        write_json(OUT/'cataclysm-classification-summary.json',summary)
        note=read_json(OUT/'cataclysm-r2k34-integrity-closure.json');ids=set(note['mechanic_ids'])
        note.update(classification_counts=dict(sorted(Counter(r['primary_classification'] for r in cat['effects'] if r['id'] in ids).items())),
            numeric_candidate_count=sum(len(c['parameters']) for r in cat['effects'] if r['id'] in ids for c in r.get('scalable_parameter_candidates', [])))
        write_json(OUT/'cataclysm-r2k34-integrity-closure.json',note)
    data=project(reviews)
    checkpoint=ledger['checkpoint']
    for name,key in VIEWS:
        doc=read_json(OUT/name)
        doc.update(checkpoint=checkpoint,status='PARTIAL',**{key:data[key]},
            note='Deterministic projection of canonical mod reviews,including explicit PARTIAL scope. '
                 'The ledger alone tracks per-mod completeness. No Stage eligibility or policy decision.')
        doc.pop('unfinished_review',None)
        write_json(OUT/name,doc)
    return {key:len(value) for key,value in data.items()}


if __name__=='__main__':
    print(refresh())
