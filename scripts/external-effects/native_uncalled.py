"""Disposition selected static procedure overloads without native invocation roots.

Only exact direct calls, bootstrap handles and method event annotations are
checked. Class-level event registration never implies every overload is called.
Other overloads, event handlers, callees and external reflective invocation are
not excluded. This does not create a payload, parameter or class-wide exclusion.
"""
from collections import defaultdict
from collect_combat_census import decode_sites


def native_references(census):
    calls=defaultdict(list);handles=defaultdict(list)
    for m in census['methods']:
        for i in decode_sites(census,m,'calls'):
            if i['opcode']!='0xba':
                calls[i['operand']].append(dict(entry=m['entry'],method=m['method'],
                    descriptor=m['descriptor'],offset=i['offset']))
    for b in census['registration_bootstraps']:
        for symbol in [b['handle']]+b['arguments']:
            if isinstance(symbol,str):handles[symbol].append(dict(entry=b['entry'],index=b['index']))
    return calls,handles


def validate(document,census,evidence):
    assert document['schema']=='tno.external_effects.uncalled_native_procedures.v1'
    assert document['mod_key']==census['mod_key'] and document['jar_sha256']==census['jar_sha256']
    native={(m['entry'],m['method'],m['descriptor']):m for m in census['methods']}
    classes={c['entry']:c for c in census['classes']}
    calls,handles=native_references(census);seen=set()
    for r in document['rows']:
        key=(r['entry'],r['method'],r['descriptor']);assert key not in seen;seen.add(key)
        m=native[key]
        assert r['method']=='execute' and m['access'] & 8,'Only explicit static procedure overloads can be dispositioned'
        assert r['access']==m['access'] and r['code_sha256']==m['code_sha256']
        assert r['entry_sha256']==classes[r['entry']]['entry_sha256']
        symbol=r['entry'][:-6]+'.'+r['method']+r['descriptor']
        assert not calls[symbol] and not handles[symbol],'Native invocation root exists'
        w=next(w for w in evidence['witnesses'] if w['id']==r['witness_id'])
        assert w['entry']==r['entry'] and w['entry_sha256']==r['entry_sha256'] and w['jar_sha256']==document['jar_sha256']
        method=next(n for n in w['methods'] if (n['name'],n['descriptor'])==key[1:])
        assert method['code_sha256']==r['code_sha256'] and not method['annotations'],'Annotated native handler cannot be excluded'
        assert r['class_annotations']==w['annotations']
        assert r['native_direct_callers']==[] and r['native_bootstrap_references']==[]
        assert r['disposition']=='NO_NATIVE_INVOCATION_ROOT_FOR_SELECTED_STATIC_OVERLOAD'
    assert document['summary']==dict(selected_static_overloads=len(seen),new_semantic_records=0,new_numeric_parameters=0,class_wide_exclusions=0)
    return document['rows']


def validate_batch(batch,census,read):
    """The exact absence proof must cover every exclusion using this packet."""
    document=read(batch['native_uncalled_registry_file'])
    evidence=read(document['evidence_file']);rows=validate(document,census,evidence)
    expected={(r['entry'],r['method'],r['descriptor']) for r in rows};cited=set()
    for exclusion in batch.get('exclusions',[]):
        for proof in exclusion.get('implementation',[]):
            if proof['evidence_file']!=document['evidence_file']:continue
            witness=next(w for w in evidence['witnesses'] if w['id']==proof['witness_id'])
            assert witness['entry']==proof['entry']==exclusion['entry']
            assert exclusion['disposition']=='NO_NATIVE_INVOCATION_ROOT_FOR_SELECTED_STATIC_OVERLOAD'
            for name in proof['methods']:
                methods=[m for m in witness['methods'] if m['name']==name]
                assert methods,'Uncalled exclusion cites an unproved method'
                for m in methods:
                    key=(proof['entry'],name,m['descriptor'])
                    assert key in expected and key not in cited,'Duplicate or unproved uncalled overload'
                    cited.add(key)
    assert cited==expected,'Uncalled absence proof and batch exclusions differ'
    return rows
