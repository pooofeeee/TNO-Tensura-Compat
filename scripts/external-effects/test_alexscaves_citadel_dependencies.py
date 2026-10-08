"""Exact dependency bodies, configured hook admission, and closure regressions."""
import copy
import unittest
from catalog_common import OUT, read_json
from validate_current_integrity import validate_external_dependency_contracts

FILE='native-evidence/citadel-alexscaves-dependencies.json'
PREFIX='com/github/alexthe666/citadel/'


def witness(root):
    return next(w for w in read_json(OUT/FILE)['witnesses'] if w['entry']==PREFIX+root+'.class')


def method(root,name,descriptor=None):
    return next(m for m in witness(root)['methods'] if m['name']==name and (descriptor is None or m['descriptor']==descriptor))


def symbols(m):
    return [str(i['operand']) for i in m['instructions'] if i.get('operand') is not None]


class CitadelDependencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.review=read_json(OUT/'mod-reviews/alexscaves.json')
        cls.census=read_json(OUT/'alexscaves-combat-census.json')
        cls.dep=read_json(OUT/'alexscaves-citadel-dependency-obligations.json')

    def test_exact_five_pinned_contracts_and_reciprocal_callers(self):
        expected={'sugar_rush_tick_controller','selective_actor_collision','actor_animation_clock',
                  'delegated_combat_navigation','radioactive_item_parent_tick'}
        self.assertEqual({o['id'].rsplit(':',1)[1] for o in self.dep['obligations']},expected)
        self.assertEqual(validate_external_dependency_contracts(self.review,self.census)['resolved_dependency_groups'],5)
        self.assertEqual(self.dep['artifact']['exact_installed_version'],'2.7.6')
        self.assertEqual(self.dep['artifact']['sha256'],'9e12468c49e5a95b7adbf22b3b4d05bc55565989b89c40b985cd73bdfe63c3c2')

    def test_unproven_pin_status_body_or_native_caller_is_rejected(self):
        for mutate in [
            lambda d:d['artifact'].update(sha256='0'*64),
            lambda d:d['obligations'][0].update(status='BLOCKED'),
            lambda d:d['obligations'][0].update(evidence=[]),
            lambda d:d['obligations'][0]['native_boundary_calls'][0]['sites'][0].update(offset=-1),
        ]:
            with self.subTest(mutate=mutate):
                dep=copy.deepcopy(self.dep);mutate(dep)
                with self.assertRaises(AssertionError):validate_external_dependency_contracts(self.review,self.census,dep)

    def test_local_radius_is_strict_and_not_dimension_admission(self):
        m=method('server/tick/modifier/LocalTickRateModifier','appliesTo');body={i['offset']:i for i in m['instructions']}
        self.assertIn('distanceToSqr',body[14]['operand'])
        self.assertEqual((body[26]['opcode'],body[27]['opcode'],body[27]['branch_target']),('0x98','0x9c',34))
        self.assertFalse(any('.dimension' in s for s in symbols(m)))
        tag=method('server/tick/modifier/LocalTickRateModifier','<init>','(Lnet/minecraft/nbt/CompoundTag;)V')
        self.assertEqual([s for s in symbols(tag) if s in ['Dimension','dimension']],['Dimension','dimension'])
        valid=symbols(method('server/tick/modifier/LocalEntityTickRateModifier','isEntityValid'))
        for name in ['isAddedToLevel','getType','isAlive','isTimeModificationValid']:
            self.assertTrue(any(name in s for s in valid))

    def test_expiry_uses_reciprocal_multiplier_and_master_clock(self):
        body={i['offset']:i for i in method('server/tick/modifier/TickRateModifier','doRemove')['instructions']}
        self.assertEqual((body[23]['operand'],body[28]['opcode'],body[39]['opcode']),(1.0,'0x6e','0x6a'))
        self.assertEqual((body[41]['opcode'],body[41]['branch_target']),('0x9b',48))
        master=symbols(method('server/tick/TickRateTracker','masterTick'))
        self.assertTrue(any('.masterTick()' in s for s in master))
        self.assertTrue(any('removeIf' in s for s in master))
        setter=method('server/tick/modifier/TickRateModifier','setMaxDuration')
        self.assertEqual(len(setter['instructions']),4)
        self.assertIn('.maxDuration',symbols(setter)[0])

    def test_server_and_client_rate_queries_are_distinct(self):
        server=symbols(method('server/tick/ServerTickRateTracker','getServerTickLengthMs'))
        self.assertTrue(any('TickRateModifierType.GLOBAL' in s for s in server))
        self.assertFalse(any('.appliesTo' in s for s in server))
        client=symbols(method('client/tick/ClientTickRateTracker','getClientTickRate'))
        self.assertTrue(any('.appliesTo' in s for s in client))
        self.assertTrue(any('.getEntityTickLengthModifier' in s for s in client))
        self.assertEqual(sum(i['opcode']=='0x6a' for i in method('client/tick/ClientTickRateTracker','getClientTickRate')['instructions']),2)

    def test_unconfigured_mixins_do_not_prove_active_tick_hooks(self):
        w=next(w for w in read_json(OUT/FILE)['witnesses'] if w['entry']=='citadel.mixins.json')
        self.assertEqual(w['data']['mixins'],['BlockBehaviourAccessor','NoiseGeneratorSettingsMixin','LivingEntityMixin'])
        self.assertEqual(w['data']['client'],[])
        self.assertIn('com/github/alexthe666/citadel/server/world/ModifiableTickRateServer',witness('mixin/MinecraftServerMixin')['interfaces'])
        body={i['offset']:i for i in method('server/CitadelEvents','onServerTick')['instructions']}
        self.assertEqual((body[29]['opcode'],body[32]['branch_target']),('0xc1',91))
        self.assertIn('.masterTick()',body[88]['operand'])
        self.assertTrue(method('ClientProxy','clientTick')['annotations'])

    def test_transport_is_clientbound_and_not_an_effect_copy(self):
        register=symbols(method('Citadel','registerPayloads'))
        self.assertTrue(any('SyncClientTickRateMessage.TYPE' in s for s in register))
        self.assertTrue(any('.playToClient(' in s for s in register))
        handler=symbols(method('server/message/SyncClientTickRateMessage','lambda$handle$0'))
        self.assertTrue(any('.isClientbound()' in s for s in handler))
        self.assertTrue(any('.handleClientTickRatePacket(' in s for s in handler))
        sync=symbols(method('client/tick/ClientTickRateTracker','syncFromServer'))
        self.assertTrue(any('.clear()' in s for s in sync));self.assertTrue(any('.fromTag(' in s for s in sync))

    def test_selective_collision_retains_native_actor_filter_and_other_shapes(self):
        helper=symbols(method('server/entity/collision/CustomCollisionsBlockCollisions','computeNext','()Lnet/minecraft/world/phys/shapes/VoxelShape;'))
        self.assertTrue(any('.canPassThrough(' in s for s in helper))
        solver=symbols(method('server/entity/collision/ICustomCollisions','collideBoundingBox2'))
        self.assertTrue(any('WorldBorder.getCollisionShape' in s for s in solver))
        root=symbols(method('server/entity/collision/ICustomCollisions','getAllowedMovementForEntity'))
        for name in ['getEntityCollisions','maxUpStep','collideBoundingBox2']:
            self.assertTrue(any(name in s for s in root))
        self.assertFalse(any('.hurt(' in s or '.destroyBlock(' in s for s in solver+helper+root))

    def test_animation_start_cancellation_does_not_cancel_clock_advance(self):
        body={i['offset']:i for i in method('animation/AnimationHandler','updateAnimations')['instructions']}
        self.assertEqual(body[87]['branch_target'],99)
        self.assertIn('.sendAnimationMessage(',body[96]['operand'])
        self.assertEqual((body[136]['operand'],body[137]['opcode']),(1,'0x60'))
        self.assertIn('.setAnimationTick(',body[138]['operand'])
        # The equality reset follows the Tick event, with no >= substitution.
        self.assertEqual(body[199]['opcode'],'0xa0')
        self.assertIn('.setAnimationTick(',body[207]['operand'])
        self.assertIn('.setAnimation(',body[219]['operand'])

    def test_animation_transport_resets_original_entity_clock(self):
        m=symbols(method('ClientProxy','handleAnimationPacket'))
        self.assertTrue(any('.getEntity(' in s for s in m))
        self.assertTrue(any('.getAnimations()' in s for s in m))
        self.assertTrue(any('.setAnimationTick(' in s for s in m))
        send=symbols(method('animation/AnimationHandler','sendAnimationMessage'))
        self.assertTrue(any('.isClientSide' in s for s in send))
        self.assertTrue(any('.sendToAllPlayers(' in s for s in send))

    def test_supplied_stuck_handler_disables_optional_teleport_damage_and_terrain(self):
        m=method('server/entity/pathfinding/raycoms/PathingStuckHandler','<init>')
        ins=m['instructions']
        fields=['teleportRangeI','canTeleportGoalZ','takeDamageOnCompleteStuckZ','completeStuckBlockBreakRangeI','canBreakBlocksZ','canPlaceLaddersZ','canBuildLeafBridgesZ']
        for field in fields:
            n=next(n for n,i in enumerate(ins) if str(i['operand']).endswith('.'+field))
            self.assertEqual(ins[n-1]['operand'],0,field)
        ctor=method('server/entity/pathfinding/raycoms/AdvancedPathNavigate','<init>')
        idx=next(n for n,i in enumerate(ctor['instructions']) if '.stuckHandler' in str(i['operand']))
        self.assertEqual(ctor['instructions'][idx-1]['local_index'],6)
        self.assertFalse(any('.withTeleport' in s or '.withBlock' in s for s in symbols(ctor)))

    def test_path_getter_does_not_compute_or_wait(self):
        m=method('server/entity/pathfinding/raycoms/PathResult','getPath')
        self.assertEqual([i['opcode'] for i in m['instructions']],['0x2a','0xb4','0xb0'])
        self.assertIn('.pathLnet/minecraft/world/level/pathfinder/Path;',symbols(m)[0])
        finish=symbols(method('server/entity/pathfinding/raycoms/PathResult','isFinished'))
        self.assertTrue(any('.isDone()' in s for s in finish))
        self.assertTrue(any('.processCalculationResults()' in s for s in finish))

    def test_radioactive_parent_tick_inherits_exact_vanilla_noop(self):
        w=witness('item/BlockItemWithSupplier')
        self.assertEqual(w['superclass'],'net/minecraft/world/item/BlockItem')
        self.assertNotIn('inventoryTick',w['declared_method_names'])
        raw=read_json(OUT/'vanilla-evidence/alexscaves-radioactive-parent-tick.json')
        item=next(c for c in raw['classes'] if c['class_name']=='net/minecraft/world/item/Item')
        block=next(c for c in raw['classes'] if c['class_name']=='net/minecraft/world/item/BlockItem')
        self.assertEqual(block['superclass'],item['class_name'])
        self.assertNotIn('inventoryTick',{m['name'] for m in block['declared_methods']})
        self.assertEqual(next(m for m in item['methods'] if m['name']=='inventoryTick')['code_hex'],'b1')


if __name__=='__main__':unittest.main()
