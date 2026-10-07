"""Native registry reachability and precise observer/animation side effects."""
import copy
import unittest

from catalog_common import OUT,read_json
from promote_combat_batch import validate_batch,literal_effect_arguments
from reconcile_native_census import reconcile
from test_shadow_clone_contracts import NativeContractHarness


class NativeRegistryContextTests(NativeContractHarness,unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m7q-native-registry-context.json')
        cls.native=read_json(OUT/'native-evidence/arphex-native-registry-context.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def method(self,name,method,descriptor=None):
        return next(m for w in self.native['witnesses'] if w['entry'].endswith('/'+name+'.class')
                    for m in w['methods'] if m['name']==method and (descriptor is None or m['descriptor']==descriptor))

    def test_scope_preserves_independent_native_hashes_and_one_real_dose(self):
        self.assertEqual((len(self.native['witnesses']),sum(len(w['methods']) for w in self.native['witnesses'])),(108,327))
        self.assertEqual(len(self.batch['effects']),1);self.assertEqual(self.batch['record_refinements'],[])
        self.assertEqual(len(self.batch['effects'][0]['scalable_parameter_candidates']),1)
        self.assertEqual(self.batch['effects'][0]['scalable_parameter_candidates'][0]['parameters'],['duration','amplifier'])
        self.assertEqual(self.batch['effects'][0]['canonical_contract_reuse'],['arphex:necrosis'])
        validate_batch(self.batch,self.prior(),self.census)
        source={(m['entry'],m['method'],m['descriptor']):m for m in self.census['methods']}
        for w in self.native['witnesses']:
            for m in w['methods']:
                self.assertEqual(source[(w['entry'],m['name'],m['descriptor'])]['code_sha256'],m['code_sha256'])

    def test_registered_base_potion_has_exact_holder_duration_amplifier_and_flags(self):
        m=self.method('ArphexModPotions','lambda$static$0')
        args=literal_effect_arguments(m,23)
        self.assertEqual(args,dict(holder='net/arphex/init/ArphexModMobEffects.NECROSISLnet/neoforged/neoforge/registries/DeferredHolder;',duration=3600,amplifier=0,explicit_flags=[0,1]))
        self.assertEqual(sum('MobEffectInstance.<init>(' in str(i['operand']) for i in m['instructions']),1)
        self.assertFalse(any('.addEffect(' in str(i['operand']) or '.hurt(' in str(i['operand']) for i in m['instructions']))
        self.assertTrue(any(i['operand']=='potion_of_necrosis' for i in self.body('ArphexModPotions','<clinit>')))
        bootstrap=next(b for b in self.census['registration_bootstraps']
                       if b['entry']=='net/arphex/init/ArphexModPotions.class' and b['index']==0)
        self.assertIn('net/arphex/init/ArphexModPotions.lambda$static$0()Lnet/minecraft/world/item/alchemy/Potion;',bootstrap['arguments'])
        b=copy.deepcopy(self.batch);b['effects'][0]['components'][0]['numerical_parameters']['duration']=3601
        with self.assertRaises(AssertionError):validate_batch(b,self.prior(),self.census)

    def test_brewing_retains_water_and_ingredient_guards_and_input_item_kind(self):
        body=self.body('NecrosisPotionBrewingRecipe','isInput')
        for symbol in ('Items.POTION','Items.SPLASH_POTION','Items.LINGERING_POTION','Potions.WATER'):
            self.assertTrue(any(symbol in str(i['operand']) for i in body))
        self.assertTrue(any('ArphexModItems.NECROTIC_FANG' in str(i['operand'])
                            for i in self.body('NecrosisPotionBrewingRecipe','isIngredient')))
        body=self.body('NecrosisPotionBrewingRecipe','getOutput');at={i['offset']:i for i in body}
        self.assertEqual([(at[n]['opcode'],at[n]['branch_target']) for n in (5,13)], [('0x99',27),('0x99',27)])
        self.assertEqual(at[16]['local_index'],1);self.assertIn('ItemStack.getItem()',at[17]['operand'])
        self.assertIn('POTION_OF_NECROSIS',at[20]['operand']);self.assertIn('PotionContents.createItemStack(',at[23]['operand'])
        self.assertIn('ItemStack.EMPTY',at[27]['operand'])
        self.assertFalse(any('.addEffect(' in str(i['operand']) for i in body))

    def test_entity_animation_requests_are_reset_before_actual_actor_field_write(self):
        m=self.method('EntityAnimationFactory','onEntityTick');body=m['instructions']
        setters=[n for n,i in enumerate(body) if '.setAnimation(Ljava/lang/String;)V' in str(i['operand'])]
        writes=[i for i in body if i['opcode']=='0xb5']
        self.assertEqual((len(setters),len(writes)),(127,127))
        for n in setters:
            self.assertEqual(body[n-1]['operand'],'undefined')
            self.assertEqual(body[n+3]['opcode'],'0xb5')
            self.assertTrue(body[n+3]['operand'].endswith('.animationprocedureLjava/lang/String;'))
        self.assertTrue(any(a['descriptor']=='Lnet/neoforged/bus/api/SubscribeEvent;' for a in m['annotations']))
        self.assertFalse(any(any(s in str(i['operand']) for s in ('ATTACK_STATE','.hurt(','.setHealth(','.setDeltaMovement(')) for i in body))

    def test_item_animation_reads_copies_but_clears_original_hand_before_client_gate(self):
        body=self.body('ItemAnimationFactory','animatedItems');at={i['offset']:i for i in body}
        self.assertEqual(sum('ItemStack.copy()' in str(i['operand']) for i in body),2)
        for getter,read,update,gate,write in [('getMainHandItem',102,110,123,140),('getOffhandItem',200,208,221,238)]:
            self.assertIn('Player.'+getter+'()',at[read]['operand'])
            self.assertIn('CustomData.update(',at[update]['operand'])
            self.assertEqual(at[gate]['opcode'],'0x99')
            self.assertTrue(at[write]['operand'].endswith('SingularityScytheItem.animationprocedureLjava/lang/String;'))
            self.assertLess(update,gate);self.assertLess(gate,write)
        for name in ('lambda$animatedItems$0','lambda$animatedItems$1'):
            b=self.body('ItemAnimationFactory',name)
            self.assertEqual([i['operand'] for i in b[1:3]],['geckoAnim',''])
            self.assertIn('CompoundTag.putString(',b[3]['operand'])
        self.assertFalse(any('.setItem(' in str(i['operand']) or '.hurtAndBreak(' in str(i['operand']) for i in body))

    def test_preview_rotations_restore_original_actor_values_only_on_normal_return(self):
        m=self.method('RenderTest10GUIProcedure','renderEntity','(Lnet/minecraft/world/entity/Entity;FDDDFFFFZ)V')
        body=m['instructions'];at={i['offset']:i for i in body}
        for offset,local in [(17,14),(23,15),(29,16),(35,17),(184,20),(191,21),(198,22),(205,23)]:
            self.assertEqual(at[offset]['local_index'],local)
        for offset,local in [(247,20),(254,21),(261,22),(268,23),(294,14),(300,15),(306,16),(312,17)]:
            self.assertEqual(at[offset]['local_index'],local)
        self.assertEqual(at[38]['operand'],180.);self.assertIn('Entity.setYRot(',at[46]['operand'])
        self.assertEqual(at[50]['operand'],0.);self.assertIn('Entity.setXRot(',at[56]['operand'])
        self.assertEqual(m['exception_handlers'],[])
        self.assertEqual(body[-1]['opcode'],'0xb1')

    def test_raw_query_and_rng_results_do_not_become_proc_or_cooldown_scalars(self):
        body=self.body('WarpCoolingProcedure')
        self.assertTrue(any('PlayerVariables.track_warp_cooldownD' in str(i['operand']) for i in body))
        self.assertFalse(any(i['opcode'] in ('0xb3','0xb5') for i in body))
        body=self.body('CompassVersionsProcedure')
        self.assertTrue(any('PlayerVariables.arphexcompassD' in str(i['operand']) for i in body))
        self.assertTrue(any(i['operand']=='java/lang/Math.floor(D)D' for i in body))
        body=self.body('RandomReturnProcedure')
        self.assertEqual(body[0]['operand'],'net/minecraft/util/RandomSource.create()Lnet/minecraft/util/RandomSource;')
        self.assertEqual([i['operand'] for i in body[1:3]],[0,2])
        self.assertIn('Mth.nextInt(',body[3]['operand'])
        self.assertEqual({c['primitive'] for r in self.batch['effects'] for c in r['scalable_parameter_candidates']},{'MOB_EFFECT_NECROSIS'})

    def test_changed_native_context_hash_cannot_close_census(self):
        r=self.prior();r['effects']+=self.batch['effects'];r['paths']+=self.batch['paths']
        r['reviewed_batches']=list(set(r['reviewed_batches']+['arphex-r2m7q-native-registry-context.json']))
        e=copy.deepcopy(self.native);e['witnesses'][0]['methods'][0]['code_sha256']='0'*64
        def read(path):return e if path.name=='arphex-native-registry-context.json' else read_json(path)
        with self.assertRaisesRegex(AssertionError,'hash mismatch'):reconcile(r,self.census,read=read)


if __name__=='__main__':unittest.main()
