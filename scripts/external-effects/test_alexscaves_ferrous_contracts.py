"""Native source, return ordering, aliases and original parameter checks."""
import copy
import unittest
from catalog_common import OUT,read_json
from assemble_authored_contracts import render
from promote_combat_batch import validate_batch

P='com/github/alexmodguy/alexscaves/'


def method(short,name,scope='ferrous-actors'):
    packet=read_json(OUT/f'native-evidence/alexscaves-{scope}.json')
    w=next(w for w in packet['witnesses'] if w['entry']==P+short+'.class')
    return next(m for m in w['methods'] if m['name']==name)


def body(short,name,scope='ferrous-actors'):
    return method(short,name,scope)['instructions']


class FerrousContractsTests(unittest.TestCase):
    def test_authored_batch_regenerates_without_duplicate_native_parameters(self):
        b=read_json(OUT/'alexscaves-r2m8h-ferrous-contracts.json')
        self.assertEqual(render(read_json(OUT/'native-findings/alexscaves-ferrous-contracts.json')),b)
        r=copy.deepcopy(read_json(OUT/'mod-reviews/alexscaves.json'));ids={e['id'] for e in b['effects']}
        r['effects']=[e for e in r['effects'] if e['id'] not in ids]
        r['paths']=[e for e in r['paths'] if not set(e['effect_ids'])&ids]
        result=validate_batch(b,r,read_json(OUT/'alexscaves-combat-census.json'))
        self.assertEqual(result['semantic_records'],len(r['effects'])+15)
        self.assertEqual(sum(len(c['parameters']) for e in b['effects'] for c in e['scalable_parameter_candidates']),15)

    def test_boundroid_raw_gravity_flag_has_no_finite_native_reader(self):
        fields=read_json(OUT/'alexscaves-native-field-use-index.json')
        symbol=P+'server/entity/living/BoundroidEntity.stopGravityZ'
        refs=[(m['entry'],m['method'],op) for m in fields['methods'] for offset,op,n in m['field_sites'] if fields['symbols'][n]==symbol]
        self.assertEqual(len(refs),3)
        self.assertTrue(all(op==0xb5 for entry,name,op in refs))
        self.assertIn('setNoGravity',str(body('server/entity/living/BoundroidWinchEntity','tick')))

    def test_winch_hurt_relay_is_original_source_amount_and_success_dependent(self):
        b=body('server/entity/living/BoundroidWinchEntity','hurt');at={i['offset']:i for i in b}
        self.assertIn('Entity.hurt',at[30]['operand'])
        call=next(n for n,i in enumerate(b) if i['offset']==30)
        self.assertEqual([b[call-2]['local_index'],b[call-1]['local_index']],[1,2])
        self.assertIn(60,[i['operand'] for i in b])
        self.assertTrue(any(i['opcode']=='0x99' and i['offset']>30 for i in b))
        self.assertIn('Monster.hurt',at[64]['operand'])

    def test_ferrouslime_delayed_formula_is_not_the_clamped_attribute(self):
        b=body('server/entity/living/FerrouslimeEntity','tick');at={i['offset']:i for i in b}
        self.assertIn('AttributeInstance.setBaseValue',at[113]['operand'])
        self.assertEqual(at[289]['operand'],2);self.assertEqual(at[290]['opcode'],'0x68')
        self.assertEqual(at[291]['opcode'],'0x86');self.assertEqual(at[292]['opcode'],'0x62')
        self.assertIn('LivingEntity.hurt',at[293]['operand']);self.assertEqual(at[296]['opcode'],'0x57')
        immediate=body('server/entity/living/FerrouslimeEntity','doHurtTarget')
        self.assertTrue(any(i['opcode']=='0xb7' and '.doHurtTarget' in str(i['operand']) for i in immediate))
        split=body('server/entity/living/FerrouslimeEntity','split')
        self.assertIn(1200,[i['operand'] for i in split])
        self.assertFalse(any(i.get('local_index')==1 and i['opcode'] in ('0x15','0x1b') for i in split))

    def test_magnetron_native_left_hand_alias_and_explicit_addends(self):
        short='server/entity/living/MagnetronEntity$MeleeGoal'
        for name in ('dealDamage','getPoseForHand'):
            b=body(short,name);calls=[n for n,i in enumerate(b) if '.getHandDamageValueAdd(' in str(i['operand'])]
            self.assertEqual(len(calls),2)
            self.assertTrue(all(b[n-1]['operand']==1 and b[n-1]['opcode']=='0x4' for n in calls))
        b=body(short,'getHandDamageValueAdd');at={i['offset']:i for i in b}
        self.assertEqual([at[o]['operand'] for o in (16,29,41,43)],[6,4,2,0])
        launch=body(short,'launch')
        self.assertIn('Entity.push',str(launch));self.assertNotIn('.knockback(',str(launch))

    def test_magnetic_weapon_ignition_hurt_wear_and_credit_are_not_reordered(self):
        short='server/entity/item/MagneticWeaponEntity'
        b=body(short,'hurtEntity','ferrous-payload');at={i['offset']:i for i in b}
        self.assertIn('igniteForSeconds',at[124]['operand']);self.assertIn('.hurt(',at[138]['operand'])
        hurt_index=next(n for n,i in enumerate(b) if i['offset']==138)
        self.assertEqual(b[hurt_index+1]['opcode'],'0x99')
        self.assertIn('.knockback(',at[199]['operand']);self.assertIn('igniteForSeconds',at[231]['operand'])
        self.assertTrue(any('.hurtEnemy(' in str(i['operand']) and i['offset']>231 for i in b))
        modifiers=body(short,'getDamageForItem','ferrous-payload')
        self.assertIn('AttributeModifier.amount()',str(modifiers))
        self.assertNotIn('.operation(',str(modifiers));self.assertNotIn('.slot(',str(modifiers))

    def test_mine_sound_and_dampener_artifacts_do_not_gain_runtime_parameters(self):
        short='server/entity/util/MineExplosion'
        w=read_json(OUT/'native-evidence/alexscaves-ferrous-payload.json')
        witness=next(w for w in w['witnesses'] if w['entry']==P+short+'.class')
        self.assertFalse(any(i['opcode']=='0xb5' and '.underwaterSound' in str(i['operand'])
                             for m in witness['methods'] for i in m['instructions']))
        dampener=body(short,'getExplosionKnockbackAfterDampener','ferrous-payload')
        self.assertEqual([i['opcode'] for i in dampener],['0x27','0xaf'])
        explode=body(short,'explode','ferrous-payload')
        self.assertIn('ignoreExplosion',str(explode));self.assertNotIn('.isAlliedTo',str(explode))
        self.assertFalse(any('.damageCalculator' in str(i['operand']) for i in explode))

    def test_multipart_handler_uses_supplied_id_and_generic_damage_source(self):
        b=body('server/message/MultipartEntityMessage','lambda$handle$0','ferrous-links')
        self.assertIn('IPayloadContext.player()',str(b))
        self.assertNotIn('Player.getId()',str(b))
        self.assertIn('DamageSources.generic()',str(b))
        self.assertIn('Entity.isMultipartEntity()',str(b))
        self.assertIn(16.0,[i['operand'] for i in b])
        at={i['offset']:i for i in b};self.assertIn('Entity.hurt',at[129]['operand'])
        self.assertEqual(at[132]['opcode'],'0x57')

    def test_false_numeric_constructor_binding_is_rejected(self):
        b=copy.deepcopy(read_json(OUT/'alexscaves-r2m8h-ferrous-contracts.json'))
        r=copy.deepcopy(read_json(OUT/'mod-reviews/alexscaves.json'));ids={e['id'] for e in b['effects']}
        r['effects']=[e for e in r['effects'] if e['id'] not in ids]
        r['paths']=[e for e in r['paths'] if not set(e['effect_ids'])&ids]
        e=next(e for e in b['effects'] if e['id']=='alexscaves:mine_guardian_custom_explosion')
        e['scalable_parameter_candidates'][0]['native_literal_constructor_argument_binding']['native_value']=6.0
        with self.assertRaises(AssertionError):validate_batch(b,r,read_json(OUT/'alexscaves-combat-census.json'))

    def test_own_navigation_gate_does_not_prove_no_teleport_from_class_name(self):
        packet=read_json(OUT/'native-evidence/alexscaves-ferrous-navigation.json')
        witness=packet['witnesses'][0]
        self.assertEqual(witness['superclass'],
                         'com/github/alexthe666/citadel/server/entity/pathfinding/raycoms/AdvancedPathNavigate')
        gate=next(m for m in witness['methods'] if m['name']=='canUpdatePath')
        self.assertEqual([i['opcode'] for i in gate['instructions']],['0x4','0xac'])
        calls=[str(i['operand']) for m in witness['methods'] for i in m['instructions']]
        self.assertTrue(any('PathingStuckHandler.createStuckHandler()' in c for c in calls))
        self.assertFalse(any('.withTeleport' in c for c in calls))


if __name__=='__main__':unittest.main()
