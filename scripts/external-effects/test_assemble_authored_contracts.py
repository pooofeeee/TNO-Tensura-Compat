"""Avoid repeated large packet reads while retaining distinct packet identities."""
import unittest
from unittest.mock import patch
from assemble_authored_contracts import render

class PacketCacheTests(unittest.TestCase):
    def test_each_selected_packet_loaded_once(self):
        a=dict(witnesses=[dict(entry='Actor.class',id='a',methods=[])])
        b=dict(witnesses=[dict(entry='Actor.class',id='b',methods=[])])
        spec=dict(mod_key='fixture',evidence_file='a.json',checkpoint='fixture',closed_scope='fixture',
            exact_next_task='fixture',contracts=[dict(id='fixture:actor',display_name='actor',source_actor=['Actor'],
            primary_classification='VANILLA_COMPOSITE',actual_behavior='fixture',implementation=[
                dict(entry='Actor.class',methods=['first']),dict(entry='Actor.class',methods=['second']),
                dict(entry='Actor.class',methods=['other'],evidence_file='b.json')])])
        with patch('assemble_authored_contracts.read_json',side_effect=[a,b]) as read:
            result=render(spec)
        self.assertEqual(read.call_count,2)
        self.assertEqual([p['witness_id'] for p in result['effects'][0]['implementation']],['a','a','b'])

if __name__=='__main__':unittest.main()
