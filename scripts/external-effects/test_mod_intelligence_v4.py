"""Independent required-field oracles and fail-closed adaptive scope checks."""
import copy
import hashlib
import json
from pathlib import Path
import unittest

import mod_intelligence as mi
from mod_intelligence_adaptive import PROFILE_SCHEMA, fingerprint
import test_mod_intelligence_v3 as fixtures


def required(plan, kind):
    return [i for i in plan['information']['REQUIRED'] if i.get('kind') == kind]


class AdaptiveScopeTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ChangePlanTests(methodName='runTest')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.f = self.fixture.f
        self.repo = self.fixture.fixture.repo
        self.profile_file = self.repo/'profiles.json'
        self.capture_profile()

    def capture_profile(self):
        c = mi.Catalog(self.f.root)
        p = c.plan('demo:bite', self.fixture.request, 'demo', repo_root=self.repo, links_file=self.fixture.links)
        site = p['source_locations'][0]
        self.profile = dict(id='explicit-literal', scope='SELECTED_LITERAL_ONLY', target='demo:bite',
            parameter={k:p['selected_parameter'][k] for k in ('primitive','name','component_index')},
            catalog_pins=dict(c.index.file_hashes), site={k:site[k] for k in
                ('file','entry','method','descriptor','code_sha256','literal')},
            required_components=[0], context_components=[], dependency_mode='FULL',
            behavior_quotes=[p['mechanics'][0]['current_behavior']], excluded_behavior_quotes=[],
            required_contract_paths=['/contract','/facts'], excluded_contract_paths=['/inspection_status'])
        self.write_profile()

    def write_profile(self):
        self.profile_file.write_text(json.dumps(dict(schema=PROFILE_SCHEMA, profiles=[self.profile])))

    def plan(self, profile_file=None):
        return mi.Catalog(self.f.root).adaptive_plan('demo:bite', self.fixture.request, 'demo',
            repo_root=self.repo, links_file=self.fixture.links, profile_file=profile_file or self.profile_file)

    def test_required_site_contract_and_chain_remain_connected(self):
        plan = self.plan()
        site, = required(plan, 'CURRENT_LITERAL_SITE')
        self.assertEqual((site['literal']['offset'], site['literal']['current_value']), (4,4.0))
        self.assertEqual(site['classification'], 'VERIFIED')
        self.assertEqual(required(plan,'RECORDED_CONTRACT')[0]['record']['contract']['hurt_return_dependency'],
                         'heal requires accepted hurt')
        ids = {i['id'] for i in plan['information']['REQUIRED']}
        for item in plan['information']['REQUIRED']:
            self.assertTrue(set(item.get('depends_on', [])) <= ids)
        for chain in plan['reasoning_chain']:
            for key in ('existing_behavior','preserved_constraints','implementation_locations','validation_requirements'):
                self.assertTrue(chain[key])
                self.assertTrue(set(chain[key]) <= ids)
        for category, rows in plan['information'].items():
            self.assertTrue(all(r['relevance'] == category for r in rows))

    def test_static_warning_bundle_preserves_topics_and_dynamic_gaps(self):
        plan=self.plan()
        bounds=next(i for i in plan['information']['UNKNOWN'] if i.get('kind')=='UNVERIFIED_BOUNDARIES')
        for topic in ('RUNTIME_EFFECT','TEST_COVERAGE','PRODUCTION_SOURCE_MAPPING','NUMERIC_BINDING_SCOPE'):
            self.assertIn(topic,bounds['topics'])
        self.assertEqual(len(bounds['source_refs']),len(bounds['topics']))
        behavior=required(plan,'REQUESTED_BEHAVIOR')[0]
        self.assertEqual(behavior['request_ref'],'/requested_behavior')
        self.assertEqual(plan['request']['requested_behavior'],self.fixture.request['requested_behavior'])

    def test_dynamic_warning_fields_are_never_bundled_away(self):
        catalog=mi.Catalog(self.f.root)
        original=catalog.plan('demo:bite',self.fixture.request,'demo',repo_root=self.repo,links_file=self.fixture.links)
        warning=dict(id='dynamic:runtime',classification='UNKNOWN',kind='RUNTIME_EFFECT',
                     reason='Additional task-specific unresolved evidence',file='runtime.json')
        original['risks_and_questions'].append(warning)
        plan=mi.adaptive_plan(catalog,original,self.repo,self.profile_file,mi.require)
        retained=next(i for i in plan['information']['UNKNOWN'] if i['id']=='dynamic:runtime')
        self.assertEqual(retained,dict(warning,relevance='UNKNOWN'))

    def test_profiles_do_not_filter_by_semantic_names(self):
        self.f.row['binary_parameters'] = {'rendering': 'hurt acceptance is required'}
        self.f.row['components'][0]['sounds'] = {'admission_gate': 'required numerical callback gate'}
        self.f.write('mod-reviews/demo.json',self.f.review)
        self.fixture.links,self.fixture.document = self.fixture.fixture.mapping()
        self.capture_profile()
        plan = self.plan()
        contract = required(plan,'RECORDED_CONTRACT')[0]['record']['contract']
        self.assertEqual(contract['binary_parameters']['rendering'],'hurt acceptance is required')
        component = required(plan,'RECORDED_COMPONENT')[0]['record']
        self.assertEqual(component['sounds']['admission_gate'],'required numerical callback gate')

    def test_gates_cannot_be_marked_exclude(self):
        self.profile['excluded_contract_paths'] = ['/contract/hurt_return_dependency']
        self.write_profile()
        with self.assertRaises(mi.CatalogError) as raised:
            self.plan()
        self.assertEqual(raised.exception.code,2)

    def test_selected_component_cannot_be_demoted(self):
        self.profile.update(required_components=[],context_components=[0])
        self.write_profile()
        with self.assertRaises(mi.CatalogError) as raised:
            self.plan()
        self.assertEqual(raised.exception.code,2)

    def test_shared_method_consumer_cannot_be_demoted(self):
        self.f.row['components'].append(dict(primitive='OTHER',numerical_parameters={'other':4.0}))
        candidate=copy.deepcopy(self.f.row['scalable_parameter_candidates'][0])
        candidate.update(primitive='OTHER',parameters=['other'])
        self.f.row['scalable_parameter_candidates'].append(candidate)
        self.f.write('mod-reviews/demo.json',self.f.review)
        self.fixture.links,self.fixture.document = self.fixture.fixture.mapping()
        self.capture_profile()
        self.profile['context_components']=[1]
        self.write_profile()
        with self.assertRaises(mi.CatalogError) as raised:
            self.plan()
        self.assertEqual(raised.exception.code,2)

    def test_explicit_dependency_requires_full_contract(self):
        self.f.row['components'][0]['external_dependency_contract']='demo:support'
        self.f.write('mod-reviews/demo.json',self.f.review)
        self.fixture.links,self.fixture.document = self.fixture.fixture.mapping()
        self.capture_profile()
        self.profile['dependency_mode']='IDENTITY'
        self.write_profile()
        with self.assertRaises(mi.CatalogError) as raised:
            self.plan()
        self.assertEqual(raised.exception.code,2)

    def test_stale_pin_or_literal_site_rejects_projection(self):
        original=copy.deepcopy(self.profile)
        for mutate in ('pin','site'):
            self.profile=copy.deepcopy(original)
            if mutate=='pin': self.profile['catalog_pins']['mod-reviews/demo.json']='f'*64
            else: self.profile['site']['literal']['offset']=5
            self.write_profile()
            with self.subTest(mutate=mutate), self.assertRaises(mi.CatalogError) as raised:
                self.plan()
            self.assertEqual(raised.exception.code,3)

    def test_absent_profile_preserves_full_constraints_and_never_excludes(self):
        self.profile_file.write_text(json.dumps(dict(schema=PROFILE_SCHEMA,profiles=[])))
        plan=self.plan()
        self.assertFalse(plan['information']['EXCLUDE'])
        self.assertIsNone(plan['scope']['profile_id'])
        contract=required(plan,'RECORDED_CONTRACT')[0]['record']
        self.assertEqual(contract['contract']['hurt_return_dependency'],'heal requires accepted hurt')
        self.assertTrue(any(i.get('kind')=='SCOPE_UNRESOLVED' for i in plan['information']['UNKNOWN']))

    def test_invalid_source_cannot_be_hidden_by_projection(self):
        self.f.row['components'][0]['numerical_parameters']['damage']=5.0
        self.f.write('mod-reviews/demo.json',self.f.review)
        with self.assertRaises(mi.CatalogError) as raised:
            self.plan()
        self.assertEqual(raised.exception.code,2)

    def test_malformed_profiles_and_path_escape_are_errors(self):
        self.profile_file.write_text(json.dumps(dict(schema=PROFILE_SCHEMA,profiles=[None])))
        with self.assertRaises(mi.CatalogError) as raised:
            self.plan()
        self.assertEqual(raised.exception.code,2)
        with self.assertRaises(mi.CatalogError) as raised:
            self.plan(self.repo/'../outside.json')
        self.assertEqual(raised.exception.code,2)

    def test_cli_budget_and_errors_use_v4_schema_without_partial_data(self):
        self.fixture.request_file.write_text(json.dumps(self.fixture.request))
        arguments=('plan','--adaptive','--request',str(self.fixture.request_file))
        code,result=self.f.invoke(*arguments,'--budget-bytes','1')
        self.assertEqual(code,2)
        self.assertEqual(result['schema'],mi.ADAPTIVE_SCHEMA)
        self.assertNotIn('data',result)
        self.assertGreater(result['budget']['required_bytes'],1)
        code,result=self.f.invoke(*arguments,'--expect-version','9.9')
        self.assertEqual(code,3)
        self.assertEqual(result['schema'],mi.ADAPTIVE_SCHEMA)


class CompletedAdaptiveOracles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plans={};cls.original={}
        root=mi.ROOT/'scripts/external-effects/examples/change_requests'
        for name in ('cockroach_heal','sugar_rush_movement','sugar_rush_dependency','sugar_rush_ambiguous'):
            request=json.loads((root/(name+'.json')).read_text())
            c=mi.Catalog()
            cls.original[name]=c.plan(request['target'],request,request['target'].split(':')[0])
            cls.plans[name]=c.adaptive_plan(request['target'],request,request['target'].split(':')[0])

    def test_local_numeric_oracle_preserves_literal_and_healing_admission(self):
        plan=self.plans['cockroach_heal'];original=self.original['cockroach_heal']
        self.assertEqual(required(plan,'CURRENT_LITERAL_SITE')[0],dict(original['source_locations'][0],relevance='REQUIRED'))
        self.assertEqual(required(plan,'RECORDED_COMPONENT')[0]['record'],original['preserved_constraints'][2]['record'])
        behavior=' '.join(required(plan,'CURRENT_MECHANIC')[0]['current_behavior'])
        for clause in ('maraca','craftingremainder','FOOD component ORbreedtag','max/death/return unchanged'):
            self.assertIn(clause,behavior)

    def test_movement_oracle_preserves_both_branches_axes_and_slow_fall_gates(self):
        plan=self.plans['sugar_rush_movement'];original=self.original['sugar_rush_movement']
        components={i['component_index']:i['record'] for i in required(plan,'RECORDED_COMPONENT')}
        self.assertEqual(set(components),{1,2})
        self.assertEqual(components[1]['numerical_parameters'],dict(upward_y_factor=0.85,downward_y_factor=0.45))
        self.assertEqual(components[2]['native_flags'],[False,False,False])
        contract=required(plan,'RECORDED_CONTRACT')[0]['record']['contract']
        original_contract=next(i['record']['contract'] for i in original['preserved_constraints'] if i['kind']=='RECORDED_CONTRACT')
        for gate in ('tick','slow_fall'):
            self.assertEqual(contract['binary_parameters'][gate],original_contract['binary_parameters'][gate])
        for key in ('source_actor','hurt_return_dependency','lifecycle'):
            self.assertEqual(contract[key],original_contract[key])
        site=required(plan,'CURRENT_LITERAL_SITE')[0]
        self.assertEqual((site['literal']['offset'],site['consumer_offset']),(51,55))
        self.assertEqual(site['recorded_binding']['native_literal_vector_components_binding']['x'],1.0)
        self.assertEqual(site['recorded_binding']['native_literal_vector_components_binding']['z'],1.0)
        dependency=required(plan,'RECORDED_OBLIGATION')[0]['record']
        self.assertEqual(dependency['artifact'],original['dependencies'][0]['record']['artifact'])
        self.assertEqual(dependency['validation_state'],original['dependencies'][0]['record']['validation_state'])
        behavior=' '.join(required(plan,'CURRENT_MECHANIC')[0]['current_behavior'])
        self.assertNotIn('native sound',behavior)
        self.assertTrue(plan['information']['EXCLUDE'])

    def test_dependency_oracle_retains_coupled_reads_and_complete_contract(self):
        plan=self.plans['sugar_rush_dependency'];original=self.original['sugar_rush_dependency']
        site=required(plan,'CURRENT_LITERAL_SITE')[0]
        binding=site['recorded_binding']
        self.assertEqual(site['literal']['offset'],181)
        self.assertEqual(binding['native_literal_numeric_input_binding']['read_offsets'],[196,201])
        self.assertEqual(binding['native_local_value_context']['request_offset'],202)
        self.assertEqual(required(plan,'RECORDED_OBLIGATION')[0]['record'],original['dependencies'][0]['record'])
        self.assertTrue(required(plan,'COUPLED_NATIVE_USES'))
        components={i['component_index']:i['record'] for i in required(plan,'RECORDED_COMPONENT')}
        self.assertEqual(set(components),{4})
        self.assertEqual(components[4]['native_protocol_context']['third_constructor_double'],10.0)
        self.assertEqual(len(plan['evidence']),len(original['evidence']))

    def test_ambiguous_oracle_asserts_no_exclusion_or_implementation(self):
        plan=self.plans['sugar_rush_ambiguous']
        self.assertEqual(plan['readiness'],'SELECTION_REQUIRED')
        self.assertEqual(plan['scope']['sufficiency'],'NOT_ESTABLISHED')
        self.assertFalse(plan['information']['EXCLUDE'])
        self.assertFalse(required(plan,'PROPOSED_EDIT'))
        selection=next(i for i in plan['information']['UNKNOWN'] if i.get('kind')=='PARAMETER_SELECTION')
        self.assertEqual(selection['candidates'],next(i['candidates'] for i in self.original['sugar_rush_ambiguous']['risks_and_questions'] if i['kind']=='PARAMETER_SELECTION'))

    def test_restore_snapshot_and_source_pins_are_retained(self):
        for name,plan in self.plans.items():
            with self.subTest(name=name):
                self.assertEqual(plan['restore']['v3_plan_fingerprint'],fingerprint(self.original[name]))
                self.assertEqual(plan['repository_inputs'],self.original[name]['repository_inputs'])
                sources={s['id'] for s in plan['evidence_sources']}
                self.assertTrue(all(e['source_id'] in sources for e in plan['evidence']))


if __name__=='__main__':
    unittest.main()
