"""Exact promotion-only migration; frozen subsection results and native facts stay unchanged."""
from functools import lru_cache
from catalog_common import *

START='f0fa5894e45258cc45161942d03bdf04a23a5bc1'
PREFIX='scripts/external-effects/'
NAMES=['validate_iceandfire_foundation.py','validate_iceandfire_frozen_core.py',
       'validate_iceandfire_frozen_dragons.py','validate_iceandfire_siren.py',
       'validate_iceandfire_siren_flute.py','validate_iceandfire_gorgon.py',
       'iceandfire_combat_common.py']

def normalized(s):return s.decode('utf-8').replace('\r\n','\n') if isinstance(s,bytes) else s.replace('\r\n','\n')

@lru_cache(None)
def before(path):return normalized(subprocess.check_output(['git','show',START+':'+path],cwd=ROOT))

def protected_rows(rows,old):
    """Preserve every pre-promotion record exactly, in order, as other mods are added."""
    mods={r['mod_key'] for r in old}
    accepted=[r for r in rows if r['mod_key'] in mods]
    assert accepted==old,'Previously accepted mod records changed'
    return accepted

def transform(path,text):
    assert Path(path).name in NAMES
    text=text.replace('from catalog_common import *','from catalog_common import *\nfrom iceandfire_promotion_migration import protected_rows, permitted_tool_change')
    text=text.replace('assert read_json(OUT/name)[key]==old', 'assert protected_rows(read_json(OUT/name)[key],old)==old')
    old="assert read_json(OUT/name)[key]==json.loads(git('show',START+':docs/benchmarks/external-effects-catalog/'+name))[key];preserved[key]=len(read_json(OUT/name)[key])"
    new="old=json.loads(git('show',START+':docs/benchmarks/external-effects-catalog/'+name))[key];preserved[key]=len(protected_rows(read_json(OUT/name)[key],old))"
    text=text.replace(old,new)
    old="now=read_json(OUT/f)[key];assert now==json.loads(git('show',d['starting_sha']+':docs/benchmarks/external-effects-catalog/'+f))[key];preserved[key]=len(now)"
    new="old=json.loads(git('show',d['starting_sha']+':docs/benchmarks/external-effects-catalog/'+f))[key];preserved[key]=len(protected_rows(read_json(OUT/f)[key],old))"
    text=text.replace(old,new)
    for allow in ['allowed','mutable']:
        text=text.replace('status==\'M\' and path in '+allow,"status=='M' and (path in "+allow+' or permitted_tool_change(path))')
    if Path(path).name=='validate_iceandfire_foundation.py':
        text=text.replace("r=read_json(OUT/'mod-reviews/iceandfire.json');assert r['status']=='PARTIAL' and not r['effects'] and not r['paths']\n    assert not r['semantic_discovery_complete'] and not r['special_damage_discovery_complete']", "r=read_json(OUT/'mod-reviews/iceandfire.json');assert r['status'] in {'PARTIAL','COMPLETE'}\n    if r['status']=='PARTIAL':\n        assert not r['effects'] and not r['paths'] and not r['semantic_discovery_complete'] and not r['special_damage_discovery_complete']\n    else:\n        assert r['decision']=='ICE_AND_FIRE_COMBAT_SEMANTIC_REVIEW_COMPLETE' and r['effects'] and r['paths'] and r['semantic_discovery_complete'] and r['special_damage_discovery_complete']")
        text=text.replace("ledger['iceandfire']['state']=='PARTIAL'", "ledger['iceandfire']['state']==r['status']")
    return text

def permitted_tool_change(path):
    if path not in {PREFIX+n for n in NAMES}:return False
    assert normalized((ROOT/path).read_bytes())==transform(path,before(path)), 'Unapproved historical tooling change: '+path
    return True

def validate_migration():
    rows=[]
    for name in NAMES:
        path=PREFIX+name;old=before(path);expected=transform(path,old)
        assert old!=expected and permitted_tool_change(path),path
        rows.append(dict(path=path,before_sha256=byte_hash(old.encode()),after_sha256=byte_hash(expected.encode())))
    return dict(status='PASS',starting_sha=START,files=rows,reason=__doc__)

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    if args.apply:
        for name in NAMES:
            path=PREFIX+name
            assert normalized((ROOT/path).read_bytes()) in {before(path),transform(path,before(path))}
            (ROOT/path).write_text(transform(path,before(path)),encoding='utf-8')
    write_json(OUT/'iceandfire-validator-migration.json',validate_migration())
