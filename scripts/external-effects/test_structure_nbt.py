"""Reader tests against independently constructed binary fixtures."""
import struct
import unittest
from structure_nbt import decode


def string(value):
    return struct.pack('>H', len(value)) + value


def tag(kind, name, payload):
    return bytes([kind]) + string(name.encode()) + payload


def root(*tags):
    return b'\x0a\x00\x00' + b''.join(tags) + b'\x00'


class NbtTests(unittest.TestCase):
    def test_all_payload_types(self):
        fields = [tag(k, str(k), struct.pack('>' + fmt, value)) for k,fmt,value in
                  [(1,'b',-2),(2,'h',-300),(3,'i',70000),(4,'q',2**40),(5,'f',1.5),(6,'d',-2.25)]]
        fields += [tag(7,'bytes',struct.pack('>i',2)+b'\x00\xff'),
                   tag(8,'string',string(b'A\xc0\x80B')),
                   tag(9,'list',b'\x03'+struct.pack('>iii',2,-4,8)),
                   tag(10,'compound',tag(8,'nested',string(b'yes'))+b'\x00'),
                   tag(11,'ints',struct.pack('>iii',2,-1,2)),
                   tag(12,'longs',struct.pack('>iq',1,2**40))]
        result = decode(root(*fields))
        self.assertEqual(result, {'1':-2,'2':-300,'3':70000,'4':2**40,'5':1.5,'6':-2.25,
                                 'bytes':[0,-1],'string':'A\0B','list':[-4,8],
                                 'compound':{'nested':'yes'},'ints':[-1,2],'longs':[2**40]})

    def test_every_truncation_rejected(self):
        fixture = root(tag(9,'list',b'\x0a'+struct.pack('>i',1)+tag(8,'name',string(b'zombie_trap'))+b'\x00'))
        self.assertEqual(decode(fixture)['list'][0]['name'],'zombie_trap')
        for size in range(len(fixture)):
            with self.subTest(size=size), self.assertRaises(ValueError):decode(fixture[:size])

    def test_invalid_shapes_rejected(self):
        invalid = [root()+b'x',b'\x08\x00\x00\x00\x00',root(tag(7,'x',struct.pack('>i',-1))),
                   root(tag(9,'x',b'\x00'+struct.pack('>i',1))),root(tag(13,'x',b'')),
                   root(tag(1,'x',b'\x01'),tag(1,'x',b'\x02')),
                   root(tag(9,'x',b'\x03'+struct.pack('>i',2**30)))]
        for fixture in invalid:
            with self.subTest(fixture=fixture), self.assertRaises(ValueError):decode(fixture)

    def test_nesting_limit(self):
        fixture = root(tag(10,'x',b'')*66+b'\x00'*66)
        with self.assertRaises(ValueError):decode(fixture)


if __name__ == '__main__':unittest.main()
