"""Residual closure, source facts and native reachability regression tests."""
import copy
from collections import Counter
import hashlib
import json
import subprocess
import unittest

from catalog_common import OUT, ROOT, read_json
from audit_catalog_integrity import EvidenceIndex
from collect_cataclysm_family import collect as collect_methods
from collect_catalog_reachability import collect as collect_callers
from refresh_catalog_views import refresh
from validate_current_integrity import validate_cataclysm_repairs


def validate_closure(note, review, evidence, reachability):
    frozen=read_json(OUT/'cataclysm-r2k33a-coverage-audit.json')
    previous=json.loads(subprocess.check_output(['git','show',note['starting_sha']+':'+
        (OUT/'cataclysm-coverage-audit.json').relative_to(ROOT).as_posix()],cwd=ROOT))
    pending={(r['entry'],r['method'],r['descriptor']):r for r in previous['residual_methods']
             if r['disposition']=='PENDING_TARGETED_RECONCILIATION'}
    bindings=note['reconciliation_boundaries']
    assert len(bindings)==len(pending)==47
    assert len({(r['entry'],r['method'],r['descriptor']) for r in bindings})==47
    index=EvidenceIndex();index.files[note['evidence_file']]=evidence
    ids={r['id'] for r in review['effects']}
    for row in bindings:
        key=row['entry'],row['method'],row['descriptor']
        old=pending[key]
        assert row['reason'] and row['disposition']!='PENDING_TARGETED_RECONCILIATION'
        assert set(row['mechanic_ids'])<=ids
        proof=row['implementation'][0];_,w=index.witness(proof,dict(id=str(key)))
        method=next(m for m in w['methods'] if (m['name'],m['descriptor'])==key[1:])
        assert method['code_sha256']==old['code_sha256']
        hits={(i['offset'],str(i.get('operand'))) for i in method['instructions']}
        assert all((h['offset'],str(h.get('operand'))) in hits for h in old['hits_to_reconcile'])
    audit=read_json(OUT/'cataclysm-coverage-audit.json')
    assert len(audit['residual_methods'])==len(frozen['residual_methods'])
    for old,new in zip(frozen['residual_methods'],audit['residual_methods']):
        assert all(old[k]==new[k] for k in ('entry','method','descriptor','code_sha256'))
    assert sum(audit['summary']['counts_by_disposition'].values())==572
    assert not audit['summary']['pending_methods_by_domain']
    assert audit['status']==review['status']=='COMPLETE'
    # Registration bootstrap, not an invocation-only absence argument.
    handles=reachability['method_reference_bootstraps']
    assert any('Bolt_strike_Entity.<init>' in str(h['arguments']) and h['entry'].endswith('ModEntities.class') for h in handles)
    assert any('The_Watcher_Entity.<init>' in str(h['arguments']) and h['entry'].endswith('ModEntities.class') for h in handles)
    for row in bindings:
        if row['disposition']!='EXCLUDED_NO_NATIVE_CALLER':
            continue
        owner=row['entry'].removesuffix('.class')
        name='<init>' if any(t in owner for t in ['AbstractElemental_Spear','MoveControllerSink','AnimationMonster/AI/']) else row['method']
        token=owner+'.'+name+'('
        assert not any(token in str(c['invocations']) and c['entry']!=row['entry'] for c in reachability['direct_callers'])
        assert not any(token in str(h['arguments']) and h['entry']!=row['entry'] for h in handles)
        assert not any(c['superclass']==owner for c in reachability['direct_subclasses'])


class ClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.note=read_json(OUT/'cataclysm-r2k34-integrity-closure.json')
        cls.review=read_json(OUT/'mod-reviews/cataclysm.json')
        cls.evidence=read_json(OUT/cls.note['evidence_file'])
        cls.reachability=read_json(OUT/cls.note['reachability_file'])
        cls.rows={r['id']:r for r in cls.review['effects']}

    def test_exact_complete_residual_accounting(self):
        validate_closure(self.note,self.review,self.evidence,self.reachability)

    def test_reject_dropped_duplicated_or_falsified_boundary(self):
        for mutation in ('missing','duplicate','wrong_hash','wrong_live_id'):
            note=copy.deepcopy(self.note);evidence=copy.deepcopy(self.evidence)
            if mutation=='missing':note['reconciliation_boundaries'].pop()
            elif mutation=='duplicate':note['reconciliation_boundaries'][1]=note['reconciliation_boundaries'][0]
            elif mutation=='wrong_live_id':note['reconciliation_boundaries'][0]['mechanic_ids']=['cataclysm:invented']
            else:
                witness=next(w for w in evidence['witnesses'] if w['entry'].endswith('/The_Watcher_Entity.class'))
                next(m for m in witness['methods'] if m['name']=='hurt')['code_sha256']='0'*64
            with self.subTest(mutation=mutation), self.assertRaises(AssertionError):
                validate_closure(note,self.review,evidence,self.reachability)

    def test_registry_method_reference_cannot_disappear(self):
        reach=copy.deepcopy(self.reachability)
        reach['method_reference_bootstraps']=[]
        with self.assertRaises(AssertionError):validate_closure(self.note,self.review,self.evidence,reach)

    def test_excluded_helper_cannot_have_hidden_direct_caller(self):
        reach=copy.deepcopy(self.reachability)
        reach['direct_callers'].append(dict(entry='native-live-caller.class',invocations=[dict(operand=
            'com/github/L_Ender/cataclysm/items/The_Immolator.yall(Lnet/minecraft/world/entity/LivingEntity;)V')]))
        with self.assertRaises(AssertionError):validate_closure(self.note,self.review,self.evidence,reach)

    def test_watcher_native_hurt_return_and_bite_formula(self):
        w=next(w for w in self.evidence['witnesses'] if w['entry'].endswith('/The_Watcher_Entity.class'))
        hurt=next(m['instructions'] for m in w['methods'] if m['name']=='hurt')
        hit=next(i for i,x in enumerate(hurt) if '.hurt(' in str(x['operand']))
        self.assertEqual(hurt[hit-1]['operand'],1000.0)
        self.assertEqual(hurt[hit+1]['opcode'],'0x57')
        self.assertEqual(hurt[hit+2]['operand'],1)
        tick=next(m['instructions'] for m in w['methods'] if m['name']=='tick')
        self.assertTrue(any(x['opcode']=='0x8e' and tick[i+1]['opcode']=='0x86' for i,x in enumerate(tick[:-1])))
        self.assertIn('float(int(current ATTACK_DAMAGE))',self.rows['cataclysm:watcher_bite_payload']['actual_behavior'])
        self.assertEqual(self.rows['cataclysm:watcher_laser_delivery']['reused_payload_ids'][0],'cataclysm:laser_contact_payload')

    def test_food_constants_match_exact_factory_arguments(self):
        w=next(w for w in self.evidence['witnesses'] if w['entry'].endswith('/ModItems.class'))
        expected={'lambda$static$224':[('POISON',60),('CONFUSION',60),('WATER_BREATHING',4800)],
                  'lambda$static$225':[('REGENERATION',100)],
                  'lambda$static$226':[('REGENERATION',100),('EFFECTBLESSING_OF_AMETHYST',1800)]}
        for name,values in expected.items():
            source=w
            if name=='lambda$static$226':
                source=next(w for w in read_json(OUT/'native-evidence/cataclysm-ghost-fear.json')['witnesses']
                            if w['entry'].endswith('/ModItems.class'))
            body=next(m['instructions'] for m in source['methods'] if m['name']==name)
            found=[]
            for i,x in enumerate(body):
                if '/MobEffects.' in str(x['operand']) or '/ModEffect.EFFECTBLESSING' in str(x['operand']):
                    found.append((str(x['operand']).split('.')[-1].split('Lnet')[0],body[i+1]['operand']))
                    self.assertEqual(body[i+2]['operand'],0)
                    self.assertEqual(body[i+4]['operand'],1.0)
            self.assertEqual(found,values)
        ordinary=self.rows['cataclysm:crab_food_effect_delivery']['source_variants'][0]
        self.assertEqual(ordinary['components'],['REGENERATION'])

    def test_merged_quake_keeps_two_distinct_native_clocks(self):
        row=self.rows['cataclysm:monstrosity_earthquake_payload']
        component=next(c for c in row['components'] if c['primitive']=='ATTACK_SEQUENCE')
        self.assertEqual(component['numerical_parameters'],{'state3_trigger_tick':19,'state4_trigger_tick':17})
        self.assertEqual(len(row['source_variants']),2)

    def test_registry_only_bolt_not_invented_gameplay_producer(self):
        row=self.rows['cataclysm:registered_bolt_strike_payload']
        self.assertEqual(row['reachability'],'REGISTERED_NO_ORDINARY_NATIVE_PRODUCER')
        self.assertEqual(row['components'][0]['numerical_parameters']['default_damage'],0)
        self.assertFalse(row['scalable_parameter_candidates'])

    def test_native_transport_is_clientbound_and_not_another_attack(self):
        w=next(w for w in self.evidence['witnesses'] if w['entry'].endswith('/Cataclysm.class'))
        body=next(m['instructions'] for m in w['methods'] if m['name']=='setupPackets')
        calls=[str(i['operand']) for i in body if 'PayloadRegistrar.playTo' in str(i['operand'])]
        self.assertEqual(len(calls),2)
        self.assertTrue(all('.playToClient(' in call for call in calls))
        self.assertTrue(all('MessageCharge' not in row['id'] and 'MessageMovePlayer' not in row['id'] for row in self.review['effects']))

    def test_protected_native_artifacts_and_explicit_canonical_repairs(self):
        validate_cataclysm_repairs()

    def test_locked_status_and_shared_packages_are_actually_canonical(self):
        for rid in ['shared_hurt','shared_heal','shared_effect_admission','shared_home','shared_life',
                    'shared_death','stun','stun_skull','stun_post_removal','ghost_form','ghost_sickness',
                    'abyssal_fear','amethyst_blessing','abyssal_status_dot','abyssal_burn_teleport',
                    'blazing_brand','bone_fracture','desert_curse','wetness','guardian_incoming_admission',
                    'guardian_helmet_phase','guardian_helmet_blast','guardian_attack_teleports']:
            self.assertIn('cataclysm:'+rid,self.rows)
        self.assertEqual(self.rows['cataclysm:blazing_brand']['primary_classification'],'VANILLA_COMPOSITE')
        self.assertEqual(self.rows['cataclysm:bone_fracture']['primary_classification'],'VANILLA_COMPOSITE')
        core=self.rows['cataclysm:abyssal_status_dot']
        self.assertEqual({p for c in core['scalable_parameter_candidates'] for p in c['parameters']},
                         {'burn_requested_damage','curse_requested_damage'})
        aliases={a['original_id']:a['canonical_ids'] for a in self.review['semantic_aliases']}
        self.assertEqual(aliases['cataclysm:cursium_rebirth'],['cataclysm:global_gear_cursium_locked_revival'])
        self.assertNotIn('cataclysm:monstrous',self.rows)

    def test_byte_identical_view_and_count_regeneration(self):
        files=['effect-catalog.json','effect-sources.json','delivery-path-matrix.json',
            'behavior-primitives.json','vanilla-comparison.json','mod-completion-ledger.json',
            'cataclysm-coverage-audit.json','cataclysm-classification-summary.json','cataclysm-r2k34-integrity-closure.json']
        before={f:(OUT/f).read_bytes() for f in files};refresh()
        self.assertTrue(all((OUT/f).read_bytes()==before[f] for f in files))


if __name__=='__main__':unittest.main()
