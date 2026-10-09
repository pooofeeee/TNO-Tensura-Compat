"""Read-only V1 retrieval of canonical, pinned mod contracts. No extraction or scans."""
import argparse
import json
import math
from pathlib import Path
import re
import sys

from audit_catalog_integrity import EvidenceIndex, object_list
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


def mapping(value, label):
    require(isinstance(value, dict), f'Expected an object: {label}')
    return value


def valid_digest(value):
    return isinstance(value, str) and re.fullmatch(r'[0-9a-f]{64}', value)


LITERAL_OPCODES = {hex(op) for op in range(2, 21)}
SCALAR_BINDINGS = {
    'native_attribute_binding', 'native_literal_call_argument_binding',
    'native_last_numeric_argument_binding', 'native_literal_numeric_input_binding',
    'native_literal_constructor_argument_binding', 'native_literal_integer_dividend_binding',
    'native_effect_attribute_binding', 'native_literal_numeric_site_binding',
    'native_item_attribute_binding', 'native_synched_int_binding', 'native_vector_scale_binding',
    'native_item_wear_binding', 'native_literal_field_numeric_binding', 'native_block_factor_binding',
    'native_subtract_tag_vector_binding', 'native_numeric_return_binding',
}


class CatalogIndex(EvidenceIndex):
    """Reuse the existing witness resolver; confine all catalog references to root."""
    def __init__(self, root):
        super().__init__(root, strict_json=True)

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
        self.targets = {t['mod_key']: t for t in object_list(self.ledger['targets'], 'ledger targets')}
        require(len(self.targets) == len(self.ledger['targets']), 'Duplicate ledger mod keys')
        artifacts = object_list(self.inventory['targets'], 'inventory targets')
        artifacts = artifacts + [a for field in ['dependency_artifacts', 'compat_candidates']
                     for a in object_list(self.inventory.get(field, []), f'inventory {field}')]
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
        require(valid_digest(artifact.get('sha256')),
                f'Missing or invalid source pin: {key}')
        mods = []
        for parsed in self.metadata(key):
            mods.extend(pick(m, ['modId', 'version', 'displayName'])
                        for m in object_list(parsed.get('mods', []), f'{key} declared mods'))
        result = dict(filename=artifact['filename'], sha256=artifact['sha256'], declared_mods=mods)
        if artifact.get('version'):
            result['recorded_version'] = artifact['version']
        return result

    def metadata(self, key):
        for metadata in object_list(self.artifacts[key].get('metadata', []), f'{key} metadata'):
            parsed = metadata.get('parsed')
            # Manifest text is a legitimate alternative to parsed TOML metadata.
            if isinstance(parsed, dict):
                yield parsed
            else:
                require(parsed is None or isinstance(parsed, str), f'Invalid metadata: {key}')

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
            rows = object_list(review['effects'], f'{key} effects')
            object_list(review['paths'], f'{key} paths')
            object_list(review.get('semantic_aliases', []), f'{key} aliases')
            for row in rows:
                object_list(row['components'], f'{row["id"]} components')
                object_list(row['implementation'], f'{row["id"]} implementation')
            require(len({r['id'] for r in rows}) == len(rows),
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
        inventory_match = False
        if packet.get('schema') == 'tno.external_effects.native_evidence.v1':
            require(isinstance(artifact_key, str) and bool(artifact_key.strip()), f'Missing witness mod key: {file}')
            require(valid_digest(digest), f'Missing or invalid witness source pin: {file}')
            if artifact_key in self.artifacts:
                require(digest == self.artifacts[artifact_key]['sha256'],
                        f'Witness source SHA-256 mismatch: {file}#{proof["entry"]}', 3)
                inventory_match = True
        elif packet.get('schema') == 'tno.external_effects.vanilla_witness.v1':
            require(isinstance(packet.get('classes'), list) and
                    isinstance(witness.get('class_name'), str) and bool(witness['class_name']) and
                    witness.get('raw_entry') == proof['entry'] and valid_digest(witness.get('raw_class_sha256')),
                    f'Invalid Vanilla class identity: {file}')
            require(isinstance(packet.get('version'), str) and bool(packet['version']),
                    f'Missing Vanilla source version: {file}')
            for field in ['client_jar_sha256', 'mappings_sha256', 'manifest_sha256']:
                require(valid_digest(packet.get(field)), f'Missing or invalid Vanilla {field}: {file}')
        elif packet.get('schema') == 'tno.external_effects.selected_reference.v1':
            require(valid_digest(witness.get('archive_sha256')),
                    f'Missing or invalid reference archive pin: {file}')
        else:
            raise CatalogError(f'Unsupported evidence schema: {file}')
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
            sites = [i for i in object_list(methods[0].get('instructions', []), f'{file} instructions')
                     if i['offset'] == proof['offset']]
            require(len(sites) == 1, f'Missing numeric consumer offset: {file}#{proof["entry"]}')
            for field in ['opcode', 'operand']:
                if field in proof:
                    require(proof[field] == sites[0].get(field), f'Numeric consumer {field} mismatch: {row["id"]}')
        result = dict(file=file, file_sha256=self.index.file_hashes[file],
                      entry=proof['entry'], source_pin_check='INVENTORY_MATCH' if inventory_match else 'PACKET_PIN_ONLY')
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
        for parsed in self.metadata(key):
            for owner, deps in mapping(parsed.get('dependencies', {}), f'{key} dependencies').items():
                declared.extend(dict(owner_mod_id=owner, **dep)
                                for dep in object_list(deps, f'{key}/{owner} dependencies'))
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

    def dependency_contracts(self, key, mechanic, obligation=None, version=None, digest=None):
        key, rows, _ = self.find(mechanic, key)
        result = self.dependencies(key)
        require(result['obligations'] is not None, f'Dependency obligations not recorded: {mechanic}', 4)
        file = result['evidence_file']
        data = self.index.read(file)
        require(data.get('schema') == 'tno.external_effects.external_dependency_obligations.v1',
                f'Unsupported dependency obligation schema: {file}')
        obligations = object_list(data['obligations'], 'dependency obligations')
        by_id = {o['id']: o for o in obligations}
        require(len(by_id) == len(obligations), f'Duplicate dependency obligation IDs: {file}')
        if obligation is not None:
            require(obligation in by_id, f'Unknown dependency obligation: {obligation}', 4)
        required = set()
        for row in rows:
            require(not row.get('pending') and not row.get('unresolved_ambiguities'),
                    f'Mechanic has unresolved semantics: {row["id"]}', 4)
            link = row.get('external_dependency_contracts')
            if link is not None:
                mapping(link, 'mechanic dependency link')
                require(link['file'] == file, f'Dependency mapping file mismatch: {row["id"]}')
                require(link['pin_sha256'] == result['artifact']['sha256'],
                        f'Dependency mapping source mismatch: {row["id"]}', 3)
                require(isinstance(link['ids'], list) and all(isinstance(i, str) for i in link['ids']),
                        f'Invalid dependency mapping IDs: {row["id"]}')
                require(all(i in by_id for i in link['ids']), f'Dangling dependency mapping: {row["id"]}')
                for identity in link['ids']:
                    affected = by_id[identity].get('affected_mechanic_ids')
                    require(affected is None or row['id'] in affected,
                            f'Conflicting dependency mapping: {row["id"]}/{identity}')
                required.update(link['ids'])
            for item in obligations:
                affected = item.get('affected_mechanic_ids', [])
                require(isinstance(affected, list) and all(isinstance(i, str) for i in affected),
                        f'Invalid affected mechanic IDs: {item["id"]}')
                if row['id'] in affected:
                    required.add(item['id'])
        require(required, f'Dependency mapping not recorded for mechanic: {mechanic}', 4)
        require(obligation is None or obligation in required,
                f'Dependency obligation does not apply to mechanic: {obligation}/{mechanic}', 4)
        artifact = result['artifact']
        require(data['status'] == 'COMPLETE' and artifact['status'] == 'AVAILABLE_VERIFIED',
                f'Dependency artifact or obligations are unresolved: {file}', 4)
        dependency_key = self.artifact_key(artifact['mod_id'])
        require(valid_digest(artifact['sha256']) and bool(artifact['exact_installed_version']),
                f'Missing resolved dependency identity: {file}')
        dependency_check = self.source_check(dependency_key, version, digest)
        selected = []
        for identity in sorted([obligation] if obligation is not None else required):
            item = by_id[identity]
            require(item['status'] == 'RESOLVED_PINNED',
                    f'Unresolved dependency obligation: {identity} ({item["status"]})', 4)
            proofs = object_list(item.get('evidence', []), f'{identity} witnesses')
            require(proofs, f'Dependency witness identities not recorded: {identity}; file references only', 4)
            witnesses = []
            missing_hashes = False
            for proof in proofs:
                require(all(isinstance(proof.get(k), str) and bool(proof[k].strip())
                            for k in ['evidence_file', 'witness_id', 'entry']),
                        f'Missing dependency witness identity: {identity}')
                evidence = self.evidence(proof, item)
                require(evidence.get('mod_key') == dependency_key and
                        evidence.get('jar_sha256') == artifact['sha256'],
                        f'Dependency witness artifact mismatch: {identity}/{proof["entry"]}', 3)
                _, witness = self.index.witness(proof, item)
                if proof['entry'].endswith('.class'):
                    require(isinstance(witness.get('class_name'), str) and bool(witness['class_name']),
                            f'Missing dependency witness class identity: {identity}')
                    require(bool(proof.get('methods')), f'Missing dependency method selection: {identity}')
                require(evidence.get('id') == proof['witness_id'], f'Missing dependency witness ID: {identity}')
                evidence['witness_id'] = evidence.pop('id')
                evidence['class_name'] = witness.get('class_name')
                class_hash = evidence.get('entry_sha256')
                require(class_hash is None or valid_digest(class_hash), f'Invalid dependency entry hash: {identity}')
                evidence['entry_sha256'] = class_hash
                evidence['hash_status'] = 'RECORDED' if class_hash else 'MISSING'
                missing_hashes |= not class_hash
                for method in evidence['methods']:
                    require(any(isinstance(method.get(k), str) and bool(method[k])
                                for k in ['descriptor', 'raw_descriptor', 'obfuscated_descriptor']),
                            f'Missing dependency method identity: {identity}/{method["name"]}')
                    method_hash = method.get('code_sha256')
                    method['code_sha256'] = method_hash
                    method['hash_status'] = 'RECORDED' if method_hash else 'MISSING'
                    missing_hashes |= not method_hash
                witnesses.append(evidence)
            references = item.get('evidence_files', []) + ([item['vanilla_evidence_file']]
                         if item.get('vanilla_evidence_file') else [])
            require(isinstance(references, list) and all(isinstance(f, str) for f in references),
                    f'Invalid dependency references: {identity}')
            selected.append(dict(pick(item, ['id', 'status', 'affected_mechanic_ids', 'actual_contract',
                'contract', 'claim_limit', 'verified_existing_reuse']), witnesses=witnesses,
                affected_mechanic_ids=item.get('affected_mechanic_ids'),
                references=[dict(file=f, validation_state='REFERENCE_ONLY') for f in references],
                validation_state='WITNESSES_RESOLVED_WITH_MISSING_HASHES' if missing_hashes else 'WITNESSES_RESOLVED'))
        result.update(requested_mechanic=mechanic, mechanic_ids=[r['id'] for r in rows],
                      required_obligation_ids=sorted(required), obligations=selected,
                      dependency_source_check=dependency_check)
        return result

    def numeric_binding(self, candidate, values, row):
        """Check recorded numeric bindings against literal sites, never call operands.

        This validates existing binding schemas; it does not infer control flow or
        assign numeric meaning to legacy observations without a selected site.
        """
        consumer = mapping(candidate.get('native_consumer', {}), 'native consumer')
        if not consumer.get('entry') or 'offset' not in consumer:
            require(not any(k.startswith('native_') and k.endswith('_binding') for k in candidate) and
                    'native_literal_effect_arguments' not in candidate,
                    f'Missing native binding consumer: {row["id"]}')
            return
        self.evidence(consumer, row)
        _, witness = self.index.witness(consumer, row)
        methods = [m for m in witness['methods'] if m['name'] in consumer['methods'] and
                   (not consumer.get('descriptor') or consumer['descriptor'] in
                    (m.get('descriptor'), m.get('raw_descriptor'), m.get('obfuscated_descriptor')))]
        require(len(methods) == 1, f'Ambiguous numeric binding: {row["id"]}')
        body = object_list(methods[0]['instructions'], 'numeric instructions')
        at = next(n for n, i in enumerate(body) if i['offset'] == consumer['offset'])

        def literal(offset, expected):
            sites = [i for i in body if i['offset'] == offset]
            require(len(sites) == 1 and sites[0]['opcode'] in LITERAL_OPCODES and
                    type(sites[0].get('operand')) in (int, float) and
                    (type(sites[0]['operand']) is int or math.isfinite(sites[0]['operand'])) and
                    sites[0]['operand'] == expected,
                    f'Numeric literal mismatch: {row["id"]}@{offset}')

        def parameters(binding, roles):
            require(set(roles) == set(candidate['parameters']), f'Invalid numeric roles: {row["id"]}')
            for parameter, role in roles.items():
                require(parameter in values and role in binding and values[parameter] == binding[role],
                        f'Numeric binding mismatch: {row["id"]}/{parameter}')

        # A scalar consumer can itself be the literal, but an invocation is not
        # proof of any numeric argument supplied to it.
        if 'native_value' in candidate and body[at]['opcode'] in LITERAL_OPCODES:
            literal(consumer['offset'], candidate['native_value'])
        for key, binding in candidate.items():
            if not key.startswith('native_') or not key.endswith('_binding'):
                continue
            mapping(binding, key)
            if key == 'native_item_attribute_binding':
                roles = mapping(candidate['native_item_attribute_parameter_roles'], 'item attribute roles')
                if binding['kind'] == 'ITEM_ATTRIBUTE_MODIFIER':
                    literal(binding['value_offset'], binding['native_value'])
                    allowed = {'native_value'}
                else:
                    owners = {'DIGGER_ATTRIBUTE_ARGUMENTS': 'DiggerItem',
                              'SWORD_ATTRIBUTE_ARGUMENTS': 'SwordItem'}
                    require(binding['kind'] in owners, f'Invalid item attribute binding: {row["id"]}')
                    require(at >= 3 and body[at]['operand'] == 'net/minecraft/world/item/' +
                            owners[binding['kind']] + '.createAttributes(Lnet/minecraft/world/item/Tier;FF)'
                            'Lnet/minecraft/world/item/component/ItemAttributeModifiers;' and
                            body[at-3]['opcode'] == '0xb2' and
                            body[at-3]['operand'] == binding['tier_symbol'] and
                            [binding['damage_offset'], binding['speed_offset']] ==
                            [i['offset'] for i in body[at-2:at]],
                            f'Invalid item attribute literal sites: {row["id"]}')
                    literal(binding['damage_offset'], binding['attack_bonus'])
                    literal(binding['speed_offset'], binding['attack_speed'])
                    allowed = {'attack_bonus', 'attack_speed'}
                require(len(roles) == len(allowed) and set(roles.values()) == allowed,
                        f'Invalid item attribute roles: {row["id"]}')
                parameters(binding, roles)
            elif key in SCALAR_BINDINGS or 'native_value' in binding:
                literal(binding['value_offset'], binding['native_value'])
                parameters(binding, {p: 'native_value' for p in candidate['parameters']})
            elif key == 'native_literal_vector_components_binding':
                require(at >= 3 and binding['operation'] in ('add', 'multiply') and
                        body[at]['operand'] == 'net/minecraft/world/phys/Vec3.' + binding['operation'] +
                        '(DDD)Lnet/minecraft/world/phys/Vec3;' and
                        binding['literal_offsets'] == [i['offset'] for i in body[at-3:at]],
                        f'Invalid vector literal sites: {row["id"]}')
                for axis, offset in zip(('x', 'y', 'z'), binding['literal_offsets']):
                    literal(offset, binding[axis])
                roles = mapping(candidate['native_vector_parameter_roles'], 'vector roles')
                require(set(roles.values()) <= {'x', 'y', 'z'}, f'Invalid vector roles: {row["id"]}')
                parameters(binding, roles)
            elif key == 'native_literal_rng_bounds_binding':
                for role in ('minimum', 'maximum'):
                    literal(binding[role + '_offset'], binding[role])
                parameters(binding, mapping(candidate['native_rng_parameter_roles'], 'RNG roles'))
            elif key == 'native_tag_double_binding':
                literal(binding['value_offset'], binding['value'])
                parameters(binding, {p: 'value' for p in candidate['parameters']})
            elif key == 'native_rounded_tag_quotient_binding':
                require(at >= 2 and body[at]['operand'] == 'java/lang/Math.round(D)J' and
                        body[at-1]['opcode'] == '0x6f', f'Invalid quotient site: {row["id"]}')
                literal(body[at-2]['offset'], binding['divisor'])
                parameters(binding, {p: 'divisor' for p in candidate['parameters']})
            elif key == 'native_synched_int_distribution_binding':
                rng = [n for n, i in enumerate(body) if i['offset'] == binding['rng_offset']]
                require(len(rng) == 1 and rng[0] >= 2, f'Invalid RNG site: {row["id"]}')
                for n, role in enumerate(('native_minimum', 'native_maximum')):
                    literal(body[rng[0]-2+n]['offset'], binding[role])
                parameters(binding, {'minimum': 'native_minimum', 'maximum': 'native_maximum'})
            elif key == 'native_food_component_binding':
                starts = [n for n, i in enumerate(body) if i['offset'] == binding['builder_allocation_offset']]
                require(len(starts) == 1 and starts[0] + 5 < at, f'Invalid food literal sites: {row["id"]}')
                for n, role in ((3, 'nutrition'), (5, 'saturation_modifier')):
                    literal(body[starts[0]+n]['offset'], binding[role])
                parameters(binding, mapping(candidate['native_food_parameter_roles'], 'food roles'))
            elif key == 'native_arrow_factory_binding':
                arguments = mapping(binding['literal_arguments'], 'arrow arguments')
                for argument in arguments.values():
                    literal(argument['offset'], argument['value'])
                # Configured base damage has a recorded expression instead of a
                # literal. Do not invent a value for that alternative binding.
                if binding['parameter_role'] in arguments:
                    parameters({role: a['value'] for role, a in arguments.items()},
                               {p: binding['parameter_role'] for p in candidate['parameters']})
        effect = candidate.get('native_literal_effect_arguments')
        if effect:
            signature = re.fullmatch(r'net/minecraft/world/effect/MobEffectInstance\.<init>\(Lnet/minecraft/core/Holder;(II(?:ZZ|ZZZ)?)\)V',
                                     str(body[at]['operand']))
            count = 2 + len(effect['explicit_flags'])
            require(signature and len(signature.group(1)) == count and at >= count,
                    f'Invalid effect literal sites: {row["id"]}')
            args = body[at-count:at]
            for instruction, value in zip(args, [effect['duration'], effect['amplifier']] + effect['explicit_flags']):
                literal(instruction['offset'], value)
            for parameter in candidate['parameters']:
                if parameter in ('duration', 'amplifier'):
                    require(values.get(parameter) == effect[parameter],
                            f'Numeric effect binding mismatch: {row["id"]}/{parameter}')

    def record(self, key, row):
        require(not row.get('pending') and not row.get('unresolved_ambiguities'),
                f'Mechanic has unresolved semantics: {row["id"]}', 4)
        proofs = row['implementation'] + row.get('shared_contracts', []) + row.get('native_resource_evidence', [])
        candidates = row.get('scalable_parameter_candidates', [])
        require(isinstance(candidates, list) and all(isinstance(c, (str, dict)) for c in candidates),
                f'Invalid numeric candidates: {row["id"]}')
        for candidate in candidates:
            if isinstance(candidate, dict):
                values = {}
                for parameter in candidate['parameters']:
                    components = [c for c in row['components'] if c['primitive'] == candidate['primitive'] and
                                  parameter in (set(c.get('numerical_parameters', {})) |
                                                set(c.get('component_numerical_parameters', {})) |
                                                set(c.get('parameter_formulas', {})))]
                    require(len(components) == 1, f'Detached numeric candidate: {row["id"]}/{parameter}')
                    numbers = mapping(components[0].get('numerical_parameters', {}), 'component numbers')
                    if parameter in numbers:
                        values[parameter] = numbers[parameter]
                    if 'native_value' in candidate and parameter in numbers:
                        require(candidate['native_value'] == numbers[parameter],
                                f'Numeric value mismatch: {row["id"]}/{parameter}')
                self.numeric_binding(candidate, values, row)
                consumer = candidate.get('native_consumer')
                if consumer and consumer.get('evidence_file'):
                    proofs.append(consumer)
                proofs.extend(site for site in object_list(candidate.get('additional_consumer_sites', []), 'additional consumers')
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
    deps.add_argument('--mechanic', help='Select obligations explicitly recorded for this mechanic ID')
    deps.add_argument('--obligation', help='Select one required obligation ID (requires --mechanic)')
    deps.add_argument('--expect-dependency-version', help='Expected resolved dependency version (requires --mechanic)')
    deps.add_argument('--expect-dependency-sha256', help='Expected resolved dependency JAR SHA-256 (requires --mechanic)')
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
            if args.command == 'dependencies':
                if args.mechanic:
                    data = catalog.dependency_contracts(key, args.mechanic, args.obligation,
                                                       args.expect_dependency_version, args.expect_dependency_sha256)
                else:
                    require(not any([args.obligation, args.expect_dependency_version, args.expect_dependency_sha256]),
                            'Obligation selection and dependency source checks require --mechanic')
                    data = catalog.dependencies(key)
            else:
                data = dict(mod_key=key)
            data['source_check'] = check
        result, code = catalog.response(args.command, data), 0
        output = json.dumps(result, ensure_ascii=False, indent=2 if pretty else None,
                            separators=None if pretty else (',', ':'), allow_nan=False)
    except CatalogError as error:
        result, code = dict(schema=SCHEMA, status='ERROR', error=str(error)), error.code
    except (OSError, ValueError, KeyError, TypeError, AssertionError) as error:
        result, code = dict(schema=SCHEMA, status='ERROR', error=f'Invalid or unavailable catalog input: {error}'), 2
    if code:
        output = json.dumps(result, ensure_ascii=False, indent=2 if pretty else None,
                            separators=None if pretty else (',', ':'), allow_nan=False)
    print(output)
    return code


if __name__ == '__main__':
    sys.exit(main())
