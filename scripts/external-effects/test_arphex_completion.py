"""Independent full-native completion guards, including negative coverage cases."""
import copy
import unittest

from catalog_common import OUT,read_json,sha256
from complete_arphex import canonical_source_validation,resource_obligations,NEXT
from reconcile_native_census import reconcile


class ArphexCompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.review=read_json(OUT/'mod-reviews/arphex.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')
        cls.coverage=read_json(OUT/'arphex-coverage-audit.json')

    def test_every_original_native_method_has_independent_disposition(self):
        index,pending=reconcile(self.review,self.census)
        self.assertEqual(len(self.census['methods']),19159)
        self.assertEqual(index['summary'],self.coverage['native_method_coverage'])
        self.assertEqual(index['summary']['pending_methods'],0)
        native={(m['entry'],m['method'],m['descriptor']):m['code_sha256'] for m in self.census['methods']}
        covered={(m['entry'],m['method'],m['descriptor']):m['code_sha256'] for m in index['methods']}
        self.assertEqual(covered,native)
        self.assertEqual(self.coverage['original_census_sha256'],sha256(OUT/'arphex-combat-census.json'))
        self.assertEqual(self.coverage['canonical_review_sha256'],sha256(OUT/'mod-reviews/arphex.json'))

    def test_current_canonical_parameters_replay_against_exact_consumers(self):
        result=canonical_source_validation(self.review,self.census)
        self.assertEqual(result,self.coverage['canonical_source_validation'])
        self.assertEqual((result['semantic_records'],result['numeric_candidate_entries']),(466,3933))

    def test_wrong_canonical_literal_is_rejected_even_with_complete_label(self):
        review=copy.deepcopy(self.review)
        row=next(r for r in review['effects'] if r['id']=='arphex:registered_necrosis_potion_native_dose')
        row['components'][0]['numerical_parameters']['duration']=3601
        with self.assertRaises(AssertionError):canonical_source_validation(review,self.census)

    def test_complete_label_cannot_hide_missing_context_proofs(self):
        review=copy.deepcopy(self.review)
        review['reviewed_batches'].remove('arphex-r2m7r-native-world-command-context.json')
        index,pending=reconcile(review,self.census)
        self.assertEqual(review['status'],'COMPLETE')
        self.assertGreater(index['summary']['pending_methods'],0)

    def test_native_resource_obligations_are_closed_and_repairs_only_change_scope(self):
        obligations=resource_obligations(self.review)
        self.assertEqual(obligations,self.coverage['resource_obligations'])
        self.assertEqual(len(obligations['queued_native_assets']),7)
        self.assertEqual(obligations['remaining_native_assets'],[])
        closure=read_json(OUT/'arphex-r2m7s-integrity-closure.json')
        self.assertEqual(len(closure['metadata_repairs']),6)
        by={r['id']:r for r in self.review['effects']}
        for change in closure['metadata_repairs']:
            self.assertEqual(change['field'],'scope')
            self.assertIn('stay explicitly queued',change['before'])
            self.assertNotIn('stay explicitly queued',change['after'])
            self.assertEqual(by[change['mechanic_id']]['scope'],change['after'])
        self.assertTrue(closure['semantic_behavior_source_and_parameters_unchanged'])

    def test_classification_counts_and_campaign_queue_come_from_current_rows(self):
        from collections import Counter
        summary=read_json(OUT/'arphex-classification-summary.json')
        self.assertEqual(Counter(r['primary_classification'] for r in self.review['effects']),summary['classification_counts'])
        self.assertEqual(summary['classification_groups'],dict(VANILLA=13,VANILLA_LIKE_OR_MIXED=94,CUSTOM=307,BINARY_OR_SPECIAL=52))
        self.assertEqual(sum(summary['classification_groups'].values()),len(self.review['effects']))
        ledger=read_json(OUT/'mod-completion-ledger.json');target=next(t for t in ledger['targets'] if t['mod_key']=='arphex')
        self.assertEqual(target['state'],self.review['status']);self.assertEqual(target['state'],'COMPLETE')
        self.assertEqual(target['pending_native_method_count'],0)
        self.assertEqual(target['semantic_effect_count'],466);self.assertEqual(target['numeric_candidate_count'],3933)
        campaign=read_json(OUT/'large-mod-campaign.json')
        # The global queue advances; this completed target retains its receipt.
        self.assertEqual(target['exact_next_task'],NEXT)
        for pin in campaign['locked_completed_reviews']:self.assertEqual(sha256(OUT/pin['file']),pin['sha256'])


if __name__=='__main__':unittest.main()
