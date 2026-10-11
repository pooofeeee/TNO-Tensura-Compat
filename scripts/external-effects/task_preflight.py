"""Deterministic task preflight over unchanged Mod Intelligence planners."""
import hashlib
import json
import math
from pathlib import Path
import sys

import mod_intelligence as mi

SCHEMA = 'tno.task_preflight.v1'
MANIFEST_SCHEMA = 'tno.task_manifest.v1'


def fields(value, required, optional=()):
    mi.require(isinstance(value, dict) and set(required) <= set(value)
               <= set(required) | set(optional), f'Expected fields: {sorted(required)}')


def text(value):
    mi.require(isinstance(value, str) and bool(value.strip()) and len(value) <= 4096,
               'Expected nonempty text of at most 4096 characters')


def strict_json(path):
    raw = path.read_bytes()
    mi.require(len(raw) <= 65536, 'Manifest exceeds 65536 bytes')

    def pairs(items):
        result = {}
        for key, value in items:
            mi.require(key not in result, f'Duplicate JSON key: {key}')
            result[key] = value
        return result

    def number(value):
        result = float(value)
        mi.require(math.isfinite(result), 'Nonfinite JSON number')
        return result

    return json.loads(raw, object_pairs_hook=pairs, parse_float=number,
                      parse_constant=number), hashlib.sha256(raw).hexdigest()


def pinned_file(record, root, optional=()):
    fields(record, ('file', 'sha256'), optional)
    text(record['file'])
    relative = Path(record['file'])
    mi.require(not relative.is_absolute() and '..' not in relative.parts,
               'Referenced files must be relative to the repository root')
    path = (root / relative).resolve()
    mi.require(path.is_relative_to(root) and path.is_file(),
               f'Missing file or path outside root: {record["file"]}')
    mi.require(mi.valid_digest(record['sha256']), 'Invalid file SHA-256')
    mi.require(hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256'],
               f'Stale file pin: {record["file"]}', 3)
    return path


def source_pin(record):
    fields(record, ('mod', 'version', 'sha256'))
    text(record['mod'])
    text(record['version'])
    mi.require(mi.valid_digest(record['sha256']), 'Invalid source SHA-256')


def preflight(manifest_path, root=mi.ROOT, catalog_path=mi.OUT):
    root = Path(root).resolve()
    manifest, digest = strict_json(Path(manifest_path))
    fields(manifest, ('schema', 'task_type', 'scope', 'change_request',
                     'approved_edit_targets', 'required_tests', 'sources', 'unresolved_questions'))
    mi.require(manifest['schema'] == MANIFEST_SCHEMA, 'Unsupported task manifest schema')
    mi.require(manifest['task_type'] in ('local_behavior', 'dependency_related', 'preservation_behavior'),
               'Unsupported task type')
    fields(manifest['scope'], ('kind', 'description'))
    scope = manifest['scope']
    mi.require(scope['kind'] in ('literal_only', 'broader_implementation'), 'Unsupported scope kind')
    text(scope['description'])
    for name in ('approved_edit_targets', 'required_tests', 'unresolved_questions'):
        mi.require(isinstance(manifest[name], list) and len(manifest[name]) <= 32,
                   f'{name} must be an array of at most 32 entries')
    mi.require(manifest['approved_edit_targets'] and manifest['required_tests'],
               'At least one edit target and required test is mandatory')
    for question in manifest['unresolved_questions']:
        text(question)
    request_path = pinned_file(manifest['change_request'], root)
    targets = [pinned_file(record, root) for record in manifest['approved_edit_targets']]
    tests = []
    for record in manifest['required_tests']:
        tests.append(pinned_file(record, root, ('command',)))
        command = record.get('command')
        mi.require(isinstance(command, list) and 0 < len(command) <= 32,
                   'Each required test needs a nonempty command argument array')
        for arg in command:
            text(arg)
    mi.require(len(set(targets)) == len(targets) and len(set(tests)) == len(tests),
               'Duplicate target/test paths')
    mi.require(not set(targets) & set(tests), 'Required test files cannot also be edit targets')
    fields(manifest['sources'], ('native',), ('dependency',))
    native = manifest['sources']['native']
    dependency = manifest['sources'].get('dependency')
    source_pin(native)
    if 'dependency' in manifest['sources']:
        source_pin(dependency)

    catalog = mi.Catalog(catalog_path)
    request, provenance = mi.read_change_intent(request_path)
    mi.require(provenance['sha256'] == manifest['change_request']['sha256'],
               'Change request changed during preflight', 3)
    key, _, _ = catalog.find(request['target'], native['mod'])
    checks = dict(native=catalog.source_check(key, native['version'], native['sha256']))
    if dependency is not None:
        checks['dependency'] = catalog.source_check(catalog.artifact_key(dependency['mod']),
                                                    dependency['version'], dependency['sha256'])
    # Select before retrieval: broader work never starts with a literal-only projection.
    adaptive = scope['kind'] == 'literal_only' and not manifest['unresolved_questions']
    planner = catalog.adaptive_plan if adaptive else catalog.plan
    plan = planner(request['target'], request, key, repo_root=root,
                   dependency_version=dependency['version'] if dependency else None,
                   dependency_digest=dependency['sha256'] if dependency else None)
    obligations = (plan['dependencies'] if not adaptive else
                   [item for item in plan['information']['REQUIRED']
                    if item['kind'] in ('RECORDED_OBLIGATION', 'RECORDED_OBLIGATION_IDENTITY')])
    reasons = list(manifest['unresolved_questions'])
    if obligations and dependency is None:
        reasons.append('Supply an expected dependency identity before applying its contract.')
    if plan['readiness'] != 'REVIEW_REQUIRED':
        reasons.append(f'Existing planner readiness: {plan["readiness"]}')
    if adaptive and plan['scope']['sufficiency'] != 'PINNED_SCOPE_ONLY':
        reasons.append('No pinned adaptive profile establishes the declared literal scope.')
    route = ('REQUIRES_ADDITIONAL_EVIDENCE' if reasons else
             'SUPPORTED_LITERAL_EDIT' if adaptive else 'BROADER_IMPLEMENTATION')
    evidence = catalog.response('plan', plan)
    evidence['schema'] = mi.ADAPTIVE_SCHEMA if adaptive else mi.PLAN_SCHEMA
    return dict(schema=SCHEMA, status='NEEDS_EVIDENCE' if reasons else 'OK',
                manifest_sha256=digest, route=route,
                task=dict(task_type=manifest['task_type'], scope=scope,
                          change_request=manifest['change_request'],
                          approved_edit_targets=manifest['approved_edit_targets'],
                          required_tests=manifest['required_tests'], unresolved_questions=reasons),
                checks=dict(files='HASH_MATCH', sources=checks, tests='NOT_RUN'),
                limits=['Scope and edit approval are caller declarations, not inferred source mappings.',
                        'Source checks compare catalog identities; installed JARs are not checked.',
                        'Required tests are caller-supplied obligations, not proven coverage.',
                        'Review the preserved plan constraints and UNKNOWNs before implementation.'],
                evidence_plan=evidence)


def main(argv=None):
    try:
        parser = mi.Parser(description=__doc__)
        parser.add_argument('--manifest', type=Path, required=True)
        parser.add_argument('--root', type=Path, default=mi.ROOT)
        parser.add_argument('--catalog', type=Path, default=mi.OUT)
        parser.add_argument('--budget-bytes', type=mi.positive_int, default=131072)
        args = parser.parse_args(argv)
        result = preflight(args.manifest, args.root, args.catalog)
        output = json.dumps(result, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
        required = len(output.encode('utf-8')) + 1
        if required > args.budget_bytes:
            raise mi.ContextBudgetError(args.budget_bytes, required, 'Preflight')
        code = 4 if result['status'] == 'NEEDS_EVIDENCE' else 0
    except mi.CatalogError as error:
        result = dict(schema=SCHEMA, status='ERROR', error=str(error))
        if isinstance(error, mi.ContextBudgetError):
            result['budget'] = error.budget
        output, code = json.dumps(result), error.code
    except (OSError, ValueError, TypeError, KeyError, RecursionError, OverflowError) as error:
        output, code = json.dumps(dict(schema=SCHEMA, status='ERROR', error=str(error))), 2
    print(output)
    return code


if __name__ == '__main__':
    sys.exit(main())
