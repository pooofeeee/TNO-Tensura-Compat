"""Exact native asset projections and loader boundary checks; no game execution."""
import copy
import json
import unittest
from structure_nbt import payload_projection
from catalog_common import OUT, read_json
from promote_combat_batch import validate_batch


class StructureProjectionTests(unittest.TestCase):
    def fixture(self):
        return dict(size=[2, 3, 4], DataVersion=123,
            palette=[{'Name': 'minecraft:air'}, {'Name': 'example:trap'}],
            blocks=[dict(pos=[0, 0, 0], state=0),
                    dict(pos=[1, 1, 1], state=1, nbt={'id':'example:unknown', 'custom':42})],
            entities=[dict(pos=[.5, 1., .5], blockPos=[0,1,0],
                           nbt={'id':'example:actor','Health':0.,'Owner':'native-owner',
                                'unknown_nested':{'number':91}})])

    def test_all_payloads_preserved_without_invented_liveness(self):
        d=self.fixture(); p=payload_projection(d)
        self.assertEqual(p['entities'], d['entities'])
        self.assertEqual(p['block_payloads'], [dict(source_block_index=1, **d['blocks'][1])])
        self.assertEqual(p['used_palettes'][0][1], dict(state_index=1,block_count=1,state=d['palette'][1]))
        p['entities'][0]['nbt']['Health']=99.
        self.assertEqual(d['entities'][0]['nbt']['Health'], 0.)

    def test_unused_palettes_not_treated_as_placed_blocks(self):
        d=self.fixture(); d['palette'].append({'Name':'example:unused_boss'});
        p=payload_projection(d)
        self.assertEqual([r['state']['Name'] for r in p['used_palettes'][0]],
                         ['minecraft:air','example:trap'])
        self.assertNotIn('example:unused_boss',json.dumps(p))

    def test_each_alternate_palette_uses_same_native_state_index(self):
        d=self.fixture(); d['palettes']=[d.pop('palette'),[{'Name':'minecraft:stone'},{'Name':'example:alternate'}]]
        p=payload_projection(d)
        self.assertEqual(p['used_palettes'][1][1]['state']['Name'], 'example:alternate')
        self.assertEqual(p['used_palettes'][1][1]['block_count'],1)

    def test_unknown_structural_fields_and_invalid_indexes_fail_closed(self):
        d=self.fixture(); d['unreviewed_future_root']='unexpected'
        with self.assertRaises(AssertionError):payload_projection(d)
        d=self.fixture(); d['blocks'][1]['state']=2
        with self.assertRaises(AssertionError):payload_projection(d)
        d=self.fixture(); d['entities'][0]['hidden_payload']='unexpected'
        with self.assertRaises(AssertionError):payload_projection(d)

    def test_projection_is_deterministic(self):
        d=self.fixture()
        self.assertEqual(json.dumps(payload_projection(d),sort_keys=True),
                         json.dumps(payload_projection(copy.deepcopy(d)),sort_keys=True))


class NativeTemplateContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m6v-native-template-payloads.json')
        cls.native=read_json(OUT/'native-evidence/arphex-native-jigsaw-templates.json')
        cls.vanilla=read_json(OUT/'vanilla-evidence/arphex-native-template-loading.json')
        cls.loader=read_json(OUT/'reference-evidence/arphex-native-template-loading-244.json')

    def body(self, name, method):
        return max((m['instructions'] for c in self.vanilla['classes'] if c['class_name'].endswith('/'+name)
                    for m in c['methods'] if m['name']==method), key=len)

    def test_exact_seven_assets_without_duplicate_encounter_records(self):
        prior=read_json(OUT/'mod-reviews/arphex.json');c=read_json(OUT/'arphex-combat-census.json')
        validate_batch(self.batch,prior,c)
        self.assertEqual(len(self.native['witnesses']),7)
        self.assertEqual(self.batch['effects'],[])
        self.assertEqual(len(self.batch['record_refinements']),1)
        self.assertEqual(self.batch['record_refinements'][0]['candidate_additions'],[])
        wanted=set(read_json(OUT/'arphex-r2m6u-native-residual-block-contracts.json')['pending_native_assets'])
        self.assertEqual({w['entry'] for w in self.native['witnesses']},wanted)

    def test_native_spawners_and_saved_dead_entities_are_distinct(self):
        ds=[w['structure_payload'] for w in self.native['witnesses']]
        self.assertEqual([sum(b['nbt'].get('id')=='minecraft:mob_spawner' for b in d['block_payloads']) for d in ds],
                         [0,0,4,19,41,14,0])
        es=[e['nbt'] for d in ds for e in d['entities']]
        self.assertEqual(len(es),43)
        self.assertEqual(sum(e.get('Health',0)>0 for e in es),8)
        self.assertEqual(sum(e.get('Health',0)==0 for e in es),35)
        self.assertTrue(all(not {'Owner','Team','Passengers'} & e.keys() for e in es if e.get('Health',0)>0))
        self.assertTrue(all(d['data_version']==3465 for d in ds))

    def test_published_formula_and_resource_proofs_cannot_drift(self):
        from promote_combat_batch import refined_review
        prior=read_json(OUT/'mod-reviews/arphex.json')
        published=refined_review(prior,self.batch)
        self.assertEqual(refined_review(published,self.batch),published)
        bad=copy.deepcopy(published)
        row=next(r for r in bad['effects'] if r['id']==self.batch['record_refinements'][0]['id'])
        next(c for c in row['components'] if c['primitive']=='NATIVE_TEMPLATE_ENCOUNTER_PRESETS')['formula']='invented'
        with self.assertRaisesRegex(AssertionError,'changed published component context'):
            refined_review(bad,self.batch)
        bad=copy.deepcopy(published)
        row=next(r for r in bad['effects'] if r['id']==self.batch['record_refinements'][0]['id'])
        row['native_resource_evidence']=[]
        with self.assertRaisesRegex(AssertionError,'missing published resource proof'):
            refined_review(bad,self.batch)

    def test_placed_ant_nests_and_cave_contact_blocks_reuse_existing_payloads(self):
        ds={w['entry'].rsplit('/',1)[-1]:w['structure_payload'] for w in self.native['witnesses']}
        counts=lambda d,name:sum(x['block_count'] for x in d['used_palettes'][0] if x['state']['Name']==name)
        self.assertEqual(counts(ds['anthill_undervoid.nbt'],'arphex:ant_nest'),62)
        self.assertEqual(counts(ds['anthill_upside.nbt'],'arphex:ant_nest'),61)
        cave=ds['spider_cave.nbt'];self.assertEqual(counts(cave,'arphex:spider_egg'),18)
        self.assertEqual(cave['entities'][0]['nbt']['id'],'arphex:spider_matriarch')
        self.assertEqual({b['nbt']['id'] for d in ds.values() for b in d['block_payloads']},
                         {'minecraft:chest','minecraft:mob_spawner','minecraft:skull'})

    def test_loader_updates_version_before_load_and_replaces_uuid(self):
        b=self.body('StructureTemplateManager','readStructure')
        fix=next(i['offset'] for i in b if 'updateToCurrentVersion' in str(i['operand']))
        load=next(i['offset'] for i in b if 'StructureTemplate.load(' in str(i['operand']))
        self.assertLess(fix,load)
        b=self.body('StructureTemplate','placeEntities')
        self.assertTrue(any(i['operand']=='UUID' for i in b))
        self.assertTrue(any('CompoundTag.remove(' in str(i['operand']) for i in b))
        b=self.body('StructurePlaceSettings','<init>')
        self.assertFalse(any('finalizeEntities' in str(i['operand']) for i in b))
        native=read_json(OUT/'native-evidence/arphex-native-residual-blocks.json')
        j=next(w for w in native['witnesses'] if w['entry'].endswith('/ArphexJigsawOnTickUpdateProcedure.class'))
        self.assertFalse(any('setFinalizeEntities' in str(i['operand']) for m in j['methods'] for i in m['instructions']))

    def test_exact_fixer_version_and_numeric_id_fallback_are_pinned(self):
        b=self.body('DataFixers','addFixers')
        self.assertEqual(b[1]['operand'],3568)
        self.assertTrue(any('MobEffectIdFix.<init>' in str(i['operand']) for i in b))
        self.assertTrue(all(8446<=i['offset']<=8471 for i in b))
        b=self.body('MobEffectIdFix','lambda$static$0')
        j=next(j for j,i in enumerate(b) if i['operand']=='minecraft:darkness')
        self.assertEqual(b[j-1]['operand'],33)
        b=self.body('MobEffectIdFix','updateLivingEntityTag')
        self.assertTrue(any(i['operand']=='ActiveEffects' for i in b))
        self.assertTrue(any(i['operand']=='active_effects' for i in b))

    def test_neoforge_preserves_namespaced_effect_identity_and_native_processors(self):
        patches={w['entry']:w for w in self.loader['witnesses']}
        effect=patches['patches/net/minecraft/util/datafix/fixes/MobEffectIdFix.java.patch']['text']
        self.assertIn('updateMobEffectIdFieldConsideringForge',effect)
        self.assertIn('"forge:id"',effect)
        self.assertIn('forgeField.isPresent()',effect)
        structure=patches['patches/net/minecraft/world/level/levelgen/structure/templatesystem/StructureTemplate.java.patch']['text']
        self.assertIn('proc.processEntity(',structure)
        self.assertIn('placementIn.shouldFinalizeEntities()',structure)
        entity=patches['patches/net/minecraft/world/entity/Entity.java.patch']['text_sections'][0]['text']
        self.assertIn('getCompound("NeoForgeData")',entity)
        self.assertNotIn('getCompound("ForgeData")',entity)
        es=[e['nbt'] for w in self.native['witnesses'] for e in w['structure_payload']['entities']]
        moth=next(e for e in es if e['id']=='arphex:spider_moth')
        self.assertIn('arphex:despawn_immunity',[x.get('forge:id') for x in moth['ActiveEffects']])
        self.assertTrue(any('ForgeData' in e for e in es))
        self.assertFalse(any('NeoForgeData' in e for e in es))


if __name__=='__main__':unittest.main()
