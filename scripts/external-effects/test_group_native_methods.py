"""Equivalence routing must preserve distinctions that change native behavior."""
import unittest
from copy import deepcopy
from group_native_methods import signature


class GroupTests(unittest.TestCase):
    def test_self_only_and_sensitive_inputs(self):
        w=dict(class_name='a/Actor',superclass='minecraft/Mob')
        m=dict(name='tick',descriptor='()V',instructions=[
            dict(offset=0,opcode='0xb6',operand='a/Actor.attack()V',local_index=1),
            dict(offset=3,opcode='0x99',operand=None,branch_target=10)],
            exception_handlers=[dict(start=0,end=3,handler=10,catch_type='java/lang/Error')])
        base=signature(w,m,1,{'0':{'handle':{'reference_kind':6},'arguments':[2]}})
        other=deepcopy(m);other['instructions'][0]['operand']='b/Actor.attack()V'
        self.assertEqual(base,signature(dict(w,class_name='b/Actor'),other,1,base['bootstraps']))
        for field,value in [('local_index',2),('operand','foreign/Actor.attack()V')]:
            other=deepcopy(m);other['instructions'][0][field]=value
            self.assertNotEqual(base,signature(w,other,1,base['bootstraps']))
        other=deepcopy(m);other['instructions'][1]['branch_target']=11
        self.assertNotEqual(base,signature(w,other,1,base['bootstraps']))
        other=deepcopy(m);other['exception_handlers'][0]['catch_type']='java/lang/Exception'
        self.assertNotEqual(base,signature(w,other,1,base['bootstraps']))
        self.assertNotEqual(base,signature(w,m,9,base['bootstraps']))
        self.assertNotEqual(base,signature(w,m,1,{'0':{'handle':{'reference_kind':5},'arguments':[2]}}))
        self.assertNotEqual(base,signature(w,m,1,{'0':{'handle':{'reference_kind':6},'arguments':[3]}}))


if __name__=='__main__':unittest.main()
