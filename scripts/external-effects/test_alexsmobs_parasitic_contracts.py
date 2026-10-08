"""Pinned feeding acceptance, side gates, forced riding and native status ordering."""
import unittest
from assemble_authored_contracts import render
from audit_numeric_labels import audit
from catalog_common import OUT,read_json
from promote_combat_batch import validate_batch
P='com/github/alexthe666/alexsmobs/'
RAW=read_json(OUT/'native-evidence/alexsmobs-remaining-actors.json')
def method(cls,name):return next(m for w in RAW['witnesses'] if w['entry']==P+cls+'.class' for m in w['methods'] if m['name']==name)
def calls(b,s):return [i for i in b if s in str(i['operand'])]
class ParasiticContracts(unittest.TestCase):
    def test_exact_render_validation_and_numeric_labels(self):
        b=read_json(OUT/'alexsmobs-r2o9-parasitic-flying.json');self.assertEqual(render(read_json(OUT/'native-specifications/alexsmobs-parasitic-flying-contracts.json')),b)
        r=read_json(OUT/'mod-reviews/alexsmobs.json');ids={e['id'] for e in b['effects']};r['effects']=[e for e in r['effects'] if e['id'] not in ids];r['paths']=[p for p in r['paths'] if not set(p['effect_ids'])&ids]
        validate_batch(b,r,read_json(OUT/'alexsmobs-combat-census.json'));self.assertEqual(audit(dict(effects=b['effects']))['unresolved_numeric_labels'],0)
    def test_mosquito_feeding_gates_blood_and_mungus_disable_on_hurt(self):
        b=method('entity/EntityCrimsonMosquito','rideTick')['instructions'];h=calls(b,'.hurt(')[0];n=b.index(h)
        self.assertEqual(b[n+1]['opcode'],'0x99');end=b[n+1]['branch_target'];self.assertTrue(all(h['offset']<i['offset']<end for i in calls(b,'.disableExplosion(')+calls(b,'.setBloodLevel(')))
    def test_mosquito_spit_consumes_blood_before_spawn(self):
        b=method('entity/EntityCrimsonMosquito','spit')['instructions'];self.assertLess(calls(b,'.setBloodLevel(')[0]['offset'],calls(b,'.addFreshEntity(')[0]['offset'])
    def test_mosquito_landing_delta_add_is_discarded(self):
        b=method('entity/EntityCrimsonMosquito','tick')['instructions'];i=next(i for i in b if i['offset']>900 and 'Vec3.add(' in str(i['operand']));self.assertEqual(b[b.index(i)+1]['opcode'],'0x57')
    def test_warped_mosco_knockback_reads_actor_resistance(self):
        b=method('entity/EntityWarpedMosco','knockbackRidiculous')['instructions'];h=calls(b,'.getAttributeValue(')[0];n=b.index(h);self.assertEqual(b[n-2].get('local_index'),0);self.assertIn('KNOCKBACK_RESISTANCE',b[n-1]['operand'])
    def test_warped_mosco_riding_status_precedes_damage(self):
        b=method('entity/EntityWarpedMosco','positionRider')['instructions'];self.assertLess(calls(b,'.addEffect(')[0]['offset'],calls(b,'.hurt(')[0]['offset']);self.assertFalse(calls(b,'isClientSide'))
    def test_hawk_melee_result_does_not_gate_sting(self):
        b=method('entity/EntityTarantulaHawk$AIMelee','tick')['instructions'];h=calls(b,'.doHurtTarget(')[0];self.assertEqual(b[b.index(h)+1]['opcode'],'0x57');self.assertLess(h['offset'],calls(b,'.heal(')[0]['offset']);self.assertLess(calls(b,'.heal(')[0]['offset'],calls(b,'.addEffect(')[0]['offset'])
    def test_bury_sets_physics_but_stop_does_not_reset_recipient(self):
        b=method('entity/EntityTarantulaHawk$AIBury','tick')['instructions'];self.assertTrue(calls(b,'.noPhysicsZ'));self.assertTrue(calls(b,'.ejectPassengers('));self.assertFalse(calls(method('entity/EntityTarantulaHawk$AIBury','stop')['instructions'],'.noPhysicsZ'))
    def test_hawk_drag_timeout_requires_empty_passenger_list(self):
        b=method('entity/EntityTarantulaHawk','tick')['instructions'];h=calls(b,'.hurt(')[0];empty=calls(b,'List.isEmpty(')[0];self.assertLess(empty['offset'],h['offset']);self.assertEqual(b[b.index(empty)+1]['opcode'],'0x99')
    def test_phage_low_health_branch_bypasses_hurt(self):
        b=method('entity/EntityEnderiophage','rideTick')['instructions'];h=calls(b,'.hurt(')[0];jump=next(i for i in b if i['offset']>304 and i['offset']<h['offset'] and i['opcode']=='0x9b');self.assertGreater(jump['branch_target'],h['offset'])
    def test_phage_infection_removal_precedes_new_effect(self):
        b=method('entity/EntityEnderiophage','rideTick')['instructions'];r=calls(b,'.removeEffect(')[0];e=calls(b,'.addEffect(')[-1];self.assertLess(r['offset'],e['offset']);self.assertTrue(calls(b,'Math.min('))
if __name__=='__main__':unittest.main()
