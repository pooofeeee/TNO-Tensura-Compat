"""Save current pointers honestly; do not promote the incomplete Cult assembly."""
from catalog_common import *
from assemble_batch import refresh

CHECKPOINT='R2c3-partial'
PROTECTED='dd7afafe21b09954e182b4634603ebbc8bd9096c'

if __name__=='__main__':
    refresh(CHECKPOINT)
    ledger=read_json(OUT/'mod-completion-ledger.json')
    cult=next(t for t in ledger['targets'] if t['mod_key']=='cultofazazel')
    assert cult['state']=='PARTIAL' and cult['semantic_effect_count'] is None
    cult['detail']='New selected native/raw-vanilla/installed-loader evidence and 29 provisional records/33 draft paths saved. Final assembly stops after Gilded Golem; see partial-notes/cultofazazel-r2c3-partial.md exact next work. No draft is promoted to the accepted catalog.'
    cult['partial_draft']='partial-drafts/cultofazazel-r2c3-partial.json'
    write_json(OUT/'mod-completion-ledger.json',ledger)
    decision=read_json(OUT/'research-decision.json')
    decision.update(checkpoint=CHECKPOINT,status='PARTIAL',save_mode=True,usage_at_save_percent=81,
        save_reason='Usage check reached81%; stop new research, preserve selected witnesses and incomplete Cult assembly, validate/push and stop. Cult remains PARTIAL; Royal Variations UNSTARTED.',
        next_task='Finish Cult from partial-notes/cultofazazel-r2c3-partial.md and the 29-record draft, starting with remaining block-property/comparison checks and assembly after Gilded Golem. Protect Cult COMPLETE before Royal Variations. Do not restart accepted Variants or broad scans.')
    decision['checkpoints']['R2c2']=PROTECTED
    decision['checkpoints'][CHECKPOINT]='Self: usage-boundary partial evidence and draft checkpoint; not Cult COMPLETE. Exact SHA recorded in final local/live-remote verification.'
    write_json(OUT/'research-decision.json',decision)
    print(CHECKPOINT,': Cult PARTIAL; accepted catalog unchanged; Royal Variations UNSTARTED')
