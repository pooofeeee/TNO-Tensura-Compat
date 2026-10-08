"""Replace compact continuation state from canonical artifacts, without history."""
import argparse
from pathlib import Path
from catalog_common import OUT,read_json,git


def render(key, verified_head):
    campaign=read_json(OUT/'large-mod-campaign.json')
    ledger=read_json(OUT/'mod-completion-ledger.json')
    review=read_json(OUT/'mod-reviews'/f'{key}.json')
    queue=read_json(OUT/f'{key}-unresolved-queue.json')
    target=next(t for t in ledger['targets'] if t['mod_key']==key)
    blockers=sorted({a for r in review['effects'] for a in r.get('unresolved_ambiguities',[]) if isinstance(a,str)})
    locked=', '.join(t['mod_key'] for t in ledger['targets'] if t['state']=='COMPLETE')
    lines=['# Compact research state','',
        '- Active campaign: `CAMPAIGN.md`; Alex\'s Caves only, then STOP.',
        '- Branch: `external-effects-catalog-research`.',
        '- Latest verified research ref: `origin/external-effects-catalog-research`.',
        f'- Last verified anchor before this checkpoint: `{verified_head}`. Resolve the current ref with Git; never reset to an older anchor.',
        f"- Protected production HEAD: `{campaign['protected_production_sha']}`; production/source gameplay unchanged.",
        f'- Current mod/status: `{key}` / {target["state"]}.',
        f'- Locked COMPLETE targets: {locked}.',
        f'- Canonical records: {target["semantic_effect_count"]}; numeric candidates: {target["numeric_candidate_count"]}.',
        f'- Classifications: {target["classification_counts"]}.',
        f'- Census: `{key}-combat-census.json` (existing pin; do not rediscover).',
        f'- Queue: `{key}-unresolved-queue.json`; ordinals refer to that exact census/hash.',
        f'- Coverage: {queue["summary"]["dispositioned_methods"]} / {queue["summary"]["total_methods"]} dispositioned; {queue["summary"]["remaining_methods"]} pending.',
        f'- Remaining semantic-role methods: {queue["summary"]["pending_by_census_role"].get("PENDING_SEMANTIC_REVIEW",0)} (routing, not a mechanic count).',
        '- Canonical authorities: `mod-reviews/'+key+'.json`, `mod-completion-ledger.json`, `large-mod-campaign.json`.',
        '- Native source/indexes: existing census, field-use index and reviewed-batch pointers; consult cold bodies only for exact unresolved boundaries.',
        '- Known blockers: '+(', '.join(blockers) if blockers else ('none; finite census and dependency contracts closed.' if target['state']=='COMPLETE' else 'consult unresolved queue and dependency obligations.')),
        '- Exact next action: '+target['exact_next_task'],
        '- STOP after AlexCaves closure. Do not load Legendary Monsters or any later mod.','']
    if review.get('external_dependency_obligations_file'):
        dep=read_json(OUT/review['external_dependency_obligations_file'])
        pin=dep['artifact']
        lines.insert(-3,f'- Citadel: {pin["status"]}; version {pin["exact_installed_version"]}; SHA-256 `{pin["sha256"]}`; contracts in `{review["external_dependency_obligations_file"]}`.')
    return '\n'.join(lines)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mod_key')
    p.add_argument('--verified-head',required=True);a=p.parse_args()
    assert git('branch','--show-current')=='external-effects-catalog-research'
    assert git('rev-parse',a.verified_head)==a.verified_head
    (OUT/'STATE.md').write_text(render(a.mod_key,a.verified_head),encoding='utf-8')
