"""Residual helper dispatch, hatching and exact existing-mechanic reuse."""
import unittest
from assemble_authored_contracts import render
from catalog_common import OUT,read_json
from promote_combat_batch import validate_batch
P='com/github/alexthe666/alexsmobs/'
RAW=read_json(OUT/'native-evidence/alexsmobs-remaining-actors.json')
def method(cls,name,desc=None):return next(m for w in RAW['witnesses'] if w['entry']==P+cls+'.class' for m in w['methods'] if m['name']==name and (not desc or m['descriptor']==desc))
def calls(b,s):return [i for i in b if s in str(i['operand'])]
class ResidualActors(unittest.TestCase):
    def test_exact_render_and_validation(self):
        b=read_json(OUT/'alexsmobs-r2od-residual-actors.json');self.assertEqual(render(read_json(OUT/'native-specifications/alexsmobs-residual-actor-contracts.json')),b)
        r=read_json(OUT/'mod-reviews/alexsmobs.json');ids={e['id'] for e in b['effects']};r['effects']=[e for e in r['effects'] if e['id'] not in ids];r['paths']=[p for p in r['paths'] if not set(p['effect_ids'])&ids];validate_batch(b,r,read_json(OUT/'alexsmobs-combat-census.json'))
    def test_cockroach_hatches_after_base_hit_without_damage(self):
        b=method('entity/EntityCockroachEgg','onHit')['instructions'];self.assertEqual(b[2]['opcode'],'0xb7');self.assertTrue(calls(b,'.finalizeSpawn('));self.assertTrue(calls(b,'.restrictTo('));self.assertEqual(len(calls(b,'.broadcastEntityEvent(')),2);self.assertFalse(calls(b,'.hurt('));self.assertFalse(calls(b,'.setOwnerUUID('))
    def test_emu_hatching_does_not_finalize_or_restrict_offspring(self):
        b=method('entity/EntityEmuEgg','onHit')['instructions'];self.assertTrue(calls(b,'.setAge('));self.assertFalse(calls(b,'.finalizeSpawn('));self.assertFalse(calls(b,'.restrictTo('));self.assertFalse(calls(b,'.hurt('))
    def test_current_egg_parent_entity_hit_is_empty(self):
        v=read_json(OUT/'vanilla-evidence/alexsmobs-egg-hit-dispatch.json')
        for c in v['classes']:
            if not c['class_name'].endswith('/Projectile'):self.assertFalse([m for m in c['declared_methods'] if m['name']=='onHitEntity'])
        b=next(m for c in v['classes'] for m in c['methods'] if m['name']=='onHitEntity')['instructions'];self.assertEqual([i['opcode'] for i in b],['0xb1'])
    def test_five_owner_search_predicates_exactly_reuse_one_body(self):
        bodies=[method('entity/'+c,'lambda$checkLeftOwner$0')['instructions'] for c in ['EntityFart','EntityHemolymph','EntityMosquitoSpit','EntitySandShot','EntityVineLasso']]
        self.assertTrue(all(b==bodies[0] for b in bodies));self.assertFalse(calls(bodies[0],'.isAlive('));self.assertTrue(calls(bodies[0],'.isPickable('))
    def test_unused_fluid_leave_constructor_and_neck_solver_have_no_native_callers(self):
        c=read_json(OUT/'alexsmobs-combat-census.json');symbols={c['symbols'][s[2]] for m in c['methods'] for s in m['calls']};self.assertFalse([s for s in symbols if 'AnimalAILeaveWaterLava.<init>' in s]);self.assertFalse([s for s in symbols if 'LaviathanNeckSolver.' in s])
    def test_mimic_predicate_precedence_matches_existing_contract(self):
        b=method('entity/EntityMimicOctopus$AIFlee$1','apply','(Lnet/minecraft/world/entity/Entity;)Z')['instructions'];self.assertTrue(calls(b,'MIMIC_OCTOPUS_FEARS'));self.assertTrue(calls(b,'.isCreative('));a=calls(b,'.isAlive(')[0];self.assertEqual(b[b.index(a)+1]['branch_target'],20);self.assertEqual(next(i for i in b if i['offset']==21)['operand'],'net/minecraft/world/entity/player/Player')
    def test_node_neighbors_use_volume_admission_and_empty_fluid_cost(self):
        b=method('entity/ai/BoneSerpentNodeProcessor','getNeighbors')['instructions'];self.assertTrue(calls(b,'Direction.values'));self.assertTrue(calls(b,'.getWaterNode('));b=method('entity/ai/BoneSerpentNodeProcessor','getNode')['instructions'];self.assertTrue(calls(b,'.getPathfindingMalus('));self.assertEqual(next(i['operand'] for i in b if i['offset']==102),8.0)
if __name__=='__main__':unittest.main()
