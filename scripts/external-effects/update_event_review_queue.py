"""Record explicit event-review progress against a finite, already-captured census."""
from catalog_common import OUT,read_json,write_json,sha256


def generate():
    census=read_json(OUT/'arphex-combat-census.json')
    evidence=read_json(OUT/'native-evidence/arphex-global-hooks.json')
    index={(m['entry'],m['method'],m['descriptor']):m for m in census['methods']}
    # Explicitly reviewed contributions, not conclusions derived from method names.
    dispositions={
        'DwellerTargetProcedure':'CLOSED_NATIVE_TARGET_EVENT_CONTRIBUTIONS_ACTOR_PAYLOAD_CONSUMERS_PENDING',
        'EntitiesTickProcedure':'CLOSED_NATIVE_SHARED_ENTITY_TICK_CONTRIBUTIONS_RAW_PRODUCERS_PENDING',
        'ClimbingProcedure':'CLOSED_SHARED_NATIVE_CLIMBING_READER_ACTOR_INITIALIZERS_PENDING',
        'WorldTickProcedure':'CLOSED_NATIVE_SHARED_WORLD_STATE',
        'PlayerChatTormentorProcedure':'CLOSED_COMBAT_FLAG_PRODUCER_MESSAGE_ADMIN_UTILITY',
        'SpiderMothDwellerEntityVisualScaleProcedure':'EXCLUDED_RENDER_ONLY_RETURN_IGNORED',
        'GameModeDetectorProcedure':'OVERLAY_DARKNESS_CLOSED_REMAINING_PLAYER_ROOT_PENDING',
        'AnyItemUsedProcedure':'CLOSED_NATIVE_ACTION_GATE',
        'EntityJumpsProcedure':'CLOSED_NATIVE_STATUS_DELIVERY',
        'DiesWithoutSourceProcedure':'CLOSED_NATIVE_ADMISSION_RESET',
        'EntitySpawnProcedure':'CLOSED_NATIVE_PROJECTILE_JOIN_SETUP',
        'EntitySpawnsProcedure':'CLOSED_NATIVE_ADMISSION_AND_PRESENTATION',
        'PlayerSleepsProcedure':'CLOSED_NATIVE_SLEEP_EVENT_REQUEST',
        'PlayerTriesToSleepProcedure':'CLOSED_NATIVE_SLEEP_EVENT_REQUEST',
        'GlobalBlockPlacedProcedure':'CLOSED_NATIVE_CONFINEMENT_GATE',
        'GlobalBlockBrokenProcedure':'CLOSED_NATIVE_CONFINEMENT_AND_UTILITY_CONTEXT',
        'AnimationTransferProcedure':'EXCLUDED_EMPTY_HANDLER',
        'TestProcedure':'EXCLUDED_LOGGING_ONLY',
        'PlayerJoinsProcedure':'EXCLUDED_MESSAGE_AND_PRESENTATION_LATCH',
        'NoDropDimensionProcedure':'EXCLUDED_INVENTORY_SAFETY_UTILITY',
        'PlayerRespawnsProcedure':'EXCLUDED_RESPAWN_DESTINATION_UTILITY',
        'BreakBlockProcedure':'ENCOUNTER_LOCATOR_STICK_BUG_PENDING_FAMILY',
        'EntitySpawnReasonProcedure':'EXCLUDED_UNREGISTERED_UNCALLED_SCOPE',
        'ScorpioidBloodlusterEntityVisualScaleProcedure':'EVENT_RETURN_IGNORED_PHYSICAL_DIMENSION_READER_PENDING',
        'SpiderMothDwellerBoundingBoxScaleProcedure':'EVENT_RETURN_IGNORED_NO_EXTERNAL_CONSUMER',
        'RushScareSolidBoundingBoxConditionProcedure':'EVENT_RETURN_IGNORED_COLLISION_READER_PENDING',
        'BloodWormEntityVisualScaleProcedure':'EVENT_RETURN_IGNORED_RENDER_GETTER_ONLY',
        'MaggotOnInitialEntitySpawnProcedure':'SHARED_RENDER_INITIALIZATION_CONTEXT_PENDING_FAMILY',
        'BloodWormOnInitialEntitySpawnProcedure':'RESISTANCE_CLOSED_SHARED_STATE_CONSUMERS_PENDING',
        'EntityJoinsWorldProcedure':'PROJECTILE_CLEANUP_OWNER_INHERITANCE_CLOSED_CRAB_ENCOUNTER_LOCATOR_PENDING',
        'WorldLoadProcedure':'INITIALIZED_RENDER_PATRON_FOREIGN_MOD_FLAGS_CONTEXT',
        'EntityHurtWithoutSourceProcedure':'CLOSED_CAUSING_NULL_ADMISSION_TRANSFER_READERS_PENDING',
        'SpiderShieldProcedure':'CLOSED_SOURCEFUL_REACTIVE_SHIELD_LENS_READER_PENDING',
        'CriticalHitProcedure':'CLOSED_NATIVE_CRITICAL_CONTROL_AXE_STATE_PRODUCER_PENDING',
        'Lifesteal2Procedure':'CLOSED_DIRECT_CAUSING_HIT_GATES_ACTOR_STATE_READERS_PENDING',
        'DwellerLifestealProcedure':'CLOSED_NATIVE_INCOMING_CONTRIBUTIONS_ACTOR_ITEM_STATE_CONSUMERS_PENDING',
    }
    roots=[]
    for w in evidence['witnesses']:
        subscribed=any(a['descriptor'].endswith('/EventBusSubscriber;') for a in w['annotations'])
        for method in w['methods']:
            annotations=[a for a in method['annotations'] if a['descriptor'].endswith('/SubscribeEvent;')]
            if not annotations:continue
            key=(w['entry'],method['name'],method['descriptor']);assert index[key]['code_sha256']==method['code_sha256']
            name=w['entry'].split('/')[-1][:-6]
            roots.append(dict(entry=w['entry'],method=method['name'],descriptor=method['descriptor'],
                code_sha256=method['code_sha256'],class_subscriber_declared=subscribed,
                explicit_subscription_values=annotations[0]['values'],
                disposition=dispositions.get(name,'PENDING_NATIVE_SEMANTIC_REVIEW'),
                evidence_file='native-evidence/arphex-global-hooks.json',witness_id=w['id']))
    roots.sort(key=lambda r:(r['entry'],r['method'],r['descriptor']))
    result=dict(schema='tno.external_effects.event_review_queue.v1',mod_key='arphex',
        checkpoint=read_json(OUT/'mod-completion-ledger.json')['checkpoint'],finite_census_file='arphex-combat-census.json',
        finite_census_sha256=sha256(OUT/'arphex-combat-census.json'),
        roots=roots,whole_mod_complete=False,
        note='This tracks reviewed event contributions only. Ignored event returns do not exclude other live getter consumers. Evidence capture and partial method dispositions do not prove family or mod completion.',
        exact_next_task=read_json(OUT/'mod-completion-ledger.json')['exact_next_task'])
    write_json(OUT/'arphex-event-review-queue.json',result)
    return result


if __name__=='__main__':
    from collections import Counter
    result=generate();print(dict(sorted(Counter(r['disposition'] for r in result['roots']).items())))
