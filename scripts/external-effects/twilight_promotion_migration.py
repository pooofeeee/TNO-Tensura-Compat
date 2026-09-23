"""Exact, auditable migration of five historical validators at final promotion.

Historical evidence and result counts stay frozen. Only obsolete current-view
PARTIAL/empty assertions and byte-preservation of these exact tooling edits change.
"""
from functools import lru_cache
from catalog_common import *

START='393426ae12907217f25279013d437181c7b16dac'
PREFIX='scripts/external-effects/'
NAMES=['validate_twilight_progress.py','validate_twilight_pair.py',
       'validate_twilight_hydra_urghast.py','validate_twilight_yeti_queen.py',
       'validate_twilight_remaining.py']


def normalized(data):
    return data.decode('utf-8').replace('\r\n','\n') if isinstance(data,bytes) else data.replace('\r\n','\n')


@lru_cache(None)
def before(path):
    return normalized(subprocess.check_output(['git','show',START+':'+path],cwd=ROOT))


def transform(path, text):
    """Only these literal migrations are accepted, never arbitrary tooling edits."""
    name=Path(path).name
    assert name in NAMES
    # R2f7 already authorized this historical ledger-growth adjustment.
    if name=='validate_twilight_hydra_urghast.py':
        text=text.replace("ledger['draft_mechanic_count']==45 and ledger['draft_path_count']==126", "ledger['draft_mechanic_count']>=45 and ledger['draft_path_count']>=126")
    if name=='validate_twilight_progress.py':
        text=text.replace('assert d[key]==old(p)[key],name\n        counts[key]=len(d[key])',
            "accepted=[r for r in d[key] if r.get('mod_key') in protected]\n        assert accepted==old(p)[key],name\n        counts[key]=len(accepted)")
        text=text.replace("assert ledger['twilightforest']['state']=='PARTIAL' and ledger['iceandfire']['state']=='UNSTARTED'",
            "assert ledger['twilightforest']['state'] in {'PARTIAL','COMPLETE'}\n    if ledger['twilightforest']['state']=='PARTIAL':\n        assert ledger['iceandfire']['state']=='UNSTARTED'\n    else:\n        assert read_json(OUT/'mod-reviews/twilightforest.json')['decision']=='TWILIGHT_FOREST_SEMANTIC_REVIEW_COMPLETE'")
    if name in ['validate_twilight_pair.py','validate_twilight_hydra_urghast.py','validate_twilight_yeti_queen.py']:
        text=text.replace("assert ledger['status']=='PARTIAL' and not ledger['effects'] and not ledger['paths']",
            "assert ledger['status'] in {'PARTIAL','COMPLETE'}\n    if ledger['status']=='PARTIAL':\n        assert not ledger['effects'] and not ledger['paths']\n    else:\n        assert ledger['decision']=='TWILIGHT_FOREST_SEMANTIC_REVIEW_COMPLETE' and ledger['effects'] and ledger['paths']")
    if name in ['validate_twilight_hydra_urghast.py','validate_twilight_yeti_queen.py','validate_twilight_remaining.py']:
        text=text.replace('from catalog_common import *','from catalog_common import *\nfrom twilight_promotion_migration import assert_historical_file')
        text=text.replace("assert (ROOT/p).read_bytes().replace(b'\\r\\n',b'\\n')==old.replace(b'\\r\\n',b'\\n'),p",'assert_historical_file(p,old)')
    if name=='validate_twilight_yeti_queen.py':
        text=text.replace("assert (ROOT/'scripts/external-effects/validate_twilight_hydra_urghast.py').read_text()==allowed_validator",
            "assert_historical_file('scripts/external-effects/validate_twilight_hydra_urghast.py',allowed_validator)")
    return text


def assert_historical_file(path,old):
    current=normalized((ROOT/path).read_bytes()); old=normalized(old)
    if current==old:return
    assert path in {PREFIX+n for n in NAMES},'Protected evidence changed: '+path
    # A hash allowlist alone could hide arbitrary edits; reproduce the complete
    # permitted text and require both historical inputs to converge exactly.
    assert transform(path,old)==transform(path,before(path)), 'Unapproved historical tooling version: '+path
    assert current==transform(path,before(path)), 'Unapproved tooling edit: '+path


def validate_migration():
    rows=[]
    for name in NAMES:
        path=PREFIX+name; old=before(path); expected=transform(path,old)
        assert expected!=old and normalized((ROOT/path).read_bytes())==expected,path
        rows.append(dict(path=path,before_sha256=byte_hash(old.encode()),after_sha256=byte_hash(expected.encode())))
    return dict(starting_sha=START,status='PASS',files=rows,reason=__doc__)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');a=p.parse_args()
    if a.apply:
        for name in NAMES:
            path=PREFIX+name
            assert normalized((ROOT/path).read_bytes()) in {before(path),transform(path,before(path))},path
            (ROOT/path).write_text(transform(path,before(path)),encoding='utf-8')
    write_json(OUT/'twilightforest-validator-migration.json',validate_migration())
