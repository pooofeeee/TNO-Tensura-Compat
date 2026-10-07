"""Selection is an exact finite boundary, never a discovery or coverage claim."""
import unittest
from pathlib import Path
from unittest.mock import patch
from prepare_native_scope import prepare

class ScopeTests(unittest.TestCase):
 def census(self):
  return dict(jar_sha256='pin',classes=[dict(entry='x/Actor.class')],methods=[
   dict(entry='x/Actor.class',method='old',descriptor='()V'),
   dict(entry='x/Actor.class',method='missing',descriptor='()Z')])
 def execute(self,selection):
  c=self.census()
  def collect(s,paths):
   return {'witnesses':[{'methods':w['methods']} for w in s['evidence_specifications']]}
  with patch('prepare_native_scope.read_json',return_value=c),patch('prepare_native_scope.sha256',return_value='pin'),patch('prepare_native_scope.collect',side_effect=collect),patch('prepare_native_scope.write_json') as write:
   r=prepare('test','scope',['x/Actor.class'],Path('pin.jar'),selection=selection)
   return r,write.call_args_list[0].args[1]
 def test_only_exact_missing_methods_are_captured(self):
  r,s=self.execute([self.census()['methods'][1]])
  self.assertEqual(r['methods'],1);self.assertEqual(s['evidence_specifications'][0]['methods'][0]['name'],'missing')
 def test_default_full_explicit_class_scope_is_preserved(self):
  r,s=self.execute(None);self.assertEqual(r['methods'],2)
 def test_unknown_or_empty_selection_is_rejected(self):
  for selected in ([],[dict(entry='x/Actor.class',method='guessed',descriptor='()Z')],
                   [dict(entry='x/Other.class',method='missing',descriptor='()Z')]):
   with self.assertRaises(AssertionError):self.execute(selected)

if __name__=='__main__':unittest.main()
