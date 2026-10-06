"""Assert native event reachability and scalar facts independently of prose."""
import unittest
from catalog_common import OUT,read_json
from collect_combat_census import decode_sites
from promote_combat_batch import validate_batch


class GlobalHooksTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.census=read_json(OUT/'arphex-combat-census.json')
        cls.native=read_json(OUT/'native-evidence/arphex-global-hooks.json')
        cls.batch=read_json(OUT/'arphex-r2m2c-small-global-deliveries.json')

    def witness(self,name):
        return next(w for w in self.native['witnesses'] if w['entry']==f'net/arphex/procedures/{name}.class')

    def test_small_batch_native_consumers_and_unique_identities(self):
        review=read_json(OUT/'mod-reviews/arphex.json');ids={r['id'] for r in self.batch['effects']}
        review['effects']=[r for r in review['effects'] if r['id'] not in ids]
        review['paths']=[p for p in review['paths'] if not set(p['effect_ids'])&ids]
        self.assertEqual(validate_batch(self.batch,review,self.census)['semantic_records'],
                         len(review['effects'])+len(self.batch['effects']))
        self.assertEqual(len(ids),9)

    def test_method_annotation_without_class_or_caller_is_not_live_registration(self):
        w=self.witness('EntitySpawnReasonProcedure')
        self.assertFalse(any(a['descriptor'].endswith('/EventBusSubscriber;') for a in w['annotations']))
        self.assertTrue(any(a['descriptor'].endswith('/SubscribeEvent;') for m in w['methods'] for a in m['annotations']))
        target='net/arphex/procedures/EntitySpawnReasonProcedure.'
        external=[(m,s) for m in self.census['methods'] if not m['entry'].startswith(w['entry'][:-6])
                  for s in decode_sites(self.census,m,'calls') if target in s['operand']]
        self.assertEqual(external,[])
        self.assertFalse(any(target in str(b['arguments']) and b['entry']!=w['entry']
                             for b in self.census['registration_bootstraps']))
        registrations=[(m['entry'],m['method'],s['offset']) for m in self.census['methods']
                       for s in decode_sites(self.census,m,'calls')
                       if '/IEventBus.register(Ljava/lang/Object;)V' in s['operand']]
        self.assertEqual(registrations,[('net/arphex/ArphexMod.class','<init>',8)])
        root=next(w for w in read_json(OUT/'native-evidence/arphex-status-core.json')['witnesses'] if w['entry']=='net/arphex/ArphexMod.class')
        ctor=next(m for m in root['methods'] if m['name']=='<init>')
        before=next(i for i in ctor['instructions'] if i['offset']==7)
        self.assertEqual(before['opcode'],'0x2a') # register(this), not a procedure class
        tick=next(m for m in self.census['methods'] if m['entry']==root['entry'] and m['method']=='tick')
        self.assertFalse(tick['access']&0x8) # instance handler matches register(this)

    def test_mob_disable_list_preserves_literal_native_defaults(self):
        config=next(w for w in self.native['witnesses'] if w['entry'].endswith('/ConfigurationSettingsConfiguration.class'))
        body=config['methods'][0]['instructions']
        at=next(n for n,i in enumerate(body) if 'List.of(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)' in str(i['operand']))
        defaults=[i['operand'] for i in body[at-3:at]]
        self.assertEqual(defaults,['mob_id','mob_id','mob_id (add as many as needed, e.g. spider_snatcher)'])
        row=next(r for r in self.batch['effects'] if r['id']=='arphex:global_entity_join_admission')
        self.assertEqual(row['binary_parameters']['disable_specific_mobs_default'],defaults)

    def test_global_resistance_is_under_living_gate_not_species_gate(self):
        body=next(m['instructions'] for m in self.witness('BloodWormOnInitialEntitySpawnProcedure')['methods']
                  if m['name']=='execute' and any(i['offset']==533 for i in m['instructions']))
        at=next(n for n,i in enumerate(body) if i['offset']==533)
        self.assertEqual([i['operand'] for i in body[at-4:at]],[40,0,0,0])
        types=[i['operand'] for i in body[:at] if i['opcode']=='0xc1']
        self.assertEqual(types[-1],'net/minecraft/world/entity/LivingEntity')
        self.assertIn('DAMAGE_RESISTANCE',body[at-5]['operand'])

    def test_motion_cleanup_uses_component_sum_not_magnitude(self):
        body=next(m['instructions'] for m in self.witness('EntityJoinsWorldProcedure')['methods']
                  if m['name']=='execute' and any('Math.abs(D)' in str(i['operand']) for i in m['instructions']))
        at=next(n for n,i in enumerate(body) if 'Math.abs(D)' in str(i['operand']))
        self.assertEqual(sum(i['opcode']=='0x63' for i in body[max(0,at-20):at]),2)
        self.assertEqual(body[at+1]['operand'],0.001)
        self.assertEqual(abs(1+(-1)+0),0)
        self.assertNotEqual((1**2+(-1)**2+0**2)**0.5,0)

    def test_zero_sleep_hurt_and_native_map_coordinate_typo_are_preserved(self):
        w=self.witness('PlayerSleepsProcedure')
        body=next(m['instructions'] for m in w['methods'] if m['name']=='lambda$execute$0')
        at=next(n for n,i in enumerate(body) if '.hurt(' in str(i['operand']))
        self.assertEqual(body[at-1]['operand'],0.0)
        self.assertEqual(body[at+1]['opcode'],'0x57')
        main=next(m['instructions'] for m in w['methods'] if m['name']=='execute' and any('tormentor_healthD' in str(i['operand']) for i in m['instructions']))
        self.assertEqual(sum('tormentor_yD' in str(i['operand']) for i in main),4)
        self.assertEqual(sum('tormentor_zD' in str(i['operand']) for i in main),0)

    def test_visual_scale_name_does_not_exclude_physical_dimensions(self):
        reader=next(m for m in self.census['methods'] if m['entry']=='net/arphex/entity/ScorpioidBloodlusterEntity.class' and m['method']=='getDefaultDimensions')
        self.assertTrue(any('ScorpioidBloodlusterEntityVisualScaleProcedure.execute(' in s['operand'] for s in decode_sites(self.census,reader,'calls')))
        excluded={r['entry'] for r in self.batch['exclusions']}
        self.assertNotIn('net/arphex/procedures/ScorpioidBloodlusterEntityVisualScaleProcedure.class',excluded)


if __name__=='__main__':unittest.main()
