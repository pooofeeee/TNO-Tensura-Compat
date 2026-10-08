"""Native registered handlers, exact source identities and dependency storage."""
import unittest
from catalog_common import OUT,read_json
from assemble_authored_contracts import render
from promote_combat_batch import validate_batch
from collect_combat_census import decode_sites
from audit_numeric_labels import audit

P='com/github/alexthe666/alexsmobs/'
N='native-evidence/alexsmobs-network.json'


def witness(entry,file=N):return next(w for w in read_json(OUT/file)['witnesses'] if w['entry']==entry)
def method(entry,name,file=N):return next(m for m in witness(entry,file)['methods'] if m['name']==name)


class AlexMobsNetworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'alexsmobs-r2o2d-registered-combat-transport.json')
        cls.census=read_json(OUT/'alexsmobs-combat-census.json')

    def test_renderer_independent_native_inputs_and_no_stage_policy(self):
        self.assertEqual(render(read_json(OUT/'native-specifications/alexsmobs-network-contracts.json')),self.batch)
        prior=read_json(OUT/'mod-reviews/alexsmobs.json');ids={r['id'] for r in self.batch['effects']}
        prior['effects']=[r for r in prior['effects'] if r['id'] not in ids]
        prior['paths']=[r for r in prior['paths'] if not set(r['effect_ids'])&ids]
        validate_batch(self.batch,prior,self.census)
        self.assertEqual(audit(dict(effects=self.batch['effects']))['native_candidate_identities'],2)
        self.assertFalse(self.batch['stage_policy_decided'])

    def test_registered_multipart_handlers_are_bidirectional_handle(self):
        file='native-evidence/alexsmobs-foundation.json'
        ins=method(P+'network/AMNetworking.class','register',file)['instructions']
        self.assertEqual(sum('.playBidirectional(' in str(i['operand']) for i in ins),3)
        boot=[b for b in self.census['registration_bootstraps'] if b['entry']==P+'network/AMNetworking.class']
        targets=[s for b in boot for s in b['arguments'] if isinstance(s,str)]
        for cls in ['MessageHurtMultipart','MessageInteractMultipart','MessageMosquitoDismount']:
            self.assertTrue(any('/'+cls+'.handle(' in s for s in targets))
            self.assertFalse(any('/'+cls+'.handleServer(' in s or '/'+cls+'.handleClient(' in s for s in targets))

    def test_inactive_alternatives_have_only_their_private_lambda_bootstraps(self):
        calls={i['operand'] for m in self.census['methods'] for i in decode_sites(self.census,m,'calls')}
        handles={s for b in self.census['registration_bootstraps'] for s in [b['handle']]+b['arguments'] if isinstance(s,str)}
        for cls,names in [('MessageHurtMultipart',['handleServer']),('MessageInteractMultipart',['handleServer']),('MessageMosquitoDismount',['handleClient','handleServer'])]:
            w=witness(P+'network/'+cls+'.class')
            for name in names:
                m=next(m for m in w['methods'] if m['name']==name)
                self.assertNotIn(w['class_name']+'.'+name+m['descriptor'],calls|handles)
                self.assertEqual(m['annotations'],[])
                lambdas=[m for m in w['methods'] if m['name'].startswith('lambda$'+name+'$')]
                self.assertEqual(len(lambdas),1)
                target=w['class_name']+'.'+lambdas[0]['name']+lambdas[0]['descriptor']
                sites=[b['entry'] for b in self.census['registration_bootstraps'] if target in b['arguments']]
                self.assertEqual(sites,[w['entry']])

    def test_multipart_damage_source_is_ownerless_and_callback_gets_null(self):
        m=method(P+'network/MessageHurtMultipart.class','lambda$handle$0');ins=m['instructions']
        callback=next(n for n,i in enumerate(ins) if '.onAttackedFromServer(' in str(i['operand']))
        self.assertEqual(ins[callback-1]['opcode'],'0x1')
        constructors=[i['operand'] for i in ins if 'DamageSource.<init>' in str(i['operand'])]
        self.assertEqual(constructors,['net/minecraft/world/damagesource/DamageSource.<init>(Lnet/minecraft/core/Holder;)V'])
        self.assertFalse(any('DamageSource.getEntity' in str(i['operand']) for i in ins))
        hurt=next(n for n,i in enumerate(ins) if '.hurt(' in str(i['operand']))
        self.assertEqual(ins[hurt+1]['opcode'],'0x57')

    def test_sync_coordinates_preserve_both_native_calls(self):
        ins=method(P+'network/MessageSyncEntityPos.class','lambda$handleClient$0')['instructions']
        self.assertEqual(sum('.setPos(' in str(i['operand']) for i in ins),1)
        self.assertEqual(sum('.teleportTo(' in str(i['operand']) for i in ins),1)
        self.assertFalse(any('.hurt(' in str(i['operand']) for i in ins))

    def test_client_overlay_counter_uses_local_identity_and_game_time(self):
        f='native-evidence/alexsmobs-client-packet-consumers.json'
        m=method(P+'ClientProxy.class','processVisualFlag',f)
        self.assertEqual([(i['offset'],i['operand']) for i in m['instructions'] if i['opcode']=='0x10'],[(11,87),(16,60)])
        ui=method(P+'client/event/ClientEvents.class','onPostGameOverlay',f)['instructions']
        self.assertTrue(any(i['opcode']=='0xb5' and '.lastStaticTickJ' in str(i['operand']) for i in ui))
        self.assertTrue(any(i['opcode']=='0xb4' and '.lastStaticTickJ' in str(i['operand']) for i in ui))
        self.assertEqual(next(i['operand'] for i in ui if i['offset']==47),60.0)

    def test_exact_citadel_getter_fallback_does_not_store_new_tag(self):
        f='native-evidence/alexsmobs-citadel-data.json';p='com/github/alexthe666/citadel/server/entity/CitadelEntityData.class'
        ins=method(p,'getOrCreateCitadelTag',f)['instructions']
        self.assertTrue(any('.getCitadelTag(' in str(i['operand']) for i in ins))
        self.assertFalse(any('.setCitadelTag(' in str(i['operand']) for i in ins))
        setter=method(p,'setCitadelTag',f)['instructions']
        self.assertEqual(setter[1]['opcode'],'0xc1')
        self.assertEqual(setter[1]['operand'],'com/github/alexthe666/citadel/server/entity/ICitadelDataEntity')

    def test_storage_mixin_is_configured_and_nbt_key_is_exact(self):
        f='native-evidence/alexsmobs-citadel-data.json';p='com/github/alexthe666/citadel/mixin/LivingEntityMixin.class'
        w=witness(p,f);self.assertIn('com/github/alexthe666/citadel/server/entity/ICitadelDataEntity',w['interfaces'])
        for name in ['citadel_writeAdditional','citadel_readAdditional']:
            m=method(p,name,f);self.assertTrue(m['annotations'])
            self.assertTrue(any(i['operand']=='CitadelData' for i in m['instructions']))
        config=next(w for w in read_json(OUT/'native-evidence/citadel-alexscaves-dependencies.json')['witnesses'] if w['entry']=='citadel.mixins.json')
        self.assertIn('LivingEntityMixin',config['data']['mixins'])
        self.assertTrue(all(w['jar_sha256']=='9e12468c49e5a95b7adbf22b3b4d05bc55565989b89c40b985cd73bdfe63c3c2' for w in read_json(OUT/f)['witnesses']))


if __name__=='__main__':unittest.main()
