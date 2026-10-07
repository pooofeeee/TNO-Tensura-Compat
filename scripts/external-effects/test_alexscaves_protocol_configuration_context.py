"""Exact packet directions, native gates and existing consumer identities."""
import unittest
from assemble_authored_contracts import render
from catalog_common import OUT,read_json
from promote_combat_batch import validate_batch

def body(cls,method):
 w=next(w for w in read_json(OUT/'native-evidence/alexscaves-remaining-protocol-setup.json')['witnesses'] if w['entry'].endswith('/'+cls+'.class'))
 return next(m['instructions'] for m in w['methods'] if m['name']==method)
def lambdas(cls):
 w=next(w for w in read_json(OUT/'native-evidence/alexscaves-remaining-protocol-setup.json')['witnesses'] if w['entry'].endswith('/'+cls+'.class'))
 return [m for m in w['methods'] if m['name'].startswith('lambda$handle')]

class ProtocolTests(unittest.TestCase):
 def test_render_and_native_bindings(self):
  b=read_json(OUT/'alexscaves-r2m8u-protocol-configuration-context.json')
  self.assertEqual(b,render(read_json(OUT/'native-findings/alexscaves-protocol-configuration-context.json')))
  self.assertEqual(validate_batch(b,read_json(OUT/'mod-reviews/alexscaves.json'),read_json(OUT/'alexscaves-combat-census.json'))['status'],'PASS')
 def test_actual_registration_directions(self):
  b=body('ACNetworking','register');self.assertEqual(sum('PayloadRegistrar.play' in str(i['operand']) for i in b),16)
  # Native registration order is separate from the manually authored findings.
  dirs=[i['operand'].split('PayloadRegistrar.')[1].split('(')[0] for i in b if 'PayloadRegistrar.play' in str(i['operand'])]
  self.assertEqual(dirs[:4],['playBidirectional']*3+['playToServer'])
 def test_beholder_rotation_handler_really_has_no_rotation_write(self):
  b=str(lambdas('BeholderRotateMessage'));self.assertIn('BeholderEyeEntity',b);self.assertNotIn('.setEyeXRot(',b);self.assertNotIn('.setEyeYRot(',b)
  b=str(body('ClientEvents','onClientTick'));self.assertIn('.setEyeXRot(',b);self.assertIn('.setEyeYRot(',b)
 def test_mounted_gate_is_distinct_from_armor_dispatch(self):
  self.assertIn('.isPassengerOfSameVehicle(',str(lambdas('MountedEntityKeyMessage')))
  b=str(lambdas('ArmorKeyMessage'));self.assertIn('Mth.clamp(',b);self.assertIn('.onKeyPacket(',b);self.assertNotIn('.isPassengerOfSameVehicle(',b)
 def test_item_tag_server_uses_context_player_not_message_entity(self):
  server=next(m for m in lambdas('UpdateItemTagMessage') if m['name'].startswith('lambda$handleServer'))
  self.assertNotIn('.getEntity(',str(server['instructions']));self.assertIn('IPayloadContext.player(',str(server['instructions']))
  self.assertIn('.getEntity(',str(next(m for m in lambdas('UpdateItemTagMessage') if m['name'].startswith('lambda$handleClient'))))
 def test_client_world_event_does_not_dispatch_an_explosion(self):
  b=str(body('ClientProxy','playWorldEvent'));self.assertIn('resetSlideAnimation(',b);self.assertNotIn('.explode(',b);self.assertNotIn('.hurt(',b)
 def test_item_registry_has_one_current_attribute_supplier(self):
  p=read_json(OUT/'native-evidence/alexscaves-item-consumers.json');w=next(w for w in p['witnesses'] if w['entry'].endswith('/ACItemRegistry.class'))
  ms=[m for m in w['methods'] if 'Item$Properties.attributes(' in str(m['instructions'])]
  self.assertEqual(len(ms),1);self.assertIn('PrimitiveClubItem.createAttributes',str(ms[0]['instructions']))

if __name__=='__main__':unittest.main()
