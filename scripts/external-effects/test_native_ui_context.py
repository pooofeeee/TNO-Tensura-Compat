"""Native preview mutation/restore, typed slot equivalence and storage lifecycle."""
import copy
import unittest
from pathlib import Path
from unittest.mock import patch
from audit_catalog_integrity import EvidenceIndex
from catalog_common import OUT,read_json
from reconcile_native_census import reconcile
from promote_combat_batch import validate_batch


class NativeUiContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b=read_json(OUT/'arphex-r2m7m-native-ui-context.json')
        cls.e=read_json(OUT/'native-evidence/arphex-native-ui-context.json')
        cls.c=read_json(OUT/'arphex-combat-census.json')
        cls.w={w['entry']:w for w in cls.e['witnesses']}

    def method(self,entry,name):
        return next(m for m in self.w[entry]['methods'] if m['name']==name)

    def review(self):
        r=read_json(OUT/'mod-reviews/arphex.json')
        r['reviewed_batches']=[f for f in r['reviewed_batches'] if f!='arphex-r2m7m-native-ui-context.json']
        return r

    def test_scope_uses_exact_context_without_new_semantics_or_scalars(self):
        self.assertEqual(len(self.w),138)
        self.assertEqual(sum(len(w['methods']) for w in self.w.values()),206)
        self.assertEqual(self.b['effects'],[]);self.assertEqual(self.b['paths'],[])
        r=self.review();r['reviewed_batches'].append('arphex-r2m7m-native-ui-context.json')
        after,_=reconcile(r,self.c)
        before,_=reconcile(self.review(),self.c)
        self.assertEqual(after['summary']['pending_methods'],before['summary']['pending_methods']-326)
        self.assertEqual(validate_batch(self.b,self.review(),self.c)['semantic_records'],len(r['effects']))

    def test_slot_constructor_descriptors_and_unused_outer_argument_stay_native(self):
        descriptors=set();counts=[]
        for context in self.b['native_context_equivalences']:
            d=read_json(OUT/context['file']);counts.append(len(d['rows']))
            descriptors.update(r['descriptor'] for r in d['rows'])
            t=d['template'];m=self.method(t['entry'],'<init>');b=m['instructions']
            self.assertEqual([i.get('local_index') for i in b[:5]],[0,2,3,4,5])
            self.assertEqual(b[5]['operand'],'net/neoforged/neoforge/items/SlotItemHandler.<init>(Lnet/neoforged/neoforge/items/IItemHandler;III)V')
            self.assertEqual(b[-1]['opcode'],'0xb1')
            self.assertFalse(any(i['opcode'] in ('0xb3','0xb5') for i in b))
        self.assertEqual(sorted(counts),[3,27,93]);self.assertEqual(len(descriptors),3)

    def test_preview_selection_can_use_live_actor_and_fallback_never_inserts_or_ticks(self):
        selectors=self.b['native_preview_entity_selection']
        self.assertEqual(len(selectors),8)
        self.assertEqual(sum(s['nearest_native_selection'] for s in selectors),6)
        for s in selectors:
            b=self.method(s['entry'],'execute')['instructions']
            self.assertEqual(any('.getEntitiesOfClass(' in str(i['operand']) for i in b),s['nearest_native_selection'])
            self.assertFalse(s['fallback_inserted'])
            self.assertTrue(s['native_entity_constructors'])
            for forbidden in ('.addFreshEntity(','.tick()','.hurt(','.setDeltaMovement('):
                self.assertFalse(any(forbidden in str(i['operand']) for i in b))

    def test_preview_restoration_is_normal_return_only_not_a_pure_query(self):
        count=0
        for w in self.w.values():
            for m in w['methods']:
                if m['name']!='renderEntityInInventoryFollowsAngle':continue
                count+=1;b=m['instructions'];self.assertEqual(m['exception_handlers'],[])
                at=next(n for n,i in enumerate(b) if 'InventoryScreen.renderEntityInInventory(' in str(i['operand']))
                self.assertTrue(any(i['opcode']=='0xb5' for i in b[:at]))
                after=b[at+1:]
                restores=[(i['operand'],after[n-1].get('local_index')) for n,i in enumerate(after) if i['opcode'] in ('0xb5','0xb6')]
                self.assertEqual(restores,[('net/minecraft/world/entity/LivingEntity.yBodyRotF',9),
                    ('net/minecraft/world/entity/LivingEntity.setYRot(F)V',10),
                    ('net/minecraft/world/entity/LivingEntity.setXRot(F)V',11),
                    ('net/minecraft/world/entity/LivingEntity.yHeadRotOF',12),
                    ('net/minecraft/world/entity/LivingEntity.yHeadRotF',13)])
        self.assertEqual(count,6)

    def test_ui_packet_and_local_handler_occurrences_are_preserved_exactly(self):
        callbacks={}
        for w in self.w.values():
            for m in w['methods']:
                if not m['name'].startswith('lambda$init$'):continue
                self.assertEqual(w['entry'],'net/arphex/client/gui/WayfinderScreen.class')
                callbacks[m['name']]=m
        self.assertEqual(set(callbacks),{'lambda$init$'+str(n) for n in range(12)})
        for n in range(12):
            m=callbacks['lambda$init$'+str(n)];b=m['instructions']
            action=n%2==0
            self.assertEqual(m['descriptor'],'(Lnet/minecraft/client/gui/components/Button;)V' if action else
                             '(Lnet/minecraft/client/gui/components/Button$Builder;)Lnet/minecraft/client/gui/components/Button;')
            self.assertEqual(sum('PacketDistributor.sendToServer(' in str(i['operand']) for i in b),int(action))
            self.assertEqual(sum('WayfinderButtonMessage.handleButtonAction(' in str(i['operand']) for i in b),int(action))
        self.assertEqual({p['method'] for p in self.b['native_prior_packet_contracts']},{'<init>','handleButtonAction'})

    def test_storage_capacity_copy_and_toss_subscriber_remain_native_utility(self):
        expected={'ProwlerPackInventoryCapability':27,'SingularitySatchelInventoryCapability':93}
        for name,capacity in expected.items():
            entry='net/arphex/item/inventory/'+name+'.class';w=self.w[entry]
            self.assertTrue(any(a['values'].get('value')==[{'enum_type':'Lnet/neoforged/api/distmarker/Dist;','constant':'CLIENT'}] for a in w['annotations']))
            init=self.method(entry,'<init>')['instructions']
            self.assertEqual([i['operand'] for i in init if i['opcode'] in ('0x10','0x11')],[capacity])
            self.assertEqual(self.method(entry,'getSlotLimit')['instructions'][0]['operand'],64)
            b=self.method(entry,'getStackInSlot')['instructions']
            self.assertTrue(b[-2]['operand'].endswith('ItemStack.copy()Lnet/minecraft/world/item/ItemStack;'))
            self.assertTrue(any('LocalPlayer.closeContainer()V' in str(i['operand']) for i in self.method(entry,'onItemDropped')['instructions']))

    def test_inventory_removal_keeps_drop_and_return_branches_without_combat_payload(self):
        entry='net/arphex/world/inventory/BackpackMenu.class'
        b=self.method(entry,'removed')['instructions']
        for native in ('ServerPlayer.isAlive()Z','ServerPlayer.hasDisconnected()Z','Player.drop(',
                       'Inventory.placeItemBackInInventory(','IItemHandlerModifiable.setStackInSlot('):
            self.assertTrue(any(native in str(i['operand']) for i in b))
        for m in self.w[entry]['methods']:
            self.assertFalse(any('.hurt(' in str(i['operand']) or '.addEffect(' in str(i['operand']) for i in m['instructions']))

    def test_independent_census_rejects_mutated_slot_or_context_before_promotion(self):
        file=self.b['native_context_equivalences'][0]['file'];changed=read_json(OUT/file)
        changed['rows'][0]['code_sha256']='0'*64
        original=EvidenceIndex.read
        def read(index,path):
            name=path.relative_to(OUT).as_posix() if isinstance(path,Path) and path.is_absolute() else str(path)
            return changed if name==file else original(index,path)
        with patch.object(EvidenceIndex,'read',autospec=True,side_effect=read):
            with self.assertRaisesRegex(AssertionError,'hash mismatch'):
                validate_batch(self.b,self.review(),self.c)
        r=self.review();r['reviewed_batches'].append('arphex-r2m7m-native-ui-context.json')
        e=copy.deepcopy(self.e);e['witnesses'][0]['methods'][0]['code_sha256']='0'*64
        def evidence_read(path):
            return e if str(path.relative_to(OUT))=='native-evidence/arphex-native-ui-context.json' else read_json(path)
        with self.assertRaisesRegex(AssertionError,'hash mismatch'):reconcile(r,self.c,read=evidence_read)


if __name__=='__main__':unittest.main()
