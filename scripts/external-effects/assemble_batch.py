"""Refresh current research views from per-mod reviews without altering historical evidence."""
from catalog_common import *
from assemble_native import assemble

def refresh(checkpoint):
    reviews={read_json(p)['mod_key']:read_json(p) for p in sorted((OUT/'mod-reviews').glob('*.json'))}
    catalog=read_json(OUT/'effect-catalog.json');catalog.update(status='PARTIAL',checkpoint=checkpoint,effects=assemble(),
        note='Per-mod VERIFIED records coexist with unfinished mods. Cross-mod R3/R4 and the final catalog decision remain incomplete; historical R2a/R2b witnesses are preserved.')
    write_json(OUT/'effect-catalog.json',catalog)
    paths=[p for r in reviews.values() for p in r['paths']]
    for name,key,rows in [
        ('delivery-path-matrix.json','paths',paths),
        ('effect-sources.json','sources',[dict(id='source:'+p['id'],path_id=p['id'],effect_ids=p['effect_ids'],mod_key=p['mod_key'],primary_test_source=p['primary_source'],setup=p['setup'],implementation=p['implementation'],status=p['status']) for p in paths]),
        ('vanilla-comparison.json','comparisons',[dict(effect_id=e['id'],mod_key=e['mod_key'],primary_classification=e['primary_classification'],closest_vanilla=e['closest_vanilla_equivalent'],similarities=e['vanilla_similarities'],differences=e['vanilla_differences'],components=e['components'],status='VERIFIED_PER_MOD') for r in reviews.values() for e in r['effects']])]:
        obj=read_json(OUT/name);obj.update(status='PARTIAL',checkpoint=checkpoint,**{key:rows},note='Completed per-mod mappings only. Cross-mod normalization/source minimization waits for R3.')
        write_json(OUT/name,obj)
    ledger=[]
    for key,filename in TARGETS:
        if key=='tensura':
            state='COMPLETE';detail='Reference-only scope complete: six TENSURA_NATIVE_EXISTING_TNO_COVERAGE references preserved; no repeated family research.'
        elif key in reviews:
            state=reviews[key]['status'];detail=reviews[key].get('scope','Native semantic review')
        elif key=='cultofazazel':
            state='PARTIAL';detail='Continue preserved native notes: registries/client Manipulation/Curios/mask/arrow findings; remaining entity/environment damage paths and final mappings pending.'
        else:
            state='UNSTARTED';detail='Broad scan/source aids exist; semantic review not started. No absence-of-effects conclusion.'
        ledger.append(dict(mod_key=key,filename=filename,state=state,detail=detail,
            semantic_effect_count=len(reviews[key]['effects']) if key in reviews else None,
            remaining_native_ambiguities=reviews[key].get('unresolved_native_ambiguities',[]) if key in reviews else None))
    write_json(OUT/'mod-completion-ledger.json',dict(schema='tno.external_effects.mod_ledger.v1',baseline=BASELINE,checkpoint=checkpoint,status='PARTIAL',targets=ledger))
    return reviews

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('checkpoint');a=p.parse_args();r=refresh(a.checkpoint)
    print('Refreshed',a.checkpoint,{k:len(v['effects']) for k,v in r.items()})
