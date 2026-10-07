"""Verify missing non-keyword field sites against an independent JDK fixture."""
import copy
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from classfile import ClassFile
from catalog_common import byte_hash,OUT,read_json
from collect_combat_census import decode_sites
from index_native_fields import index,pack,write_index


class NativeFieldIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();p=Path(cls.tmp.name)/'NativeFieldFixture.java'
        p.write_text('public class NativeFieldFixture { static int plain=3; boolean flag; '
                     'public void step(){ plain=plain+1; System.out.println(plain); } '
                     'public boolean query(){ return flag; } }')
        subprocess.run([shutil.which('javac'),str(p)],check=True,capture_output=True)
        cls.raw=p.with_suffix('.class').read_bytes();c=ClassFile(cls.raw)
        cls.census=dict(mod_key='fixture',jar_sha256='pin',classes=[dict(name=c.name,entry=c.name+'.class',entry_sha256=byte_hash(cls.raw))],
          methods=[dict(entry=c.name+'.class',method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b''))) for m in c.methods])

    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def test_fields_without_combat_keyword_hits_are_retained(self):
        d=index(self.census,lambda e:self.raw)
        self.assertEqual(d['summary']['native_field_sites'],5)
        sites=[i for m in d['methods'] for i in m['field_sites']]
        self.assertEqual(sum(i['operand']=='NativeFieldFixture.plainI' for i in sites),4)
        self.assertEqual(sum(i['operand']=='NativeFieldFixture.flagZ' for i in sites),1)
        self.assertFalse(any('java/lang/System.out' in i['operand'] for i in sites))
        self.assertFalse(d['semantic_coverage_granted'])

    def test_changed_original_class_and_method_hashes_are_rejected(self):
        for mutate in ['class','method']:
            c=copy.deepcopy(self.census)
            if mutate=='class':c['classes'][0]['entry_sha256']='wrong'
            else:next(m for m in c['methods'] if m['method']=='step')['code_sha256']='wrong'
            with self.assertRaises(AssertionError):index(c,lambda e:self.raw)

    def test_interning_preserves_all_exact_sites_and_stable_bytes(self):
        d=index(self.census,lambda e:self.raw);p=pack(d)
        for m,q in zip(d['methods'],p['methods']):self.assertEqual(m['field_sites'],decode_sites(p,q,'field_sites'))
        out=Path(self.tmp.name)/'output.json';write_index(out,p);first=out.read_bytes();write_index(out,pack(d))
        self.assertEqual(first,out.read_bytes())

    def test_pinned_lookup_foundation_keeps_no_semantic_completion_claim(self):
        d=read_json(OUT/'arphex-native-field-use-index.json')
        self.assertEqual(d['summary'],dict(original_census_classes_checked=3702,methods_with_native_field_sites=5502,native_field_sites=24226))
        self.assertFalse(d['semantic_coverage_granted'])
        live=[m for m in d['methods'] if any('.reload_renderZ' in i['operand'] for i in decode_sites(d,m,'field_sites'))]
        self.assertTrue(any(m['entry'].endswith('/TranscendentalTormentorOnEntityTickUpdateProcedure.class') for m in live))
        self.assertTrue(any(m['entry'].endswith('/WorldLoadProcedure.class') for m in live))


if __name__=='__main__':unittest.main()
