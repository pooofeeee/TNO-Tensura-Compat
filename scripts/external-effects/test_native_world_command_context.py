"""Last native method coverage and independent configured encounter payloads."""
import copy
import unittest
from collections import Counter

from catalog_common import OUT,read_json
from promote_combat_batch import refined_review,validate_batch
from reconcile_native_census import reconcile
from test_shadow_clone_contracts import NativeContractHarness


class NativeWorldCommandTests(NativeContractHarness,unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m7r-native-world-command-context.json')
        cls.native=read_json(OUT/'native-evidence/arphex-native-world-command-context.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def test_scope_and_zero_pending_come_from_independent_native_census(self):
        classes=[w for w in self.native['witnesses'] if w['entry'].endswith('.class')]
        self.assertEqual((len(classes),sum(len(w['methods']) for w in classes)),(70,154))
        self.assertEqual(len(self.batch['effects']),1);self.assertEqual(len(self.batch['record_refinements']),4)
        self.assertEqual(self.batch['effects'][0]['scalable_parameter_candidates'],[])
        self.assertFalse(any(c['candidate_additions'] for c in self.batch['record_refinements']))
        validate_batch(self.batch,self.prior(),self.census)
        r=refined_review(self.prior(),self.batch);r['effects']+=self.batch['effects'];r['paths']+=self.batch['paths']
        r['reviewed_batches']=list(set(r['reviewed_batches']+['arphex-r2m7r-native-world-command-context.json']))
        index,pending=reconcile(r,self.census)
        self.assertEqual(index['summary']['pending_methods'],0)
        self.assertEqual(index['summary']['exact_dispositioned_methods'],len(self.census['methods']))
        self.assertEqual(len(index['methods']),19159)

    def test_permission_and_native_argument_bounds_are_not_invented_policy(self):
        body=self.body('ArphexCommandCommand','lambda$registerCommand$0')
        self.assertEqual(body[1]['operand'],2);self.assertIn('CommandSourceStack.hasPermission(I)Z',body[2]['operand'])
        body=self.body('ArphexCommandCommand','registerCommand')
        values={body[n-3]['operand']:tuple(i['operand'] for i in body[n-2:n]) for n,i in enumerate(body) if 'DoubleArgumentType.doubleArg(DD)' in str(i['operand'])}
        self.assertEqual(values,dict(level=(0.,100.),tier=(1.,5.),tormentor_health=(0.,1024.),tormentor_rotation=(-180.,180.)))
        body=self.body('TormentorTierSetProcedure')
        self.assertEqual(next(i['operand'] for i in body if i['offset']==11),2.)
        self.assertEqual(next(i['branch_target'] for i in body if i['offset']==15),53)

    def test_raw_health_rounding_rotation_and_player_level_have_distinct_storage(self):
        health=self.body('TormentorHealthProcedure');at={i['offset']:i for i in health}
        self.assertEqual(at[10]['operand'],'java/lang/Math.round(D)J');self.assertEqual(at[13]['opcode'],'0x8a')
        self.assertTrue(at[14]['operand'].endswith('.tormentor_healthD'))
        rotation=self.body('TormentorRotationProcedure')
        self.assertFalse(any('Math.round' in str(i['operand']) for i in rotation))
        level=self.body('TormentorlevelsetProcedure');at={i['offset']:i for i in level}
        self.assertIn('DoubleArgumentType.getDouble(',at[48]['operand'])
        self.assertTrue(at[51]['operand'].endswith('.killedtormentorD'))
        self.assertTrue(all(i['offset']>51 for i in level if 'Math.round' in str(i['operand'])))

    def test_force_spawn_initializes_before_world_and_result_gates_without_owner(self):
        body=self.body('ForceSpawnTormentorProcedure');at={i['offset']:i for i in body}
        self.assertEqual(at[1]['branch_target'],5);self.assertEqual(at[14]['branch_target'],35)
        self.assertEqual(at[21]['operand'],1024.)
        self.assertTrue(at[24]['operand'].endswith('.tormentor_healthD'))
        self.assertEqual(at[36]['operand'],'net/minecraft/server/level/ServerLevel')
        self.assertIn('MobSpawnType.MOB_SUMMONED',at[81]['operand'])
        self.assertIn('EntityType.spawn(',at[84]['operand']);self.assertEqual(at[89]['branch_target'],128)
        self.assertEqual([i['offset'] for i in body if any(x in str(i['operand']) for x in ('.setYRot(','.setYBodyRot(','.setYHeadRot('))],[101,113,125])
        self.assertFalse(any(any(s in str(i['operand']) for s in ('.setOwner(','.setTarget(','.hurt(','.addEffect(')) for i in body))

    def test_seal_and_discard_keep_distinct_native_lifecycle_and_binary_state(self):
        body=self.body('SealCommandProcedure');at={i['offset']:i for i in body}
        self.assertTrue(at[11]['operand'].endswith('.tormentor_healthD'))
        self.assertEqual(at[86]['operand'],'arphex despawn @e[type=arphex:tormentor_test]')
        self.assertEqual(at[191]['operand'],'kill @e[type=arphex:tormentor]')
        body=self.body('DespawnCommandProcedure')
        self.assertTrue(any(i['operand']=='arphex:' for i in body))
        self.assertEqual(sum('.discard()V' in str(i['operand']) for i in body),1)
        self.assertFalse(any('.hurt(' in str(i['operand']) for i in body))
        for name,field in [('MirrorCommandProcedure','shield_power_unlockedZ'),('SeismicCommandProcedure','slam_power_unlockedZ')]:
            self.assertEqual(sum(i['opcode']=='0xb5' and str(i['operand']).endswith(field) for i in self.body(name)),2)

    def test_common_structure_processor_entity_admission_and_return_are_exact(self):
        body=self.body('StructureFeature','place')
        at=next(n for n,i in enumerate(body) if '.setIgnoreEntities(' in str(i['operand']))
        self.assertEqual(body[at-1]['operand'],0)
        self.assertEqual(sum('.addProcessor(' in str(i['operand']) for i in body),1)
        self.assertTrue(any(i['operand']=='net/minecraft/world/level/levelgen/structure/templatesystem/BlockIgnoreProcessor' for i in body))
        self.assertFalse(any('.setFinalizeEntities(' in str(i['operand']) for i in body))
        at=next(n for n,i in enumerate(body) if '.placeInWorld(' in str(i['operand']))
        self.assertEqual([i['opcode'] for i in body[at+1:at+4]],['0x57','0x4','0xac'])

    def test_exact_configuration_graph_retains_all_native_template_references(self):
        resources=[w for w in self.native['witnesses'] if not w['entry'].endswith('.class')]
        self.assertEqual(len(resources),170)
        configs=[w for w in resources if '/configured_feature/' in w['entry']]
        placed=[w for w in resources if '/placed_feature/' in w['entry']]
        roots=[w for w in resources if '/biome_modifier/' in w['entry'] or '/worldgen/biome/' in w['entry']]
        self.assertEqual((len(configs),len(placed),len(roots)),(44,44,44))
        config_ids={'arphex:'+w['entry'].rsplit('/',1)[-1][:-5] for w in configs}
        self.assertEqual({w['data']['feature'] for w in placed},config_ids)
        refs={w['data']['config']['structure'] for w in configs};self.assertEqual(len(refs),39)
        # Published evidence plus exactly one protected earlier template prove
        # the resource set; no generated expected list stands in for the JSON.
        proofs=self.batch['native_resource_evidence']
        templates={p['entry'] for p in proofs if p['entry'].endswith('.nbt')}
        self.assertEqual(templates,{'data/'+r.split(':')[0]+'/structure/'+r.split(':')[1]+'.nbt' for r in refs})
        self.assertEqual(sum(p['evidence_file']!='native-evidence/arphex-native-world-command-context.json' for p in proofs),1)

    def test_raw_saved_actor_and_native_spawner_seeds_are_not_new_attack_scalars(self):
        payloads=[w['structure_payload'] for w in self.native['witnesses'] if 'structure_payload' in w]
        self.assertEqual(len(payloads),38)
        self.assertEqual({p['data_version'] for p in payloads},{3465})
        entities=[x['nbt'] for p in payloads for x in p['entities']]
        self.assertEqual(len(entities),1);self.assertEqual((entities[0]['id'],entities[0]['Health']),('arphex:spider_prowler',250.))
        self.assertEqual([(e['forge:id'],e['Duration'],e['Amplifier']) for e in entities[0]['ActiveEffects']],
                         [('minecraft:levitation',10,1),('minecraft:resistance',-1,2),('minecraft:regeneration',48,0)])
        sp=[b['nbt'] for p in payloads for b in p['block_payloads'] if b['nbt'].get('id')=='minecraft:mob_spawner']
        self.assertEqual(len(sp),14)
        self.assertEqual(Counter(n['SpawnData']['entity'].get('id','NO_LITERAL_ENTITY_ID') for n in sp),self.batch['effects'][0]['native_spawner_targets'])
        for n in sp:self.assertEqual(tuple(n[k] for k in ('MinSpawnDelay','MaxSpawnDelay','SpawnCount','MaxNearbyEntities','RequiredPlayerRange','SpawnRange')),(200,800,4,6,16,4))
        self.assertEqual(self.batch['effects'][0]['scalable_parameter_candidates'],[])

    def test_empty_spawner_has_no_invented_actor_and_failed_lookup_is_native(self):
        d=read_json(OUT/'vanilla-evidence/arphex-native-world-spawner.json')
        spawn=next(c for c in d['classes'] if c['class_name'].endswith('/SpawnData'))
        constructors=[m for m in spawn['methods'] if m['name']=='<init>']
        self.assertFalse(any('EntityType.PIG' in str(i['operand']) or i['operand']=='minecraft:pig' for m in constructors for i in m['instructions']))
        spawner=next(c for c in d['classes'] if c['class_name'].endswith('/BaseSpawner'))
        at={i['offset']:i for i in next(m for m in spawner['methods'] if m['name']=='serverTick')['instructions']}
        self.assertIn('EntityType.by(',at[81]['operand']);self.assertIn('Optional.isEmpty()',at[88]['operand'])
        self.assertIn('BaseSpawner.delay(',at[97]['operand']);self.assertEqual(at[100]['opcode'],'0xb1')
        registry=next(c for c in d['classes'] if c['class_name'].endswith('/DefaultedMappedRegistry'))
        body=registry['methods'][0]['instructions']
        self.assertEqual(body[2]['opcode'],'0xb7');self.assertIn('MappedRegistry.get(',body[2]['operand'])
        self.assertIn('Optional.ofNullable(',body[3]['operand'])

    def test_changed_last_native_method_hash_cannot_close_coverage(self):
        r=refined_review(self.prior(),self.batch);r['effects']+=self.batch['effects'];r['paths']+=self.batch['paths']
        r['reviewed_batches']=list(set(r['reviewed_batches']+['arphex-r2m7r-native-world-command-context.json']))
        e=copy.deepcopy(self.native);next(w for w in e['witnesses'] if w['entry'].endswith('.class'))['methods'][0]['code_sha256']='0'*64
        def read(path):return e if path.name=='arphex-native-world-command-context.json' else read_json(path)
        with self.assertRaisesRegex(AssertionError,'hash mismatch'):reconcile(r,self.census,read=read)


if __name__=='__main__':unittest.main()
