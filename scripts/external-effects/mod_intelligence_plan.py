"""Bounded numeric Change Plans. No code generation or intent-prose inference."""
import hashlib
import math
from pathlib import Path

PLAN_SCHEMA = 'tno.mod_intelligence.v3'
INTENT_SCHEMA = 'tno.mod_intelligence.change_request.v1'
LEGACY_INTENT_SCHEMA = 'tno.mod_intelligence.change_intent.v1'
CHANGE_TYPES = {'modify numeric parameter', 'modify movement multiplier'}


def normalize_request(request, require):
    require(isinstance(request, dict), 'Change request must be an object')
    if request.get('schema') == LEGACY_INTENT_SCHEMA:
        required = {'schema', 'target_mechanic', 'requested_modification', 'desired_behavior', 'constraints'}
        require(required <= set(request) <= required | {'affected_parameter', 'proposed_value'},
                'Invalid legacy change intent fields')
        request = dict(schema=INTENT_SCHEMA, target=request['target_mechanic'],
            change_type='modify numeric parameter', requested_behavior=request['desired_behavior'],
            constraints=request['constraints'], parameter=request.get('affected_parameter'),
            proposed_value=request.get('proposed_value'), note=request['requested_modification'])
    allowed = {'schema', 'target', 'change_type', 'requested_behavior', 'parameter',
               'proposed_value', 'constraints', 'note'}
    require({'target', 'change_type', 'requested_behavior'} <= set(request) <= allowed,
            'Request requires target/change_type/requested_behavior; unsupported fields are rejected')
    require(request.get('schema', INTENT_SCHEMA) == INTENT_SCHEMA, 'Unsupported change request schema')
    for field in ('target', 'change_type', 'requested_behavior', 'note'):
        if field in request:
            require(isinstance(request[field], str) and bool(request[field].strip()) and len(request[field]) <= 4096,
                    f'Invalid request text: {field}')
    constraints = request.get('constraints', [])
    require(isinstance(constraints, list) and len(constraints) <= 32 and
            all(isinstance(c, str) and bool(c.strip()) and len(c) <= 1024 for c in constraints),
            'Constraints must be at most 32 nonempty strings of at most 1024 characters')
    parameter = request.get('parameter')
    if parameter is not None:
        require(isinstance(parameter, dict) and {'primitive', 'name'} <= set(parameter) <=
                {'primitive', 'name', 'mechanic_id', 'component_index'}, 'Invalid parameter selector')
        for field in ('primitive', 'name', 'mechanic_id'):
            if field in parameter:
                require(isinstance(parameter[field], str) and bool(parameter[field].strip()) and len(parameter[field]) <= 256,
                        f'Invalid parameter selector: {field}')
        if 'component_index' in parameter:
            require(type(parameter['component_index']) is int and parameter['component_index'] >= 0,
                    'Invalid parameter component_index')
    value = request.get('proposed_value')
    require(value is None or type(value) is int or (type(value) is float and math.isfinite(value)),
            'Proposed value must be a finite number or null')
    require(value is None or parameter is not None, 'A proposed value requires an explicit parameter selector')
    return dict(request, schema=INTENT_SCHEMA, constraints=constraints)


def literal_sites(candidate, parameter, vector_only=False):
    """Project only two binding families already checked by V1 against instructions."""
    vector = candidate.get('native_literal_vector_components_binding')
    if vector and vector.get('operation') == 'multiply':
        axis = candidate.get('native_vector_parameter_roles', {}).get(parameter)
        if axis in ('x', 'y', 'z'):
            return [dict(offset=vector['literal_offsets'][('x', 'y', 'z').index(axis)],
                         current_value=vector[axis], axis=axis, operation='vector.multiply')]
    if vector_only:
        return []
    scalar_keys = ('native_literal_numeric_site_binding', 'native_literal_numeric_input_binding',
                   'native_literal_call_argument_binding', 'native_literal_constructor_argument_binding',
                   'native_effect_attribute_binding', 'native_numeric_return_binding')
    sites = []
    for key in scalar_keys:
        binding = candidate.get(key)
        if isinstance(binding, dict) and 'native_value' in binding and 'value_offset' in binding:
            sites.append(dict(offset=binding['value_offset'], current_value=binding['native_value'], binding=key))
    return sites


def validation_records(catalog, context, identities, root, links_file, require):
    """Optional pinned historical reports, without interpreting Markdown as proof."""
    inputs = {p['file']: p['sha256'] for p in context['repository_inputs']}
    path = Path(links_file) if links_file is not None else root / 'scripts/external-effects/mod_intelligence_links.json'
    if not path.is_absolute():
        path = root / path
    require(path.resolve().is_relative_to(root), 'Repository mapping escapes root')
    file = path.resolve().relative_to(root).as_posix()
    mappings = [file] if file in inputs else []
    records = []
    for file in mappings:
        raw = (root / file).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == inputs[file], 'Repository mapping changed during planning', 3)
        index = type(catalog.index)(root)
        document = index.read(file)
        if document.get('schema') != 'tno.mod_intelligence.repository_links.v1':
            continue
        for entry in document['mechanics']:
            if entry['id'] not in identities:
                continue
            reports = entry.get('validation_records', [])
            require(isinstance(reports, list) and len(reports) <= 10, 'Invalid validation record list')
            for record in reports:
                require(isinstance(record, dict) and set(record) == {'file', 'sha256', 'scope'},
                        'Invalid validation record')
                require(isinstance(record['sha256'], str) and len(record['sha256']) == 64 and
                        all(c in '0123456789abcdef' for c in record['sha256']), 'Invalid validation record digest')
                path = (root / record['file']).resolve()
                require(path.is_relative_to(root) and path.suffix == '.md' and
                        record['scope'] == 'STATIC_CODING_FIXTURE', 'Invalid validation record scope/path')
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                require(digest == record['sha256'], 'Stale validation record pin', 3)
                inputs[record['file']] = digest
                if record not in records:
                    records.append(dict(record, execution='NOT_RERUN', interpretation='HISTORICAL_REPORT_ONLY'))
    return records, [dict(file=f, sha256=h) for f, h in sorted(inputs.items())]


def build_plan(catalog, identity, request, mod, limit, repo_root, links_file,
               dependency_version, dependency_digest, require):
    request = normalize_request(request, require)
    require(request['target'] == identity, 'Request target does not match mechanic')
    require(1 <= limit <= 100, 'Invalid plan limit')
    impact = catalog.impact(identity, mod, 100, repo_root=repo_root, links_file=links_file,
        dependency_version=dependency_version, dependency_digest=dependency_digest)
    context = catalog._context_projection(identity, impact)
    sections = {k: [] for k in ('mechanics', 'source_locations', 'preserved_constraints',
                               'dependencies', 'required_tests', 'patterns', 'risks_and_questions')}
    def item(section, classification, kind, **fields):
        result = dict(id=f'{section}:{len(sections[section])}', classification=classification, kind=kind, **fields)
        sections[section].append(result)
        return result['id']
    unknown = lambda kind, **fields: item('risks_and_questions', 'UNKNOWN', kind, **fields)
    review = lambda kind, **fields: item('risks_and_questions', 'REQUIRES_REVIEW', kind, **fields)
    for boundary in context['verified_behavior']:
        item('mechanics', 'VERIFIED', 'CURRENT_MECHANIC', mechanic_id=boundary['id'],
             current_behavior=boundary['actual_behavior'], evidence_basis='V1_VALIDATED_CANONICAL_CONTRACT')
        item('preserved_constraints', 'VERIFIED', 'RECORDED_CONTRACT', mechanic_id=boundary['id'],
             record={k: v for k, v in boundary.items() if k not in ('id', 'actual_behavior', 'relationship')})
    parameters = []
    for group in context['numbers_and_formulas']:
        item('preserved_constraints', 'VERIFIED', 'RECORDED_NUMERIC_OBSERVATIONS',
             mechanic_id=group['mechanic_id'], record=group['observations'])
        for n, component in enumerate(group['components']):
            item('preserved_constraints', 'VERIFIED', 'RECORDED_COMPONENT', mechanic_id=group['mechanic_id'],
                 component_index=n, record=component)
            for name, value in component.get('numerical_parameters', {}).items():
                if type(value) not in (int, float):
                    continue
                parameters.append(dict(mechanic_id=group['mechanic_id'], component_index=n,
                    primitive=component['primitive'], name=name, current_value=value))
    for group in context['delivery_paths']:
        item('preserved_constraints', 'VERIFIED', 'RECORDED_DELIVERY', mechanic_id=group['mechanic_id'], record=group['paths'])
    selector = request.get('parameter')
    selected = [] if selector is None else [p for p in parameters if all(p[k] == v for k, v in selector.items())]
    if selector is not None:
        require(selected, 'Unknown recorded numeric parameter', 4)
        require(len(selected) == 1, 'Ambiguous parameter; supply mechanic_id/component_index')
    supported = request['change_type'] in CHANGE_TYPES
    if not supported:
        unknown('UNSUPPORTED_CHANGE_TYPE', reason='This prototype handles scalar/vector numeric changes only.')
    if selector is None:
        review('PARAMETER_SELECTION', candidates=parameters,
               reason='Requested prose is not interpreted; choose an exact parameter before locating an edit.')
    if request.get('proposed_value') is None:
        review('PROPOSED_VALUE', reason='Choose a value and define observable acceptance criteria; no value is inferred.')
    if selected and request['change_type'] == 'modify movement multiplier':
        require(selected[0]['primitive'] == 'FORCED_MOVEMENT', 'Movement changes require a FORCED_MOVEMENT parameter')
    links = {e['id']: e for e in impact['evidence_links']}
    methods = impact['confirmed_contract']['methods']
    consumers = [c for c in impact['confirmed_contract']['consumers'] if selected and
                 c['mechanic_id'] == selected[0]['mechanic_id'] and c['primitive'] == selected[0]['primitive'] and
                 selected[0]['name'] in c.get('parameters', [])]
    method_ids, locations = set(), []
    for consumer in consumers if supported else []:
        proof = consumer.get('native_consumer', {})
        sites = literal_sites(consumer, selected[0]['name'], request['change_type'] == 'modify movement multiplier')
        if not sites or not proof:
            continue
        _, rows, _ = catalog.find(identity, impact['mod_key'])
        row = next(r for r in rows if r['id'] == selected[0]['mechanic_id'])
        resolved = catalog.evidence(proof, row)
        if len(consumer['parameters']) > 1:
            review('COUPLED_PARAMETER_BINDING', parameters=consumer['parameters'],
                   reason='One recorded numeric input serves multiple parameters; an independent edit is not established.')
        local = consumer.get('native_local_value_context', {})
        if len(consumer.get('native_literal_numeric_input_binding', {}).get('read_offsets', [])) > 1:
            review('COUPLED_NATIVE_USES', record=local,
                   reason='The selected literal feeds multiple recorded local reads; review each use before editing.')
        for method in methods:
            link = links[method['evidence_link']]
            descriptor = method.get('descriptor', method.get('raw_descriptor', method.get('obfuscated_descriptor')))
            if link['file'] != resolved['file'] or method['entry'] != resolved['entry'] or not any(
                    m['name'] == method['name'] and m.get('descriptor', m.get('raw_descriptor', m.get('obfuscated_descriptor'))) == descriptor
                    for m in resolved['methods']):
                continue
            if not descriptor or not method.get('code_sha256') or not link.get('class_hash'):
                continue
            method_ids.add(method['id'])
            for site in sites:
                require(site['current_value'] == selected[0]['current_value'], 'Selected literal/value mismatch')
                location = item('source_locations', 'VERIFIED', 'CURRENT_LITERAL_SITE',
                    file=link['file'], entry=method['entry'], method=method['name'], descriptor=descriptor,
                    code_sha256=method['code_sha256'], evidence_link=link['id'], editable=False,
                    consumer_offset=proof['offset'], literal=site,
                    recorded_binding={k: v for k, v in consumer.items() if k != 'relationship'})
                locations.append(location)
    if selected and not locations:
        unknown('NUMERIC_LITERAL_SITE', reason='No supported exact literal binding with recorded class/method hashes; no edit location is asserted.')
    constraints = [i['id'] for i in sections['preserved_constraints']]
    preservation = item('preserved_constraints', 'REQUIRES_REVIEW', 'PRESERVATION_OBLIGATION',
        depends_on=constraints, selected_parameter=selected[0] if selected else None,
        instruction='Preserve recorded gates, operation types, units, delivery and other parameters. Review formulas/prose containing the changed value; current formulas are not future guarantees.')
    edits = []
    if locations:
        edits.append(item('source_locations', 'REQUIRES_REVIEW', 'PROPOSED_EDIT', depends_on=locations + [preservation],
            proposed_value=request.get('proposed_value'), instruction='Locate the equivalent source expression in the pinned baseline; review coupled uses before changing the selected numeric input. No code is generated.'))
    for dependency in context['dependencies']:
        data = {k: v for k, v in dependency.items() if k != 'relationship'}
        item('dependencies', 'VERIFIED', 'RECORDED_OBLIGATION', scope='WHOLE_MECHANIC', record=data)
    if sections['dependencies']:
        review('DEPENDENCY_EFFECT', reason='Required by the mechanic; changing this parameter does not prove an edit to the dependency is needed.')
    for source in context['source_locations']['repository']:
        item('patterns', 'VERIFIED', 'PINNED_EXAMPLE', record={k: v for k, v in source.items() if k != 'relationship'})
    for test in context['tests']['references']:
        classification = 'VERIFIED' if test['relationship'] == 'EVIDENCE_BACKED_RELATIONSHIP' else 'UNKNOWN'
        item('required_tests', classification, 'EXISTING_TEST_REFERENCE',
             record={k: v for k, v in test.items() if k != 'relationship'}, coverage='ASSOCIATION_ONLY_NOT_NEW_CHANGE_COVERAGE')
    scenarios = [('Check the selected proposed value at its verified consumer and define expected outputs.' if locations else
                  'Resolve the parameter binding and source location before choosing an edit or its expected outputs.'),
                 'Exercise the recorded gate boundaries and unchanged delivery/lifecycle behavior.',
                 'Check unchanged parameters and neighboring effects in the edited method.',
                 'Reject stale source identities and run applicable existing tests plus new regressions.']
    if locations and any(i['literal'].get('axis') for i in sections['source_locations'] if i['kind'] == 'CURRENT_LITERAL_SITE'):
        scenarios.append('Check unchanged vector axes; where the recorded contract has another directional branch, check it remains unchanged. Verify the intended branch uses the proposed factor.')
    if sections['dependencies']:
        scenarios.append('Check the recorded dependency protocol/gates and decide which integration scenarios the proposed change reaches.')
    validation_ids = [item('required_tests', 'REQUIRES_REVIEW', 'VALIDATION_OBLIGATION',
        depends_on=edits + [preservation], scenario=s) for s in scenarios]
    records, repository_inputs = validation_records(catalog, context, impact['canonical_ids'],
                                                    Path(repo_root).resolve(), links_file, require)
    for record in records:
        item('patterns', 'VERIFIED', 'VALIDATION_RECORD', record=record)
    for warning in context['warnings']:
        unknown(warning['area'], reason=warning['reason'])
    for constraint in request['constraints']:
        review('CALLER_CONSTRAINT', constraint=constraint, reason='A requested constraint, not a verified property of the proposed implementation.')
    review('REQUESTED_BEHAVIOR', requested_behavior=request['requested_behavior'],
           reason='No boost-strength interpretation, value choice, or future correctness is inferred.')
    unknown('PRODUCTION_SOURCE_MAPPING', reason='Native class/offset locations are read-only evidence. Existing editable mappings are static Python fixtures.')
    unknown('PLAN_COMPLETENESS', reason='This plan does not prove all affected callers, dependencies, tests, or runtime behaviors are known.')
    selected_keys = {(links[m['evidence_link']]['file'], m['entry'], m['name'],
                     m.get('descriptor', m.get('raw_descriptor', m.get('obfuscated_descriptor'))))
                    for m in methods if m['id'] in method_ids}
    for consumer in impact['confirmed_contract']['consumers']:
        if consumer in consumers:
            continue
        proof = consumer.get('native_consumer', {})
        if not selected_keys or not proof.get('entry') or 'offset' not in proof:
            continue
        _, rows, _ = catalog.find(identity, impact['mod_key'])
        row = next(r for r in rows if r['id'] == consumer['mechanic_id'])
        resolved = catalog.evidence(proof, row)
        if any((resolved['file'], resolved['entry'], m['name'],
                m.get('descriptor', m.get('raw_descriptor', m.get('obfuscated_descriptor')))) in selected_keys
               for m in resolved['methods']):
            review('SHARED_CONSUMER_METHOD', primitive=consumer['primitive'], parameters=consumer['parameters'],
                   reason='Other recorded numeric consumers share the proposed edit method; preserve their inputs and gate behavior.')
    peers = []
    for peer in impact['possible_impact']['mechanics']:
        reasons = [r for r in peer['reasons'] if r['kind'] == 'RECORDED_METHOD_OVERLAP' and
                   (r['evidence_file'], r['entry'], r['method'], r['descriptor']) in selected_keys]
        if reasons:
            peers.append((peer, reasons))
    for peer, reasons in peers[:limit]:
        review('CONDITIONAL_SHARED_METHOD', mechanic_id=peer['id'],
               reasons=[{k: v for k, v in r.items() if k != 'relationship'} for r in reasons],
               reason='A change to this shared method could affect this mechanic; the selected literal alone does not prove that impact.')
    if len(peers) > limit or impact['possible_impact']['has_more'] or any(p['has_more_reasons'] for p in impact['possible_impact']['mechanics']):
        unknown('PEER_COVERAGE', reason='Filtered candidate scan is bounded; unreturned peers/reasons remain possible.')
    evidence_ids = {i['evidence_link'] for i in sections['source_locations'] if 'evidence_link' in i}
    evidence_ids.update(e for d in context['dependencies'] for e in d['evidence_links'])
    evidence = [dict({k: v for k, v in e.items() if k != 'relationship'}, classification='VERIFIED')
                for e in context['evidence'] if e['id'] in evidence_ids]
    source_ids = {e['source_id'] for e in evidence}
    sources = [dict({k: v for k, v in s.items() if k != 'relationship'}, classification='VERIFIED')
               for s in context['evidence_sources'] if s['id'] in source_ids]
    readiness = 'UNSUPPORTED_CHANGE' if not supported else ('SELECTION_REQUIRED' if not selected else
                 ('LITERAL_SITE_UNKNOWN' if not locations else 'REVIEW_REQUIRED'))
    return dict(plan='BOUNDED_NUMERIC_CHANGE_PLAN_V3', readiness=readiness, mod_key=impact['mod_key'],
        request=dict(request, classification='REQUIRES_REVIEW'),
        selected_parameter=dict(selected[0], classification='VERIFIED', verification='RECORDED_VALUE') if selected else None,
        **sections, reasoning_chain=[dict(classification='REQUIRES_REVIEW',
            request='request', existing_behavior=[i['id'] for i in sections['mechanics']],
            preserved_constraints=[preservation], implementation_locations=edits,
            validation_requirements=validation_ids)], evidence=evidence, evidence_sources=sources,
        repository_inputs=repository_inputs, projection=dict(candidate_peer_limit=100, returned_peer_limit=limit,
            all_root_constraints_retained=True, omitted_method_records=len(methods)-len(method_ids),
            omitted_unselected_numeric_consumers=len(impact['confirmed_contract']['consumers'])-len(consumers)))
