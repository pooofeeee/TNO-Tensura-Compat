"""Exact native identity/direction/clone/storage assertions, not a schema snapshot."""
import copy
import unittest
from catalog_common import OUT,read_json
from promote_combat_batch import validate_batch,refined_review
from test_shadow_clone_contracts import NativeContractHarness


class NativeStateTransportTests(NativeContractHarness,unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m7a-native-state-transport.json')
        cls.native=read_json(OUT/'native-evidence/arphex-native-state-transport.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def body(self,name,method='execute'):
        name='ArphexModVariables$'+name if name!='ArphexMod' and name!='ArphexMod$NetworkMessage' else name
        return super().body(name,method)

    def test_native_contracts_refine_existing_identities_without_copied_scalars(self):
        prior=self.prior();after=refined_review(prior,self.batch)
        summary=validate_batch(self.batch,prior,self.census)
        self.assertEqual(summary['semantic_records'],462)
        self.assertEqual(summary['numeric_candidate_entries'],3903)
        self.assertEqual((len(self.native['witnesses']),sum(len(w['methods']) for w in self.native['witnesses'])),(9,66))
        self.assertFalse(self.batch['effects']);self.assertFalse(self.batch['paths'])
        self.assertTrue(all(not r.get('candidate_additions') for r in self.batch['record_refinements']))
        self.assertEqual([r['scalable_parameter_candidates'] for r in prior['effects']],
                         [r['scalable_parameter_candidates'] for r in after['effects']])

    def test_native_bidirectional_registration_is_not_serverbound_state_application(self):
        body=self.body('ArphexMod','lambda$registerNetworking$0')
        self.assertTrue(any('.playBidirectional(' in str(i['operand']) for i in body))
        for n in ('PlayerVariablesSyncMessage','SavedDataSyncMessage'):
            b=self.body(n,'handleData');by={i['offset']:i for i in b}
            self.assertIn('PacketFlow.CLIENTBOUND',by[6]['operand'])
            self.assertEqual((by[9]['opcode'],by[9]['branch_target']),('0xa6',42))
            self.assertEqual((by[16]['opcode'],by[16]['branch_target']),('0xc6',42))
            self.assertIn('.enqueueWork(',by[27]['operand'])
            self.assertEqual(by[42]['opcode'],'0xb1')

    def test_saved_data_storage_scopes_are_distinct_native_consumers(self):
        m=self.body('MapVariables','get');w=self.body('WorldVariables','get')
        self.assertTrue(any('ServerLevelAccessor'==str(i['operand']).split('/')[-1] for i in m))
        self.assertTrue(any('Level.OVERWORLD' in str(i['operand']) for i in m))
        self.assertTrue(any('MinecraftServer.getLevel(' in str(i['operand']) for i in m))
        self.assertFalse(any('OVERWORLD' in str(i['operand']) or 'MinecraftServer.getLevel(' in str(i['operand']) for i in w))
        self.assertTrue(any(i['operand']=='arphex_mapvars' for i in m))
        self.assertTrue(any(i['operand']=='arphex_worldvars' for i in w))
        for body,name in [(m,'MapVariables'),(w,'WorldVariables')]:
            self.assertIn(name+'.clientSide',body[-2]['operand']);self.assertEqual(body[-1]['opcode'],'0xb0')

    def test_dirty_and_sync_recipients_do_not_become_owner_or_damage_source(self):
        m=self.body('MapVariables','syncData');w=self.body('WorldVariables','syncData');p=self.body('PlayerVariables','syncPlayerVariables')
        self.assertIn('.setDirty()',m[1]['operand']);self.assertIn('.setDirty()',w[1]['operand'])
        self.assertTrue(any('.sendToAllPlayers(' in str(i['operand']) for i in m))
        self.assertTrue(any('.sendToPlayersInDimension(' in str(i['operand']) for i in w))
        self.assertTrue(any('.sendToPlayer(' in str(i['operand']) for i in p))
        self.assertTrue(any(i['opcode']=='0xc1' and i['operand']=='net/minecraft/server/level/ServerPlayer' for i in p))
        self.assertFalse(any('.sendToServer(' in str(i['operand']) for b in [m,w,p] for i in b))

    def test_clone_copies_original_fields_to_fresh_actual_event_entity(self):
        b=self.body('EventBusVariableHandlers','clonePlayer');by={i['offset']:i for i in b}
        self.assertIn('.getOriginal()',by[1]['operand']);self.assertIn('PlayerVariables.<init>()V',by[18]['operand'])
        self.assertIn('.isWasDeath()',by[247]['operand'])
        self.assertEqual((by[250]['opcode'],by[250]['branch_target']),('0x9a',613))
        always={i['operand'].split('.')[-1] for i in b if i['opcode']=='0xb5' and i['offset']<247}
        conditional={i['operand'].split('.')[-1] for i in b if i['opcode']=='0xb5' and i['offset']>247}
        self.assertEqual((len(always),len(conditional)),(28,45));self.assertFalse(always&conditional)
        self.assertTrue({'track_warp_cooldownD','inherent_power_cooldownD','power_shield_cooldownD','power_slam_cooldownD'}<=always)
        self.assertTrue({'holdingspaceZ','holdleftclickZ','sphere_nearD','laser_emitter_nearD','power_pressZ'}<=conditional)
        self.assertIn('.getEntity()',by[614]['operand']);self.assertEqual(by[620]['local_index'],2)
        self.assertIn('.setData(',by[621]['operand'])
        for j,i in enumerate(b):
            if i['opcode']=='0xb5':
                self.assertEqual(b[j-1]['opcode'],'0xb4');self.assertEqual(i['operand'],b[j-1]['operand'])
                self.assertEqual((b[j-3]['local_index'],b[j-2]['local_index']),(2,1))

    def test_every_serialized_field_roundtrips_the_same_exact_native_key_and_type(self):
        for name,read,write,count in [('MapVariables','read','save',58),('WorldVariables','read','save',1),('PlayerVariables','deserializeNBT','serializeNBT',73)]:
            encoded={};decoded={};wb=self.body(name,write);rb=self.body(name,read)
            for j,i in enumerate(wb):
                if '.put' in str(i['operand']) and '/nbt/' in str(i['operand']):
                    self.assertEqual(wb[j-1]['opcode'],'0xb4')
                    key=wb[j-3];self.assertIn(key['opcode'],('0x12','0x13'))
                    self.assertEqual(wb[j-2]['local_index'],0)
                    encoded[wb[j-1]['operand']]=(key['operand'],i['operand'].split('.put')[-1].split('(')[0])
            for j,i in enumerate(rb):
                if i['opcode']=='0xb5':
                    self.assertIn('net/minecraft/nbt/CompoundTag.get',rb[j-1]['operand'])
                    key=rb[j-2];self.assertIn(key['opcode'],('0x12','0x13'))
                    decoded[i['operand']]=(key['operand'],rb[j-1]['operand'].split('.get')[-1].split('(')[0])
            self.assertEqual(len(encoded),count);self.assertEqual(encoded,decoded)
            self.assertFalse(any(i.get('branch_target') is not None for b in [wb,rb] for i in b))

    def test_client_attachment_is_mutated_on_actual_context_player_not_replaced(self):
        b=self.body('PlayerVariablesSyncMessage','lambda$handleData$2')
        self.assertEqual(sum('.player()' in str(i['operand']) for i in b),3)
        self.assertTrue(any('.getData(' in str(i['operand']) for i in b))
        self.assertFalse(any('.setData(' in str(i['operand']) for i in b))
        self.assertIn('.deserializeNBT(',b[-2]['operand'])
        s=self.body('SavedDataSyncMessage','lambda$handleData$2')
        self.assertTrue(any('MapVariables.clientSide' in str(i['operand']) for i in s))
        self.assertTrue(any('WorldVariables.clientSide' in str(i['operand']) for i in s))
        self.assertFalse(any('.getDataStorage(' in str(i['operand']) for i in s))

    def test_event_annotations_keep_login_respawn_dimension_and_clone_roots_live(self):
        w=next(w for w in self.native['witnesses'] if w['entry'].endswith('$EventBusVariableHandlers.class'))
        for m in w['methods']:
            self.assertTrue(any(a['descriptor']=='Lnet/neoforged/bus/api/SubscribeEvent;' for a in m['annotations']))
        self.assertEqual(len(w['methods']),6)
        for m in ('onPlayerLoggedInSyncPlayerVariables','onPlayerRespawnedSyncPlayerVariables','onPlayerChangedDimensionSyncPlayerVariables'):
            b=self.body('EventBusVariableHandlers',m)
            self.assertTrue(any('.syncPlayerVariables(' in str(i['operand']) for i in b))
            self.assertFalse(any('.sendToAllPlayers(' in str(i['operand']) for i in b))

    def test_transport_has_no_native_damage_status_heal_or_motion_payload(self):
        forbidden=('.hurt(','.addEffect(','.heal(','.setHealth(','.setDeltaMovement(','EntityType.spawn(')
        for w in self.native['witnesses']:
            for m in w['methods']:
                self.assertFalse(any(any(s in str(i['operand']) for s in forbidden) for i in m['instructions']))


class NativeBlockStateCarrierTests(NativeContractHarness,unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m7b-native-block-state-carriers.json')
        cls.native=read_json(OUT/'native-evidence/arphex-native-block-state-carriers.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')
        cls.vanilla=read_json(OUT/'vanilla-evidence/arphex-native-block-state-carriers.json')
        cls.patch=read_json(OUT/'reference-evidence/arphex-native-block-state-carriers-244.json')['witnesses'][0]
        cls.carriers=[w for w in cls.native['witnesses'] if '/block/entity/' in w['entry']]

    def test_refinement_counts_do_not_add_copied_values_or_inventory_scalars(self):
        summary=validate_batch(self.batch,self.prior(),self.census)
        self.assertEqual((summary['semantic_records'],summary['numeric_candidate_entries']),(462,3903))
        self.assertEqual((len(self.native['witnesses']),sum(len(w['methods']) for w in self.native['witnesses'])),(8,145))
        self.assertEqual(len(self.carriers),7);self.assertEqual(len(self.batch['record_refinements']),5)
        self.assertEqual(len(self.batch['exclusions']),2);self.assertFalse(self.batch['effects'])
        self.assertTrue(all(not r.get('candidate_additions') for r in self.batch['record_refinements']))

    def test_native_stored_nine_slots_are_not_the_separate_three_row_menu(self):
        for w in self.carriers:
            n=w['entry'].rsplit('/',1)[-1][:-6]
            b=self.body(n,'<init>');at=next(j for j,i in enumerate(b) if '.withSize(' in str(i['operand']))
            self.assertEqual(b[at-2]['operand'],9)
            m=self.body(n,'createMenu')
            self.assertTrue(any('ChestMenu.threeRows(ILnet/minecraft/world/entity/player/Inventory;)' in str(i['operand']) for i in m))
            self.assertFalse(any(i.get('local_index')==0 for i in m))
        c=next(c for c in self.vanilla['classes'] if c['class_name'].endswith('/ChestMenu'))
        m=next(m for m in c['methods'] if m['name']=='<init>' and any('SimpleContainer' in str(i['operand']) for i in m['instructions']))
        body=m['instructions'];at=next(j for j,i in enumerate(body) if 'SimpleContainer.<init>(I)' in str(i['operand']))
        self.assertEqual((body[at-3]['operand'],body[at-1]['opcode']),(9,'0x68'))
        factory=next(m for m in c['methods'] if m['name']=='threeRows' and len(m['instructions'])==8)
        self.assertEqual(factory['instructions'][-3]['operand'],3)

    def test_parent_load_save_and_unconditional_load_items_order_is_preserved(self):
        for w in self.carriers:
            n=w['entry'].rsplit('/',1)[-1][:-6]
            load=self.body(n,'loadAdditional');save=self.body(n,'saveAdditional')
            self.assertIn('RandomizableContainerBlockEntity.loadAdditional(',load[3]['operand'])
            self.assertIn('RandomizableContainerBlockEntity.saveAdditional(',save[3]['operand'])
            load_at=next(i['offset'] for i in load if 'ContainerHelper.loadAllItems' in str(i['operand']))
            gate=next(i for i in load if i.get('branch_target') is not None)
            self.assertLess(gate['branch_target'],load_at)
            save_at=next(i['offset'] for i in save if 'ContainerHelper.saveAllItems' in str(i['operand']))
            self.assertGreater(next(i['branch_target'] for i in save if i.get('branch_target') is not None),save_at)
        parent=next(c for c in self.vanilla['classes'] if c['class_name'].endswith('/RandomizableContainerBlockEntity'))
        self.assertTrue(parent['superclass'].endswith('/BaseContainerBlockEntity'))
        self.assertFalse(any(m['name'] in ('loadAdditional','saveAdditional') for m in parent['declared_methods']))
        base=next(c for c in self.vanilla['classes'] if c['class_name'].endswith('/BaseContainerBlockEntity'))
        for m in base['methods']:
            self.assertIn('BlockEntity.'+m['name']+'(',m['instructions'][3]['operand'])

    def test_native_persistent_tag_is_conditional_loaded_and_copied_on_save(self):
        text=''.join(s['text'] for s in self.patch['text_sections'])
        self.assertIn('contains("NeoForgeData", net.minecraft.nbt.Tag.TAG_COMPOUND)',text)
        self.assertIn('this.customPersistentData = p_338466_.getCompound("NeoForgeData")',text)
        self.assertIn('p_187471_.put("NeoForgeData", this.customPersistentData.copy())',text)
        self.assertIn('if (this.customPersistentData == null)',text)
        self.assertNotIn('ForgeData"',text.replace('NeoForgeData"',''))
        block=next(c for c in self.vanilla['classes'] if c['class_name'].endswith('/BlockEntity'))
        b=next(m for m in block['methods'] if m['name']=='saveWithoutMetadata')['instructions']
        self.assertTrue(any('BlockEntity.saveAdditional(' in str(i['operand']) and i['opcode']=='0xb6' for i in b))

    def test_shared_inventory_methods_are_exact_self_owner_equivalent(self):
        from compare_native_methods import normalized
        names=('loadAdditional','saveAdditional','getUpdatePacket','getUpdateTag','getContainerSize','isEmpty','getMaxStackSize','createMenu','getItems','setItems','canPlaceItem','getSlotsForFace','canPlaceItemThroughFace','canTakeItemThroughFace','getItemHandler')
        for n in names:
            bodies=[normalized(next(m for m in w['methods'] if m['name']==n)['instructions'],w['class_name']) for w in self.carriers]
            self.assertTrue(all(b==bodies[0] for b in bodies))

    def test_eight_native_capability_providers_ignore_side_and_return_native_handler(self):
        w=next(w for w in self.native['witnesses'] if w['entry'].endswith('/ArphexModBlockEntities.class'))
        callbacks=[m for m in w['methods'] if m['name'].startswith('lambda$registerCapabilities$')]
        self.assertEqual(len(callbacks),8)
        for m in callbacks:
            b=m['instructions']
            self.assertTrue(any('.getItemHandler()' in str(i['operand']) for i in b))
            self.assertFalse(any(i.get('local_index')==1 for i in b))
        self.assertTrue(any('TesseractTransporterBlockEntity' in str(i['operand']) for m in callbacks for i in m['instructions']))
        registration=next(m for m in w['methods'] if m['name']=='registerCapabilities')
        self.assertTrue(any(a['descriptor']=='Lnet/neoforged/bus/api/SubscribeEvent;' for a in registration['annotations']))

    def test_all_carrier_methods_have_no_authored_combat_payload_or_tick(self):
        for w in self.carriers:
            self.assertNotIn('tick',w['declared_method_names'])
            for m in w['methods']:
                self.assertFalse(any(any(s in str(i['operand']) for s in ('.hurt(','.addEffect(','.heal(','.setDeltaMovement(','EntityType.spawn(')) for i in m['instructions']))


if __name__=='__main__':unittest.main()
