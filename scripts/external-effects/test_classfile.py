"""Cross-check discovery offsets against JDK javap; never starts Minecraft."""
import re
import subprocess
import struct
import unittest
from classfile import ClassFile, modified_utf8
from catalog_common import *

JAVA_BIN=Path('C:/Program Files/Java/jdk-21/bin')

class ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder=WORK/'parser-validation'; cls.folder.mkdir(parents=True,exist_ok=True)
        # Keeping many live locals forces WIDE loads/stores and WIDE iinc.
        locals_text='\n'.join(f'int v{i}=x+{i};' for i in range(270))
        sum_text='+'.join(f'v{i}' for i in range(270))
        source='''import java.util.function.IntUnaryOperator;
public class CatalogReaderFixture {
  static String text="nul\\u0000 emoji \\ud83d\\ude00";
  static long big=9000000000L; static double decimal=3.125;
  public int dense(int x) { return switch(x) { case 0->7;case 1->11;case 2->13;default->17;}; }
  public int sparse(int x) { return switch(x) { case -100->7;case 200->11;case 3000->13;default->17;}; }
  public String dynamic(int x) { IntUnaryOperator f=y->y+1; return "n="+f.applyAsInt(x); }
  public int[][] arrays(int x) { return new int[x][3]; }
  public int wide(int x) { LOCALS v269++; return SUM; }
}'''.replace('LOCALS',locals_text).replace('SUM',sum_text)
        path=cls.folder/'CatalogReaderFixture.java'; path.write_text(source,encoding='utf-8')
        subprocess.run([str(JAVA_BIN/'javac.exe'),'-encoding','UTF-8',str(path)],check=True,capture_output=True)
        cls.data=(cls.folder/'CatalogReaderFixture.class').read_bytes(); cls.parsed=ClassFile(cls.data)
        cls.javap=subprocess.check_output([str(JAVA_BIN/'javap.exe'),'-c','-p',str(cls.folder/'CatalogReaderFixture.class')],text=True)

    def test_instruction_offsets_match_javap(self):
        expected=[int(x) for x in re.findall(r'^\s+(\d+):\s+[a-z][a-z0-9_]*\b',self.javap,re.M)]
        actual=[i['offset'] for m in self.parsed.methods if 'code' in m for i in self.parsed.instructions(m['code'])]
        self.assertEqual(expected,actual)
        opcodes={i['opcode'] for m in self.parsed.methods if 'code' in m for i in self.parsed.instructions(m['code'])}
        for op in ('0xaa','0xab','0xc4','0xba','0xb9','0xc5','0x14'): self.assertIn(op,opcodes)

    def test_constants_and_modified_utf8(self):
        self.assertIn('nul\0 emoji \U0001f600',self.parsed.strings())
        self.assertEqual(modified_utf8(b'abc\xc0\x80\xed\xa0\xbd\xed\xb8\x80'),'abc\0\U0001f600')
        self.assertIn(9000000000,[v[1] for v in self.parsed.cp if v and v[0]==5])
        self.assertIn(3.125,[v[1] for v in self.parsed.cp if v and v[0]==6])

    def test_bad_magic_and_truncation_rejected(self):
        for data in (b'\0\0\0\0'+self.data[4:],self.data[:50],self.data[:-1]):
            with self.assertRaises((AssertionError,ValueError)): ClassFile(data)

    def test_invalid_and_truncated_opcodes_rejected(self):
        for code in (b'\xcb',b'\xb6\x00',b'\xaa\x00',b'\xc4'):
            with self.assertRaises((AssertionError,ValueError,IndexError,struct.error)):
                list(self.parsed.instructions(code))

    def test_real_methods_match_javap(self):
        inv=read_json(OUT/'jar-inventory.json')
        target=next(x for x in inv['targets'] if x['key']=='variantsandventures')
        prefix='com/faboslav/variantsandventures/common/'
        entries=[prefix+x+'.class' for x in ('entity/mob/GelidEntity','entity/mob/ThicketEntity',
                 'entity/mob/VerdantEntity','entity/event/GelidOnSnowballHitEvent','mixin/ZombieMixin')]
        checks=[]
        with zipfile.ZipFile(target['path']) as jar:
            for entry in entries:
                data=jar.read(entry); parsed=ClassFile(data)
                javap=subprocess.check_output([str(JAVA_BIN/'javap.exe'),'-c','-p','-classpath',target['path'],entry[:-6].replace('/','.')],text=True)
                expected=[int(x) for x in re.findall(r'^\s+(\d+):\s+[a-z][a-z0-9_]*\b',javap,re.M)]
                actual=[i['offset'] for m in parsed.methods if 'code' in m for i in parsed.instructions(m['code'])]
                self.assertEqual(expected,actual,entry)
                checks.append(dict(entry=entry,class_sha256=byte_hash(data),instruction_count=len(actual),javap_sha256=byte_hash(javap.encode())))
        write_json(self.folder/'real-class-checks.json',checks)

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ReaderTests))
    write_json(OUT/'parser-validation.json',dict(schema='tno.external_effects.parser_validation.v1',
        status='PASS' if result.wasSuccessful() else 'FAIL',tests=result.testsRun,
        failures=len(result.failures),errors=len(result.errors),
        fixture_sha256=byte_hash(ReaderTests.data),javac_sha256=sha256(JAVA_BIN/'javac.exe'),
        javap_sha256=sha256(JAVA_BIN/'javap.exe'),real_class_checks=read_json(ReaderTests.folder/'real-class-checks.json'),
        note='Offset/constant/corruption checks validate this discovery reader, not semantic coverage or runtime behavior.'))
    raise SystemExit(0 if result.wasSuccessful() else 1)
