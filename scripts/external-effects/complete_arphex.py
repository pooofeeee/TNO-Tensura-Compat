"""Close ArPhEx only after canonical source replay and independent full coverage."""
from copy import deepcopy
from collections import Counter
from catalog_common import *
from audit_catalog_integrity import audit_catalog
from promote_combat_batch import validate_batch
from reconcile_native_census import reconcile
from refresh_catalog_views import refresh

CHECKPOINT='R2m7s-arphex-full-native-integrity-and-coverage-complete'
NEXT='R2m8a — AlexCaves pinned-native foundation and first bounded combat family:recover existing deterministic indexes before any new scan,build the finite native queue,and close shared/status admission and actual native producers without Stage policy or production/runtime work.'


def canonical_source_validation(review,census):
    # Replay the actual canonical rows, not historical builders or counts.
    # Empty semantic state makes every current candidate prove its own source.
    prior=deepcopy(review);prior['effects']=[];prior['paths']=[]
    batch=dict(mod_key='arphex',checkpoint=CHECKPOINT,effects=review['effects'],
               paths=review['paths'],exclusions=[],record_refinements=[])
    return validate_batch(batch,prior,census)


def resource_obligations(review):
    opened=set();closed=set();notes=set()
    for name in review['reviewed_batches']:
        b=read_json(OUT/name)
        opened.update(b.get('pending_native_assets',[]))
        closed.update(b.get('closed_native_assets',[]))
        for k in ('pending_scoped_callbacks','pending_shared_contexts'):
            notes.update(str(v) for v in b.get(k,[]))
    return dict(queued_native_assets=sorted(opened),closed_queued_native_assets=sorted(opened&closed),
                remaining_native_assets=sorted(opened-closed),historical_scope_labels=len(notes),
                scope_label_disposition='Superseded by complete independent native method/field context coverage and exact resource follow-ups;historical snapshots do not grant coverage.')


def complete():
    review=read_json(OUT/'mod-reviews/arphex.json');census=read_json(OUT/'arphex-combat-census.json')
    assert review['status']=='PARTIAL', 'Do not overwrite a completed/protected review.'
    source=canonical_source_validation(review,census)
    index,pending=reconcile(review,census)
    assert index['summary']['pending_methods']==0
    obligations=resource_obligations(review);assert not obligations['remaining_native_assets']
    assert all(not r['unresolved_ambiguities'] for r in review['effects'])
    campaign=read_json(OUT/'large-mod-campaign.json')
    for pin in campaign['locked_completed_reviews']:assert sha256(OUT/pin['file'])==pin['sha256']
    before=deepcopy(review['effects']);repairs=[]
    stale='Native template contents and remaining attachment/state/registry/census context stay explicitly queued.'
    replacement='Pinned follow-up template/state/registry and finite-census context contracts are complete.'
    for row in review['effects']:
        if stale in row.get('scope',''):
            assert row['scope'].count(stale)==1
            old=row['scope'];row['scope']=old.replace(stale,replacement)
            repairs.append(dict(mechanic_id=row['id'],field='scope',before=old,after=row['scope'],
                reason='Current canonical scope retained a historical pending claim after its exact follow-up closures. Behavior,source,components and parameters are unchanged.'))
    assert len(repairs)==6
    assert [{k:v for k,v in r.items() if k!='scope'} for r in before]==[
            {k:v for k,v in r.items() if k!='scope'} for r in review['effects']]
    review.update(status='COMPLETE',checkpoint=CHECKPOINT,notes_file='arphex-r2m7s-integrity-closure.json',
        scope='Complete pinned-native Stage-relevant static semantic coverage;all19159 finite methods and explicit native resource obligations independently dispositioned. No Stage eligibility/policy/runtime claims.',
        exact_next_task=NEXT,remaining_native_ambiguities=0,unresolved_native_ambiguities=0,
        semantic_discovery_complete=True,source_mapping_complete=True,delivery_mapping_complete=True,
        coverage_audit_file='arphex-coverage-audit.json',classification_summary_file='arphex-classification-summary.json')
    write_json(OUT/'mod-reviews/arphex.json',review)
    coverage=dict(schema='tno.external_effects.native_coverage_audit.v1',mod_key='arphex',checkpoint=CHECKPOINT,
        status='PASS',whole_mod_complete=True,jar_sha256=census['jar_sha256'],
        original_census_file='arphex-combat-census.json',original_census_sha256=sha256(OUT/'arphex-combat-census.json'),
        canonical_review_sha256=sha256(OUT/'mod-reviews/arphex.json'),
        native_method_coverage=index['summary'],canonical_source_validation=source,
        native_contract_index_sha256=byte_hash(json.dumps(index,sort_keys=True,separators=(',',':')).encode()),
        resource_obligations=obligations,semantic_record_count=len(review['effects']),
        numeric_candidate_count=source['numeric_candidate_entries'],unresolved_count=0,
        proof='Original finite class/method hashes,canonical literal/receiver/primitive consumer replay,independent exact forwarding/bridge/uncalled checks and resource projection obligations. Completion labels and old passing tests do not establish coverage.',
        runtime_validated=False,stage_policy_decided=False)
    write_json(OUT/'arphex-coverage-audit.json',coverage)
    classifications=source['classification_counts'];primitives=Counter(c['primitive'] for r in review['effects'] for c in r['components'])
    groups=dict(VANILLA=sum(classifications.get(k,0) for k in ('VANILLA_DIRECT','VANILLA_EQUIVALENT')),
        VANILLA_LIKE_OR_MIXED=sum(classifications.get(k,0) for k in ('VANILLA_COMPOSITE','VANILLA_LIKE_EXTENDED')),
        CUSTOM=sum(v for k,v in classifications.items() if k.startswith('CUSTOM_')),
        BINARY_OR_SPECIAL=classifications.get('BINARY_MECHANIC',0))
    assert sum(groups.values())==source['semantic_records']
    summary=dict(schema='tno.external_effects.classification_summary.v1',mod_key='arphex',status='COMPLETE',checkpoint=CHECKPOINT,
        semantic_mechanics=source['semantic_records'],classification_counts=classifications,classification_groups=groups,
        primitive_family_counts=dict(sorted(primitives.items())),numeric_candidate_count=source['numeric_candidate_entries'],unresolved_count=0,
        native_method_coverage=index['summary'],coverage_audit_file='arphex-coverage-audit.json',
        excluded_surface_summary=['Source-proven rendering/model/particle/sound and client display contexts,including actual native animation/preview cleanup writes.',
            'Ordinary container/storage/mining/repair/acquisition/chat/cosmetic utilities;material combat lifecycle retained.',
            'Exact registration/accessor/bridge/serialization/query bodies with their independent native producers/targets.',
            'Unreferenced static shoot overload families proven from the original complete calls,handles and annotations.',
            'Ordinary worldgen decoration;configured saved combat/template/spawner data retained separately from attack scalars.'],
        native_source_diagnostics=read_json(OUT/'discovery/arphex-scan.json').get('resource_parse_errors',[]),
        scope='Static semantic coverage of the pinned native artifact;source diagnostics and native failure branches are preserved. No runtime readiness,Stage eligibility or balance decision.')
    write_json(OUT/'arphex-classification-summary.json',summary)
    ledger=read_json(OUT/'mod-completion-ledger.json');target=next(t for t in ledger['targets'] if t['mod_key']=='arphex')
    target.update(state='COMPLETE',detail=review['scope'],semantic_effect_count=source['semantic_records'],
        numeric_candidate_count=source['numeric_candidate_entries'],classification_counts=classifications,
        remaining_native_ambiguities=0,pending_native_method_count=0,pending_semantic_method_count=0,
        coverage_audit_file='arphex-coverage-audit.json',checkpoint_file='arphex-r2m7s-integrity-closure.json',
        classification_summary_file='arphex-classification-summary.json',exact_next_task=NEXT)
    ledger.update(checkpoint=CHECKPOINT,status='PARTIAL',exact_next_task=NEXT);write_json(OUT/'mod-completion-ledger.json',ledger)
    campaign.update(checkpoint=CHECKPOINT,current_mod='alexscaves',exact_next_task=NEXT,status='PARTIAL')
    campaign['last_completed_census']=campaign.pop('current_census')
    campaign['last_completed_census']['coverage_audit_file']='arphex-coverage-audit.json'
    campaign['locked_completed_reviews'].append(dict(file='mod-reviews/arphex.json',sha256=sha256(OUT/'mod-reviews/arphex.json')))
    campaign['closed_batches'].append(dict(file='arphex-r2m7s-integrity-closure.json',mod_key='arphex',semantic_records_added=0,classification_counts={},whole_mod_complete=True))
    write_json(OUT/'large-mod-campaign.json',campaign)
    decision=read_json(OUT/'research-decision.json');decision.update(checkpoint=CHECKPOINT,next_task=NEXT,large_mod_campaign_file='large-mod-campaign.json');write_json(OUT/'research-decision.json',decision)
    refresh();audit=audit_catalog();assert audit['status']=='PASS'
    closure=dict(schema='tno.external_effects.full_native_integrity_closure.v1',mod_key='arphex',checkpoint=CHECKPOINT,status='COMPLETE',
        semantic_records=source['semantic_records'],classification_counts=classifications,classification_groups=groups,
        numeric_candidate_count=source['numeric_candidate_entries'],unresolved_count=0,pending_native_method_count=0,
        canonical_source_replay=source,native_method_coverage=index['summary'],resource_obligations=obligations,
        metadata_repairs=repairs,semantic_records_added=0,semantic_records_removed=0,semantic_records_merged=0,
        semantic_behavior_source_and_parameters_unchanged=True,
        completed_mod_integrity={k:audit[k] for k in ('status','completed_mods_audited','semantic_records','numeric_candidate_entries')},
        locked_prior_reviews_unchanged=len(campaign['locked_completed_reviews'])-1,
        production_changed=False,runtime_tests=0,stage_policy_decided=False,exact_next_task=NEXT)
    write_json(OUT/'arphex-r2m7s-integrity-closure.json',closure)
    print({k:closure[k] for k in ('status','semantic_records','numeric_candidate_count','unresolved_count','pending_native_method_count','completed_mod_integrity')})
    return closure


if __name__=='__main__':complete()
