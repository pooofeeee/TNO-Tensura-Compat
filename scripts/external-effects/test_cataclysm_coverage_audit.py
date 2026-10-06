"""Focused tests for the pinned census reconciliation checkpoint only."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import unittest

from catalog_common import ROOT, OUT, read_json
from collect_cataclysm_coverage_audit import generate, NEXT_TASK


class CoverageAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = OUT / 'cataclysm-r2k33a-coverage-audit.json'
        cls.audit = read_json(cls.path)

    def test_byte_identical_regeneration(self):
        generated = generate(self.audit['source_commit'])
        self.assertEqual(self.path.read_text(),json.dumps(generated,ensure_ascii=False,indent=2)+'\n')

    def test_unique_complete_structural_accounting(self):
        summary = self.audit['summary']
        self.assertEqual(summary['total_unique_census_methods'],572)
        self.assertEqual(sum(summary['counts_by_disposition'].values()),572)
        rows = self.audit['residual_methods']
        self.assertEqual(len({(r['entry'],r['method'],r['descriptor']) for r in rows}),len(rows))
        counts = Counter(r['disposition'] for r in rows)
        expected = dict(summary['counts_by_disposition'])
        expected.pop('CITED_WITH_NATIVE_WITNESS')
        self.assertEqual(dict(counts),expected)
        for row in rows:
            self.assertEqual(len(row['code_sha256']),64)
            if row['disposition']=='LOCKED_CHECKPOINT_BINDING':
                fact = row['evidence_pointer'].removeprefix('/facts/')
                self.assertIn(fact,read_json(OUT / row['checkpoint_file'])['facts'])

    def test_pending_boundaries_not_silently_complete(self):
        summary = self.audit['summary']
        self.assertEqual(summary['counts_by_disposition']['PENDING_TARGETED_RECONCILIATION'],55)
        self.assertEqual(summary['pending_methods_by_domain']['R2k33b_BLOCKS_TRAPS_EMP'],8)
        self.assertIsNone(summary['material_unresolved_ambiguity_count'])
        pending = [r for r in self.audit['residual_methods']
                   if r['disposition']=='PENDING_TARGETED_RECONCILIATION']
        self.assertTrue(all(r['hits_to_reconcile'] and r['queue_domain'] for r in pending))
        self.assertEqual(self.audit['status'],'PARTIAL')
        self.assertEqual(self.audit['exact_next_task'],NEXT_TASK)

    def test_locked_native_facts_and_explicit_semantic_repairs(self):
        for item in self.audit['input_files']:
            if item['file']=='mod-reviews/cataclysm.json':
                if read_json(OUT/item['file']).get('integrity_checkpoint'):
                    from validate_current_integrity import validate_cataclysm_repairs
                    validate_cataclysm_repairs()
                    continue
                # Only checkpoint/queue metadata changes in this audit.
                path=(OUT/item['file']).relative_to(ROOT).as_posix()
                before=json.loads(subprocess.check_output(['git','show',self.audit['source_commit']+':'+path],cwd=ROOT))
                current=read_json(OUT/item['file'])
                for collection in ('effects','paths'):
                    indexed={r['id']:r for r in current[collection]}
                    self.assertTrue(all(indexed[r['id']]==r for r in before[collection]))
                self.assertEqual(current['protected_checkpoints'][:len(before['protected_checkpoints'])],
                                 before['protected_checkpoints'])
                if current['checkpoint']==self.audit['checkpoint']:
                    metadata={'checkpoint','notes_file','scope','exact_next_task','protected_checkpoints'}
                    self.assertEqual({k:v for k,v in current.items() if k not in metadata},
                                     {k:v for k,v in before.items() if k not in metadata})
            else:
                # This audit is a frozen source-commit snapshot. Later integrity
                # repairs may update checkpoint classifications/reference hashes;
                # they must not rewrite the underlying native behavior facts.
                path=(OUT/item['file']).relative_to(ROOT).as_posix()
                original=subprocess.check_output(['git','show',self.audit['source_commit']+':'+path],cwd=ROOT)
                self.assertEqual(hashlib.sha256(original).hexdigest(),item['sha256'])
                before=json.loads(original)
                current=read_json(OUT/item['file'])
                if 'facts' in before:
                    self.assertEqual(current['facts'],before['facts'])
                else:
                    self.assertEqual((OUT/item['file']).read_bytes(),original)
        self.assertEqual(subprocess.check_output(['git','rev-parse','codex/production-continuation'],cwd=ROOT,text=True).strip(),
                         'eb37f0bfc0e7aa863632f163881566c0ae2a8701')

    def test_ledger_remains_partial_and_only_audit_files_change(self):
        ledger=read_json(OUT/'mod-completion-ledger.json')
        if ledger['checkpoint']!=self.audit['checkpoint']:
            # A later family may legitimately advance this immutable snapshot.
            return
        cat=next(t for t in ledger['targets'] if t['mod_key']=='cataclysm')
        self.assertEqual(cat['state'],'PARTIAL')
        self.assertEqual(cat['exact_next_task'],NEXT_TASK)
        self.assertEqual(cat['semantic_effect_count'],991)
        self.assertEqual(ledger['checkpoint'],self.audit['checkpoint'])
        before=json.loads(subprocess.check_output(['git','show',self.audit['source_commit']+':'+
            (OUT/'mod-completion-ledger.json').relative_to(ROOT).as_posix()],cwd=ROOT))
        self.assertEqual([t for t in ledger['targets'] if t['mod_key']!='cataclysm'],
                         [t for t in before['targets'] if t['mod_key']!='cataclysm'])
        allowed={(OUT/f).relative_to(ROOT).as_posix() for f in
            ['cataclysm-r2k33a-coverage-audit.json','mod-reviews/cataclysm.json','mod-completion-ledger.json']}
        allowed.update(['scripts/external-effects/collect_cataclysm_coverage_audit.py',
                        'scripts/external-effects/test_cataclysm_coverage_audit.py'])
        changed=set(subprocess.check_output(['git','diff','--name-only',self.audit['source_commit']],cwd=ROOT,text=True).splitlines())
        self.assertLessEqual(changed,allowed)


if __name__ == '__main__':
    unittest.main()
