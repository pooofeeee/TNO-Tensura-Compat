"""Native reachability, inherited goal dispatch and physical actor contexts."""
import copy
import unittest
from collections import defaultdict
from catalog_common import OUT,read_json
from promote_combat_batch import validate_batch,refined_review
from reconcile_native_census import reconcile


class NativeActorContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b=read_json(OUT/'arphex-r2m7o-native-actor-context.json')
        cls.c=read_json(OUT/'arphex-combat-census.json')
        cls.e=read_json(OUT/'native-evidence/arphex-native-actor-context.json')
        cls.w={w['entry']:w for w in cls.e['witnesses']}

    def method(self,entry,name):
        return next(m for m in self.w[entry]['methods'] if m['name']==name)

    def previous_method(self,proof,name):
        doc=read_json(OUT/proof['evidence_file'])
        w=next(w for w in doc['witnesses'] if w['id']==proof['witness_id'])
        self.assertEqual(w['entry'],proof['entry'])
        return next(m for m in w['methods'] if m['name']==name)

    def test_scope_refines_eight_families_without_new_payload_or_scalar(self):
        self.assertEqual(len(self.w),39)
        self.assertEqual(sum(len(w['methods']) for w in self.w.values()),184)
        self.assertEqual(self.b['effects'],[]);self.assertEqual(self.b['paths'],[])
        self.assertEqual(len(self.b['record_refinements']),8)
        self.assertFalse(any(r.get('candidate_additions') for r in self.b['record_refinements']))
        r=read_json(OUT/'mod-reviews/arphex.json');after=refined_review(r,self.b)
        self.assertEqual(validate_batch(self.b,r,self.c)['semantic_records'],len(r['effects']))
        count=lambda d:sum(len(c['parameters']) for e in d['effects'] for c in e['scalable_parameter_candidates'])
        self.assertEqual(count(r),count(after))
        after['reviewed_batches']=list(set(after['reviewed_batches']+['arphex-r2m7o-native-actor-context.json']))
        idx,_=reconcile(after,self.c)
        indexed={(m['entry'],m['method'],m['descriptor']):m for m in idx['methods']}
        for entry,w in self.w.items():
            for m in w['methods']:
                self.assertEqual(indexed[(entry,m['name'],m['descriptor'])]['code_sha256'],m['code_sha256'])

    def test_shoot_reachability_comes_from_original_calls_and_handles(self):
        families=self.b['native_unreferenced_shoot_families'];self.assertEqual(len(families),20)
        targets={f['entry'][:-6]+'.shoot'+m['descriptor'] for f in families for m in f['methods']}
        self.assertEqual(len(targets),80)
        incoming=defaultdict(list)
        for m in self.c['methods']:
            for offset,opcode,symbol in m['calls']:
                target=self.c['symbols'][symbol]
                if target in targets:
                    incoming[target].append(dict(entry=m['entry'],method=m['method'],descriptor=m['descriptor'],
                        code_sha256=m['code_sha256'],offset=offset,opcode=hex(opcode)))
        for f in families:
            self.assertEqual(len(f['methods']),4)
            expected=[dict(target=s,caller=p) for s in sorted(f['entry'][:-6]+'.shoot'+m['descriptor']
                        for m in f['methods']) for p in incoming[s]]
            self.assertEqual(f['internal_callers'],expected)
            self.assertTrue(all(p['caller']['entry']==f['entry'] and p['caller']['method']=='shoot' for p in expected))
            self.assertEqual(f['external_native_callers'],[])
            self.assertFalse(any(a in targets for b in self.c['registration_bootstraps'] for a in b['arguments']))
            for m in self.w[f['entry']]['methods']:
                if m['name']=='shoot':self.assertFalse(m['annotations'])
        self.assertEqual(sum(len(f['internal_callers']) for f in families),40)

    def test_ranged_loops_are_live_through_actual_registered_subclasses(self):
        classes={c['entry']:c for c in self.c['classes']}
        rows=self.b['native_ranged_scheduler_contracts'];self.assertEqual(len(rows),3)
        expected={'SpiderBroodEntity':(100,10.),'SpiderMothLarvaeEntity':(120,40.),
                  'SpiderMothSummonLarvaeEntity':(60,40.)}
        for r in rows:
            name=r['actor'].rsplit('/',1)[-1][:-6]
            self.assertEqual(classes[r['registered_subclass']]['superclass'],r['goal'][:-6])
            body=self.previous_method(r['registration'],'registerGoals')['instructions']
            at=next(n for n,i in enumerate(body) if r['registered_subclass'][:-6]+'.<init>' in str(i['operand']))
            self.assertEqual([i['operand'] for i in body[at-3:at]],[1.25,*expected[name]])
            override=self.previous_method(r['subclass_continuation'],'canContinueToUse')['instructions']
            self.assertEqual([i['opcode'] for i in override],['0x2a','0xb6','0xac'])
            self.assertEqual(override[1]['operand'],r['registered_subclass'][:-6]+'.canUse()Z')
            self.assertTrue(r['base_continuation_shadowed'])
            self.assertEqual(r['native_interval_min'],r['native_interval_max'])

    def test_firing_arm_preserves_los_clock_and_shoot_order_without_radius_rejection(self):
        for r in self.b['native_ranged_scheduler_contracts']:
            body=self.method(r['goal'],'tick')['instructions']
            at={i['offset']:i for i in body}
            self.assertEqual([at[n]['opcode'] for n in (136,139,140,141,142,145)],
                             ['0xb4','0x4','0x64','0x5a','0xb5','0x9a'])
            self.assertTrue(at[136]['operand'].endswith('.attackTimeI'))
            self.assertEqual(at[149]['opcode'],'0x9a');self.assertEqual(at[172]['opcode'],'0xb1')
            fire=next(i for i in body if 'RangedAttackMob.performRangedAttack(' in str(i['operand']))
            self.assertEqual(fire['offset'],225)
            arm=[i for i in body if 134<=i['offset']<=225]
            self.assertEqual([(i['offset'],i['opcode']) for i in arm if 0x99<=int(i['opcode'],16)<=0xa6],[(145,'0x9a'),(149,'0x9a')])
            self.assertEqual(at[207]['operand'],0.10000000149011612);self.assertEqual(at[209]['operand'],1.)
            self.assertIn('Mth.clamp(FFF)F',at[210]['operand'])
            for offset,value in ((165,0),(186,1),(312,0)):self.assertEqual(at[offset]['operand'],value)
            self.assertEqual([i['offset'] for i in body if 'SynchedEntityData.set(' in str(i['operand'])],[169,190,316])
            self.assertIn('Mth.floor(F)I',at[250]['operand']);self.assertIn('Mth.lerp(DDD)D',at[287]['operand'])
            self.assertFalse(any('.hurt(' in str(i['operand']) or '.addEffect(' in str(i['operand']) for i in body))

    def test_strict_melee_and_native_environment_admission_stay_distinct(self):
        for actor in ('AiToRideEntity','AnyDimensionSpawnerEntity'):
            body=self.method('net/arphex/entity/'+actor+'$1.class','canPerformAttack')['instructions']
            at={i['offset']:i for i in body}
            self.assertEqual(at[29]['opcode'],'0x6a');self.assertEqual(at[34]['opcode'],'0x62')
            self.assertEqual(at[36]['opcode'],'0x98');self.assertEqual(at[37]['opcode'],'0x9c')
            self.assertTrue(at[48]['operand'].endswith('Sensing.hasLineOfSight(Lnet/minecraft/world/entity/Entity;)Z'))
        body=self.method('net/arphex/entity/SpiderSnatcherEntity.class','makeStuckInBlock')['instructions']
        self.assertIn('Blocks.COBWEB',body[1]['operand']);self.assertEqual(body[4]['opcode'],'0xb1')
        self.assertIn('Monster.makeStuckInBlock(',body[-2]['operand'])
        body=self.method('net/arphex/entity/TormentorHitboxEntity.class','canDrownInFluidType')['instructions']
        self.assertEqual([i['opcode'] for i in body[-2:]],['0x3','0xac'])
        self.assertFalse(any(i.get('local_index')==1 for i in body))

    def test_passenger_offset_is_physical_parent_geometry_with_original_arguments(self):
        for actor in ('DraconicCloneEntity','DraconicFlyStalkEntity','TormentorCaterpillarEntity'):
            body=self.method('net/arphex/entity/'+actor+'.class','getPassengerAttachmentPoint')['instructions']
            self.assertEqual([i['local_index'] for i in body[:4]],[0,1,2,3])
            self.assertIn('Monster.getPassengerAttachmentPoint(',body[4]['operand'])
            self.assertEqual([i['operand'] for i in body[5:8]],[0.,1.,0.])
            self.assertEqual(body[8]['operand'],'net/minecraft/world/phys/Vec3.add(DDD)Lnet/minecraft/world/phys/Vec3;')
            self.assertEqual(body[-1]['opcode'],'0xb0')

    def test_default_item_and_pickup_values_do_not_become_duplicate_payloads(self):
        getter_count=0;pickup_count=0
        for w in self.w.values():
            for m in w['methods']:
                body=m['instructions']
                if m['name']=='getItem':
                    getter_count+=1;self.assertEqual([i['opcode'] for i in body],['0xb2','0xb0'])
                    self.assertEqual(body[0]['operand'],w['entry'][:-6]+'.PROJECTILE_ITEMLnet/minecraft/world/item/ItemStack;')
                if m['name']=='getDefaultPickupItem':
                    pickup_count+=1
                    self.assertEqual(body[0]['operand'],'net/minecraft/world/item/ItemStack')
                    self.assertTrue(any('ItemStack.<init>(' in str(i['operand']) for i in body))
                    self.assertFalse(any('.hurt(' in str(i['operand']) or '.addEffect(' in str(i['operand']) for i in body))
        self.assertEqual((getter_count,pickup_count),(20,19))

    def test_changed_native_actor_hash_cannot_close_coverage(self):
        r=refined_review(read_json(OUT/'mod-reviews/arphex.json'),self.b)
        r['reviewed_batches']=list(set(r['reviewed_batches']+['arphex-r2m7o-native-actor-context.json']))
        e=copy.deepcopy(self.e);e['witnesses'][0]['methods'][0]['code_sha256']='0'*64
        def read(path):
            return e if path.name=='arphex-native-actor-context.json' else read_json(path)
        with self.assertRaisesRegex(AssertionError,'hash mismatch'):reconcile(r,self.c,read=read)


if __name__=='__main__':unittest.main()
