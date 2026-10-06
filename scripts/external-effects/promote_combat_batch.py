"""Promote explicitly reviewed native contracts; never infer semantics or policy."""
import argparse
from collections import Counter
from copy import deepcopy

from catalog_common import OUT,read_json,write_json
from audit_catalog_integrity import EvidenceIndex,audit_review
from refresh_catalog_views import refresh


def validate_batch(batch,review,census):
    assert batch['mod_key']==review['mod_key']==census['mod_key']
    native={(r['entry'],r['method'],r['descriptor']):r for r in census['methods']}
    index=EvidenceIndex();ids={r['id'] for r in review['effects']}
    candidates=set()
    for row in batch['effects']:
        assert row['id'] not in ids,('existing semantic record must be reused',row['id'])
        ids.add(row['id'])
        assert row['actual_behavior'] and row['source_actor'] and row['native_boundary']
        for proof in row['implementation']:
            _,w=index.witness(proof,row)
            for m in w['methods']:
                if m['name'] in proof['methods']:
                    if proof.get('evidence_format')=='VANILLA_COMPARISON':
                        continue
                    key=(proof['entry'],m['name'],m['descriptor'])
                    assert native[key]['code_sha256']==m['code_sha256'],('unindexed native contract',key)
        for candidate in row['scalable_parameter_candidates']:
            consumer=candidate['native_consumer']
            _,w=index.witness(consumer,row)
            m=next(m for m in w['methods'] if m['name']==consumer['methods'][0] and m['descriptor']==consumer['descriptor'])
            hit=next(i for i in m['instructions'] if i['offset']==consumer['offset'])
            assert hit['operand']==consumer['operand'],('detached native parameter',row['id'],candidate)
            assert hit['opcode']==consumer['opcode']
            scalar_sinks=('MobEffectInstance.<init>(','.hurt(','.heal(','.setHealth(',
                '.addEffect(','.setDeltaMovement(','.setYRot(','.setXRot(',
                '.makeStuckInBlock(','.putDouble(','.queueServerWork(','.inflate(',
                'ItemCooldowns.addCooldown(')
            rng=(candidate['primitive'] in ('ATTACK_SELECTION','SUMMON_DELIVERY') and
                 'Mth.nextInt(' in str(hit['operand']))
            assert hit['opcode']=='0xb5' or rng or any(s in str(hit['operand']) for s in scalar_sinks),('not a native scalar consumer',consumer)
            assert consumer['entry']==candidate['native_parameter_identity']['entry']
            for parameter in candidate['parameters']:
                identity=tuple(candidate['native_parameter_identity'][k] for k in ('entry','method','descriptor','offset'))+(candidate['primitive'],parameter)
                assert identity not in candidates,('same native parameter counted twice',identity)
                candidates.add(identity)
    merged=deepcopy(review)
    merged['effects']+=batch['effects'];merged['paths']+=batch['paths']
    return audit_review(merged,index)


def promote(batch_path):
    batch=read_json(batch_path);key=batch['mod_key']
    review=read_json(OUT/'mod-reviews'/f'{key}.json')
    census=read_json(OUT/f'{key}-combat-census.json')
    summary=validate_batch(batch,review,census)
    review['effects']=sorted(review['effects']+batch['effects'],key=lambda r:r['id'])
    review['paths']=sorted(review['paths']+batch['paths'],key=lambda r:r['id'])
    review.update(checkpoint=batch['checkpoint'],notes_file=batch_path.name,
        scope=batch['closed_scope'],exact_next_task=batch['exact_next_task'])
    review.setdefault('reviewed_batches',[]).append(batch_path.name)
    write_json(OUT/'mod-reviews'/f'{key}.json',review)
    ledger=read_json(OUT/'mod-completion-ledger.json')
    ledger.update(checkpoint=batch['checkpoint'],exact_next_task=batch['exact_next_task'])
    target=next(t for t in ledger['targets'] if t['mod_key']==key)
    target.update(state='PARTIAL',detail=batch['closed_scope']+' Other finite census contracts remain pending.',
        exact_next_task=batch['exact_next_task'],semantic_effect_count=summary['semantic_records'],
        numeric_candidate_count=summary['numeric_candidate_entries'])
    write_json(OUT/'mod-completion-ledger.json',ledger)
    campaign=read_json(OUT/'large-mod-campaign.json')
    campaign.update(checkpoint=batch['checkpoint'],exact_next_task=batch['exact_next_task'])
    campaign.setdefault('closed_batches',[]).append(dict(file=batch_path.name,mod_key=key,
        semantic_records_added=len(batch['effects']),classification_counts=dict(sorted(Counter(r['primary_classification'] for r in batch['effects']).items()))))
    write_json(OUT/'large-mod-campaign.json',campaign)
    decision=read_json(OUT/'research-decision.json')
    decision.update(checkpoint=batch['checkpoint'],next_task=batch['exact_next_task'],
        large_mod_campaign_file='large-mod-campaign.json')
    write_json(OUT/'research-decision.json',decision)
    refresh()
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('batch',type=__import__('pathlib').Path)
    print(promote(parser.parse_args().batch))
