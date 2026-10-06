"""Independent native/census facts for shared intrinsic projectile contracts."""
import unittest

from catalog_common import OUT,read_json
from collect_combat_census import decode_sites
from promote_combat_batch import validate_batch


class ProjectileContractsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native=read_json(OUT/'native-evidence/arphex-arrow-shared-and-status.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')
        cls.batch=read_json(OUT/'arphex-r2m3a-four-intrinsic-arrow-contracts.json')

    def method(self,name,method,descriptor=None):
        w=next(w for w in self.native['witnesses'] if w['entry'].split('/')[-1]==name+'.class')
        return next(m for m in w['methods'] if m['name']==method and (descriptor is None or m['descriptor']==descriptor))

    def test_batch_has_four_unique_payload_contracts_and_real_scalar_consumers(self):
        review=read_json(OUT/'mod-reviews/arphex.json');ids={r['id'] for r in self.batch['effects']}
        review['effects']=[r for r in review['effects'] if r['id'] not in ids]
        review['paths']=[p for p in review['paths'] if not set(p['effect_ids'])&ids]
        self.assertEqual(validate_batch(self.batch,review,self.census)['semantic_records'],len(review['effects'])+4)
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects'] for c in r['scalable_parameter_candidates']),32)

    def test_child_hit_payloads_follow_void_parent_without_success_branch(self):
        for name in ('BloodProjectileEntity','WidowArrowEntity','WebbedArrowEntity'):
            body=self.method(name,'onHitEntity')['instructions']
            parent=next(n for n,i in enumerate(body) if 'AbstractArrow.onHitEntity(' in str(i['operand']))
            child=next(n for n,i in enumerate(body) if '/procedures/' in str(i['operand']))
            self.assertLess(parent,child)
            self.assertTrue(body[parent]['operand'].endswith(')V'))
            self.assertFalse(any(0x99<=int(i['opcode'],16)<=0xa6 for i in body[parent:child]))
        parent=next(w for w in read_json(OUT/'reference-evidence/bossesrise-knight-offense-244.json')['witnesses']
                    if w['class_name']=='net/minecraft/world/entity/projectile/AbstractArrow')
        body=next(m['instructions'] for m in parent['methods'] if m['name']=='onHitEntity')
        at=next(n for n,i in enumerate(body) if '.hurt(' in str(i['operand']))
        self.assertEqual(body[at+1]['opcode'],'0x99')
        self.assertTrue(any('DamageSources.arrow(' in str(i['operand']) for i in body))

    def test_blood_status_has_owner_regeneration_and_native_flags(self):
        body=self.method('BloodProjectileProjectileHitsLivingEntityProcedure','execute')['instructions']
        values=[]
        for n,i in enumerate(body):
            if 'MobEffectInstance.<init>' in str(i['operand']):values.append([x['operand'] for x in body[n-4:n]])
        self.assertEqual(values,[[80,1,0,1],[10,1,0,1],[60,1,1,0]])
        row=next(r for r in self.batch['effects'] if r['id']=='arphex:blood_arrow_intrinsic_combat')
        regen=next(c for c in row['scalable_parameter_candidates'] if c['primitive']=='MOB_EFFECT_REGENERATION')
        self.assertEqual(regen['native_receiver_binding']['origin_local_index'],1)
        self.assertEqual(regen['native_recipient_role'],'current_arrow_owner')
        hit=self.method('BloodProjectileEntity','onHitEntity')['instructions']
        self.assertTrue(any('.getOwner()' in str(i['operand']) for i in hit))

    def test_webbed_flying_baseline_is_owner_not_iterator(self):
        tick=self.method('WebbedArrowEntity','tick')['instructions']
        at=next(n for n,i in enumerate(tick) if 'WebbedArrowWhileProjectileFlyingTickProcedure.execute(' in str(i['operand']))
        self.assertIn('.getOwner()',tick[at-1]['operand'])
        body=self.method('WebbedArrowWhileProjectileFlyingTickProcedure','execute')['instructions'];by={i['offset']:i for i in body}
        self.assertEqual(by[151]['local_index'],11) # iterator
        self.assertEqual([by[n]['local_index'] for n in (153,168,175,183)],[7,7,7,7]) # passed owner
        self.assertEqual(by[158]['operand'],'momenthealth')
        self.assertEqual(by[173]['operand'],'momenthealth')
        self.assertIn('.putDouble(',by[202]['operand'])
        # Independent finite key index: no hidden victim initializer is assumed.
        entries={m['entry'] for m in self.census['methods'] if any(i['operand']=='momenthealth' for i in decode_sites(self.census,m))}
        self.assertEqual(entries,{'net/arphex/procedures/WebbedArrowWhileProjectileFlyingTickProcedure.class',
                                 'net/arphex/procedures/WebbedArrowProjectileHitsLivingEntityProcedure.class'})

    def test_webbed_profiles_follow_raw_health_gate_and_clear_first(self):
        body=self.method('WebbedArrowProjectileHitsLivingEntityProcedure','execute')['instructions']
        profiles=[]
        for n,i in enumerate(body):
            if 'MobEffectInstance.<init>' in str(i['operand']):profiles.append([x['operand'] for x in body[n-4:n]])
        self.assertEqual(profiles,[[60,0,0,0],[80,1,0,0],[100,2,0,0],[120,3,0,0],[140,4,0,0]])
        self.assertIn('getHealth()',next(i['operand'] for i in body if i['offset']==18))
        self.assertIn('.putDouble(',next(i['operand'] for i in body if i['offset']==47))
        self.assertLess(47,107)

    def test_unused_shoot_helpers_are_excluded_but_blood_ranged_path_is_live(self):
        for name in ('WidowArrowEntity','WebbedArrowEntity'):
            prefix=f'net/arphex/entity/{name}.shoot('
            callers=[m for m in self.census['methods'] if m['entry']!=f'net/arphex/entity/{name}.class'
                     and any(prefix in i['operand'] for i in decode_sites(self.census,m,'calls'))]
            self.assertEqual(callers,[])
            self.assertFalse(any(prefix in str(b['arguments']) for b in self.census['registration_bootstraps']))
        prefix='net/arphex/entity/BloodProjectileEntity.shoot('
        callers={(m['entry'],m['method']) for m in self.census['methods'] if m['entry']!='net/arphex/entity/BloodProjectileEntity.class'
                 and any(prefix in i['operand'] for i in decode_sites(self.census,m,'calls'))}
        self.assertEqual(callers,{(f'net/arphex/entity/{name}.class','performRangedAttack') for name in ('SpiderMothLarvaeEntity','SpiderMothSummonLarvaeEntity')})
        body=self.method('BloodProjectileEntity','shoot','(Lnet/minecraft/world/entity/LivingEntity;Lnet/minecraft/world/entity/LivingEntity;)Lnet/arphex/entity/BloodProjectileEntity;')['instructions']
        by={i['offset']:i for i in body}
        self.assertEqual([by[n]['operand'] for n in (43,75,82,84,95,102)],[1.1,.20000000298023224,3.0,12.0,2.5,3])

    def test_brood_pickup_does_not_create_custom_status(self):
        w=next(w for w in self.native['witnesses'] if w['entry'].endswith('/SpiderBroodEntityProjectile.class'))
        names=set(w['declared_method_names'])
        self.assertFalse(names&{'onHitEntity','onHitBlock','tick','doKnockback','hurt'})
        self.assertFalse(any('/procedures/' in str(i['operand']) for m in w['methods'] for i in m['instructions']))
        body=self.method('SpiderBroodEntity','performRangedAttack')['instructions'];by={i['offset']:i for i in body}
        self.assertEqual([by[n]['operand'] for n in (32,84,91,94)],[1.1,.20000000298023224,1.600000023841858,12.0])

    def test_native_constructor_retains_shooter_owner(self):
        refs=read_json(OUT/'vanilla-evidence/arphex-arrow-owner-construction.json')['classes']
        arrow=next(w for w in refs if w['class_name'].endswith('/AbstractArrow'))
        ctor=next(m for m in arrow['methods'] if 'Lbtn;' in m['obfuscated_descriptor'])
        body=ctor['instructions'];at=next(n for n,i in enumerate(body) if '.setOwner(' in str(i['operand']))
        self.assertEqual([i['opcode'] for i in body[at-2:at]],['0x2a','0x2c'])
        projectile=next(w for w in refs if w['class_name'].endswith('/Projectile'))
        setter=next(m for m in projectile['methods'] if m['name']=='setOwner')['instructions']
        self.assertTrue(any('ownerUUID' in str(i['operand']) for i in setter))
        self.assertTrue(any('cachedOwner' in str(i['operand']) for i in setter))


if __name__=='__main__':unittest.main()
