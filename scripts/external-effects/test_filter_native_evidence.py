"""Selection conservation and explicit incomplete-selection rejection, no semantics."""
import json
from pathlib import Path
import subprocess
import unittest

FILTER=Path(__file__).with_name('filter_native_evidence.jq')

class OutputFilterTests(unittest.TestCase):
    def setUp(self):
        self.method=dict(name='hurt',descriptor='(F)Z',code_sha256='a'*64,
            instructions=[dict(offset=0,opcode='0x2a',operand=None,local_index=0),
                dict(offset=1,opcode='0xb6',operand='owner.Native.hurt(F)Z')],
            annotations=[dict(descriptor='ExactAnnotation')],exception_handlers=[])
        self.raw=dict(witnesses=[dict(entry='A.class',class_name='A',superclass='Native',
            interfaces=['OwnerInterface'],id='a',mod_key='mod',jar_sha256='b'*64,
            entry_sha256='c'*64,methods=[self.method,dict(name='display',descriptor='()V',instructions=[])])])
        self.scope=[dict(entry='A.class',method='hurt',descriptor='(F)Z')]
    def run_filter(self,scope):
        return subprocess.run(['jq','-c','--argjson','scope',json.dumps(scope),'--arg','source','raw.json',
            '-f',str(FILTER)],input=json.dumps(self.raw),text=True,capture_output=True)
    def test_preserves_full_selected_method_and_identity(self):
        p=self.run_filter(self.scope);self.assertEqual(p.returncode,0,p.stderr)
        d=json.loads(p.stdout);self.assertEqual(d['selected'][0]['method'],self.method)
        self.assertEqual(d['selected'][0]['interfaces'],['OwnerInterface'])
        self.assertEqual(d['selected'][0]['jar_sha256'],'b'*64)
        self.assertEqual(d['omitted_methods'],1)
        self.assertTrue(d['selection_complete']);self.assertFalse(d['instructions_truncated'])
        self.assertFalse(d['omitted_data_proves_absence'])
    def test_unknown_or_wrong_descriptor_fails_explicitly(self):
        scope=[dict(self.scope[0],descriptor='()V')]
        p=self.run_filter(scope);self.assertNotEqual(p.returncode,0)
        self.assertIn('incomplete',p.stderr)
    def test_duplicate_scope_fails_explicitly(self):
        p=self.run_filter(self.scope*2);self.assertNotEqual(p.returncode,0)

if __name__=='__main__':unittest.main()
