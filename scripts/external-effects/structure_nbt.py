"""Bounded big-endian NBT reader for pinned native structure evidence, not world editing."""
import struct
from classfile import modified_utf8


class Reader:
    def __init__(self, data, max_nodes=1000000):
        if type(max_nodes) is not int or not 1 <= max_nodes <= 64000000:
            raise ValueError('Invalid NBT structural budget')
        self.data = data
        self.offset = 0
        self.nodes = 0
        self.max_nodes = max_nodes

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
        if depth > 64 or self.nodes > self.max_nodes:
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


def decode(data, max_nodes=1000000):
    reader = Reader(data, max_nodes=max_nodes)
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


def decode_payload(data, max_nodes=1000000):
    """Read the same projection without retaining ordinary block dictionaries.

    Large native templates can contain millions of ordinary blocks. Every
    block is still decoded and checked; only its palette count and any NBT
    payload survive. Entity/BE data and palette alternatives are preserved.
    """
    from collections import Counter
    reader = Reader(data, max_nodes=max_nodes)
    if reader.number('B') != 10:
        raise ValueError('Expected compound NBT root')
    reader.string()
    document, counts, payloads, total = {}, Counter(), [], 0
    while True:
        kind = reader.number('B')
        if kind == 0:
            break
        name = reader.string()
        if name in document:
            raise ValueError('Duplicate NBT compound key')
        if name != 'blocks':
            document[name] = reader.value(kind, 1)
            continue
        if kind != 9 or reader.number('B') != 10:
            raise ValueError('Expected compound structure block list')
        total = reader.length()
        document[name] = []
        for index in range(total):
            block = reader.value(10, 2)
            assert set(block) <= {'pos', 'state', 'nbt'}
            assert type(block['state']) is int and block['state'] >= 0
            assert len(block['pos']) == 3 and all(type(v) is int for v in block['pos'])
            counts[block['state']] += 1
            if 'nbt' in block:
                assert isinstance(block['nbt'], dict)
                payloads.append(dict(source_block_index=index, **block))
    if reader.offset != len(data):
        raise ValueError('Trailing NBT payload')
    result = payload_projection(document)
    palettes = document.get('palettes', [document.get('palette')])
    assert all(all(i < len(p) for i in counts) for p in palettes)
    result['source_block_count'] = total
    result['used_palettes'] = [[dict(state_index=i, block_count=counts[i],
        state=p[i]) for i in sorted(counts)] for p in palettes]
    result['block_payloads'] = payloads
    return result
