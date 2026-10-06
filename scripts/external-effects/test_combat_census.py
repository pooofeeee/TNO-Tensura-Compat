"""Focused census reduction tests; no semantic classification from names."""
import unittest
from collect_combat_census import structural_disposition, pack_sites, decode_sites


class ReductionTests(unittest.TestCase):
    def method(self,name='irrelevant',access=0,code=b'code'):
        return dict(name=name,access=access,code=code)

    def test_name_alone_never_proves_a_mechanic(self):
        self.assertEqual(structural_disposition(self.method('DamageMonster'),[],[]),'CALL_GRAPH_CONTEXT')

    def test_admission_override_stays_pending_without_a_damage_call(self):
        self.assertEqual(structural_disposition(self.method('isInvulnerableTo'),[],[]),'PENDING_SEMANTIC_REVIEW')

    def test_native_hit_stays_pending_in_utility_named_method(self):
        self.assertEqual(structural_disposition(self.method(),[],[dict(operand='LivingEntity.hurt')]),'PENDING_SEMANTIC_REVIEW')

    def test_field_access_is_context_not_numeric_or_exclusion(self):
        body=[dict(opcode=o) for o in ['0x2a','0xb4','0xae']]
        self.assertEqual(structural_disposition(self.method('getDamage'),body,[body[1]]),'FIELD_ACCESS_CONTEXT')

    def test_only_actual_bridge_flags_get_bridge_context(self):
        self.assertEqual(structural_disposition(self.method(access=0x1040),[],[]),'SYNTHETIC_BRIDGE_CONTEXT')
        self.assertEqual(structural_disposition(self.method(access=0x1000),[],[]),'CALL_GRAPH_CONTEXT')

    def test_abstract_signature_is_retained(self):
        self.assertEqual(structural_disposition(self.method('hurt',code=b''),[],[]),'DECLARATION_CONTEXT')

    def test_symbol_interning_preserves_repeated_distinct_consumers(self):
        sites=[dict(offset=4,opcode='0xb6',operand='Entity.hurt()'),
               dict(offset=10,opcode='0xb6',operand='Entity.hurt()')]
        doc=pack_sites(dict(methods=[dict(hits=sites[:],calls=sites[:])]))
        self.assertEqual(decode_sites(doc,doc['methods'][0]),sites)
        self.assertEqual(len(doc['symbols']),1)
        self.assertEqual(len(doc['methods'][0]['calls']),2)


if __name__=='__main__':unittest.main()
