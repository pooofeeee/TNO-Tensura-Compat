"""Audit authored numeric labels independently of candidate totals.

Native candidate replay belongs to promote_combat_batch. This audit rejects
missing/shadowed label dispositions, dangling aliases, incorrect conversions,
changed structural sites and duplicate complete native parameter identities.
Structural formulas remain explicitly authored semantic interpretations.
"""
import math
from collections import Counter
from catalog_common import OUT, read_json
from audit_catalog_integrity import EvidenceIndex


def close(a, b):
    return type(a) in (int, float) and type(b) in (int, float) and math.isclose(
        a, b, rel_tol=1e-7, abs_tol=1e-10)


def audit(review, evidence=None):
    evidence=evidence or EvidenceIndex()
    rows={r['id']:r for r in review['effects']}
    values={}; candidates=set(); identities={}; links={}; kinds=Counter()
    for row in rows.values():
        rid=row['id']
        for c in row['components']:
            for p,v in c.get('numerical_parameters',{}).items():
                key=(rid,c['primitive'],p)
                assert key not in values, ('shadowed numeric label',key)
                assert type(v) in (int,float) and math.isfinite(v), ('non-scalar label',key)
                values[key]=v
            for p,link in c.get('numeric_label_bindings',{}).items():
                key=(rid,link['original_primitive'],p)
                assert key not in links, ('shadowed numeric disposition',key)
                links[key]=link
        for c in row['scalable_parameter_candidates']:
            native=c['native_parameter_identity']
            for p in c['parameters']:
                key=(rid,c['primitive'],p)
                assert key not in candidates, ('duplicate candidate label',key)
                candidates.add(key)
                identity=(native['entry'],native['method'],native['descriptor'],
                          native['offset'],c['primitive'],p)
                assert identity not in identities, ('duplicate complete native identity',key,identities.get(identity))
                identities[identity]=key
    assert candidates<=values.keys(), 'candidate missing numerical value'
    assert not candidates&links.keys(), 'candidate also treated as summary alias'
    for key,link in links.items():
        assert key in values and link['original_summary_value']==values[key], ('stale summary',key)
        kind=link['binding'];kinds[kind]+=1
        if kind in ('EXACT_SIGNED_LITERAL_INPUT','DERIVED_SUMMARY_FROM_NATIVE_LITERAL','EXISTING_CANONICAL_PARAMETER'):
            target=(link.get('target_record',key[0]),link['target_primitive'],link['target_parameter'])
            assert target in candidates, ('dangling/non-candidate alias',key,target)
            expected=values[target]*link.get('multiplier',1)
            if kind=='EXACT_SIGNED_LITERAL_INPUT':
                assert close(abs(values[key]),abs(expected)), ('wrong signed magnitude',key)
            else:
                assert close(values[key],expected), ('wrong numeric conversion',key)
            if kind=='EXISTING_CANONICAL_PARAMETER':assert link.get('reason'),key
        elif kind=='DERIVED_NATIVE_STRUCTURE':
            assert link.get('formula') and link.get('sites'), ('unexplained derivation',key)
            proof=link['proof'];_,w=evidence.witness(proof,rows[key[0]])
            methods=[m for m in w['methods'] if m['name'] in proof['methods']
                     and m['descriptor']==proof['descriptor']]
            assert len(methods)==1, ('ambiguous derived body',key)
            body={i['offset']:i for i in methods[0]['instructions']}
            for site in link['sites']:
                assert site['offset'] in body and body[site['offset']]['operand']==site['operand'], ('changed derived site',key,site)
        else:raise AssertionError(('unknown numeric disposition',key,kind))
    missing=values.keys()-candidates-links.keys()
    assert not missing, ('undispositioned numeric labels',sorted(missing))
    return dict(status='PASS',numeric_labels=len(values),native_candidate_identities=len(identities),
                summary_label_dispositions=len(links),disposition_counts=dict(sorted(kinds.items())),
                unresolved_numeric_labels=0,
                derivation_scope='Structural sites and authored formulas verified; no semantics inferred from numeric equality.')


if __name__=='__main__':
    import argparse,json
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mod_key');a=p.parse_args()
    print(json.dumps(audit(read_json(OUT/'mod-reviews'/f'{a.mod_key}.json')),indent=2))
