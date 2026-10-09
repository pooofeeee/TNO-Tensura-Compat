"""Read-only V1 retrieval of canonical, pinned mod contracts. No extraction or scans."""
import argparse
import json
from pathlib import Path
import re
import sys

from audit_catalog_integrity import EvidenceIndex
from catalog_common import OUT, sha256

SCHEMA = 'tno.mod_intelligence.v1'
KEY_ALIASES = {'bossesrise': 'block_factorys_bosses', 'bomd': 'bosses_of_mass_destruction'}


class CatalogError(Exception):
    def __init__(self, message, code=2):
        super().__init__(message)
        self.code = code


def require(condition, message, code=2):
    if not condition:
        raise CatalogError(message, code)


def pick(value, keys):
    return {key: value[key] for key in keys if key in value}


class CatalogIndex(EvidenceIndex):
    """Reuse the existing witness resolver; confine all catalog references to root."""
    def read(self, file):
        path = (self.root / file).resolve()
        require(path.is_relative_to(self.root), f'Catalog reference escapes root: {file}')
        return super().read(path.relative_to(self.root).as_posix())


class Catalog:
    def __init__(self, root=OUT):
        self.root = Path(root).resolve()
        self.index = CatalogIndex(self.root)
        self.ledger = self.index.read('mod-completion-ledger.json')
        self.inventory = self.index.read('jar-inventory.json')
        require(self.ledger['baseline'] == self.inventory['baseline'], 'Inventory/ledger baseline mismatch')
        self.targets = {t['mod_key']: t for t in self.ledger['targets']}
        require(len(self.targets) == len(self.ledger['targets']), 'Duplicate ledger mod keys')
        artifacts = (self.inventory['targets'] + self.inventory.get('dependency_artifacts', [])
                     + self.inventory.get('compat_candidates', []))
        self.artifacts = {a['key']: a for a in artifacts}
        self.reviews = {}

    def key(self, key):
        key = KEY_ALIASES.get(key, key)
        require(key in self.targets, f'Unknown catalog mod: {key}', 4)
        return key

    def artifact_key(self, key):
        key = KEY_ALIASES.get(key, key)
        require(key in self.artifacts, f'Unknown inventoried artifact: {key}', 4)
        return key

    def source(self, key):
        artifact = self.artifacts[key]
        require(re.fullmatch(r'[0-9a-f]{64}', artifact.get('sha256', '')),
                f'Missing or invalid source pin: {key}')
        mods = []
        for metadata in artifact.get('metadata', []):
            parsed = metadata.get('parsed')
            if isinstance(parsed, dict):
                mods.extend(pick(m, ['modId', 'version', 'displayName'])
                            for m in parsed.get('mods', []))
        result = dict(filename=artifact['filename'], sha256=artifact['sha256'], declared_mods=mods)
        if artifact.get('version'):
            result['recorded_version'] = artifact['version']
        return result

    def source_check(self, key, version=None, digest=None, jar=None):
        source = self.source(key)
        checks = dict(catalog_pin=source, local_artifact='NOT_CHECKED')
        if version is not None:
            versions = {str(m.get('version')) for m in source['declared_mods']}
            if source.get('recorded_version'):
                versions.add(source['recorded_version'])
            require(version in versions,
                    f'Source version mismatch for {key}: expected {version}; catalog declares {sorted(versions)}', 3)
            checks['expected_version'] = dict(value=version, status='MATCH')
        if digest is not None:
            require(re.fullmatch(r'[0-9a-fA-F]{64}', digest), 'Expected SHA-256 must contain 64 hexadecimal digits')
            require(digest.lower() == source['sha256'], f'Source SHA-256 mismatch for {key}', 3)
            checks['expected_sha256'] = dict(value=digest.lower(), status='MATCH')
        if jar is not None:
            actual = sha256(jar)
            require(actual == source['sha256'], f'Local JAR SHA-256 mismatch for {key}: {actual}', 3)
            checks['local_artifact'] = dict(path=str(Path(jar).resolve()), sha256=actual, status='MATCH')
        return checks

    def review(self, key):
        key = self.key(key)
        if key not in self.reviews:
            target = self.targets[key]
            file = f'mod-reviews/{key}.json'
            require(target['state'] == 'COMPLETE' and (self.root / file).is_file(),
                    f'No completed semantic catalog for {key}: {target["state"]}; {target["detail"]}', 4)
            review = self.index.read(file)
            require(review['mod_key'] == key and review['status'] == 'COMPLETE',
                    f'Ledger/review completion mismatch for {key}')
            require(review['baseline'] == self.ledger['baseline'] == self.inventory['baseline'],
                    f'Catalog baseline mismatch for {key}')
            require(len({r['id'] for r in review['effects']}) == len(review['effects']),
                    f'Duplicate mechanic IDs in {key}')
            self.reviews[key] = review
        return self.reviews[key]

    def completed_keys(self, mod=None):
        if mod:
            key = self.key(mod)
            self.review(key)
            return [key]
        return sorted(key for key, t in self.targets.items()
                      if t['state'] == 'COMPLETE' and (self.root / f'mod-reviews/{key}.json').is_file())

    def mods(self):
        return [dict(mod_key=key, state=t['state'], scope=t['detail'],
                     semantic_catalog_available=t['state'] == 'COMPLETE'
                     and (self.root / f'mod-reviews/{key}.json').is_file(),
                     mechanic_count=t.get('semantic_effect_count'), source=self.source(key))
                for key, t in sorted(self.targets.items())]

    @staticmethod
    def summary(row):
        return dict(id=row['id'], mod_key=row['mod_key'], name=row['display_name'],
                    classification=row['primary_classification'],
                    summary=row['actual_behavior'][:240],
                    summary_truncated=len(row['actual_behavior']) > 240,
                    primitives=sorted({c['primitive'] for c in row['components']}),
                    registry_ids=row.get('registry_ids', []))

    def search(self, query, mod=None, limit=10, offset=0, classification=None, primitive=None):
        terms = query.casefold().split()
        require(terms, 'Search query must not be empty')
        hits = []
        for key in self.completed_keys(mod):
            review = self.review(key)
            for row in review['effects']:
                if classification and row['primary_classification'] != classification:
                    continue
                if primitive and not any(c['primitive'] == primitive for c in row['components']):
                    continue
                text = json.dumps(pick(row, ['id', 'display_name', 'actual_behavior', 'human_summary',
                    'source_actor', 'registry_ids', 'primary_classification', 'components',
                    'numerical_parameters', 'implementation']), ensure_ascii=False).casefold()
                if all(term in text for term in terms):
                    hits.append(row)
        hits.sort(key=lambda row: (row['mod_key'], row['id']))
        selected = hits[offset:offset + limit]
        return dict(query=query, total=len(hits), offset=offset, limit=limit,
                    has_more=offset + limit < len(hits),
                    results=[self.summary(row) for row in selected],
                    sources={key: self.source(key) for key in sorted({row['mod_key'] for row in selected})})

    def find(self, identity, mod=None):
        matches = []
        for key in self.completed_keys(mod):
            review = self.review(key)
            rows = [row for row in review['effects'] if row['id'] == identity]
            aliases = [a for a in review.get('semantic_aliases', []) if a['original_id'] == identity]
            if aliases:
                require(len(aliases) == 1 and not rows, f'Ambiguous alias: {identity}')
                alias = aliases[0]
                by_id = {row['id']: row for row in review['effects']}
                require(all(i in by_id for i in alias['canonical_ids']), f'Dangling alias: {identity}')
                rows = [by_id[i] for i in alias['canonical_ids']]
            if rows:
                matches.append((key, rows, aliases[0] if aliases else None))
        require(len(matches) == 1, f'Mechanic not found or ambiguous: {identity}', 4)
        return matches[0]

    def evidence(self, proof, row):
        file, witness = self.index.witness(proof, row)
        packet = self.index.read(file)
        require(packet.get('baseline', self.ledger['baseline']) == self.ledger['baseline'],
                f'Evidence baseline mismatch: {file}')
        artifact_key = KEY_ALIASES.get(witness.get('mod_key'), witness.get('mod_key'))
        digest = witness.get('jar_sha256')
        if digest:
            require(re.fullmatch(r'[0-9a-f]{64}', digest), f'Invalid witness source pin: {file}')
            if artifact_key in self.artifacts:
                require(digest == self.artifacts[artifact_key]['sha256'],
                        f'Witness source SHA-256 mismatch: {file}#{proof["entry"]}', 3)
        descriptor = proof.get('descriptor')
        names = proof.get('methods', [])
        methods = [m for m in witness.get('methods', []) if m['name'] in names and
                   (not descriptor or descriptor in (m.get('descriptor'), m.get('raw_descriptor'),
                                                     m.get('obfuscated_descriptor')))]
        require(set(names) <= {m['name'] for m in methods}, f'Missing exact method: {file}#{proof["entry"]}')
        for method in methods:
            if method.get('code_sha256'):
                require(re.fullmatch(r'[0-9a-f]{64}', method['code_sha256']), f'Invalid method hash: {file}')
        require(not any(len(hashes) > 1 for hashes in self.index.methods.values()),
                'Conflicting code hashes for a selected method identity')
        if 'offset' in proof:
            require(len(methods) == 1, f'Ambiguous numeric consumer: {file}#{proof["entry"]}')
            sites = [i for i in methods[0].get('instructions', []) if i['offset'] == proof['offset']]
            require(len(sites) == 1, f'Missing numeric consumer offset: {file}#{proof["entry"]}')
            for field in ['opcode', 'operand']:
                if field in proof:
                    require(proof[field] == sites[0].get(field), f'Numeric consumer {field} mismatch: {row["id"]}')
        result = dict(file=file, file_sha256=self.index.file_hashes[file],
                      entry=proof['entry'], source_pin_check='INVENTORY_MATCH' if digest
                      and artifact_key in self.artifacts else 'PACKET_PIN_ONLY')
        result.update(pick(witness, ['id', 'mod_key', 'jar_sha256', 'entry_sha256', 'raw_class_sha256', 'archive_sha256']))
        result['packet_source'] = pick(packet, ['version', 'client_jar_sha256', 'mappings_sha256', 'manifest_sha256'])
        result['methods'] = [pick(m, ['name', 'descriptor', 'raw_descriptor', 'obfuscated_descriptor', 'code_sha256'])
                             for m in methods]
        if 'offset' in proof:
            result['site'] = pick(proof, ['offset', 'opcode', 'operand'])
        return result

    def dependencies(self, key):
        key = self.key(key)
        review = self.review(key)
        declared = []
        for metadata in self.artifacts[key].get('metadata', []):
            parsed = metadata.get('parsed')
            if isinstance(parsed, dict):
                for owner, deps in parsed.get('dependencies', {}).items():
                    declared.extend(dict(owner_mod_id=owner, **dep) for dep in deps)
        result = dict(mod_key=key, declared=declared, obligations=None,
                      obligation_status='NOT_RECORDED')
        file = review.get('external_dependency_obligations_file')
        if file:
            data = self.index.read(file)
            require(data['mod_key'] == key and data['native_jar_sha256'] == self.source(key)['sha256'],
                    f'Dependency obligation source mismatch: {file}', 3)
            require(not review.get('external_dependency_complete') or data['status'] == 'COMPLETE',
                    f'Dependency completion mismatch: {file}')
            artifact = data['artifact']
            pinned = self.artifacts.get(artifact['mod_id'])
            if pinned:
                require(artifact['sha256'] == pinned['sha256'] and
                        artifact['exact_installed_version'] == pinned.get('version'),
                        f'Dependency artifact mismatch: {file}', 3)
            result.update(obligation_status=data['status'], evidence_file=file,
                          artifact=pick(artifact, ['mod_id', 'filename', 'declared_minimum',
                            'exact_installed_version', 'sha256', 'status']),
                          obligations=[pick(o, ['id', 'status', 'actual_contract', 'contract', 'claim_limit',
                            'affected_mechanic_ids', 'evidence_files', 'evidence', 'vanilla_evidence_file'])
                                       for o in data['obligations']])
        return result

    def record(self, key, row):
        require(not row.get('pending') and not row.get('unresolved_ambiguities'),
                f'Mechanic has unresolved semantics: {row["id"]}', 4)
        proofs = row['implementation'] + row.get('shared_contracts', []) + row.get('native_resource_evidence', [])
        candidates = row.get('scalable_parameter_candidates', [])
        for candidate in candidates:
            if isinstance(candidate, dict):
                for parameter in candidate['parameters']:
                    components = [c for c in row['components'] if c['primitive'] == candidate['primitive'] and
                                  parameter in (set(c.get('numerical_parameters', {})) |
                                                set(c.get('component_numerical_parameters', {})) |
                                                set(c.get('parameter_formulas', {})))]
                    require(len(components) == 1, f'Detached numeric candidate: {row["id"]}/{parameter}')
                    values = components[0].get('numerical_parameters', {})
                    if 'native_value' in candidate and parameter in values:
                        require(candidate['native_value'] == values[parameter],
                                f'Numeric value mismatch: {row["id"]}/{parameter}')
                consumer = candidate.get('native_consumer')
                if consumer and consumer.get('evidence_file'):
                    proofs.append(consumer)
                proofs.extend(site for site in candidate.get('additional_consumer_sites', [])
                              if site.get('evidence_file') and site.get('methods'))
        evidence = []
        seen = set()
        for proof in proofs:
            signature = json.dumps(proof, sort_keys=True)
            if signature not in seen:
                evidence.append(self.evidence(proof, row))
                seen.add(signature)
        facts = []
        references = row.get('fact_references', []) + [ref for c in row['components'] for ref in c.get('fact_references', [])]
        for ref in references:
            require(ref['key'] in self.index.read(ref['file']).get('facts', {}), f'Missing fact: {ref}')
            fact = dict(ref, value=self.index.read(ref['file'])['facts'][ref['key']])
            if fact not in facts:
                facts.append(fact)
        review = self.review(key)
        paths = {p['id']: p for p in review['paths']}
        deliveries = []
        for identity in row['delivery_paths']:
            require(identity in paths and row['id'] in paths[identity]['effect_ids'], f'Broken delivery link: {identity}')
            deliveries.append(pick(paths[identity], ['id', 'labels', 'primary_source', 'setup', 'effect_ids']))
        contract = pick(row, ['source_actor', 'hurt_return_dependency', 'binary_parameters',
                        'eligibility', 'stacking', 'removal', 'lifecycle', 'duration_and_tick_semantics',
                        'custom_state', 'flags', 'damage_path', 'contract_refinements',
                        'closest_vanilla_equivalent', 'vanilla_similarities', 'vanilla_differences',
                        'non_independent_parameters', 'native_optional_integrations', 'existing_compat_modification'])
        if contract.get('vanilla_differences') == row['actual_behavior']:
            contract.pop('vanilla_differences')
        components = [{k: v for k, v in component.items() if k not in
                       ['implementation', 'vanilla_implementation', 'comparison_evidence']}
                      for component in row['components']]
        return dict(id=row['id'], mod_key=key, name=row['display_name'],
                    classification=row['primary_classification'], inspection_status=row['inspection_status'],
                    verification='CANONICAL_STATIC_CONTRACT_WITH_SELECTED_WITNESSES',
                    actual_behavior=row['actual_behavior'],
                    contract=contract, components=components,
                    numeric_parameters=pick(row, ['numerical_parameters', 'component_numerical_parameters',
                        'parameter_formulas', 'numeric_observations']),
                    parameter_candidates=candidates,
                    numeric_binding_note='Canonical observations only; legacy string candidates have no inferred consumer binding.',
                    facts=facts, delivery_paths=deliveries, evidence=evidence,
                    reference_files=row.get('reference_evidence', []),
                    canonical_ref=dict(file=f'mod-reviews/{key}.json', id=row['id'], checkpoint=review.get('checkpoint')))

    def get(self, identity, mod=None, sections=None):
        key, rows, alias = self.find(identity, mod)
        records = [self.record(key, row) for row in rows]
        sections = set(sections or ['semantics', 'numbers', 'evidence', 'dependencies'])
        fields = {'semantics': ['actual_behavior', 'contract', 'facts', 'delivery_paths'],
                  'numbers': ['components', 'numeric_parameters', 'parameter_candidates', 'numeric_binding_note'],
                  'evidence': ['evidence', 'reference_files']}
        base = ['id', 'mod_key', 'name', 'classification', 'inspection_status', 'verification', 'canonical_ref']
        data = dict(mod_key=key, requested_id=identity,
                    mechanics=[pick(record, base + [field for section in sorted(sections)
                              for field in fields.get(section, [])]) for record in records])
        if 'dependencies' in sections:
            dependencies = self.dependencies(key)
            if dependencies['obligations'] is not None:
                dependencies['obligations'] = [pick(o, ['id', 'status']) for o in dependencies['obligations']]
            data['dependencies'] = dependencies
        if alias:
            data['alias'] = pick(alias, ['original_id', 'canonical_ids', 'reason'])
            data['alias_evidence'] = [self.evidence(proof, dict(id=identity)) for proof in alias['native_evidence']]
        return data

    def response(self, command, data):
        return dict(schema=SCHEMA, command=command, status='OK',
                    scope='STATIC_PINNED_CATALOG', catalog_checkpoint=self.ledger['checkpoint'],
                    data=data, inputs=[dict(file=file, sha256=digest)
                                       for file, digest in sorted(self.index.file_hashes.items())])


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise CatalogError(message)


def bounded_int(value):
    number = int(value)
    if not 1 <= number <= 100:
        raise argparse.ArgumentTypeError('limit must be between 1 and 100')
    return number


def nonnegative_int(value):
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError('offset must be nonnegative')
    return number


def parser():
    cli = Parser(description=__doc__)
    cli.add_argument('--catalog', type=Path, default=OUT, help='Existing catalog directory')
    cli.add_argument('--pretty', action='store_true', help='Indent JSON output')
    commands = cli.add_subparsers(dest='command', required=True, parser_class=Parser)
    commands.add_parser('mods', help='List catalog coverage and exact source pins')
    search = commands.add_parser('search', help='AND search over canonical mechanics; bounded summaries')
    search.add_argument('query')
    search.add_argument('--mod')
    search.add_argument('--limit', type=bounded_int, default=10)
    search.add_argument('--offset', type=nonnegative_int, default=0)
    search.add_argument('--classification')
    search.add_argument('--primitive')
    get = commands.add_parser('get', help='Retrieve an exact mechanic ID or canonical alias')
    get.add_argument('id')
    get.add_argument('--mod', help='Restrict lookup to a catalog mod key')
    get.add_argument('--section', action='append', choices=['semantics', 'numbers', 'evidence', 'dependencies'],
                     help='Emit only these sections (repeatable); selected witnesses are always checked')
    deps = commands.add_parser('dependencies', help='Read declared dependencies and resolved obligations')
    deps.add_argument('mod')
    verify = commands.add_parser('verify', help='Check an inventoried mod or dependency pin without extraction')
    verify.add_argument('mod')
    for command in [search, get, deps, verify]:
        command.add_argument('--expect-version', help='Exact embedded or inventoried dependency version, not a filename version')
        command.add_argument('--expect-sha256', help='Expected catalog JAR SHA-256')
        command.add_argument('--jar', type=Path, help='Hash this local JAR against the catalog pin; never scan it')
    return cli


def main(argv=None):
    pretty = False
    try:
        args = parser().parse_args(argv)
        pretty = args.pretty
        catalog = Catalog(args.catalog)
        constraints = {name: getattr(args, 'expect_' + name, None) for name in ['version', 'sha256']}
        if args.command == 'mods':
            data = dict(mods=catalog.mods())
        elif args.command == 'search':
            require(args.mod or not any([constraints['version'], constraints['sha256'], args.jar]),
                    'Source checks on search require --mod')
            check = catalog.source_check(catalog.key(args.mod), constraints['version'], constraints['sha256'], args.jar) if args.mod else None
            data = catalog.search(args.query, args.mod, args.limit, args.offset, args.classification, args.primitive)
            if check:
                data['source_check'] = check
        elif args.command == 'get':
            key, _, _ = catalog.find(args.id, args.mod)
            check = catalog.source_check(key, constraints['version'], constraints['sha256'], args.jar)
            data = catalog.get(args.id, key, args.section)
            data['source_check'] = check
        else:
            key = catalog.artifact_key(args.mod) if args.command == 'verify' else catalog.key(args.mod)
            check = catalog.source_check(key, constraints['version'], constraints['sha256'], args.jar)
            data = catalog.dependencies(key) if args.command == 'dependencies' else dict(mod_key=key)
            data['source_check'] = check
        result, code = catalog.response(args.command, data), 0
    except CatalogError as error:
        result, code = dict(schema=SCHEMA, status='ERROR', error=str(error)), error.code
    except (OSError, ValueError, KeyError, TypeError, AssertionError) as error:
        result, code = dict(schema=SCHEMA, status='ERROR', error=f'Invalid or unavailable catalog input: {error}'), 2
    print(json.dumps(result, ensure_ascii=False, indent=2 if pretty else None,
                     separators=None if pretty else (',', ':'), allow_nan=False))
    return code


if __name__ == '__main__':
    sys.exit(main())
