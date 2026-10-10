"""Pinned, task-specific projection of validated V3 plans. No semantic guessing."""
import copy
import hashlib
import json
from pathlib import Path

ADAPTIVE_SCHEMA = 'tno.mod_intelligence.v4'
PROFILE_SCHEMA = 'tno.mod_intelligence.scope_profiles.v1'
SECTIONS = ('mechanics', 'source_locations', 'preserved_constraints', 'dependencies',
            'required_tests', 'patterns', 'risks_and_questions')


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def leaves(value, path=''):
    if isinstance(value, dict) and value:
        for key, child in value.items():
            yield from leaves(child, path + '/' + key.replace('~', '~0').replace('/', '~1'))
    else:
        yield path, value


def subset(value, paths):
    """Select explicit JSON pointers, preserving original values and structure."""
    result = {}
    for path in paths:
        keys = [k.replace('~1', '/').replace('~0', '~') for k in path.split('/')[1:]]
        source, target = value, result
        for key in keys[:-1]:
            source = source[key]
            target = target.setdefault(key, {})
        target[keys[-1]] = copy.deepcopy(source[keys[-1]])
    return result


def choose_profile(catalog, plan, root, profile_file, require):
    path = Path(profile_file) if profile_file is not None else root/'scripts/external-effects/mod_intelligence_scope_profiles.json'
    if not path.is_absolute():
        path = root/path
    require(path.resolve().is_relative_to(root), 'Scope profile escapes repository')
    if not path.exists() and profile_file is None:
        return None, None
    require(path.stat().st_size <= 65536, 'Scope profiles exceed 65536 bytes')
    index = type(catalog.index)(root)
    file = path.resolve().relative_to(root).as_posix()
    document = index.read(file)
    require(document.get('schema') == PROFILE_SCHEMA and isinstance(document.get('profiles'), list), 'Invalid scope profile schema')
    profiles = document['profiles']
    require(len(profiles) <= 32, 'Too many scope profiles')
    require(all(isinstance(p, dict) and isinstance(p.get('id'), str) for p in profiles) and
            len({p['id'] for p in profiles}) == len(profiles), 'Invalid or duplicate scope profile')
    selected = plan['selected_parameter']
    matches = [p for p in profiles if selected and p.get('target') == selected['mechanic_id'] and
               p.get('parameter') == {k: selected[k] for k in ('primitive', 'name', 'component_index')}]
    require(len(matches) <= 1, 'Ambiguous scope profile')
    provenance = dict(file=file, sha256=index.file_hashes[file])
    if not matches or plan['readiness'] != 'REVIEW_REQUIRED' or len(plan['mechanics']) != 1:
        return None, provenance
    profile = matches[0]
    require(profile.get('scope') == 'SELECTED_LITERAL_ONLY', 'Unsupported adaptive scope')
    pins = profile['catalog_pins']
    require(isinstance(pins, dict) and pins and all(isinstance(f, str) and isinstance(h, str) and
            len(h) == 64 and all(c in '0123456789abcdef' for c in h) for f, h in pins.items()), 'Invalid scope pins')
    require(all(catalog.index.file_hashes.get(f) == h for f, h in pins.items()), 'Stale or unselected scope profile input', 3)
    require('mod-reviews/'+plan['mod_key']+'.json' in pins and
            all(e['file'] in pins for e in plan['evidence_sources']), 'Incomplete catalog scope pins')
    sites = [s for s in plan['source_locations'] if s['kind'] == 'CURRENT_LITERAL_SITE']
    require(len(sites) == 1 and isinstance(profile['site'], dict) and
            all(sites[0].get(k) == v for k, v in profile['site'].items()), 'Scope literal site mismatch', 3)
    require({'file', 'entry', 'method', 'descriptor', 'code_sha256', 'literal'} <= set(profile['site']), 'Incomplete scope site identity')
    components = {i['component_index']: i for i in plan['preserved_constraints'] if i['kind'] == 'RECORDED_COMPONENT'}
    required, context = profile['required_components'], profile['context_components']
    require(isinstance(required, list) and isinstance(context, list) and
            all(type(n) is int for n in required + context) and len(set(required + context)) == len(required + context) and
            set(required + context) == set(components) and selected['component_index'] in required, 'Incomplete component scope partition')
    for warning in plan['risks_and_questions']:
        if warning['kind'] == 'SHARED_CONSUMER_METHOD':
            related = [n for n, c in components.items() if c['record']['primitive'] == warning['primitive'] and
                       set(warning['parameters']) <= set(c['record'].get('numerical_parameters', {}))]
            require(related and set(related) <= set(required), 'Scope omits a shared-method consumer')
    require(profile['dependency_mode'] in ('FULL', 'IDENTITY'), 'Invalid dependency scope')
    dependency_id = components[selected['component_index']]['record'].get('external_dependency_contract')
    require(not dependency_id or profile['dependency_mode'] == 'FULL', 'Scope omits an explicit component dependency')
    if dependency_id:
        require(dependency_id in {d['record']['id'] for d in plan['dependencies']}, 'Missing explicit component dependency')
    behavior = plan['mechanics'][0]['current_behavior']
    require(isinstance(profile['behavior_quotes'], list) and profile['behavior_quotes'] and
            all(isinstance(q, str) and q and q in behavior for q in profile['behavior_quotes']), 'Scope behavior quote mismatch')
    excluded_quotes = profile.get('excluded_behavior_quotes', [])
    require(isinstance(excluded_quotes, list) and all(isinstance(q, str) and q and q in behavior for q in excluded_quotes),
            'Scope excluded quote mismatch')
    contract = next(i['record'] for i in plan['preserved_constraints'] if i['kind'] == 'RECORDED_CONTRACT')
    paths, excluded = profile['required_contract_paths'], profile['excluded_contract_paths']
    allowed_exclusions = {'/inspection_status', '/contract/contract_refinements',
                          '/contract/closest_vanilla_equivalent', '/contract/vanilla_similarities'}
    require(isinstance(excluded, list) and set(excluded) <= allowed_exclusions, 'Behavioral gates cannot be classified EXCLUDE')
    require(isinstance(paths, list) and isinstance(excluded, list) and
            all(isinstance(p, str) and p.startswith('/') and p != '/' for p in paths + excluded), 'Invalid contract scope paths')
    require(not any(a == b or a.startswith(b+'/') or b.startswith(a+'/') for a in paths for b in excluded),
            'Required/excluded contract paths overlap')
    require(not any(q in included for q in excluded_quotes for included in profile['behavior_quotes']),
            'Required/excluded behavior quotes overlap')
    subset(contract, paths + excluded)  # Missing paths fail before any projection.
    return profile, provenance


def adaptive_plan(catalog, plan, repo_root, profile_file, require):
    root = Path(repo_root).resolve()
    profile, provenance = choose_profile(catalog, plan, root, profile_file, require)
    buckets = {k: [] for k in ('REQUIRED', 'CONTEXT', 'EXCLUDE', 'UNKNOWN')}
    def keep(item, category):
        buckets[category].append(dict(copy.deepcopy(item), relevance=category))
    def defer(item, category='CONTEXT', suffix='', basis=None):
        reference = dict(id=item['id']+suffix, relevance=category, classification=item['classification'])
        if suffix.startswith('/excluded_quote/'):
            reference['restore_ref'] = item['id']+'/current_behavior'
        if basis:
            reference['basis'] = basis
        buckets[category].append(reference)
    unresolved = plan['readiness'] != 'REVIEW_REQUIRED'
    for section in SECTIONS:
        for original in plan[section]:
            item = copy.deepcopy(original)
            kind = item['kind']
            if unresolved:
                if section == 'risks_and_questions':
                    keep(item, 'UNKNOWN' if item['classification'] == 'UNKNOWN' or kind == 'PARAMETER_SELECTION' else 'REQUIRED')
                elif kind == 'VALIDATION_OBLIGATION':
                    keep(item, 'REQUIRED')
                else:
                    defer(item)
                continue
            if profile is None:
                keep(item, 'UNKNOWN' if item['classification'] == 'UNKNOWN' else 'REQUIRED')
                continue
            if section == 'mechanics':
                defer(item)
                item['current_behavior'] = profile['behavior_quotes']
                item['id'] += '/scoped_behavior'
                keep(item, 'REQUIRED')
                for n, quote in enumerate(profile.get('excluded_behavior_quotes', [])):
                    defer(original, 'EXCLUDE', f'/excluded_quote/{n}', 'OUTSIDE_PINNED_LITERAL_EDIT_SCOPE')
            elif kind == 'RECORDED_CONTRACT':
                item['record'] = subset(original['record'], profile['required_contract_paths'])
                keep(item, 'REQUIRED')
                for path, value in leaves(original['record']):
                    if any(path == p or path.startswith(p+'/') for p in profile['required_contract_paths']):
                        continue
                    excluded = any(path == p or path.startswith(p+'/') for p in profile['excluded_contract_paths'])
                    defer(original, 'EXCLUDE' if excluded else 'CONTEXT', '/record'+path,
                          'HISTORICAL_OR_COMPARATIVE_METADATA' if excluded else None)
            elif kind == 'RECORDED_COMPONENT':
                if item['component_index'] in profile['required_components']:
                    keep(item, 'REQUIRED')
                else:
                    defer(item)
            elif kind == 'RECORDED_NUMERIC_OBSERVATIONS' and not item['record']:
                defer(item, 'EXCLUDE', basis='EMPTY_RECORD_NO_CONSTRAINTS')
            elif kind == 'RECORDED_OBLIGATION' and profile['dependency_mode'] == 'IDENTITY':
                defer(item)
                item['id'] += '/identity'
                item['record'] = {k: v for k, v in item['record'].items() if k in
                    ('id', 'status', 'validation_state', 'artifact', 'source_check', 'missing_method_hashes', 'claim_limit', 'retrieve')}
                item['scope'] = 'WHOLE_MECHANIC_IDENTITY_CONTRACT_IN_CONTEXT'
                keep(item, 'REQUIRED')
            elif section == 'patterns':
                defer(item)
            elif kind == 'EXISTING_TEST_REFERENCE':
                defer(item, 'UNKNOWN', basis='UNVERIFIED_TEST_ASSOCIATION')
            else:
                keep(item, 'UNKNOWN' if item['classification'] == 'UNKNOWN' else 'REQUIRED')
    # These are fixed V3 diagnostics, not task facts. Preserve their topics and
    # restoration IDs once; dynamic gaps/errors remain separate and complete.
    standard_bounds = {'TRANSITIVE_AND_CROSS_MOD_IMPACT', 'RUNTIME_EFFECT', 'TEST_COVERAGE',
                       'NUMERIC_BINDING_SCOPE', 'PEER_CONTRACT_SCOPE', 'EDIT_TARGETS',
                       'DEPENDENCY_METHOD_PROJECTION', 'POSSIBLE_PEERS',
                       'PRODUCTION_SOURCE_MAPPING', 'PLAN_COMPLETENESS'}
    bounds = [i for i in buckets['UNKNOWN'] if i.get('kind') in standard_bounds and
              set(i) <= {'id', 'relevance', 'classification', 'kind', 'reason'}]
    if bounds:
        buckets['UNKNOWN'] = [i for i in buckets['UNKNOWN'] if i not in bounds]
        buckets['UNKNOWN'].append(dict(id='adaptive:bounds', relevance='UNKNOWN', classification='UNKNOWN',
            kind='UNVERIFIED_BOUNDARIES', topics=[i['kind'] for i in bounds], source_refs=[i['id'] for i in bounds],
            reason='Runtime reachability, transitive/cross-mod effects, full test coverage and production edit mapping remain unverified. Numeric validation covers supported bindings only. Projected dependency evidence and peer links require V3 follow-up for omitted detail.'))
    for item in buckets['REQUIRED']:
        if item.get('kind') == 'REQUESTED_BEHAVIOR':
            require(item['requested_behavior'] == plan['request']['requested_behavior'], 'Request behavior reference mismatch')
            item.pop('requested_behavior')
            item['request_ref'] = '/requested_behavior'
        if item.get('kind') == 'CALLER_CONSTRAINT':
            item['request_ref'] = '/constraints/' + str(plan['request']['constraints'].index(item.pop('constraint')))
    required_ids = {i['id'] for i in buckets['REQUIRED']}
    constraint_ids = [i['id'] for i in buckets['REQUIRED'] if i.get('kind', '').startswith('RECORDED_')]
    for item in buckets['REQUIRED']:
        if item.get('kind') == 'PRESERVATION_OBLIGATION':
            item['depends_on'] = constraint_ids
            if profile:
                item['instruction'] = 'Preserve the required scoped gates, units, other inputs and coupled uses. This projection applies only to replacing the selected literal; broader edits require the V3 contract.'
        elif 'depends_on' in item:
            item['depends_on'] = [i for i in item['depends_on'] if i in required_ids]
    chain = copy.deepcopy(plan['reasoning_chain'])
    for link in chain:
        link['relevance'] = 'REQUIRED'
        for key in ('existing_behavior', 'preserved_constraints', 'implementation_locations', 'validation_requirements'):
            link[key] = [i for i in link[key] if i in required_ids]
        if profile:
            link['existing_behavior'] = [i['id'] for i in buckets['REQUIRED'] if i.get('kind') == 'CURRENT_MECHANIC']
    evidence_ids = {i['evidence_link'] for i in buckets['REQUIRED'] if 'evidence_link' in i}
    if not profile or profile['dependency_mode'] == 'FULL':
        evidence_ids.update(e for i in buckets['REQUIRED'] if i.get('kind') == 'RECORDED_OBLIGATION'
                            for e in i['record'].get('evidence_links', []))
    evidence = [dict(e, relevance='REQUIRED') for e in plan['evidence'] if e['id'] in evidence_ids]
    sources = {e['source_id'] for e in evidence}
    source_evidence = [dict(s, relevance='REQUIRED') for s in plan['evidence_sources'] if s['id'] in sources]
    for e in plan['evidence']:
        if e['id'] not in evidence_ids:
            defer(e)
    for e in plan['evidence_sources']:
        if e['id'] not in sources:
            defer(e)
    if profile is None:
        buckets['UNKNOWN'].append(dict(id='adaptive:scope', relevance='UNKNOWN', classification='UNKNOWN',
            kind='SCOPE_UNRESOLVED', reason='No applicable pinned literal profile. No information is declared unrelated.',
            fallback='SELECTION_ONLY' if unresolved else 'FULL_V3_CONSTRAINTS'))
    return dict(plan='ADAPTIVE_LITERAL_PLAN_V4', readiness=plan['readiness'], mod_key=plan['mod_key'],
        request=dict(plan['request'], relevance='REQUIRED'), selected_parameter=dict(plan['selected_parameter'], relevance='REQUIRED') if plan['selected_parameter'] else None,
        scope=dict(profile_id=profile['id'] if profile else None, profile_input=provenance,
            restriction='SELECTED_LITERAL_ONLY' if profile else 'UNRESOLVED',
            sufficiency='PINNED_SCOPE_ONLY' if profile else 'NOT_ESTABLISHED',
            excluded_runtime_impact='NOT_PROVEN', backend_validation='FULL_V3_UNCHANGED'),
        information=buckets, reasoning_chain=chain, evidence=evidence, evidence_sources=source_evidence,
        repository_inputs=plan['repository_inputs'], restore=dict(command='plan WITHOUT --adaptive',
            v3_plan_fingerprint=fingerprint(plan), references='V3 item IDs and JSON pointers'),
        selection_counts={k: len(v) for k, v in buckets.items()})
