"""Render explicitly authored contracts and bind selected original native inputs.

No classification, primitive, formula, eligibility or reachability is inferred.
The authored specification is a review product; native capture is independent.
"""
import argparse
from copy import deepcopy
from pathlib import Path

from catalog_common import OUT, BASELINE, read_json, write_json
from promote_combat_batch import (literal_numeric_input_binding,
    literal_last_numeric_argument_binding, literal_vector_components_binding,
    literal_effect_arguments, literal_effect_attribute_binding,literal_attribute_binding,
    literal_constructor_argument_binding, literal_call_argument_binding)


def render(spec):
    spec = deepcopy(spec)
    files = {}

    def proof(selection):
        selection = dict(selection)
        packet = selection.pop('evidence_file', spec['evidence_file'])
        doc = files.setdefault(packet, read_json(OUT/packet))
        witness = next(w for w in doc['witnesses'] if w['entry']==selection['entry'])
        selection.update(evidence_file=packet, witness_id=witness['id'])
        return selection, witness

    rows = []
    paths = deepcopy(spec.get('paths',[]))
    for source in spec['contracts']:
        row = dict(source)
        row['mod_key'] = spec['mod_key']
        row['implementation'] = [proof(s)[0] for s in source['implementation']]
        row['native_boundary'] = [dict(entry=p['entry'],methods=p['methods'])
                                  for p in row['implementation']]
        row.setdefault('inspection_status', 'VERIFIED_PINNED_NATIVE_CONTRACT')
        row.setdefault('registry_ids', [])
        row.setdefault('vanilla_similarities', 'Native APIs retain their original admission, '
                       'defenses and lifecycle; exact differences are recorded below.')
        row.setdefault('vanilla_differences', row['actual_behavior'])
        row.setdefault('alternate_sources', [])
        row.setdefault('primary_test_source', row['native_boundary'])
        row.setdefault('reference_evidence', sorted({p['evidence_file'] for p in row['implementation']}))
        row.setdefault('unresolved_ambiguities', [])
        if not row.get('delivery_paths'):
            path = row['id'] + ':native_boundary'
            row['delivery_paths'] = [path]
            paths.append(dict(id=path,mod_key=spec['mod_key'],labels=['OTHER'],
                effect_ids=[row['id']],primary_source=row['source_actor'],
                implementation=deepcopy(row['implementation'])))
        row.setdefault('scalable_parameter_candidates', [])
        for authored in row.pop('candidate_bindings', []):
            c = dict(authored)
            selection = c.pop('consumer')
            p,w = proof(selection)
            name = p['methods'][0]
            matches = [m for m in w['methods'] if m['name']==name and
                       (not p.get('descriptor') or m['descriptor']==p['descriptor'])]
            assert len(matches)==1, 'Ambiguous authored native method'
            m = matches[0]; offset = c.pop('offset')
            hit = next(i for i in m['instructions'] if i['offset']==offset)
            p.update(descriptor=m['descriptor'],offset=offset,
                     opcode=hit['opcode'],operand=hit['operand'])
            binding = c.pop('binding', None)
            helpers = {'LITERAL_INPUT': ('native_literal_numeric_input_binding',literal_numeric_input_binding),
                       'LAST_NUMERIC_ARGUMENT': ('native_last_numeric_argument_binding',literal_last_numeric_argument_binding),
                       'VECTOR_COMPONENTS': ('native_literal_vector_components_binding',literal_vector_components_binding),
                       'EFFECT_ARGUMENTS': ('native_literal_effect_arguments',literal_effect_arguments),
                       'EFFECT_ATTRIBUTE': ('native_effect_attribute_binding',literal_effect_attribute_binding),
                       'ATTRIBUTE': ('native_attribute_binding',literal_attribute_binding)}
            if binding=='CONSTRUCTOR_ARGUMENT':
                c['native_literal_constructor_argument_binding']=literal_constructor_argument_binding(m,offset,c.pop('argument_index'))
            elif binding=='CALL_ARGUMENT':
                c['native_literal_call_argument_binding']=literal_call_argument_binding(m,offset,c.pop('argument_index'))
            elif binding:
                field, helper = helpers[binding]
                c[field] = helper(m,offset)
            c.update(native_consumer=p, native_parameter_identity=dict(entry=p['entry'],
                method=name, descriptor=m['descriptor'],offset=offset),observation_only=True)
            row['scalable_parameter_candidates'].append(c)
        rows.append(row)
    exclusions=[]
    for authored in spec.get('exclusions',[]):
        exclusion=dict(authored)
        exclusion['implementation']=[proof(s)[0] for s in authored['implementation']]
        if 'entry' not in exclusion:
            exclusion['entries']=sorted({p['entry'] for p in exclusion['implementation']})
        exclusions.append(exclusion)
    refinements=deepcopy(spec.get('record_refinements',[]))
    for change in refinements:
        change['implementation_additions']=[proof(s)[0]
            for s in change.get('implementation_additions',[])]
    return dict(schema='tno.external_effects.reviewed_combat_batch.v1',baseline=BASELINE,
        mod_key=spec['mod_key'],checkpoint=spec['checkpoint'],closed_scope=spec['closed_scope'],
        effects=sorted(rows,key=lambda r:r['id']),paths=sorted(paths,key=lambda r:r['id']),exclusions=exclusions,
        record_refinements=refinements,
        exact_next_task=spec['exact_next_task'],stage_policy_decided=False,runtime_tests=0,
        **({key:spec[key] for key in ('native_context_graph_registry_file','native_context_graph_registry_files',
                                    'native_forwarding_registry_file')
            if key in spec}),
        **({'validation':deepcopy(spec['validation'])} if spec.get('validation') else {}))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('specification',type=Path);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();result=render(read_json(a.specification));write_json(a.output,result)
    print({'contracts':len(result['effects']),'exclusions':len(result['exclusions'])})
