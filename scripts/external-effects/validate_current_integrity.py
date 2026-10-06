"""Shared independent validation after the historical promotion builders retire."""
import hashlib
import json
import subprocess

from catalog_common import OUT, ROOT, read_json
from audit_catalog_integrity import audit_review, EvidenceIndex


def digest(row):
    return hashlib.sha256(json.dumps(row,sort_keys=True,ensure_ascii=False).encode()).hexdigest()


def validate_mod(mod_key):
    review=read_json(OUT/'mod-reviews'/str(mod_key+'.json'))
    result=audit_review(review,EvidenceIndex())
    target=next(t for t in read_json(OUT/'mod-completion-ledger.json')['targets'] if t['mod_key']==mod_key)
    assert review['status']==target['state']=='COMPLETE'
    assert result['semantic_records']==target['semantic_effect_count']
    assert result['numeric_candidate_entries']==target['numeric_candidate_count']
    return result


def validate_cataclysm_repairs():
    report=read_json(OUT/'catalog-integrity-repairs.json')
    review=read_json(OUT/'mod-reviews/cataclysm.json')
    path=(OUT/'mod-reviews/cataclysm.json').relative_to(ROOT).as_posix()
    before=json.loads(subprocess.check_output(['git','show',report['starting_sha']+':'+path],cwd=ROOT))
    old={r['id']:r for r in before['effects']};current={r['id']:r for r in review['effects']}
    declared={r['original_id']:r for r in report['canonical_record_changes']['cataclysm']}
    aliases={a['original_id']:a['canonical_ids'] for a in review['semantic_aliases']}
    excluded={c.get('original_id') for c in review['native_context_records']}
    for rid,row in old.items():
        if rid in current and row==current[rid]:
            continue
        change=declared[rid]
        assert change['before_sha256']==digest(row)
        if rid in current:
            assert change['after_sha256']==digest(current[rid])
        else:
            assert rid in aliases or rid in excluded
            assert change['after_sha256'] is None
    assert subprocess.check_output(['git','rev-parse','codex/production-continuation'],cwd=ROOT,text=True).strip()==report['protected_production_sha']
    # All existing native bytecode remains independently locked; mutable
    # canonical records are repaired explicitly rather than blindly frozen.
    for item in report['protected_native_files']:
        assert hashlib.sha256((OUT/item['file']).read_bytes()).hexdigest()==item['sha256']
    return validate_mod('cataclysm')
