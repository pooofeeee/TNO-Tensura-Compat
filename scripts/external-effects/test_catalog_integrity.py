"""Mutation tests against independent canonical/native facts, not assembler output."""
import copy
import importlib
import json
import unittest

from catalog_common import OUT, read_json
from audit_catalog_integrity import audit_catalog, audit_review, EvidenceIndex
from refresh_catalog_views import project


class CatalogIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.review=read_json(OUT/'mod-reviews/eternalstarlight.json')

    def test_all_completed_reviews_including_cataclysm(self):
        result=audit_catalog()
        self.assertEqual(result['status'],'PASS')
        completed={t['mod_key'] for t in read_json(OUT/'mod-completion-ledger.json')['targets']
                   if t['state']=='COMPLETE'}
        self.assertEqual(result['completed_mods_audited'],len(completed))
        self.assertTrue(completed <= result['mods'].keys())
        self.assertTrue(all(m['status'].startswith('PASS') for m in result['mods'].values()))
        self.assertEqual(sum(s['declaration_resource_context_rows'] for s in result['source_census_checks'].values()),6)
        self.assertEqual(sum(s['exact_native_hit_rows'] for s in result['source_census_checks'].values()),611)
        self.assertEqual(read_json(OUT/'catalog-integrity-audit.json'),result,
                         'published integrity snapshot is stale')

    def test_reject_duplicate_semantics_under_another_id(self):
        duplicate=copy.deepcopy(self.review['effects'][0]);duplicate['id']='es:fake_duplicate'
        self.review['effects'].append(duplicate)
        for path in self.review['paths']:
            if path['id'] in duplicate['delivery_paths']:path['effect_ids'].append(duplicate['id'])
        with self.assertRaises(AssertionError):audit_review(self.review,EvidenceIndex())

    def test_reject_missing_native_method(self):
        self.review['effects'][0]['implementation'][0]['methods']=['inventedCallback']
        with self.assertRaises(AssertionError):audit_review(self.review,EvidenceIndex())

    def test_reject_unsupported_stage_policy(self):
        self.review['effects'][0]['stage_scaling_needed']=True
        with self.assertRaises(AssertionError):audit_review(self.review,EvidenceIndex())

    def test_reject_document_references_as_numeric_values(self):
        self.review['effects'][0]['components'][0]['numerical_parameters']['source_variants']=['f.json#id']
        with self.assertRaises(AssertionError):audit_review(self.review,EvidenceIndex())

    def test_reject_candidate_detached_from_real_component(self):
        row=next(r for r in self.review['effects'] if r['id']=='es:native_wither_tick')
        row['scalable_parameter_candidates'][0]['primitive']='UNRELATED_PRIMITIVE'
        with self.assertRaises(AssertionError):audit_review(self.review,EvidenceIndex())

    def test_reject_false_wither_classification(self):
        next(r for r in self.review['effects'] if r['id']=='es:native_wither_tick')['primary_classification']='BINARY_MECHANIC'
        with self.assertRaises(AssertionError):audit_review(self.review,EvidenceIndex())

    def test_reject_false_native_constant(self):
        row=next(r for r in self.review['effects'] if r['id']=='es:native_wither_tick')
        row['components'][0]['numerical_parameters']['requested_damage']=2
        row['scalable_parameter_candidates'][0]['native_value']=2
        with self.assertRaises(AssertionError):audit_review(self.review,EvidenceIndex())

    def test_reject_changed_native_code_hash(self):
        index=EvidenceIndex();file='vanilla-evidence/cult-completion.json'
        data=copy.deepcopy(index.read(file));w=next(w for w in data['classes'] if w['class_name'].endswith('WitherMobEffect'))
        m=next(m for m in w['methods'] if m['name']=='applyEffectTick');m['code_hex']='00'+m['code_hex'][2:]
        index.files[file]=data
        with self.assertRaises(AssertionError):audit_review(self.review,index)

    def test_reject_broken_reciprocal_delivery(self):
        self.review['paths'][0]['effect_ids']=[]
        with self.assertRaises(AssertionError):audit_review(self.review,EvidenceIndex())

    def test_cataclysm_shared_payloads_and_context_exclusions(self):
        review=read_json(OUT/'mod-reviews/cataclysm.json');ids={r['id'] for r in review['effects']}
        self.assertIn('cataclysm:monstrosity_earthquake_payload',ids)
        self.assertNotIn('cataclysm:monstrosity_berserk_quake',ids)
        self.assertIn('cataclysm:laser_contact_payload',ids)
        self.assertNotIn('cataclysm:laser_gatling_laser_burn',ids)
        self.assertNotIn('cataclysm:combat_blocks_registry',ids)
        row=next(r for r in review['effects'] if r['id']=='cataclysm:laser_contact_payload')
        self.assertTrue(row['source_variants'])
        self.assertEqual(len([c for c in row['scalable_parameter_candidates'] if c['primitive']=='BURN']),1)

    def test_cult_aliases_not_independent_candidates(self):
        review=read_json(OUT/'mod-reviews/cultofazazel.json')
        rows={r['id']:r for r in review['effects']}
        for rid,alias in [('cultofazazel:azazel_wheel','vertical'),('cultofazazel:honey_properties','factor'),
                          ('cultofazazel:golem_healing_pull','heal'),('cultofazazel:golem_healing_pull','pull')]:
            self.assertNotIn(alias,rows[rid]['scalable_parameter_candidates'])
            self.assertTrue(any(a['parameter']==alias and a['independent_runtime_parameter'] is False
                                for a in rows[rid]['non_independent_parameters']))
        self.assertNotIn('vertical',rows['cultofazazel:azazel_wheel']['numerical_parameters'])

    def test_all_catalog_views_match_canonical_reviews(self):
        reviews=[read_json(p) for p in sorted((OUT/'mod-reviews').glob('*.json'))]
        data=project(reviews)
        for file,key in [('effect-catalog.json','effects'),('effect-sources.json','sources'),
                         ('delivery-path-matrix.json','paths'),('vanilla-comparison.json','comparisons'),
                         ('behavior-primitives.json','primitives')]:
            self.assertEqual(read_json(OUT/file)[key],data[key])
        self.assertEqual(data,project(list(reversed(reviews))))

    def test_retired_policy_builders_cannot_republish(self):
        for name in ('iceandfire','eternalstarlight','bossesrise','bomd'):
            with self.subTest(name=name), self.assertRaises(RuntimeError):
                importlib.import_module('complete_'+name).build()


if __name__=='__main__':unittest.main()
