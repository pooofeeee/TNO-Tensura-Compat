"""An absent native entry is independently pinned, never silently skipped."""
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
from catalog_common import sha256
from native_evidence import collect


class NativeAbsenceTests(unittest.TestCase):
    def test_absence_and_presence_are_distinct_and_reproduce(self):
        with tempfile.TemporaryDirectory() as tmp:
            jar=Path(tmp)/'native.jar'
            with zipfile.ZipFile(jar,'w') as z:z.writestr('present.json','{}')
            inventory=dict(targets=[dict(key='fixture',sha256=sha256(jar),path=str(jar))],compat_candidates=[])
            spec=dict(evidence_specifications=[dict(id='absence',mod_key='fixture',entry='missing.nbt',expected_absent=True)])
            with patch('native_evidence.read_json',return_value=inventory):
                a=collect(spec);self.assertEqual(a,collect(spec))
                self.assertTrue(a['witnesses'][0]['entry_absent'])
                self.assertNotIn('entry_sha256',a['witnesses'][0])
                spec['evidence_specifications'][0]['entry']='present.json'
                with self.assertRaises(AssertionError):collect(spec)


if __name__=='__main__':unittest.main()
