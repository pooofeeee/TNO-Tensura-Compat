"""Pinned control/ownership, dead port fields and literal native consumer checks."""
import unittest
from catalog_common import OUT,read_json
from assemble_authored_contracts import render
from promote_combat_batch import validate_batch
from audit_numeric_labels import audit

P='com/github/alexthe666/alexsmobs/'
F='native-evidence/alexsmobs-item-combat.json'
def method(cls,name,file=F):
    w=next(w for w in read_json(OUT/file)['witnesses'] if w['entry']==P+cls+'.class')
    return next(m for m in w['methods'] if m['name']==name)


class AlexMobsTetherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.batch=read_json(OUT/'alexsmobs-r2o3b-tether-portal-controls.json')

    def test_renderer_and_all_native_inputs(self):
        self.assertEqual(render(read_json(OUT/'native-specifications/alexsmobs-tether-contracts.json')),self.batch)
        prior=read_json(OUT/'mod-reviews/alexsmobs.json');ids={r['id'] for r in self.batch['effects']}
        prior['effects']=[r for r in prior['effects'] if r['id'] not in ids]
        prior['paths']=[r for r in prior['paths'] if not set(r['effect_ids'])&ids]
        validate_batch(self.batch,prior,read_json(OUT/'alexsmobs-combat-census.json'))
        self.assertEqual(audit(dict(effects=self.batch['effects']))['native_candidate_identities'],54)
        self.assertFalse(self.batch['stage_policy_decided'])

    def test_lasso_has_real_native_source_fallback(self):
        ins=method('entity/EntityVineLasso','onEntityHit')['instructions']
        self.assertTrue(any('ServerLifecycleHooks.getCurrentServer' in str(i['operand']) for i in ins))
        self.assertTrue(any('.getNearestPlayer(' in str(i['operand']) for i in ins))
        self.assertEqual(next(i['operand'] for i in ins if i['offset']==73),64.0)
        self.assertLess(next(i['offset'] for i in ins if 'getNearestPlayer' in str(i['operand'])),next(i['offset'] for i in ins if '.lassoTo(' in str(i['operand'])))
        self.assertFalse(any('.hurt(' in str(i['operand']) for i in ins))

    def test_vanilla_pick_and_level_clip_are_block_traces(self):
        doc=read_json(OUT/'vanilla-evidence/alexsmobs-tether-native-dispatch.json')
        root=next(w for w in doc['classes'] if w['class_name'].endswith('/Entity'))
        ins=root['methods'][0]['instructions']
        self.assertTrue(any(i['opcode']=='0xb6' and str(i['operand']).endswith('(Lnet/minecraft/world/level/ClipContext;)Lnet/minecraft/world/phys/BlockHitResult;') for i in ins))
        for cls in ['Player','LivingEntity']:
            w=next(w for w in doc['classes'] if w['class_name'].endswith('/'+cls))
            self.assertNotIn('pick',[m['name'] for m in w['declared_methods']])
        loader=read_json(OUT/'reference-evidence/alexsmobs-tether-native-loader.json')
        patch=next(w for w in loader['witnesses'] if w['entry'].endswith('/Entity.java.patch'))
        self.assertNotIn(' pick(',patch['text'])

    def test_private_legacy_modifier_maps_have_no_native_reader(self):
        index=read_json(OUT/'alexsmobs-native-field-use-index.json')
        for cls,field in [('ItemTendonWhip','tendonModifiers'),('ItemSkelewagSword','skelewagModifiers')]:
            matches=[n for n,s in enumerate(index['symbols']) if s.startswith(P+'item/'+cls+'.'+field)]
            self.assertEqual(len(matches),1)
            sites=[(m['method'],i) for m in index['methods'] for i in m['field_sites'] if i[2]==matches[0]]
            self.assertEqual([(name,i[1]) for name,i in sites],[('<init>',181)])

    def test_tendon_attribute_value_is_compared_to_holder_and_hurt_does_not_gate_chain(self):
        ins=method('entity/EntityTendonSegment','getDamageForItem')['instructions']
        at=next(n for n,i in enumerate(ins) if i['offset']==61)
        self.assertEqual(ins[at]['operand'],'net/minecraft/core/Holder.value()Ljava/lang/Object;')
        self.assertTrue(ins[at+1]['operand'].endswith('Attributes.ATTACK_DAMAGELnet/minecraft/core/Holder;'))
        self.assertEqual(ins[at+2]['opcode'],'0xa6')
        v=read_json(OUT/'vanilla-evidence/alexsmobs-tether-native-dispatch.json')
        for cls in ['Attribute','RangedAttribute']:
            w=next(w for w in v['classes'] if w['class_name'].endswith('/'+cls))
            self.assertNotIn('net/minecraft/core/Holder',w['interfaces'])
        tick=method('entity/EntityTendonSegment','tick')['instructions']
        touched=next(i['offset'] for i in tick if i['opcode']=='0xb5' and '.hasTouchedZ' in str(i['operand']))
        hurt=next(i['offset'] for i in tick if '.hurt(' in str(i['operand']))
        chain=next(i['offset'] for i in tick if '.createChain(' in str(i['operand']))
        self.assertLess(touched,hurt);self.assertGreater(chain,hurt)
        # The hurt true/false outcomes converge without a write before chaining.
        at=next(n for n,i in enumerate(tick) if i['offset']==hurt)
        self.assertEqual(tick[at+1]['branch_target'],tick[at+2]['offset'])

    def test_grapple_nbt_callbacks_are_not_conventional_owner_persistence(self):
        load=method('entity/EntitySquidGrapple','readAdditionalSaveData')['instructions']
        save=method('entity/EntitySquidGrapple','addAdditionalSaveData')['instructions']
        self.assertTrue(any('.putUUID(' in str(i['operand']) for i in load))
        self.assertFalse(any('.getUUID(' in str(i['operand']) for i in load))
        self.assertTrue(any('.getUUID(' in str(i['operand']) for i in save))
        self.assertFalse(any('.putUUID(' in str(i['operand']) for i in save))
        tick=method('entity/EntitySquidGrapple','tick')['instructions']
        self.assertFalse(any('.hurt(' in str(i['operand']) for i in tick))
        self.assertTrue(any('.fallDistanceF' in str(i['operand']) and i['opcode']=='0xb5' for i in tick))

    def test_portal_clear_is_one_native_block_and_transport_has_no_damage(self):
        clear=method('entity/EntityVoidPortal','clearObstructions')['instructions']
        self.assertEqual(sum('.destroyBlock(' in str(i['operand']) for i in clear),1)
        loops=[i for i in clear if i['opcode']=='0xa3']
        self.assertEqual(len(loops),3)
        for branch in loops:
            n=clear.index(branch);self.assertEqual(clear[n-1]['operand'],-1)
        tick=method('entity/EntityVoidPortal','tick')['instructions']
        self.assertFalse(any('.hurt(' in str(i['operand']) or '.addEffect(' in str(i['operand']) for i in tick))
        self.assertTrue(any('VOID_PORTAL_IGNORES' in str(i['operand']) for i in tick))
        self.assertTrue(any('.getParts()' in str(i['operand']) for i in tick))

    def test_elytra_callbacks_are_real_patched_native_flight_dispatch(self):
        doc=read_json(OUT/'reference-evidence/alexsmobs-tether-native-loader.json')
        patch=next(w for w in doc['witnesses'] if w['entry'].endswith('/LivingEntity.java.patch'))
        text=''.join(s['text'] for s in patch['text_sections'])
        self.assertIn('itemstack.canElytraFly(this) && itemstack.elytraFlightTick(this, this.fallFlyTicks)',text)
        ins=method('item/ItemTarantulaHawkElytra','elytraFlightTick')['instructions']
        self.assertTrue(any('EquipmentSlot.CHEST' in str(i['operand']) for i in ins))
        self.assertEqual(ins[-2]['operand'],1)


if __name__=='__main__':unittest.main()
