"""Independent hand-built shape/mutation cases, plus exact finite-queue proofs."""
import copy
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from catalog_common import OUT,read_json,byte_hash
from native_forwarding import forwarding_shape,validate
from reconcile_native_census import reconcile
from classfile import ClassFile


def ins(op,operand=None,offset=0,**extra):
    return dict(opcode=op,operand=operand,offset=offset,**extra)


class ForwardingTests(unittest.TestCase):
    def bridge(self):
        return [ins('0x2a'),ins('0x2b'),ins('0xc0','example/Actor'),
                ins('0xb6','example/Renderer.render(Lexample/Actor;)V'),ins('0xb1')]

    def shape(self,body,handlers=()):
        return forwarding_shape('example/Renderer.class','render','(Ljava/lang/Object;)V',0x1041,body,handlers)

    def test_exact_typed_bridge_and_native_cast_retained(self):
        self.assertEqual(self.shape(self.bridge()),dict(kind='EXACT_COMPILER_BRIDGE',
            target=dict(entry='example/Renderer.class',method='render',descriptor='(Lexample/Actor;)V')))
        b=self.bridge();del b[2]
        self.assertIsNone(self.shape(b))

    def test_bridge_flags_owner_and_argument_identity_are_required(self):
        b=self.bridge()
        self.assertIsNone(forwarding_shape('example/Renderer.class','render','(Ljava/lang/Object;)V',1,b))
        for index,new in [(0,ins('0x2b')),(1,ins('0x2c')),
                          (3,ins('0xb6','example/Other.render(Lexample/Actor;)V')),
                          (3,ins('0xb8','example/Renderer.render(Lexample/Actor;)V'))]:
            bad=copy.deepcopy(b);bad[index]=new;self.assertIsNone(self.shape(bad))

    def test_side_effects_constants_branches_and_exception_handlers_refused(self):
        for added in [ins('0xb8','example/Combat.hurt()V'),ins('0x3'),ins('0x99'),ins('0xb5','example/Actor.healthF')]:
            b=self.bridge();b.insert(1,added);self.assertIsNone(self.shape(b))
        self.assertIsNone(self.shape(self.bridge(),[(0,1,2,3)]))

    def test_instance_noop_and_constant_gate_are_not_exclusions(self):
        self.assertIsNone(forwarding_shape('x/Actor.class','die','()V',1,[ins('0xb1')]))
        self.assertIsNone(forwarding_shape('x/Actor.class','canAttack','()Z',9,[ins('0x3'),ins('0xac')]))
        self.assertEqual(forwarding_shape('x/Helper.class','execute','()V',9,[ins('0xb1')]),
                         dict(kind='EMPTY_STATIC_VOID_HELPER'))

    def test_only_object_constructor_is_pure_context(self):
        b=[ins('0x2a'),ins('0xb7','java/lang/Object.<init>()V'),ins('0xb1')]
        self.assertEqual(forwarding_shape('x/H.class','<init>','()V',1,b),dict(kind='OBJECT_ONLY_CONTEXT_CONSTRUCTOR'))
        b[1]['operand']='x/Boss.<init>()V'
        self.assertIsNone(forwarding_shape('x/H.class','<init>','()V',1,b))

    def test_covariant_return_and_wide_parameter_slots_are_not_guessed(self):
        b=[ins('0x2a'),ins('0x1f'),ins('0x2d'),ins('0xc0','example/Actor'),
           ins('0xb6','example/Renderer.copy(JLexample/Actor;)Lexample/Actor;'),ins('0xb0')]
        self.assertIsNotNone(forwarding_shape('example/Renderer.class','copy','(JLjava/lang/Object;)Ljava/lang/Object;',0x1041,b))
        b[2]=ins('0x2c');self.assertIsNone(forwarding_shape('example/Renderer.class','copy','(JLjava/lang/Object;)Ljava/lang/Object;',0x1041,b))


class NativeForwardingRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.census=read_json(OUT/'arphex-combat-census.json')
        cls.review=read_json(OUT/'mod-reviews/arphex.json')
        cls.document=read_json(OUT/'arphex-native-forwarding-registry.json')
        prior=copy.deepcopy(cls.review)
        prior['reviewed_batches']=[f for f in prior['reviewed_batches'] if f!='arphex-r2m6w-exact-native-forwarding.json']
        cls.index,_=reconcile(prior,cls.census)
        cls.covered={(m['entry'],m['method'],m['descriptor']) for m in cls.index['methods']}

    def test_exact_finite_context_counts_and_method_hashes(self):
        rows=validate(self.document,self.census,self.covered)
        self.assertEqual(len(rows),1383)
        self.assertEqual(self.document['summary']['counts_by_kind'],
                         {'EMPTY_STATIC_VOID_HELPER':18,'EXACT_COMPILER_BRIDGE':2,'OBJECT_ONLY_CONTEXT_CONSTRUCTOR':1363})
        self.assertTrue(all(byte_hash(bytes.fromhex(r['code_hex']))==r['code_sha256'] for r in rows))

    def test_bridge_cannot_self_prove_from_capture_or_cyclic_targets(self):
        with self.assertRaisesRegex(AssertionError,'Bridge target lacks prior'):
            validate(self.document,self.census,set())

    def test_forged_method_class_hash_or_duplicate_row_is_rejected(self):
        for field in ['code_sha256','entry_sha256','code_hex']:
            d=copy.deepcopy(self.document);d['rows'][0][field]='00'
            with self.assertRaises(AssertionError):validate(d,self.census,self.covered)
        d=copy.deepcopy(self.document);d['rows'].append(d['rows'][0])
        with self.assertRaises(AssertionError):validate(d,self.census,self.covered)

    def test_queue_reduction_grants_no_new_semantic_record_or_scalar(self):
        rows=validate(self.document,self.census,self.covered)
        self.assertFalse(any('scalable_parameter_candidates' in r for r in rows))
        self.assertFalse(any('effects' in r for r in rows))
        self.assertTrue(all(r['kind']!='FIELD_ACCESS_CONTEXT' for r in rows))

    def test_audit_index_uses_one_canonical_relative_file_identity(self):
        from audit_catalog_integrity import EvidenceIndex
        i=EvidenceIndex();name='arphex-native-forwarding-registry.json'
        self.assertIs(i.read(name),i.read(OUT/name))
        self.assertEqual(set(i.file_hashes),{name})


class JdkCodeMetadataTests(unittest.TestCase):
    def test_exception_table_matches_independent_compiled_fixture(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'ContextFixture.java'
            p.write_text('public class ContextFixture { public int guarded(int n) { '
                         'try { return 8/n; } catch (ArithmeticException e) { return 0; } } }')
            subprocess.run([shutil.which('javac'),str(p)],check=True,capture_output=True)
            raw=p.with_suffix('.class').read_bytes()
            default=ClassFile(raw)
            self.assertTrue(all('exception_handlers' not in m for m in default.methods))
            parsed=ClassFile(raw,retain_code_metadata=True)
            m=next(m for m in parsed.methods if m['name']=='guarded')
            self.assertEqual(len(m['exception_handlers']),1)
            start,end,target,cp=m['exception_handlers'][0]
            self.assertTrue(0<=start<end<=len(m['code']))
            self.assertTrue(0<=target<len(m['code']))
            self.assertEqual(parsed.resolve(cp),'java/lang/ArithmeticException')


if __name__=='__main__':unittest.main()
