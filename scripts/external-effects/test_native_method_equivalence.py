"""Normalization must not hide meaningful native differences."""
import unittest
from compare_native_methods import normalized


class NativeMethodEquivalenceTests(unittest.TestCase):
    def test_self_owner_only(self):
        a=[dict(offset=2,opcode='0xb5',operand='a/Arrow.levelI'),
           dict(offset=5,opcode='0xc0',operand='a/Arrow'),
           dict(offset=8,opcode='0xb6',operand='a/ArrowOther.hurt()V'),
           dict(offset=11,opcode='0xb6',operand='a/Arrow$Child.hurt()V')]
        result=normalized(a,'a/Arrow')
        self.assertEqual([i['operand'] for i in result],
                         ['SELF.levelI','SELF','a/ArrowOther.hurt()V','a/Arrow$Child.hurt()V'])
        self.assertEqual(a[0]['operand'],'a/Arrow.levelI')

    def test_literals_branches_locals_and_foreign_owners_remain_distinct(self):
        body=[dict(offset=3,opcode='0x19',operand=None,local_index=2),
              dict(offset=5,opcode='0x9a',operand=None,branch_target=17),
              dict(offset=8,opcode='0x10',operand=3),
              dict(offset=10,opcode='0xb6',operand='minecraft/Arrow.hurt()V')]
        for n,key,value in [(0,'local_index',3),(1,'branch_target',18),
                            (2,'operand',4),(3,'operand','minecraft/OtherArrow.hurt()V')]:
            changed=[dict(i) for i in body];changed[n][key]=value
            self.assertNotEqual(normalized(body,'own/Arrow'),normalized(changed,'own/OtherArrow'))


if __name__ == '__main__':unittest.main()
