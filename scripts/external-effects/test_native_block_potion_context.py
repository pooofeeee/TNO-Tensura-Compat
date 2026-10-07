"""Independent native property bindings, tick delegation and environment context."""
import copy
import unittest
from catalog_common import OUT,read_json
from promote_combat_batch import validate_batch,literal_block_factor_binding,refined_review
from reconcile_native_census import reconcile


class NativeBlockPotionContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b=read_json(OUT/'arphex-r2m7n-native-block-potion-context.json')
        cls.c=read_json(OUT/'arphex-combat-census.json')
        cls.e=read_json(OUT/'native-evidence/arphex-native-block-potion-context.json')
        cls.w={w['entry']:w for w in cls.e['witnesses']}
        cls.change=cls.b['record_refinements'][0]

    def method(self,entry,name):
        return next(m for m in self.w[entry]['methods'] if m['name']==name)

    def review(self):
        return read_json(OUT/'mod-reviews/arphex.json')

    def test_exact_pending_scope_and_existing_profile_are_preserved(self):
        self.assertEqual(len(self.w),81)
        self.assertEqual(sum(len(w['methods']) for w in self.w.values()),175)
        self.assertEqual(self.b['effects'],[]);self.assertEqual(self.b['paths'],[])
        self.assertEqual(self.change['id'],'arphex:native_crystal_flesh_web_block_motion_profiles')
        r=self.review();summary=validate_batch(self.b,r,self.c)
        self.assertEqual(summary['semantic_records'],len(r['effects']))
        changed=refined_review(r,self.b)
        self.assertEqual(len(changed['effects']),len(r['effects']))
        index,_=reconcile(dict(changed,reviewed_batches=list(set(r['reviewed_batches']+
                            ['arphex-r2m7n-native-block-potion-context.json']))),self.c)
        coverage={(m['entry'],m['method'],m['descriptor']):m for m in index['methods']}
        census={(m['entry'],m['method'],m['descriptor']):m for m in self.c['methods']}
        for entry,w in self.w.items():
            for m in w['methods']:
                key=entry,m['name'],m['descriptor']
                self.assertEqual(m['code_sha256'],census[key]['code_sha256'])
                self.assertEqual(coverage[key]['code_sha256'],m['code_sha256'])

    def test_four_motion_properties_are_distinct_exact_native_consumers(self):
        candidates=self.change['candidate_additions'];self.assertEqual(len(candidates),4)
        actual=set()
        for c in candidates:
            p=c['native_consumer'];m=self.method(p['entry'],'<init>')
            binding=literal_block_factor_binding(m,p['offset'])
            self.assertEqual(binding,c['native_block_factor_binding'])
            self.assertEqual(binding['native_value'],0.8999999761581421)
            actual.add((p['entry'].rsplit('/',1)[-1],binding['property']))
            self.assertTrue(c['observation_only']);self.assertEqual(len(c['parameters']),1)
        self.assertEqual(actual,{(n+'.class',prop) for n in ('SilkenSoilBlock','SilkenStoneBlock')
                                 for prop in ('speedFactor','jumpFactor')})

    def test_registered_constructor_handles_use_existing_pinned_initializer(self):
        context=self.b['native_registration_context'];self.assertEqual(len(context),2)
        for r in context:
            p=r['initializer'];self.assertEqual(p['evidence_file'],'native-evidence/arphex-native-spatial-item-support.json')
            w=next(w for w in read_json(OUT/p['evidence_file'])['witnesses'] if w['id']==p['witness_id'])
            init=next(m for m in w['methods'] if m['name']=='<clinit>')
            self.assertTrue(all(i in init['instructions'] for i in r['registration_instructions']))
            b=next(b for b in self.c['registration_bootstraps'] if b['entry']==p['entry'] and b['index']==r['bootstrap_index'])
            self.assertEqual([a['value'] for a in r['bootstrap']['arguments']],b['arguments'])
            self.assertIn(r['entry'][:-6]+'.<init>()V',b['arguments'])
            self.assertEqual(r['registration_instructions'][0]['operand'],r['registry_key'].split(':')[1])

    def test_effect_tick_delegates_preserve_original_recipient_amplifier_and_return(self):
        for name in ('EnhancedSenses','EtherealCharge'):
            entry='net/arphex/potion/'+name+'MobEffect.class'
            self.assertEqual([i['opcode'] for i in self.method(entry,'shouldApplyEffectTickThisTick')['instructions']],['0x4','0xac'])
            body=self.method(entry,'applyEffectTick')['instructions']
            self.assertEqual(body[9]['operand'],'net/arphex/procedures/'+name+'OnEffectActiveTickProcedure.execute(Lnet/minecraft/world/level/LevelAccessor;DDDLnet/minecraft/world/entity/Entity;)V')
            self.assertEqual([i['local_index'] for i in body[10:13]],[0,1,2])
            self.assertEqual(body[-2]['operand'],'net/minecraft/world/effect/MobEffect.applyEffectTick(Lnet/minecraft/world/entity/LivingEntity;I)Z')
            self.assertEqual(body[-1]['opcode'],'0xac')
            target=next(r for r in self.b['reused_native_call_targets'] if r['entry']=='net/arphex/procedures/'+name+'OnEffectActiveTickProcedure.class' and r['method']=='execute')
            self.assertTrue(target['proofs'])

    def test_visibility_flammability_and_codec_fields_are_actual_values(self):
        counts={'isVisibleInGui':0,'isVisibleInInventory':0,'renderInventoryText':0}
        for w in self.w.values():
            for m in w['methods']:
                if m['name'] in counts:
                    counts[m['name']]+=1
                    self.assertEqual([i['opcode'] for i in m['instructions']],['0x3','0xac'])
        self.assertEqual(counts,{'isVisibleInGui':19,'isVisibleInInventory':7,'renderInventoryText':7})
        body=self.method('net/arphex/block/ScorchedSandBlock.class','getFlammability')['instructions']
        self.assertEqual(body[0]['operand'],30);self.assertEqual(body[-1]['opcode'],'0xac')
        for name in ('ScorchedSandBlock','TrophyBlock'):
            body=self.method('net/arphex/block/'+name+'.class','codec')['instructions']
            self.assertEqual([i['opcode'] for i in body],['0xb2','0xb0'])
            self.assertEqual(body[0]['operand'],'net/arphex/block/'+name+'.CODECLcom/mojang/serialization/MapCodec;')
        for w in self.w.values():
            for m in w['methods']:
                if m['name']=='getLightBlock':self.assertEqual(m['instructions'][0]['operand'],15)

    def test_container_removal_owns_native_drop_and_neighbour_update(self):
        for name in ('TrophyBlock','WarpManifoldBlock'):
            body=self.method('net/arphex/block/'+name+'.class','onRemove')['instructions']
            self.assertTrue(any('Containers.dropContents(' in str(i['operand']) for i in body))
            self.assertTrue(any('Level.updateNeighbourForOutputSignal(' in str(i['operand']) for i in body))
            self.assertEqual(body[4]['opcode'],'0xa5')
            self.assertFalse(any('.hurt(' in str(i['operand']) or '.addEffect(' in str(i['operand']) for i in body))

    def test_changed_property_value_cannot_validate_as_native_refinement(self):
        b=copy.deepcopy(self.b)
        b['record_refinements'][0]['candidate_additions'][0]['native_block_factor_binding']['native_value']=1.0
        with self.assertRaises(AssertionError):validate_batch(b,self.review(),self.c)


if __name__=='__main__':unittest.main()
