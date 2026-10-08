"""Independent dispatch, native payload ordering and original parameter replay."""
import unittest
from catalog_common import OUT,read_json
from assemble_authored_contracts import render
from promote_combat_batch import validate_batch
from collect_combat_census import decode_sites
from audit_numeric_labels import audit

P='com/github/alexthe666/alexsmobs/'
F='native-evidence/alexsmobs-item-combat.json'
def witness(cls,file=F):return next(w for w in read_json(OUT/file)['witnesses'] if w['entry']==P+cls+'.class')
def method(cls,name,file=F):return next(m for m in witness(cls,file)['methods'] if m['name']==name)


class AlexMobsProjectileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'alexsmobs-r2o3a-projectile-launcher-packages.json')
        cls.census=read_json(OUT/'alexsmobs-combat-census.json')

    def test_renderer_and_native_numeric_replay(self):
        self.assertEqual(render(read_json(OUT/'native-specifications/alexsmobs-projectile-contracts.json')),self.batch)
        prior=read_json(OUT/'mod-reviews/alexsmobs.json');ids={r['id'] for r in self.batch['effects']}
        prior['effects']=[r for r in prior['effects'] if r['id'] not in ids]
        prior['paths']=[r for r in prior['paths'] if not set(r['effect_ids'])&ids]
        validate_batch(self.batch,prior,self.census)
        self.assertEqual(audit(dict(effects=self.batch['effects']))['native_candidate_identities'],52)
        self.assertFalse(self.batch['stage_policy_decided'])

    def test_damage_returns_do_not_gate_status_blood_or_entity_removal(self):
        for cls in ['EntityMosquitoSpit','EntityHemolymph','EntitySandShot']:
            ins=method('entity/'+cls,'onEntityHit')['instructions']
            at=next(n for n,i in enumerate(ins) if '.hurt(' in str(i['operand']))
            self.assertEqual(ins[at+1]['opcode'],'0x57')
            self.assertFalse(any('.remove(' in str(i['operand']) or '.discard(' in str(i['operand']) for i in ins))
        spit=method('entity/EntityMosquitoSpit','onEntityHit')['instructions']
        self.assertTrue(any('EntityCrimsonMosquito.setBloodLevel' in str(i['operand']) for i in spit))
        sand=method('entity/EntitySandShot','onEntityHit')['instructions']
        self.assertTrue(any('MobEffects.BLINDNESS' in str(i['operand']) for i in sand))
        self.assertTrue(any('net/minecraft/world/entity/player/Player'==i['operand'] and i['opcode']=='0xc1' for i in sand))

    def test_sand_has_unconditional_then_conditional_gravity(self):
        ins=method('entity/EntitySandShot','tick')['instructions']
        ys=[i['offset'] for i in ins if i['opcode']=='0x14' and i['operand']==-0.029999999329447746]
        self.assertEqual(ys,[341,364])
        gate=next(i['offset'] for i in ins if '.isNoGravity()' in str(i['operand']))
        self.assertLess(ys[0],gate);self.assertGreater(ys[1],gate)

    def test_fart_does_not_update_left_owner_and_provocation_is_two_way(self):
        ins=method('entity/EntityFart','tick')['instructions']
        self.assertFalse(any('.checkLeftOwner(' in str(i['operand']) for i in ins))
        body=method('entity/EntityFart','onEntityHit')['instructions']
        self.assertEqual(sum('.isAlliedTo(' in str(i['operand']) for i in body),2)
        self.assertTrue(any('IHurtableMultipart' in str(i['operand']) for i in body))
        self.assertFalse(any('.hurt(' in str(i['operand']) for i in body))
        calls={i['operand'] for m in self.census['methods'] for i in decode_sites(self.census,m,'calls')}
        self.assertNotIn(P+'entity/EntityFart.checkLeftOwner()Z',calls)

    def test_rocket_explode_is_event_and_discard_without_damage(self):
        ins=method('entity/EntityEnderiophageRocket','explode')['instructions']
        calls=[i['operand'] for i in ins if i['opcode'] in ('0xb6','0xb7','0xb8','0xb9')]
        self.assertEqual(len(calls),3)  # level getter, broadcast, discard
        self.assertTrue(any('.broadcastEntityEvent(' in str(s) for s in calls))
        self.assertTrue(any('.discard()' in str(s) for s in calls))
        self.assertFalse(any('.explode(' in str(s) or '.hurt(' in str(s) or '.addEffect(' in str(s) for s in calls))

    def test_arrow_old_factory_is_not_current_dispatch(self):
        native=method('item/ItemModArrow','createArrow')
        self.assertNotIn('LivingEntity;Lnet/minecraft/world/item/ItemStack;',native['descriptor'])
        v=read_json(OUT/'vanilla-evidence/alexsmobs-arrow-dispatch.json')
        weapon=next(w for w in v['classes'] if w['class_name'].endswith('/ProjectileWeaponItem'))
        factories=[i['operand'] for m in weapon['methods'] for i in m['instructions'] if 'ArrowItem.createArrow' in str(i['operand'])]
        self.assertEqual(len(factories),1);self.assertIn('LivingEntity;Lnet/minecraft/world/item/ItemStack;',factories[0])
        calls={i['operand'] for m in self.census['methods'] for i in decode_sites(self.census,m,'calls')}
        handles={s for b in self.census['registration_bootstraps'] for s in [b['handle']]+b['arguments'] if isinstance(s,str)}
        self.assertNotIn(P+'item/ItemModArrow.createArrow'+native['descriptor'],calls|handles)
        # Pinned loader patch adds isInfinite only, no compatibility factory.
        loader=read_json(OUT/'reference-evidence/alexsmobs-native-arrow-dispatch-loader.json')
        patch=next(w for w in loader['witnesses'] if w['entry'].endswith('/ArrowItem.java.patch'))
        self.assertIn('isInfinite',patch['text']);self.assertNotIn('createArrow',patch['text'])

    def test_registered_dispenser_uses_item_behavior_not_projectile_factory(self):
        w=witness('item/AMItemRegistry$1','native-evidence/alexsmobs-arrow-dispenser.json')
        self.assertEqual(w['superclass'],'net/minecraft/core/dispenser/DefaultDispenseItemBehavior')
        self.assertNotIn('execute',w['declared_method_names'])
        v=read_json(OUT/'vanilla-evidence/alexsmobs-arrow-dispatch.json')
        parent=next(w for w in v['classes'] if w['class_name'].endswith('/DefaultDispenseItemBehavior'))
        self.assertNotIn('getProjectile',[m['name'] for m in parent['declared_methods']])
        ins=parent['methods'][0]['instructions']
        self.assertTrue(any('spawnItem' in str(i['operand']) for i in ins))
        self.assertFalse(any('getProjectile' in str(i['operand']) for i in ins))
        calls={i['operand'] for m in self.census['methods'] for i in decode_sites(self.census,m,'calls')}
        self.assertNotIn(w['class_name']+'.getProjectile'+w['methods'][1]['descriptor'],calls)
        loader=read_json(OUT/'reference-evidence/alexsmobs-native-arrow-dispatch-loader.json')
        self.assertTrue(next(w for w in loader['witnesses'] if w['entry'].endswith('/DefaultDispenseItemBehavior.java.patch'))['absent'])

    def test_shark_extra_damage_is_after_accepted_parent_hurt(self):
        v=read_json(OUT/'vanilla-evidence/alexsmobs-arrow-dispatch.json')
        w=next(w for w in v['classes'] if w['class_name'].endswith('/AbstractArrow'))
        m=next(m for m in w['methods'] if m['name']=='onHitEntity');ins=m['instructions'];code=bytes.fromhex(m['code_hex'])
        at=next(n for n,i in enumerate(ins) if '.hurt(' in str(i['operand']))
        branch=ins[at+1];self.assertEqual(branch['opcode'],'0x99')
        failure=branch['offset']+int.from_bytes(code[branch['offset']+1:branch['offset']+3],'big',signed=True)
        post=next(i['offset'] for i in ins if '.doPostHurtEffects(' in str(i['operand']))
        self.assertLess(post,failure)
        body=method('entity/EntitySharkToothArrow','doPostHurtEffects')['instructions']
        self.assertTrue(any('.getBaseDamage()' in str(i['operand']) for i in body))
        self.assertLess(next(i['offset'] for i in body if '.damageShield(' in str(i['operand'])),next(i['offset'] for i in body if '.hurt(' in str(i['operand'])))


if __name__=='__main__':unittest.main()
