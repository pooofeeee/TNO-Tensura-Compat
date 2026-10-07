"""Independent source/consumer, scope and negative-mutation checks."""
import copy
import unittest
from pathlib import Path

from catalog_common import OUT,WORK,read_json,sha256
from collect_combat_census import decode_sites
from promote_combat_batch import validate_batch,empty_review
from reconcile_native_census import reconcile

FILE='alexscaves-r2m8a-status-foundation.json'
PACKET='native-evidence/alexscaves-status-foundation.json'
PREFIX='com/github/alexmodguy/alexscaves/'


def source_method(packet,short,name):
    witness=next(w for w in packet['witnesses'] if w['entry']==PREFIX+short+'.class')
    return next(m for m in witness['methods'] if m['name']==name)


def radiation_formula(packet):
    """Read the actual linear expression, not the authored JSON formula."""
    body=source_method(packet,'server/potion/IrradiatedEffect','applyEffectTick')['instructions']
    prefix=body[:12]
    assert [i['opcode'] for i in prefix]==['0x2b','0xb8','0x3e','0xc','0x1d','0x86','0x12','0x6a','0x66','0x38','0x2b','0xc1']
    assert prefix[1]['operand']==PREFIX+'server/item/HazmatArmorItem.getWornAmount(Lnet/minecraft/world/entity/LivingEntity;)I'
    assert prefix[2]['local_index']==prefix[4]['local_index']==3
    assert prefix[9]['local_index']==4
    at=next(n for n,i in enumerate(body) if i['offset']==79)
    assert '.hurt(' in body[at]['operand'] and body[at-1]['local_index']==4
    return f"{prefix[3]['operand']:g}F - exactWornHazmatPieces*{prefix[6]['operand']:g}F"


def validate_radiation_formula(rows,packet):
    row=next(r for r in rows if r['id']=='alexscaves:irradiated')
    component=next(c for c in row['components'] if c['primitive']=='CUSTOM_RADIATION_DAMAGE')
    assert component['parameter_formulas']['requested_damage']==radiation_formula(packet)


class AlexCavesStatusFoundationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/FILE);cls.packet=read_json(OUT/PACKET)
        cls.census=read_json(OUT/'alexscaves-combat-census.json')
        cls.fields=read_json(OUT/'alexscaves-native-field-use-index.json')
        cls.rows={r['id']:r for r in cls.batch['effects']}

    def test_current_rows_and_native_candidates_validate_without_prior_semantics(self):
        result=validate_batch(self.batch,empty_review('alexscaves'),self.census)
        self.assertEqual((result['semantic_records'],result['numeric_candidate_entries']),(3,12))
        self.assertEqual(result['classification_counts'],{'CUSTOM_CONTROL':1,'CUSTOM_STATUS':2})
        self.assertEqual(set(self.rows),{'alexscaves:bubbled','alexscaves:irradiated','alexscaves:stunned'})
        validate_radiation_formula(self.batch['effects'],self.packet)

    def test_discovery_recovery_and_additive_fields_keep_original_boundaries(self):
        original=read_json(OUT/'discovery/alexscaves-scan.json')
        self.assertEqual(self.census['prior_index_recovery'],'BYTE_IDENTICAL')
        self.assertEqual(self.census['parsed_classes'],original['parsed_classes'])
        for pin in original['index_artifacts']:
            self.assertEqual(sha256(WORK/'alexscaves'/Path(pin['path']).name),pin['sha256'])
        native={(m['entry'],m['method'],m['descriptor']):m for m in self.census['methods']}
        for m in self.fields['methods']:
            self.assertEqual(m['code_sha256'],native[(m['entry'],m['method'],m['descriptor'])]['code_sha256'])
        self.assertEqual(self.fields['summary']['original_census_classes_checked'],1340)
        # BUBBLED references were not in the keyword hits: the field index must
        # retain the real active air-supply injection rather than infer absence.
        air=next(m for m in self.fields['methods'] if m['method']=='ac_increaseAirSupply')
        self.assertTrue(any('.BUBBLEDL' in self.fields['symbols'][s] for o,op,s in air['field_sites']))

    def test_registered_suppliers_and_event_bus_are_actual_native_producers(self):
        registry=source_method(self.packet,'server/potion/ACEffectRegistry','<clinit>')['instructions']
        native=self.census['registration_bootstraps']
        for name,index,cls in [('bubbled',4,'BubbledEffect'),('irradiated',3,'IrradiatedEffect'),('stunned',1,'StunnedEffect')]:
            at=next(n for n,i in enumerate(registry) if i['operand']==name)
            self.assertEqual(registry[at+1]['operand'],f'bootstrap#{index}:get()Ljava/util/function/Supplier;')
            self.assertIn('DeferredRegister.register',registry[at+2]['operand'])
            boot=next(b for b in native if b['entry']==PREFIX+'server/potion/ACEffectRegistry.class' and b['index']==index)
            self.assertIn(f'lambda$static${index}',str(boot['arguments']))
            supplier=source_method(self.packet,'server/potion/ACEffectRegistry',f'lambda$static${index}')['instructions']
            self.assertEqual(supplier[0]['operand'],PREFIX+'server/potion/'+cls)
            self.assertEqual(supplier[2]['operand'],PREFIX+'server/potion/'+cls+'.<init>()V')
        init=source_method(self.packet,'AlexsCaves','<init>')['instructions']
        self.assertTrue(any(i['operand']==PREFIX+'server/CommonProxy.commonInit()V' for i in init))
        bus=source_method(self.packet,'server/CommonProxy','commonInit')['instructions']
        self.assertTrue(any('IEventBus.register(Ljava/lang/Object;)' in str(i['operand']) for i in bus))
        for name in ('livingHeal','livingAttack','livingTick'):
            method=source_method(self.packet,'server/event/CommonEvents',name)
            self.assertTrue(any(a['descriptor']=='Lnet/neoforged/bus/api/SubscribeEvent;' for a in method['annotations']))

    def test_bubbled_air_motion_damage_order_and_mixins_stay_distinct(self):
        method=source_method(self.packet,'server/potion/BubbledEffect','applyEffectTick');by={i['offset']:i for i in method['instructions']}
        self.assertEqual([by[o]['operand'] for o in (54,101,105,119,121,282)],[-0.08,0.800000011920929,0.800000011920929,2,-20,2.0])
        self.assertIn('canBreatheUnderwater',by[1]['operand']);self.assertIn('AQUATIC',by[11]['operand'])
        self.assertEqual(by[17]['branch_target'],67)
        self.assertEqual(by[30]['branch_target'],287)
        self.assertIn('setAirSupply',by[140]['operand'])
        self.assertIn('DamageSources.drown()',by[279]['operand']);self.assertEqual(by[286]['opcode'],'0x57')
        self.assertLess(140,265);self.assertLess(265,283)
        for short,name,target in [('mixin/EntityMixin','ac_isInWater','isInWater'),('mixin/LivingEntityMixin','ac_increaseAirSupply','increaseAirSupply')]:
            m=source_method(self.packet,short,name)
            injection=next(a for a in m['annotations'] if a['descriptor'].endswith('/Inject;'))['values']
            self.assertTrue(injection['cancellable']);self.assertIn(target,injection['method'][0])
            self.assertEqual(injection['at'][0]['values']['value'],'HEAD')
        air=source_method(self.packet,'mixin/LivingEntityMixin','ac_increaseAirSupply')['instructions']
        self.assertEqual(next(i for i in air if i['offset']==11)['local_index'],1)

    def test_radiation_cadence_source_equipment_exhaustion_and_heal_veto(self):
        validate_radiation_formula(self.batch['effects'],self.packet)
        tick=source_method(self.packet,'server/potion/IrradiatedEffect','applyEffectTick')['instructions'];by={i['offset']:i for i in tick}
        self.assertEqual(by[4]['local_index'],3);self.assertEqual(by[27]['local_index'],3)
        self.assertEqual(by[28]['branch_target'],38);self.assertIn('causeFoodExhaustion',by[35]['operand'])
        self.assertIn('RaycatEntity',by[39]['operand']);self.assertIn('causeRadiationDamage',by[74]['operand'])
        self.assertEqual(by[82]['opcode'],'0x57')
        self.assertFalse(any('RESISTS_RADIATION' in str(i['operand']) for i in tick))
        cadence=source_method(self.packet,'server/potion/IrradiatedEffect','shouldApplyEffectTickThisTick')['instructions']
        self.assertEqual(next(i for i in cadence if i['offset']==6)['operand'],200)
        self.assertEqual(next(i for i in cadence if i['offset']==10)['opcode'],'0x6c')
        armor=source_method(self.packet,'server/item/HazmatArmorItem','getWornAmount')['instructions']
        self.assertEqual([i['operand'].split('EquipmentSlot.')[1].split('Lnet/')[0] for i in armor if 'EquipmentSlot.' in str(i['operand'])],['HEAD','CHEST','LEGS','FEET'])
        self.assertEqual(sum(i.get('increment')==1 for i in armor),4)
        source=source_method(self.packet,'server/misc/ACDamageTypes$DamageSourceRandomMessages','<init>')['instructions']
        self.assertEqual(source[2]['operand'],'net/minecraft/world/damagesource/DamageSource.<init>(Lnet/minecraft/core/Holder;)V')
        heal=source_method(self.packet,'server/event/CommonEvents','livingHeal')['instructions']
        self.assertTrue(any('RESISTS_RADIATION' in str(i['operand']) for i in heal))
        self.assertTrue(any('LivingHealEvent.setCanceled' in str(i['operand']) for i in heal))

    def test_stun_direct_entity_gate_native_attribute_and_control_reset(self):
        attack=source_method(self.packet,'server/event/CommonEvents','livingAttack')['instructions']
        self.assertEqual(sum('getDirectEntity()' in str(i['operand']) for i in attack),2)
        self.assertFalse(any('DamageSource.getEntity()' in str(i['operand']) for i in attack))
        self.assertFalse(any('AbstractArrow.getOwner' in str(i['operand']) for i in attack))
        self.assertEqual(sum('setCanceled' in str(i['operand']) for i in attack),1)
        self.assertFalse(any('.hurt(' in str(i['operand']) for i in attack))
        v=read_json(OUT/'vanilla-evidence/alexscaves-status-lifecycle.json')
        mob=next(w for w in v['classes'] if w['class_name']=='net/minecraft/world/entity/Mob')
        self.assertTrue(any('updateControlFlags()' in str(i['operand']) for m in mob['methods'] if m['name']=='tick' for i in m['instructions']))
        flags=next(m for m in mob['methods'] if m['name']=='updateControlFlags')['instructions']
        self.assertEqual(sum('GoalSelector.setControlFlag' in str(i['operand']) for i in flags),3)
        template=next(w for w in v['classes'] if w['class_name'].endswith('$AttributeTemplate'))
        ops=[i['opcode'] for i in template['methods'][0]['instructions']]
        self.assertIn('0x60',ops);self.assertIn('0x6b',ops)

    def test_legacy_empty_cure_lists_do_not_prove_active_cure_immunity(self):
        for m in self.census['methods']:
            self.assertFalse(any('.getCurativeItems(' in i['operand'] for i in decode_sites(self.census,m,'calls')))
        self.assertFalse(any('getCurativeItems' in str(b['arguments']) for b in self.census['registration_bootstraps']))
        v=read_json(OUT/'vanilla-evidence/alexscaves-status-lifecycle.json')
        effect=next(w for w in v['classes'] if w['class_name']=='net/minecraft/world/effect/MobEffect')
        self.assertNotIn('getCurativeItems',{m['name'] for m in effect['declared_methods']})
        loader=read_json(OUT/'reference-evidence/cataclysm-ghost-fear-244.json')
        fill=next(w for w in loader['witnesses'] if w['entry'].endswith('/IMobEffectExtension.class'))
        self.assertEqual(fill['methods'][0]['name'],'fillEffectCures')
        self.assertTrue(any('EffectCures.DEFAULT_CURES' in str(i['operand']) for i in fill['methods'][0]['instructions']))

    def test_partial_callbacks_remain_pending_despite_full_capture(self):
        review=empty_review('alexscaves');review['effects']=self.batch['effects'];review['paths']=self.batch['paths'];review['reviewed_batches']=[FILE]
        index,pending=reconcile(review,self.census)
        keys={(m['entry'],m['method']) for m in pending}
        for short,name in [('server/event/CommonEvents','livingTick'),('server/potion/ACEffectRegistry','<clinit>'),('AlexsCaves','<init>')]:
            self.assertIn((PREFIX+short+'.class',name),keys)
        self.assertFalse(index['whole_mod_complete'])

    def test_wrong_native_coefficients_and_computed_formula_are_rejected(self):
        for id,primitive,parameter in [('alexscaves:bubbled','FORCED_MOVEMENT','x_factor'),('alexscaves:stunned','ATTRIBUTE_MODIFIER','movement_speed_coefficient'),('alexscaves:irradiated','EFFECT_TICK_CADENCE','cadence_numerator'),('alexscaves:irradiated','FOOD_EXHAUSTION','amount'),('alexscaves:bubbled','NATIVE_DAMAGE_REQUEST','requested_damage')]:
            batch=copy.deepcopy(self.batch);r=next(r for r in batch['effects'] if r['id']==id)
            next(c for c in r['components'] if c['primitive']==primitive)['numerical_parameters'][parameter]+=0.1
            with self.assertRaises(AssertionError):validate_batch(batch,empty_review('alexscaves'),self.census)
        rows=copy.deepcopy(self.batch['effects'])
        r=next(r for r in rows if r['id']=='alexscaves:irradiated')
        r['components'][0]['parameter_formulas']['requested_damage']='always1'
        with self.assertRaises(AssertionError):validate_radiation_formula(rows,self.packet)

    def test_regeneration_is_byte_identical(self):
        import json
        from assemble_alexscaves_status_foundation import build
        generated=(json.dumps(build(),ensure_ascii=False,indent=2)+'\n').encode()
        self.assertEqual(generated,(OUT/FILE).read_bytes())


if __name__=='__main__':unittest.main()
