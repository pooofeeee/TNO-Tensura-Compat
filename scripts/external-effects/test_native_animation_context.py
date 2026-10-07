"""Controller/string identity and exact reused clip consumers, not inferred attacks."""
import copy
import unittest
from catalog_common import OUT,read_json
from collect_combat_census import decode_sites
from reconcile_native_census import reconcile
from promote_combat_batch import validate_batch,refined_review
from test_shadow_clone_contracts import NativeContractHarness


class NativeAnimationContextTests(NativeContractHarness,unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m7e-native-animation-context.json')
        cls.native=read_json(OUT/'native-evidence/arphex-native-animation-control-context.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def test_existing_gameplay_candidates_and_classifications_are_unchanged(self):
        prior=self.prior();after=refined_review(prior,self.batch);s=validate_batch(self.batch,prior,self.census)
        self.assertEqual((s['semantic_records'],s['numeric_candidate_entries']),(462,3903))
        self.assertEqual([(r['id'],r['primary_classification'],r['scalable_parameter_candidates']) for r in prior['effects']],
                         [(r['id'],r['primary_classification'],r['scalable_parameter_candidates']) for r in after['effects']])
        self.assertEqual((len(self.native['witnesses']),sum(len(w['methods']) for w in self.native['witnesses'])),(9,27))
        self.assertEqual(sum(len(read_json(OUT/c['file'])['rows']) for c in self.batch['native_context_equivalences']),128)

    def test_controller_reset_writes_raw_clip_and_not_synced_or_physical_state(self):
        for w in self.native['witnesses']:
            b=next(m['instructions'] for m in w['methods'] if m['name']=='procedurePredicate')
            writes={i['operand'].split('.')[-1] for i in b if i['opcode']=='0xb5'}
            self.assertEqual(writes,{'animationprocedureLjava/lang/String;','prevAnimLjava/lang/String;'})
            self.assertTrue(any('AnimationController.forceAnimationReset(' in str(i['operand']) for i in b))
            self.assertTrue(any('RawAnimation.thenPlay(' in str(i['operand']) for i in b))
            self.assertTrue(any('AnimationController$State.STOPPED' in str(i['operand']) for i in b))
            self.assertFalse(any(t in str(i['operand']) for i in b for t in
                                 ('.hurt(','.addEffect(','.setTarget(','.setDeltaMovement(','.setAnimation(Ljava/lang/String;)V','SynchedEntityData.set(')))

    def test_all_external_raw_string_reads_remain_exact_and_are_not_missing_gates(self):
        index=read_json(OUT/self.batch['native_field_index_file']);actual=[]
        for m in index['methods']:
            for i in decode_sites(index,m,'field_sites'):
                if i['opcode']=='0xb4' and i['operand'].endswith('.animationprocedureLjava/lang/String;') and m['method'] not in ('procedurePredicate','movementPredicate','attackingPredicate'):
                    actual.append(dict(entry=m['entry'],method=m['method'],descriptor=m['descriptor'],code_sha256=m['code_sha256'],field=i['operand'],offset=i['offset']))
        self.assertEqual(sorted(actual,key=lambda r:(r['entry'],r['method'],r['offset'])),self.batch['native_animation_external_field_readers'])
        self.assertEqual(len(actual),8)
        old=[('arphex-arachnoid-source-projectile-sources.json','ArachnoidTrisectorOnEntityTickUpdateProcedure',7209,'animation.arachnoid_trisector.forcefield_loop'),
             ('arphex-centipede-native-families.json','CentipedeEvictorOnEntityTickUpdateProcedure',1346,'animation.centipedeevictor.grabmove'),
             ('arphex-shadow-payload-family.json','SpiderLarvaeOnEntityTickUpdateProcedure',1234,'animation.spiderlarvae.grab')]
        for file,name,offset,clip in old:
            w=next(w for w in read_json(OUT/'native-evidence'/file)['witnesses'] if w['entry'].endswith('/'+name+'.class'))
            b=max((m['instructions'] for m in w['methods'] if m['name']=='execute'),key=len)
            at=next(j for j,i in enumerate(b) if i['offset']==offset)
            self.assertEqual(b[at+1]['operand'],clip);self.assertIn('String.equals(',b[at+2]['operand'])
            self.assertTrue(any('.setAnimation(Ljava/lang/String;)V' in str(i['operand']) for i in b[at:at+18]))

    def test_synced_string_get_and_set_keep_one_own_data_accessor(self):
        for name in ('SpiderLarvaeEntity','SpiderLarvaeTinyEntity'):
            get=self.body(name,'getSyncedAnimation');put=self.body(name,'setAnimation')
            self.assertEqual(get[2]['operand'],put[2]['operand'])
            self.assertIn(name+'.ANIMATION',put[2]['operand'])
            self.assertEqual(put[3]['local_index'],1)
            self.assertIn('SynchedEntityData.set(',put[4]['operand'])
            self.assertIn('SynchedEntityData.get(',get[3]['operand'])
            self.assertFalse(any('.hurt(' in str(i['operand']) for i in get+put))

    def context_review(self):
        r=copy.deepcopy(read_json(OUT/'mod-reviews/arphex.json'))
        file='arphex-r2m7e-native-animation-context.json'
        if file not in r['reviewed_batches']:r['reviewed_batches'].append(file)
        return r

    def test_context_equality_closes_only_selected_methods_and_grants_no_mechanic(self):
        index,_=reconcile(self.context_review(),self.census)
        files={c['file'] for c in self.batch['native_context_equivalences']}
        rows=[r for r in index['methods'] if any(p.get('registry_file') in files for p in r['proofs'])]
        self.assertEqual(len(rows),128);self.assertTrue(all(r['method']=='procedurePredicate' for r in rows))
        for r in rows:
            self.assertTrue(all(p['kind']=='REVIEWED_EXCLUSION' and p.get('reason') for p in r['proofs'] if p.get('registry_file') in files))

    def test_partial_unreviewed_or_changed_identity_cannot_close_context(self):
        bfile='arphex-r2m7e-native-animation-context.json';efile='native-evidence/arphex-native-animation-control-context.json'
        for kind in ('unreviewed','partial','hash'):
            batch=copy.deepcopy(self.batch);native=copy.deepcopy(self.native)
            if kind=='unreviewed':batch['native_context_equivalences'][0]['reason']=''
            elif kind=='partial':
                for w in native['witnesses']:
                    for m in w['methods']:m['instruction_offset_ranges']=[[0,1]]
            else:native['witnesses'][0]['entry_sha256']='0'*64
            def read(path):
                relative=str(path.relative_to(OUT))
                return batch if relative==bfile else native if relative==efile else read_json(path)
            with self.assertRaises(AssertionError):reconcile(self.context_review(),self.census,read=read)


if __name__=='__main__':unittest.main()
