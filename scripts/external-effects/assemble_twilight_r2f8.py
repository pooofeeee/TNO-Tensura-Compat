"""Protect whole semantic/source closure before final distinct-record promotion."""
from catalog_common import *
from assemble_batch import refresh


def build():
    cp='R2f8-remaining-content-complete'
    closure=read_json(OUT/'twilightforest-global-source-closure.json')
    assert closure['decision']=='TWILIGHT_REMAINING_CONTENT_COMPLETE'
    nxt=closure['exact_next_task']
    review=read_json(OUT/'mod-reviews/twilightforest.json')
    assert review['status']=='PARTIAL' and not review['effects'] and not review['paths']
    review.update(checkpoint=cp,scope='Whole combat-significant semantic discovery, source/delivery mapping, all40 custom types, all31 transformers, scoped compatibility and explicit exclusions closed. Final distinct-record deduplication/promotion is the only remaining Twilight task.',notes_file='twilightforest-global-source-closure.json',exact_next_task=nxt)
    write_json(OUT/'mod-reviews/twilightforest.json',review);refresh(cp)
    for name in ['effect-catalog.json','effect-sources.json','delivery-path-matrix.json','vanilla-comparison.json','behavior-primitives.json']:
        doc=read_json(OUT/name);doc.update(checkpoint=cp,unfinished_review=dict(mod_key='twilightforest',status='PARTIAL',draft_file=review['draft_file'],promoted_records=0,remaining='Final deduplication/promotion only; semantic/source closure protected as R2f8.'));write_json(OUT/name,doc)
    decision=read_json(OUT/'research-decision.json');decision.update(checkpoint=cp,next_task=nxt,latest_twilight_subsection_decision='TWILIGHT_REMAINING_CONTENT_COMPLETE',save_mode=False,save_reason='Owner authorizes automatic continuation; do not stop at an arbitrary usage percentage. Protect R2f8 then immediately deduplicate/promote Twilight.')
    decision['checkpoints']['R2f8af-combat-callbacks-complete']=git('rev-parse','HEAD').strip();decision['checkpoints'][cp]='Self: exact SHA supplied after push/live verification.';write_json(OUT/'research-decision.json',decision)
    text='''# R2f8 — TWILIGHT_REMAINING_CONTENT_COMPLETE

The installed Twilight4.8.3345 combat-significant semantic/source review is closed. Final deduplication and promotion remain; the mod ledger is deliberately PARTIAL until that separate checkpoint.

- 277 reviewed mechanic drafts and1,014 path cases. These are pre-deduplication counts, not final distinct counts.
- 40/40 custom DamageTypes USED, one custom status (`twilightforest:frosted`), zero REVIEW_REQUIRED or remaining native ambiguities.
- All1,943 outer classes are represented by the protected discovery index. Supplemental exact combat API scan covers279 methods;19 additional hits are explicit noncombat dispositions with pinned bodies.
- All31 registered nested transformers are covered by protected source witnesses and semantic dispositions. No runtime transformer application is claimed.
- Exact native producer/registry/inheritance/resource evidence and protected source contracts are reused. The supplemental scan alone is not a proof of semantic completeness.
- Forward Twilight namespace scan and reverse scans of four pinned compatibility JARs have no direct Tensura/L2 or Twilight-specific hits respectively. Generic hooks and native optional integrations remain documented; this is not pack-wide runtime compatibility certification.

The19 new exclusions cover native item drops, decorative paintings/item frames, passive Raven worldgen, WIP/debug entities and administrative teleporting. No additional deep utility subsection or new mechanic was created. Historical utility drafts stay immutable; final promotion will disposition them under the corrected combat scope and deduplicate equivalent contracts while preserving materially different delivery.

[Whole source closure](twilightforest-global-source-closure.json), [caller census](twilightforest-global-source-census.json), [compatibility](compat-findings/twilightforest-global.json), [integrity](twilightforest-global-source-integrity.json), [full validation](r2f8-remaining-content-validation.json).

Validation: five tooling tests, installed evidence/reference integrity, protected semantic sections and accepted four mods, source/caller/custom-type coverage, research-only boundaries and diff checks. Runtime0; no L2, Stage, production or Phase6/7 changes. IceAndFire is unstarted.

Exact next task: immediately perform final Twilight deduplication and promotion into the five accepted views and ledger, validate/push/live-verify COMPLETE, then start narrow IceAndFireCE beta15 research.
'''
    (OUT/'twilightforest-r2f8-complete-review.md').write_text(text,encoding='utf-8')
    print('R2f8 whole semantic/source closure assembled; final promotion pending')


if __name__=='__main__':build()
