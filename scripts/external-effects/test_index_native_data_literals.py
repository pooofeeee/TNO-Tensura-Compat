"""Small independent classfile fixtures for the bounded literal lookup aid."""
import copy
import struct
import unittest

from catalog_common import byte_hash
from index_native_data_literals import index, selected_methods


def fixture():
    def u2(n): return struct.pack('>H', n)
    def u4(n): return struct.pack('>I', n)
    def utf(s): return b'\x01' + u2(len(s)) + s.encode()
    cp = [utf('Test'), b'\x07'+u2(1), utf('java/lang/Object'), b'\x07'+u2(3),
          utf('execute'), utf('()V'), utf('Code'), utf('net/minecraft/nbt/CompoundTag'), b'\x07'+u2(8),
          utf('getString'), utf('(Ljava/lang/String;)Ljava/lang/String;'), b'\x0c'+u2(10)+u2(11),
          b'\x0a'+u2(9)+u2(12), utf('literal_key'), b'\x08'+u2(14),
          utf('AClass'), b'\x07'+u2(16)]
    # null receiver, literal string, getString/pop; distinct class literal/pop.
    code = bytes.fromhex('01120fb6000d57121157b1')
    attr = u2(2)+u2(0)+u4(len(code))+code+u2(0)+u2(0)
    raw = bytes.fromhex('cafebabe')+u2(0)+u2(52)+u2(len(cp)+1)+b''.join(cp)
    raw += u2(0x21)+u2(2)+u2(4)+u2(0)+u2(0)+u2(1)
    raw += u2(9)+u2(5)+u2(6)+u2(1)+u2(7)+u4(len(attr))+attr+u2(0)
    call = 'net/minecraft/nbt/CompoundTag.getString(Ljava/lang/String;)Ljava/lang/String;'
    census = dict(mod_key='test', jar_sha256='pinned', classes=[dict(entry='Test.class', entry_sha256=byte_hash(raw))],
                  symbols=[call], methods=[dict(entry='Test.class', method='execute', descriptor='()V',
                  code_sha256=byte_hash(code), calls=[[3, 182, 0]])])
    return raw, census


class NativeDataLiteralIndexTests(unittest.TestCase):
    def test_exact_literal_and_hash_retained_class_reference_not_mistaken_for_string(self):
        raw, census = fixture(); result = index(census, lambda _: raw)
        self.assertEqual(result['summary'], dict(selected_classes=1, selected_methods=1))
        self.assertEqual(result['methods'][0]['literal_strings'], [dict(offset=1, value='literal_key')])
        self.assertEqual(result['methods'][0]['code_sha256'], census['methods'][0]['code_sha256'])
        self.assertFalse(result['semantic_coverage_granted'])

    def test_queue_is_selected_by_exact_native_api_not_class_or_method_name(self):
        raw, census = fixture()
        census['symbols'][0] = 'other/CompoundTag.getString(Ljava/lang/String;)Ljava/lang/String;'
        self.assertEqual(selected_methods(census), [])
        def forbidden(_): raise AssertionError('Unselected class read')
        self.assertEqual(index(census, forbidden)['methods'], [])

    def test_changed_class_or_method_rejected(self):
        raw, census = fixture()
        with self.assertRaisesRegex(AssertionError, 'Changed class'):
            index(census, lambda _: raw + b'x')
        census = copy.deepcopy(census); census['methods'][0]['code_sha256'] = 'wrong'
        with self.assertRaisesRegex(AssertionError, 'Changed method'):
            index(census, lambda _: raw)

    def test_deterministic_output_and_no_inferred_argument_mapping(self):
        raw, census = fixture()
        first = index(census, lambda _: raw)
        self.assertEqual(first, index(census, lambda _: raw))
        self.assertFalse(any(k in first['methods'][0] for k in ('primitive', 'parameter', 'disposition', 'record_ids')))


if __name__ == '__main__':
    unittest.main()
