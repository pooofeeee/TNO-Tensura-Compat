"""Negative source-graph mutations; no package/name grants coverage by itself."""
import copy
import unittest
from native_context_graph import prove, external_allowed, validate


def fixture():
    e='example/client/model/Test.class';name=e[:-6]
    c=dict(mod_key='test',jar_sha256='pin',classes=[dict(entry=e,name=name,
        superclass='java/lang/Object',entry_sha256='class')],registration_bootstraps=[],
        symbols=['java/lang/Object.<init>()V',name+'.valueF',name+'.second()V',name+'.first()V',
                 'net/minecraft/world/entity/Entity.hurt(Lnet/minecraft/world/damagesource/DamageSource;F)Z'],
        methods=[dict(entry=e,method='first',descriptor='()V',access=1,
             code_sha256='first',hits=[],calls=[[0,182,2]]),
             dict(entry=e,method='second',descriptor='()V',access=1,
             code_sha256='second',hits=[],calls=[[0,182,3]])])
    return c


class ContextGraphTests(unittest.TestCase):
    def test_cycle_only_closes_with_independent_side_effect_proof(self):
        c=fixture();self.assertEqual(prove(c)['summary']['methods'],2)
        c['methods'][1]['calls'].append([3,182,4])
        self.assertEqual(prove(c)['summary']['methods'],0)

    def test_external_game_field_write_is_rejected_transitively(self):
        c=fixture();c['symbols'].append('net/minecraft/world/entity/Entity.fallDistanceF')
        c['methods'][1]['hits']=[[5,181,5]]
        self.assertEqual(prove(c)['summary']['methods'],0)

    def test_own_presentation_state_is_distinct_from_game_state(self):
        c=fixture();c['methods'][1]['hits']=[[5,181,1]]
        self.assertEqual(prove(c)['summary']['methods'],2)
        c['methods'][1]['access']=0x100
        self.assertEqual(prove(c)['summary']['methods'],0)

    def test_unknown_dispatch_and_time_controller_are_not_visual(self):
        for op in ('net/minecraft/world/entity/Entity.setXRot(F)V',
                   'net/minecraft/client/multiplayer/ClientLevel.setBlock()V',
                   'com/github/alexthe666/citadel/server/tick/ServerTickRateTracker.add()V',
                   'example/Mystery.getDamage()F'):
            self.assertFalse(external_allowed(op))
        self.assertTrue(external_allowed('net/minecraft/world/entity/Entity.getX()D'))

    def test_checked_game_reader_is_not_itself_dispositioned(self):
        c=fixture();e='example/server/Actor.class'
        c['classes'].append(dict(entry=e,name=e[:-6],superclass='java/lang/Object',entry_sha256='actor'))
        c['symbols'].append(e[:-6]+'.query()I')
        c['methods'].append(dict(entry=e,method='query',descriptor='()I',access=1,
            code_sha256='query',hits=[],calls=[]))
        c['methods'][0]['calls']=[[0,182,5]]
        rows=prove(c)['rows'];self.assertEqual(len(rows),2)
        self.assertFalse(any(r['entry']==e for r in rows))

    def test_typed_sound_return_only_in_explicit_new_profile(self):
        c=fixture();m=c['methods'][0];m['entry']='example/server/Actor.class'
        c['classes'].append(dict(entry=m['entry'],name=m['entry'][:-6],
            superclass='java/lang/Object',entry_sha256='actor'))
        m['descriptor']='()Lnet/minecraft/sounds/SoundEvent;';m['calls']=[]
        self.assertFalse(any(r['entry']==m['entry'] for r in prove(c)['rows']))
        self.assertTrue(any(r['entry']==m['entry'] for r in prove(c,'presentation-audio-ui-v2')['rows']))
        m['calls']=[[0,182,4]]  # hurt remains disallowed, even with sound return.
        self.assertFalse(any(r['entry']==m['entry'] for r in prove(c,'presentation-audio-ui-v2')['rows']))

    def test_new_audio_ui_roots_cannot_write_game_state(self):
        c=fixture();old=c['classes'][0]['name'];new='example/client/gui/Test'
        c['classes'][0].update(name=new,entry=new+'.class')
        c['symbols']=[s.replace(old,new) for s in c['symbols']]
        for m in c['methods']:m['entry']=new+'.class'
        self.assertEqual(prove(c,'presentation-audio-ui-v2')['summary']['methods'],2)
        c['symbols'].append('net/minecraft/world/entity/Entity.fallDistanceF')
        c['methods'][1]['hits']=[[5,181,5]]
        self.assertEqual(prove(c,'presentation-audio-ui-v2')['summary']['methods'],0)


if __name__=='__main__':unittest.main()

class NativeValueAndGenerationTests(unittest.TestCase):
    def value_fixture(self):
        c=fixture();m=c['methods'][0];m['descriptor']='()Lnet/minecraft/world/phys/shapes/VoxelShape;';m['calls']=[]
        return c
    def generation_fixture(self):
        c=fixture();old=c['classes'][0]['name'];new='example/server/level/feature/Layout'
        c['classes'][0].update(entry=new+'.class',name=new)
        c['symbols']=[s.replace(old,new) for s in c['symbols']]
        for m in c['methods']:m['entry']=new+'.class'
        return c
    def test_typed_value_is_retained_without_actor_mutation(self):
        c=self.value_fixture();self.assertEqual(prove(c,'native-value-metadata-v3')['summary']['methods'],1)
        c['methods'][0]['calls']=[[0,182,4]]
        self.assertEqual(prove(c,'native-value-metadata-v3')['summary']['methods'],0)
    def test_value_graph_rejects_collection_write_alias(self):
        c=self.value_fixture();c['symbols'].append('java/util/Map.put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;');c['methods'][0]['calls']=[[0,185,5]]
        self.assertEqual(prove(c,'native-value-metadata-v3')['summary']['methods'],0)
    def test_generation_own_layout_fields_are_allowed_not_actor_fields(self):
        c=self.generation_fixture();c['methods'][1]['hits']=[[0,181,1]]
        self.assertEqual(prove(c,'generation-layout-v4')['summary']['methods'],2)
        c['symbols'].append('net/minecraft/world/entity/Entity.fallDistanceF');c['methods'][1]['hits']=[[0,181,5]]
        self.assertEqual(prove(c,'generation-layout-v4')['summary']['methods'],0)
    def test_generation_package_does_not_hide_combat_or_opaque_placement(self):
        c=self.generation_fixture()
        for s in ['net/minecraft/world/level/WorldGenLevel.addFreshEntity(Lnet/minecraft/world/entity/Entity;)Z','net/minecraft/world/level/levelgen/feature/Feature.place()Z','example/server/block/Unknown.activate()V']:
            c['symbols'].append(s);c['methods'][1]['calls']=[[0,182,len(c['symbols'])-1]]
            self.assertEqual(prove(c,'generation-layout-v4')['summary']['methods'],0)
    def test_value_profile_cannot_mutate_render_or_network_state(self):
        self.assertFalse(external_allowed('net/minecraft/client/renderer/GameRenderer.setPostEffect(Ljava/lang/Object;)V','native-value-metadata-v3'))
        self.assertFalse(external_allowed('net/minecraft/network/Connection.send(Ljava/lang/Object;)V','native-value-metadata-v3'))
    def test_generation_terrain_write_does_not_authorize_block_entity_mutation(self):
        self.assertTrue(external_allowed('net/minecraft/world/level/WorldGenLevel.setBlock(Lnet/minecraft/core/BlockPos;Lnet/minecraft/world/level/block/state/BlockState;I)Z','generation-layout-v4'))
        self.assertFalse(external_allowed('net/minecraft/world/level/block/entity/SpawnerBlockEntity.setEntityId()V','generation-layout-v4'))

class NativeQueryTests(unittest.TestCase):
    def query(self):
        from catalog_common import byte_hash
        c=fixture();raw=bytes.fromhex('034fac')
        # A query writing an array alias must fail despite no field/call sites.
        m=c['methods'][0];m.update(descriptor='()I',calls=[],code_sha256=byte_hash(raw))
        key=(m['entry'],m['method'],m['descriptor'])
        return c,key,raw
    def test_complete_bytecode_rejects_array_alias_and_checks_operand_boundaries(self):
        from native_context_graph import opcode_read_only
        self.assertFalse(opcode_read_only(bytes.fromhex('034fac')))
        self.assertTrue(opcode_read_only(bytes.fromhex('104fac')))  # 0x4f is an operand, not IASTORE.
        self.assertFalse(opcode_read_only(bytes.fromhex('2ac2c303ac')))
    def test_query_context_requires_exact_hash_and_no_heap_mutation(self):
        from catalog_common import byte_hash
        c,k,raw=self.query();self.assertEqual(prove(c,'native-query-context-v5',{k:raw},{k})['summary']['methods'],0)
        safe=bytes.fromhex('104fac');c['methods'][0]['code_sha256']=byte_hash(safe)
        self.assertEqual(prove(c,'native-query-context-v5',{k:safe},{k})['summary']['methods'],1)
        self.assertEqual(prove(c,'native-query-context-v5',{k:raw},{k})['summary']['methods'],0)
        c['methods'][0]['access']|=0x20
        self.assertEqual(prove(c,'native-query-context-v5',{k:safe},{k})['summary']['methods'],0)
    def test_query_does_not_authorize_randomness_or_opaque_callbacks(self):
        for symbol in ('java/lang/Math.random()D','net/minecraft/util/Mth.wobble(D)D',
                       'net/minecraft/util/RandomSource.nextFloat()F',
                       'java/util/Optional.map(Ljava/util/function/Function;)Ljava/util/Optional;',
                       'java/lang/String.valueOf(Ljava/lang/Object;)Ljava/lang/String;',
                       'net/minecraft/world/phys/Vec3.offsetRandom(Lnet/minecraft/util/RandomSource;F)Lnet/minecraft/world/phys/Vec3;',
                       'net/minecraft/world/level/Level.addParticle()V'):
            self.assertFalse(external_allowed(symbol,'native-query-context-v5'),symbol)
        self.assertTrue(external_allowed('net/minecraft/world/entity/Entity.distanceToSqr(DDD)D','native-query-context-v5'))


class SelectedDisplayTests(unittest.TestCase):
    def test_complete_fields_reject_write_omitted_from_keyword_census(self):
        c=fixture();c['methods'][1]['hits']=[]
        methods=[dict(entry=m['entry'],method=m['method'],descriptor=m['descriptor'],
                      code_sha256=m['code_sha256']) for m in c['methods']]
        fields=dict(mod_key=c['mod_key'],jar_sha256=c['jar_sha256'],owner_scope='ALL_FIELD_OWNERS',
                    selection=methods,symbols=['net/minecraft/world/entity/Entity.yHeadRotF'],
                    methods=[dict(methods[1],field_sites=[[1,181,0]])])
        self.assertEqual(prove(c,'presentation-audio-ui-v2')['summary']['methods'],2)
        self.assertEqual(prove(c,'presentation-audio-ui-v2',field_index=fields)['rows'],[])
        fields.pop('owner_scope')
        with self.assertRaises(AssertionError):prove(c,'presentation-audio-ui-v2',field_index=fields)

    def test_exact_selection_does_not_grant_coverage_to_dependencies(self):
        c=fixture();m=c['methods'][0];key=(m['entry'],m['method'],m['descriptor'])
        doc=prove(c,'presentation-audio-ui-v2',selection={key})
        self.assertEqual(len(doc['rows']),1)
        self.assertEqual(doc['rows'][0]['method'],m['method'])
        validate(doc,c)
        self.assertEqual(prove(c,'presentation-audio-ui-v2',selection=set())['rows'],[])

    def test_display_api_extension_never_authorizes_game_writes_or_callbacks(self):
        for symbol in ('net/minecraft/client/gui/GuiGraphics.blit()V',
                       'net/minecraft/client/Minecraft.renderBuffers()Lnet/minecraft/client/renderer/RenderBuffers;',
                       'net/minecraft/world/level/block/entity/BlockEntity.getBlockPos()Lnet/minecraft/core/BlockPos;'):
            self.assertTrue(external_allowed(symbol,'presentation-access-v6'))
        for symbol in ('net/minecraft/world/entity/Entity.setYRot(F)V',
                       'net/minecraft/network/Connection.send(Ljava/lang/Object;)V',
                       'net/neoforged/bus/api/IEventBus.post(Ljava/lang/Object;)V',
                       'java/util/function/Consumer.accept(Ljava/lang/Object;)V'):
            self.assertFalse(external_allowed(symbol,'presentation-access-v6'))

    def test_display_body_rejects_hidden_array_alias_write(self):
        from catalog_common import byte_hash
        c=fixture();codes={}
        for m in c['methods']:
            raw=b'\xb1';m['code_sha256']=byte_hash(raw)
            codes[(m['entry'],m['method'],m['descriptor'])]=raw
        keys=set(codes)
        self.assertEqual(len(prove(c,'presentation-access-v6',codes,keys)['rows']),2)
        key=next(k for k in keys if k[1]==c['methods'][1]['method'])
        raw=bytes.fromhex('034fb1');codes[key]=raw;c['methods'][1]['code_sha256']=byte_hash(raw)
        self.assertEqual(prove(c,'presentation-access-v6',codes,keys)['rows'],[])
