"""Bounded big-endian NBT reader for pinned native structure evidence, not world editing."""
import struct
from classfile import modified_utf8


class Reader:
    def __init__(self, data):
        self.data = data
        self.offset = 0
        self.nodes = 0

    def take(self, size):
        if size < 0 or self.offset + size > len(self.data):
            raise ValueError('Truncated or negative-length NBT payload')
        value = self.data[self.offset:self.offset + size]
        self.offset += size
        return value

    def number(self, fmt):
        return struct.unpack('>' + fmt, self.take(struct.calcsize('>' + fmt)))[0]

    def string(self):
        return modified_utf8(self.take(self.number('H')))

    def length(self):
        length = self.number('i')
        if length < 0 or length > len(self.data):
            raise ValueError('Invalid NBT collection length')
        return length

    def value(self, kind, depth=0):
        self.nodes += 1
        if depth > 64 or self.nodes > 1000000:
            raise ValueError('NBT structural budget exceeded')
        if 1 <= kind <= 6:
            return self.number({1:'b',2:'h',3:'i',4:'q',5:'f',6:'d'}[kind])
        if kind == 7:
            return [b if b < 128 else b - 256 for b in self.take(self.length())]
        if kind == 8:
            return self.string()
        if kind == 9:
            subtype, length = self.number('B'), self.length()
            if subtype > 12 or (subtype == 0 and length):
                raise ValueError('Invalid NBT list type')
            return [self.value(subtype, depth + 1) for _ in range(length)]
        if kind == 10:
            result = {}
            while True:
                subtype = self.number('B')
                if subtype == 0:
                    return result
                name = self.string()
                if name in result:
                    raise ValueError('Duplicate NBT compound key')
                result[name] = self.value(subtype, depth + 1)
        if kind in (11, 12):
            return [self.number('i' if kind == 11 else 'q') for _ in range(self.length())]
        raise ValueError('Invalid NBT type: ' + str(kind))


def decode(data):
    reader = Reader(data)
    if reader.number('B') != 10:
        raise ValueError('Expected compound NBT root')
    reader.string()
    result = reader.value(10)
    if reader.offset != len(data):
        raise ValueError('Trailing NBT payload')
    return result


def payload_projection(document):
    """Retain entity/BE payloads and used palettes, without inferring live behavior.

    Ordinary block coordinates are omitted; the archive entry hash remains the
    authority for geometry. All entity and block-entity NBT is preserved, even
    zero-health entities, unknown tags and apparently cosmetic data.
    """
    from collections import Counter
    from copy import deepcopy
    assert set(document) <= {'size', 'entities', 'blocks', 'palette', 'palettes',
                             'DataVersion', 'author'}, 'unknown structure root field'
    size = document['size']
    assert len(size) == 3 and all(type(v) is int and v >= 0 for v in size)
    palettes = document.get('palettes', [document.get('palette')])
    assert palettes and all(isinstance(p, list) for p in palettes)
    counts = Counter()
    block_payloads = []
    for index, block in enumerate(document['blocks']):
        assert set(block) <= {'pos', 'state', 'nbt'}, 'unknown structure block field'
        state = block['state']
        assert type(state) is int and all(0 <= state < len(p) for p in palettes)
        assert len(block['pos']) == 3 and all(type(v) is int for v in block['pos'])
        counts[state] += 1
        if 'nbt' in block:
            assert isinstance(block['nbt'], dict)
            block_payloads.append(dict(source_block_index=index, **deepcopy(block)))
    entities = document['entities']
    for entity in entities:
        assert set(entity) <= {'pos', 'blockPos', 'nbt'}, 'unknown structure entity field'
        assert isinstance(entity['nbt'], dict)
        assert len(entity['pos']) == len(entity['blockPos']) == 3
    return dict(schema='tno.external_effects.structure_payload_projection.v1',
                data_version=document.get('DataVersion'), size=deepcopy(size),
                source_block_count=len(document['blocks']),
                used_palettes=[[dict(state_index=i, block_count=counts[i],
                                     state=deepcopy(p[i])) for i in sorted(counts)]
                               for p in palettes],
                block_payloads=block_payloads, entities=deepcopy(entities),
                scope='Raw native NBT; no data-fixing, registry resolution, '
                      'reachability, alive-state or Stage eligibility inferred.')
