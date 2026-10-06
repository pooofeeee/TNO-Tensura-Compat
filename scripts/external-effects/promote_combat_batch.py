"""Promote explicitly reviewed native contracts; never infer semantics or policy."""
import argparse
from collections import Counter
from copy import deepcopy

from catalog_common import OUT,read_json,write_json
from audit_catalog_integrity import EvidenceIndex,audit_review
from refresh_catalog_views import refresh


def effect_holder_binding(method,offset):
    """Read the holder argument of this allocation, not a nearby effect query."""
    body=method['instructions'];at=next(n for n,i in enumerate(body) if i['offset']==offset)
    assert 'MobEffectInstance.<init>(' in str(body[at]['operand'])
    start=max(n for n,i in enumerate(body[:at]) if i['opcode']=='0xbb' and
              i['operand']=='net/minecraft/world/effect/MobEffectInstance')
    holder=next(i for i in body[start:at] if i['opcode']=='0xb2' and
                ('/MobEffects.' in str(i['operand']) or '/ArphexModMobEffects.' in str(i['operand'])))
    return holder['operand'],body[start]['offset'],holder['offset']


def damage_source_binding(method,offset):
    """Bind an explicitly allocated native source to its following hurt call.

    This helper supports direct allocation sites only. It does not infer the
    provenance of a source local, field, factory result or an inherited source.
    """
    body=method['instructions'];at=next(n for n,i in enumerate(body) if i['offset']==offset)
    assert '.hurt(' in str(body[at]['operand'])
    start=max(n for n,i in enumerate(body[:at]) if i['opcode']=='0xbb' and
              i['operand']=='net/minecraft/world/damagesource/DamageSource')
    ctor=next(i for i in body[start:at] if 'DamageSource.<init>(' in str(i['operand']))
    holder=next(i for i in body[start:at] if i['opcode']=='0xb2' and
                '/DamageTypes.' in str(i['operand']))
    assert not any('.hurt(' in str(i['operand']) for i in body[start:at])
    return holder['operand'],body[start]['offset'],ctor['offset'],ctor['operand']


def effect_receiver_binding(method,offset):
    """Trace a simple generated LivingEntity cast/local used by addEffect.

    Complex expression recipients require their own exact evidence; this helper
    deliberately refuses to infer them from a decompiler variable name.
    """
    body=method['instructions'];at=next(n for n,i in enumerate(body) if i['offset']==offset)
    assert 'LivingEntity.addEffect(Lnet/minecraft/world/effect/MobEffectInstance;)Z' in str(body[at+1]['operand'])
    start=max(n for n,i in enumerate(body[:at]) if i['opcode']=='0xbb' and
              i['operand']=='net/minecraft/world/effect/MobEffectInstance')
    def local(i,store=False):
        op=int(i['opcode'],16)
        if op==(0x3a if store else 0x19):return i['local_index']
        low=0x4b if store else 0x2a
        assert low<=op<=low+3,('not an object local operation',i)
        return op-low
    receiver=body[start-1];receiver_local=local(receiver)
    stores=[n for n,i in enumerate(body[:start]) if
            (i['opcode']=='0x3a' or 0x4b<=int(i['opcode'],16)<=0x4e) and local(i,True)==receiver_local]
    assert stores,('recipient has no simple cast binding',receiver)
    store=stores[-1];cast=body[store-1];origin=body[store-2]
    assert cast['opcode']=='0xc0' and cast['operand'] in (
        'net/minecraft/world/entity/LivingEntity','net/minecraft/server/level/ServerPlayer')
    assert not any(origin['offset']<i.get('branch_target',-1)<=offset for i in body),('recipient cast is not a closed straight-line binding',origin)
    return dict(origin_local_index=local(origin),origin_load_offset=origin['offset'],
                cast_offset=cast['offset'],cast_type=cast['operand'],
                receiver_local_index=receiver_local,store_offset=body[store]['offset'],
                receiver_load_offset=receiver['offset'])


def validate_batch(batch,review,census):
    assert batch['mod_key']==review['mod_key']==census['mod_key']
    native={(r['entry'],r['method'],r['descriptor']):r for r in census['methods']}
    index=EvidenceIndex();ids={r['id'] for r in review['effects']}
    candidates=set()
    for row in batch['effects']:
        assert row['id'] not in ids,('existing semantic record must be reused',row['id'])
        ids.add(row['id'])
        assert row['actual_behavior'] and row['source_actor'] and row['native_boundary']
        for proof in row['implementation']+row.get('shared_contracts',[]):
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
            expected=dict(entry=consumer['entry'],method=consumer['methods'][0],
                          descriptor=consumer['descriptor'],offset=consumer['offset'])
            assert candidate['native_parameter_identity']==expected,('identity differs from consumer',candidate)
            scalar_sinks=('MobEffectInstance.<init>(','.hurt(','.heal(','.setHealth(',
                '.addEffect(','.setDeltaMovement(','.setYRot(','.setXRot(',
                '.makeStuckInBlock(','.putDouble(','.queueServerWork(','.inflate(',
                'ItemCooldowns.addCooldown(','.teleportTo(',
                '.setBaseDamage(','.shoot(','.push(','.igniteForSeconds(',
                'LivingIncomingDamageEvent.setAmount(')
            rng=(candidate['primitive'] in ('ATTACK_SELECTION','SUMMON_DELIVERY','PROC_CHANCE') and
                 'Mth.nextInt(' in str(hit['operand']))
            assert hit['opcode']=='0xb5' or rng or any(s in str(hit['operand']) for s in scalar_sinks),('not a native scalar consumer',consumer)
            if candidate['primitive'].startswith('MOB_EFFECT_'):
                symbol,allocation,load=effect_holder_binding(m,consumer['offset'])
                assert (symbol,allocation,load)==(candidate['native_holder_symbol'],
                    candidate['native_holder_allocation_offset'],candidate['native_holder_load_offset'])
            if 'native_damage_type_symbol' in candidate:
                assert damage_source_binding(m,consumer['offset'])==(
                    candidate['native_damage_type_symbol'],candidate['native_damage_source_allocation_offset'],
                    candidate['native_damage_source_constructor_offset'],candidate['native_damage_source_constructor'])
            if 'native_receiver_binding' in candidate:
                assert effect_receiver_binding(m,consumer['offset'])==candidate['native_receiver_binding'],('wrong native recipient binding',candidate)
            seen={tuple(expected[k] for k in ('entry','method','descriptor','offset'))}
            for site in candidate.get('additional_consumer_sites',[]):
                identity=tuple(site[k] for k in ('entry','method','descriptor','offset'))
                assert identity not in seen,('duplicate auxiliary site',identity)
                seen.add(identity)
                other_proof=dict(consumer,entry=site['entry'],methods=[site['method']],descriptor=site['descriptor'])
                if site['entry']!=consumer['entry']:
                    assert 'evidence_file' in site and 'witness_id' in site,('cross-class site lacks its own proof',site)
                for key in ('evidence_file','witness_id'):
                    if key in site:other_proof[key]=site[key]
                _,other=index.witness(other_proof,row)
                other_method=next(x for x in other['methods'] if x['name']==site['method'] and x['descriptor']==site['descriptor'])
                other_hit=next(i for i in other_method['instructions'] if i['offset']==site['offset'])
                assert other_hit['operand']==hit['operand'],('auxiliary site uses a different consumer',site)
                if candidate['primitive'].startswith('MOB_EFFECT_'):
                    assert effect_holder_binding(other_method,site['offset'])[0]==candidate['native_holder_symbol']
                if 'native_damage_type_symbol' in candidate:
                    source=damage_source_binding(other_method,site['offset'])
                    assert (source[0],source[3])==(candidate['native_damage_type_symbol'],candidate['native_damage_source_constructor']),('auxiliary source identity differs',site)
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
