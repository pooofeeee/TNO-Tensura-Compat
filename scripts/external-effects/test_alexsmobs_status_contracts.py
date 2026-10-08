"""Pinned dispatch, instruction ordering, and signed-input status regressions."""
import copy
import unittest
from catalog_common import OUT, read_json
from collect_combat_census import decode_sites
from assemble_authored_contracts import render
from promote_combat_batch import validate_batch
from audit_numeric_labels import audit

P='com/github/alexthe666/alexsmobs/'
F='native-evidence/alexsmobs-foundation.json'
C='native-evidence/alexsmobs-status-consumers.json'


def method(entry,name,file=F):
    w=next(w for w in read_json(OUT/file)['witnesses'] if w['entry']==P+entry+'.class')
    return next(m for m in w['methods'] if m['name']==name)


class AlexMobsStatusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'alexsmobs-r2o2a-status-foundation.json')
        cls.census=read_json(OUT/'alexsmobs-combat-census.json')
        cls.rows={r['id']:r for r in cls.batch['effects']}

    def test_renderer_and_independent_native_bindings(self):
        self.assertEqual(render(read_json(OUT/'native-specifications/alexsmobs-status-contracts.json')),self.batch)
        review=dict(mod_key='alexsmobs',effects=[],paths=[],reviewed_batches=[])
        self.assertEqual(validate_batch(self.batch,review,self.census)['semantic_records'],17)
        r=dict(self.batch,effects=self.batch['effects'])
        self.assertEqual(audit(r)['native_candidate_identities'],40)
        broken=copy.deepcopy(self.batch)
        c=next(r for r in broken['effects'] if r['scalable_parameter_candidates'])['scalable_parameter_candidates'][0]
        c['native_literal_numeric_site_binding']['native_value']+=1
        with self.assertRaises(AssertionError):validate_batch(broken,review,self.census)

    def test_obsolete_overloads_have_no_native_callers_or_base_dispatch(self):
        calls={i['operand'] for m in self.census['methods'] for i in decode_sites(self.census,m,'calls')}
        handles={s for b in self.census['registration_bootstraps'] for s in [b['handle']]+b['arguments'] if isinstance(s,str)}
        old='(Lnet/minecraft/world/entity/LivingEntity;Lnet/minecraft/world/entity/ai/attributes/AttributeMap;I)V'
        for cls,names in [('EffectClinging',['removeAttributeModifiers']),('EffectFleetFooted',['removeAttributeModifiers']),('EffectPowerDown',['addAttributeModifiers','removeAttributeModifiers']),('EffectDebilitatingSting',['addAttributeModifiers','removeAttributeModifiers'])]:
            for name in names:
                m=method('effect/'+cls,name)
                self.assertEqual(m['descriptor'],old)
                symbol=P+'effect/'+cls+'.'+name+old
                self.assertNotIn(symbol,calls|handles)
        raw=read_json(OUT/'vanilla-evidence/alexsmobs-effect-dispatch.json')
        base=next(c for c in raw['classes'] if c['class_name'].endswith('/MobEffect'))
        descriptors={m['obfuscated_descriptor'] for m in base['declared_methods'] if m['name'] in ['addAttributeModifiers','removeAttributeModifiers']}
        self.assertEqual(descriptors,{'(Lbut;)V','(Lbut;I)V'})

    def test_sting_and_flu_ignore_damage_return_before_summoning(self):
        for cls in ['EffectDebilitatingSting','EffectEnderFlu']:
            ins=method('effect/'+cls,'applyEffectTick')['instructions']
            hits=[n for n,i in enumerate(ins) if '.hurt(' in str(i['operand'])]
            self.assertTrue(hits)
            self.assertTrue(all(ins[n+1]['opcode']=='0x57' for n in hits))
            self.assertTrue(any('EntityType.create' in str(i['operand']) for i in ins[hits[-1]+1:]))
        ctor=method('effect/EffectDebilitatingSting','<init>')['instructions']
        self.assertTrue(any('/Attributes.MOVEMENT_SPEED' in str(i['operand']) for i in ctor))
        self.assertFalse(any('ARTHROPOD' in str(i['operand']) for i in ctor))

    def test_soulsteal_precedes_later_zeroing_and_uses_causing_entity(self):
        ins=method('event/ServerEvents','onLivingDamageEvent')['instructions']
        n=next(n for n,i in enumerate(ins) if '.heal(' in str(i['operand']))
        self.assertTrue(any('DamageSource.getEntity()' in str(i['operand']) for i in ins[:n]))
        self.assertFalse(any('getDirectEntity' in str(i['operand']) for i in ins))
        self.assertTrue(any('.setNewDamage(' in str(i['operand']) for i in ins[n+1:]))
        self.assertEqual([(i['offset'],i['operand']) for i in ins if i['offset'] in [80,85,99,104,105]],[(80,.25),(85,.25),(99,2.0),(104,2),(105,2)])

    def test_fleet_counter_and_modifier_are_shared_not_per_entity(self):
        ins=method('effect/EffectFleetFooted','applyEffectTick')['instructions']
        self.assertTrue(any('.addPermanentModifier(' in str(i['operand']) for i in ins))
        self.assertTrue(any('.removeEffectAfterI' in str(i['operand']) for i in ins))
        self.assertFalse(any('getPersistentData' in str(i['operand']) for i in ins))
        self.assertEqual(next(i['operand'] for i in ins if i['offset']==104),5)

    def test_power_down_casts_holder_without_dereferencing(self):
        for name,cast in [('onGetStarBrightness',47),('onFogDensity',108)]:
            ins=method('client/event/ClientEvents',name,C)['instructions'];n=next(n for n,i in enumerate(ins) if i['offset']==cast)
            self.assertEqual(ins[n]['opcode'],'0xc0')
            self.assertEqual(ins[n]['operand'],P+'effect/EffectPowerDown')
            self.assertEqual(ins[n-1]['operand'],'net/minecraft/world/effect/MobEffectInstance.getEffect()Lnet/minecraft/core/Holder;')
        row=self.rows['alexsmobs:power_down']
        self.assertEqual(len(row['scalable_parameter_candidates']),1)
        self.assertIn('class-cast failure',row['actual_behavior'])

    def test_partial_event_proofs_do_not_close_unreviewed_branches(self):
        for row in self.rows.values():
            for p in row['implementation']:
                if p['entry']==P+'event/ServerEvents.class':self.assertTrue(p.get('partial_contract'))


if __name__=='__main__':unittest.main()
