"""Native contract and negative-mutation checks for the second status batch."""
import copy
import json
import unittest

from catalog_common import OUT,read_json
from collect_combat_census import decode_sites
from promote_combat_batch import validate_batch
from reconcile_native_census import reconcile

FILE='alexscaves-r2m8b-darkness-rage-and-vision-context.json'
OLD='native-evidence/alexscaves-status-foundation.json'
NEW='native-evidence/alexscaves-status-lifecycle.json'
PREFIX='com/github/alexmodguy/alexscaves/'


def method(packet,short,name):
    w=next(w for w in packet['witnesses'] if w['entry']==PREFIX+short+'.class')
    return next(m for m in w['methods'] if m['name']==name)


def validate_rage_modifier(row,packet):
    body=method(packet,'server/potion/RageEffect','applyEffectTick')['instructions']
    by={i['offset']:i for i in body}
    component=next(c for c in row['components'] if c['primitive']=='ATTRIBUTE_MODIFIER')
    assert component['native_operation']==by[53]['operand'].split('Operation.')[1].split('Lnet/')[0]
    assert component['numerical_parameters']['missing_health_amplifier_coefficient']==by[16]['operand']
    init=method(packet,'server/potion/RageEffect','<clinit>')['instructions']
    assert component['modifier_id']==init[0]['operand']+':'+init[1]['operand']
    assert [by[o]['opcode'] for o in (14,15,18,30,31,34)]==['0x60','0x86','0x6a','0x6e','0x66','0x6a']
    assert 'removeRageModifier' in by[39]['operand'] and 'addTransientModifier' in by[59]['operand']


class AlexCavesStatusLifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/FILE);cls.old=read_json(OUT/OLD);cls.new=read_json(OUT/NEW)
        cls.census=read_json(OUT/'alexscaves-combat-census.json')
        cls.review=read_json(OUT/'mod-reviews/alexscaves.json')
        first=read_json(OUT/'alexscaves-r2m8a-status-foundation.json')
        ids={r['id'] for r in first['effects']}
        paths={p['id'] for p in first['paths']}
        cls.prior=copy.deepcopy(cls.review)
        cls.prior['effects']=[r for r in cls.prior['effects'] if r['id'] in ids]
        cls.prior['paths']=[p for p in cls.prior['paths'] if p['id'] in paths]
        cls.prior['reviewed_batches']=['alexscaves-r2m8a-status-foundation.json']

    def test_source_bound_candidates_and_unique_canonical_statuses(self):
        result=validate_batch(self.batch,self.prior,self.census)
        self.assertEqual((result['semantic_records'],result['numeric_candidate_entries']),(5,21))
        self.assertEqual(result['classification_counts'],{'CUSTOM_CONTROL':3,'CUSTOM_STATUS':2})
        self.assertEqual({r['id'] for r in self.batch['effects']},{'alexscaves:darkness_incarnate','alexscaves:rage'})

    def test_locked_first_status_records_are_unchanged(self):
        old=read_json(OUT/'alexscaves-r2m8a-status-foundation.json')
        self.assertEqual({r['id']:r for r in self.prior['effects']},{r['id']:r for r in old['effects']})
        self.assertEqual({p['id']:p for p in self.prior['paths']},{p['id']:p for p in old['paths']})

    def test_rage_formula_id_operation_and_no_damage_callback(self):
        row=next(r for r in self.batch['effects'] if r['id']=='alexscaves:rage')
        validate_rage_modifier(row,self.old)
        body=method(self.old,'server/potion/RageEffect','applyEffectTick')['instructions'];by={i['offset']:i for i in body}
        self.assertIn('getHealth()',by[23]['operand']);self.assertIn('getMaxHealth()',by[27]['operand'])
        self.assertEqual(by[9]['branch_target'],62)
        self.assertFalse(any('.hurt(' in str(i['operand']) for i in body))
        self.assertEqual(by[47]['operand'],PREFIX+'server/potion/RageEffect.RAGE_ATTACK_DAMAGE_IDLnet/minecraft/resources/ResourceLocation;')

    def test_rage_selection_gates_keep_rng_order_and_two_way_alliance(self):
        by={i['offset']:i for i in method(self.old,'server/potion/RageEffect','applyEffectTick')['instructions']}
        self.assertEqual([by[o]['operand'] for o in (97,107,121,204)],[10,2,80.0,2])
        self.assertEqual(by[90]['branch_target'],371)
        self.assertEqual(by[178]['branch_target'],213)
        self.assertEqual(by[196]['branch_target'],257)
        self.assertIn('Mob.isAlliedTo',by[227]['operand']);self.assertIn('LivingEntity.isAlliedTo',by[237]['operand'])
        self.assertIn('canAttack',by[247]['operand'])
        self.assertIn('setLastHurtByMob',by[279]['operand']);self.assertIn('setTarget',by[286]['operand'])
        self.assertLess(205,227)

    def test_rage_has_no_own_expiry_cleanup_or_registered_attribute_template(self):
        callers=[]
        for m in self.census['methods']:
            if any('RageEffect.removeRageModifier(' in i['operand'] for i in decode_sites(self.census,m,'calls')):
                callers.append((m['entry'],m['method']))
        self.assertEqual(callers,[(PREFIX+'server/potion/RageEffect.class','applyEffectTick')])
        ctor=method(self.old,'server/potion/RageEffect','<init>')['instructions']
        self.assertFalse(any('addAttributeModifier(' in str(i['operand']) for i in ctor))
        for name in ('livingRemoveEffect','livingExpireEffect'):
            self.assertFalse(any('Rage' in str(i['operand']) or 'rage_attack_boost' in str(i['operand']) for i in method(self.old,'server/event/CommonEvents',name)['instructions']))
        vanilla=read_json(OUT/'vanilla-evidence/alexscaves-status-attributes.json')['classes'][0]
        for m in (m for m in vanilla['methods'] if m['name']=='<init>'):
            by={i['offset']:i for i in m['instructions']}
            self.assertEqual((by[5]['opcode'],by[5]['operand']),
                ('0xbb','it/unimi/dsi/fastutil/objects/Object2ObjectOpenHashMap'))
            self.assertEqual(by[9]['operand'],'it/unimi/dsi/fastutil/objects/Object2ObjectOpenHashMap.<init>()V')
            self.assertEqual((by[12]['opcode'],by[12]['operand']),
                ('0xb5','net/minecraft/world/effect/MobEffect.attributeModifiersLjava/util/Map;'))
        self.assertTrue(any('attributeModifiers' in str(i['operand']) for m in vanilla['methods'] if m['name']=='removeAttributeModifiers' for i in m['instructions']))

    def test_darkness_native_flight_enable_restore_and_sync_gates(self):
        by={i['offset']:i for i in method(self.old,'server/potion/DarknessIncarnateEffect','toggleFlight')['instructions']}
        self.assertEqual(by[68]['operand'],0.05000000074505806);self.assertEqual(by[82]['operand'],4.0)
        self.assertEqual(by[7]['branch_target'],169);self.assertEqual(by[14]['branch_target'],169)
        self.assertIn('ServerPlayer',by[11]['operand'])
        self.assertEqual(by[158]['branch_target'],169);self.assertEqual(by[162]['branch_target'],169)
        self.assertIn('fallDistance',by[171]['operand']);self.assertEqual(by[170]['operand'],0.0)
        self.assertEqual(by[104]['branch_target'],151);self.assertEqual(by[119]['branch_target'],130)

    def test_darkness_flag_handoff_precedes_separate_disappearance_reader(self):
        m=method(self.new,'mixin/LivingEntityMixin','ac_livingTick');by={i['offset']:i for i in m['instructions']}
        self.assertEqual(by[8]['operand'],0);self.assertIn('setSlowFallingFlag',by[9]['operand'])
        self.assertEqual(by[12]['opcode'],'0x2a');self.assertEqual(by[12]['local_index'],0)
        self.assertEqual([by[o]['operand'] for o in (20,22,23,24,25)],[80,0,0,0,0])
        self.assertIn('MobEffectInstance.<init>',by[26]['operand']);self.assertEqual(by[32]['opcode'],'0x57')
        self.assertIn('hadDarknessIncarnateEffect',by[136]['operand']);self.assertEqual(by[224]['operand'],1)
        self.assertIn('setSlowFallingFlag',by[225]['operand']);self.assertLess(26,225)
        annotation=next(a for a in m['annotations'] if a['descriptor'].endswith('/Inject;'))
        self.assertEqual(annotation['values']['at'][0]['values']['value'],'TAIL')

    def test_light_removal_native_gate_is_not_rewritten_as_scalar_damage(self):
        light=method(self.old,'server/potion/DarknessIncarnateEffect','isInLight')['instructions'];by={i['offset']:i for i in light}
        self.assertIn('getRootVehicle',by[1]['operand']);self.assertIn('LightLayer.BLOCK',by[12]['operand'])
        self.assertEqual([by[o]['operand'] for o in (44,54,61)],[0.259,0.74,15])
        self.assertEqual(by[38]['branch_target'],64)
        row=next(r for r in self.batch['effects'] if r['id']=='alexscaves:darkness_incarnate')
        self.assertFalse(any(c['primitive']=='ENVIRONMENTAL_STATUS_REMOVAL' for c in row['scalable_parameter_candidates']))

    def test_deepsight_is_preserved_as_live_vision_utility_without_invented_payload(self):
        exclusion=next(e for e in self.batch['exclusions'] if e['disposition']=='REGISTERED_CLIENT_VISION_UTILITY')
        self.assertIn('Live registered',exclusion['reason'])
        w=next(w for w in self.old['witnesses'] if w['entry'].endswith('/DeepsightEffect.class'))
        self.assertNotIn('applyEffectTick',w['declared_method_names'])
        self.assertFalse(any(any(s in str(i['operand']) for s in ('.hurt(','.setDeltaMovement(','.addAttributeModifier(','.addEffect(')) for m in w['methods'] for i in m['instructions']))
        intensity=method(self.old,'server/potion/DeepsightEffect','getIntensity')['instructions']
        self.assertTrue(any('isInfiniteDuration' in str(i['operand']) for i in intensity))
        for short,name in [('mixin/client/LightTextureMixin','ac_getBrightness'),('client/event/ClientEvents','fogRender')]:
            body=method(self.new,short,name)['instructions']
            self.assertTrue(any('DeepsightEffect.getIntensity' in str(i['operand']) for i in body))
            self.assertFalse(any('.hurt(' in str(i['operand']) or '.addEffect(' in str(i['operand']) for i in body))

    def test_mixed_native_methods_do_not_disappear_from_remaining_queue(self):
        review=copy.deepcopy(self.prior);review['effects']+=self.batch['effects'];review['paths']+=self.batch['paths'];review['reviewed_batches'].append(FILE)
        _,pending=reconcile(review,self.census);keys={(m['entry'],m['method']) for m in pending}
        for short,name in [('mixin/LivingEntityMixin','ac_livingTick'),('server/event/CommonEvents','livingRemoveEffect'),('server/event/CommonEvents','livingExpireEffect')]:
            self.assertIn((PREFIX+short+'.class',name),keys)

    def test_wrong_native_coefficient_operation_or_id_fails(self):
        for field,value in [('native_operation','ADD_MULTIPLIED_BASE'),('modifier_id','alexscaves:other')]:
            row=copy.deepcopy(next(r for r in self.batch['effects'] if r['id']=='alexscaves:rage'))
            row['components'][0][field]=value
            with self.assertRaises(AssertionError):validate_rage_modifier(row,self.old)
        b=copy.deepcopy(self.batch);row=next(r for r in b['effects'] if r['id']=='alexscaves:darkness_incarnate')
        next(c for c in row['components'] if c['primitive']=='FLIGHT_CONTROL')['numerical_parameters']['active_speed_multiplier']=5.0
        with self.assertRaises(AssertionError):validate_batch(b,self.prior,self.census)

    def test_regeneration_is_byte_identical(self):
        from assemble_alexscaves_status_lifecycle import build
        self.assertEqual((json.dumps(build(),ensure_ascii=False,indent=2)+'\n').encode(),(OUT/FILE).read_bytes())


if __name__=='__main__':unittest.main()
