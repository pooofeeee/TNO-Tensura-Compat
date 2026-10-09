"""Pinned NEB contract integrity and consequential native boundary regressions.

These checks use retained native evidence independently of the authored prose.
They do not assert inherited dispatch or Minecraft runtime behavior.
"""
from copy import deepcopy
import unittest

from assemble_authored_contracts import render
from audit_catalog_integrity import EvidenceIndex, audit_review
from audit_numeric_labels import audit
from catalog_common import OUT, read_json
from promote_combat_batch import empty_review, validate_batch
from reconcile_native_census import reconcile


NATIVE_PIN = '99ce6e9fd6737278182e055a3fb98b5013a5c53cc7a62700078daa21e158778c'
BASE_PIN = 'c12ec9aaa1488c662ede52b4bd0150ec114e7bdac32af20c0e723612dd79d8b9'
PACKET = 'native-evidence/tensura_neb-foundation.json'
BASE_PACKET = 'native-evidence/tensura_neb-tensura-boundaries.json'


class NebContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = read_json(OUT/'tensura_neb-r2p2-local-native-contracts.json')
        cls.review = read_json(OUT/'mod-reviews/tensura_neb.json')
        cls.census = read_json(OUT/'tensura_neb-combat-census.json')
        cls.packet = read_json(OUT/PACKET)
        cls.base = read_json(OUT/BASE_PACKET)

    def witness(self, suffix, packet=None):
        return next(w for w in (packet or self.packet)['witnesses']
                    if w['entry'].endswith(suffix))

    def method(self, suffix, name, packet=None):
        return next(m for m in self.witness(suffix, packet)['methods']
                    if m['name'] == name)

    def test_authored_render_and_independent_audits(self):
        spec = read_json(OUT/'tensura_neb-r2p2-authored-contracts.json')
        self.assertEqual(render(spec), self.batch)
        validate_batch(self.batch, empty_review('tensura_neb'), self.census)
        self.assertEqual(audit_review(self.review, EvidenceIndex())['status'], 'PASS')
        self.assertEqual(audit(self.review)['unresolved_numeric_labels'], 0)

    def test_changed_numeric_value_is_rejected_against_native_site(self):
        batch = deepcopy(self.batch)
        candidate = batch['effects'][0]['scalable_parameter_candidates'][0]
        candidate['native_value'] += 1
        component = batch['effects'][0]['components'][0]
        component['numerical_parameters'][candidate['parameters'][0]] += 1
        with self.assertRaises(AssertionError):
            validate_batch(batch, empty_review('tensura_neb'), self.census)

    def test_changed_numeric_consumer_is_rejected(self):
        batch = deepcopy(self.batch)
        batch['effects'][0]['scalable_parameter_candidates'][0]['native_consumer']['operand'] = 999
        with self.assertRaises(AssertionError):
            validate_batch(batch, empty_review('tensura_neb'), self.census)

    def test_detached_numeric_primitive_is_rejected(self):
        review = deepcopy(self.review)
        review['effects'][0]['scalable_parameter_candidates'][0]['primitive'] = 'UNRELATED'
        with self.assertRaises(AssertionError):
            audit_review(review, EvidenceIndex())

    def test_changed_cited_method_hash_is_rejected(self):
        evidence = EvidenceIndex()
        packet = deepcopy(self.packet)
        self.method('/MixinSolarBeamProjectile.class', 'getDamageType', packet)['code_sha256'] = '0'*64
        evidence.files[PACKET] = packet
        with self.assertRaisesRegex(AssertionError, 'Method hash mismatch'):
            reconcile(self.review, self.census, read=evidence.read)

    def test_captured_but_uncited_method_returns_to_pending(self):
        review = deepcopy(self.review)
        review['effects'] = [r for r in review['effects']
                             if r['id'] != 'tensura_neb:carrion_solar_beam_source_mixin']
        _, pending = reconcile(review, self.census)
        self.assertIn(('getDamageType', '/MixinSolarBeamProjectile.class'),
                      [(m['method'], '/'+m['entry'].rsplit('/', 1)[1]) for m in pending])

    def test_full_local_capture_matches_finite_census(self):
        captured = {(w['entry'], m['name'], m['descriptor']): m['code_sha256']
                    for w in self.packet['witnesses'] for m in w.get('methods', [])}
        expected = {(m['entry'], m['method'], m['descriptor']): m['code_sha256']
                    for m in self.census['methods']}
        self.assertEqual(captured, expected)
        self.assertEqual(len(captured), 476)
        self.assertFalse(any('instruction_offset_ranges' in m
                             for w in self.packet['witnesses'] for m in w.get('methods', [])))

    def test_resource_and_shared_evidence_keep_distinct_artifact_pins(self):
        self.assertEqual({w['jar_sha256'] for w in self.packet['witnesses']}, {NATIVE_PIN})
        self.assertEqual({w['jar_sha256'] for w in self.base['witnesses']}, {BASE_PIN})
        resources = [w for w in self.packet['witnesses'] if not w['entry'].endswith('.class')]
        self.assertEqual(len(resources), 50)
        self.assertTrue(all('data' in w or 'text' in w for w in resources))

    def test_phase_transition_has_four_separate_clone_calls(self):
        body = self.method('/RimuruOgreFightEntity.class', 'enterLastPhase')['instructions']
        calls = [n for n, i in enumerate(body) if '.summonClones(II)V' in str(i['operand'])]
        self.assertEqual([(body[n-2]['operand'], body[n-1]['operand']) for n in calls],
                         [(1, 5), (1, 5), (3, 7), (3, 7)])

    def test_spawn_mixin_targets_kyoya_and_solar_source_checks_owner_type(self):
        spawn = self.witness('/MixinOtherworlder.class')
        mixin = next(a for a in spawn['annotations'] if a['descriptor'].endswith('/Mixin;'))
        self.assertEqual(mixin['values']['value'],
                         [{'class': 'Lio/github/manasmods/tensura/entity/human/KyoyaTachinbanaEntity;'}])
        body = self.method('/MixinSolarBeamProjectile.class', 'getDamageType')['instructions']
        symbols = [str(i['operand']) for i in body]
        self.assertTrue(any('.getOwner()' in s for s in symbols))
        self.assertTrue(any('NebEntityTypes.CARRION' in s for s in symbols))
        self.assertTrue(any('TensuraDamageTypes.AURA_BULLET' in s for s in symbols))
        self.assertTrue(any(i['opcode'] == '0x99' and i['branch_target'] == 40 for i in body))

    def test_storage_reset_does_not_remove_active_effects(self):
        body = self.method('/TensuraStorages.class', 'resetEffect', self.base)['instructions']
        setters = [str(i['operand']).split('.')[-1] for i in body if i['opcode'] == '0xb9']
        self.assertEqual(setters, ['setSeveranceAmount(F)V', 'setSeveranceRemoveTime(I)V',
                                  'setOnBlackFlame(Z)V', 'setIgnorePainNull(Z)V', 'markDirty()V'])
        self.assertFalse(any('removeEffect' in str(i['operand']) for i in body))

    def test_selected_base_facts_resolve_to_original_shared_witnesses(self):
        facts = read_json(OUT/'tensura_neb-tensura-boundary-facts.json')
        self.assertEqual(facts['dependency_jar_sha256'], BASE_PIN)
        self.assertEqual(len(facts['facts']), 10)
        evidence = EvidenceIndex()
        for key, fact in facts['facts'].items():
            for proof in fact['implementation']:
                _, witness = evidence.witness(proof, dict(id=key))
                self.assertEqual(witness['jar_sha256'], BASE_PIN)

    def test_zero_local_pending_does_not_close_external_obligations(self):
        index, pending = reconcile(self.review, self.census)
        self.assertEqual(pending, [])
        self.assertEqual(index['summary']['exact_contract_methods'], 365)
        self.assertEqual(index['summary']['explicit_exclusion_methods'], 111)
        queue = read_json(OUT/'tensura_neb-unresolved-queue.json')
        self.assertFalse(queue['mod_level_completion'])
        self.assertEqual(self.review['status'], 'PARTIAL')
        self.assertFalse(self.review['external_dependency_closure_complete'])
        obligations = read_json(OUT/'tensura_neb-dependency-obligations.json')
        self.assertEqual(obligations['status'], 'BLOCKED_EXTERNAL')
        self.assertEqual(len(obligations['obligations']), 4)
        self.assertIsNone(obligations['artifact']['sha256'])


if __name__ == '__main__':
    unittest.main()
