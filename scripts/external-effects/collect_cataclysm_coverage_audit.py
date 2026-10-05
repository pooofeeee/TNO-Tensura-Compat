"""Reconcile the existing census with pinned semantic citations; never scan a JAR."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import subprocess

from catalog_common import ROOT, OUT, write_json

PREFIX = 'com/github/L_Ender/cataclysm/'
GROUPS = ('watched_methods', 'custom_damage_key_methods', 'custom_source_factory_methods',
          'effect_reference_methods', 'boss_tag_reader_methods')
NEXT_TASK = ('R2k33b: Native combat blocks/traps and EMP complete bounded family. Start only '
    'blockentities/EMP_Block_Entity, ObsidianExplosionTrapBricks_Block_Entity, '
    'SandstoneIgniteTrap_Block_Entity, Door_Of_Seal_BlockEntity and blocks/Altar_Of_Fire_Block, '
    'EndStoneTeleportTrapBricks, PurpurVoidRuneTrapBlock plus directly reached trap activation, '
    'Poison Dart/owned hazard payloads and material registry/config boundaries. Reuse locked '
    'Guardian/Ignis encounter, Harbinger EMP response, native statuses/sources/runes and all '
    'completed families. Review only missing combat collision/damage/control/lifecycle semantics; '
    'exclude ordinary door/altar/structure utility. Then reconcile remaining R2k33a residual '
    'packet/projectile/inactive-code checks and protected early-contract publication before '
    'final coverage closure. Cataclysm remains PARTIAL.')

# These bindings point to completed facts, not fresh semantic classifications.
LOCKED = {}
def bind(entry, methods, note, fact):
    for method in methods:
        LOCKED[(PREFIX + entry + '.class', method)] = (note, fact)

bind('entity/AnimationMonster/BossMonsters/Ender_Guardian_Entity',
     ['hurt', 'isInvulnerableTo'], 'cataclysm-r2k3a-guardian-admission.json', 'incoming_order')
bind('entity/AnimationMonster/BossMonsters/Ender_Guardian_Entity',
     ['BrokenHelmet'], 'cataclysm-r2k3a-guardian-admission.json', 'helmet_blast')
bind('entity/AnimationMonster/BossMonsters/Ender_Guardian_Entity',
     ['ProperTeleport'], 'cataclysm-r2k3a-guardian-admission.json', 'hug_teleport')
bind('effects/EffectBlessing_Of_Amethyst', ['applyEffectTick'],
     'cataclysm-r2k2c-ghost-fear.json', 'blessing')
bind('effects/EffectGhostForm', ['applyEffectTick'],
     'cataclysm-r2k2c-ghost-fear.json', 'ghost_expiry')
bind('effects/EffectWetness', ['applyEffectTick'],
     'cataclysm-r2k2e-remaining-status.json', 'wetness_core')
bind('event/ServerEventHandler', ['onPlayerAttack', 'onLivingJump', 'onPlaceBlock',
     'onBreakBlock', 'onPlayerInteract3', 'onPlayerInteract4', 'onPlayerInteract5',
     'onPlayerInteract', 'onUseItem'], 'cataclysm-r2k2b-stun.json', 'action_gates')
bind('event/ServerEventHandler', ['BlockHeal'],
     'cataclysm-r2k2c-ghost-fear.json', 'fear')
bind('event/ServerEventHandler', ['preventEffectRemoval'],
     'cataclysm-r2k2c-ghost-fear.json', 'removal_mismatch')
bind('mixin/LivingEntityMixin', ['onCanAttack'],
     'cataclysm-r2k2b-stun.json', 'left_click_and_target')
bind('client/event/ClientEvent', ['MovementInput'],
     'cataclysm-r2k2e-remaining-status.json', 'desert_control')


def generate(source_ref):
    sha = subprocess.check_output(['git', 'rev-parse', source_ref + '^{commit}'],
                                  cwd=ROOT, text=True).strip()
    cache, hashes = {}, {}
    def read(relative):
        if relative not in cache:
            path = (OUT / relative).relative_to(ROOT).as_posix()
            raw = subprocess.check_output(['git', 'show', sha + ':' + path], cwd=ROOT)
            cache[relative] = json.loads(raw)
            hashes[relative] = hashlib.sha256(raw).hexdigest()
        return cache[relative]

    census = read('cataclysm-source-census.json')
    review = read('mod-reviews/cataclysm.json')
    claims = defaultdict(list)
    for record in review['effects']:
        for proof in record.get('implementation', []):
            if proof.get('entry'):
                for method in proof.get('methods', []):
                    claims[(proof['entry'], method)].append((record['id'], proof))
    union = {}
    for group in GROUPS:
        for source in census[group]:
            key = (source['entry'], source['method'], source['descriptor'])
            row = union.setdefault(key, dict(entry=key[0], method=key[1], descriptor=key[2],
                code_sha256=source['code_sha256'], groups=[], hits=[]))
            assert row['code_sha256'] == source['code_sha256']
            row['groups'].append(group)
            for hit in source['hits']:
                if hit not in row['hits']:
                    row['hits'].append(hit)
    residual, counts = [], Counter()
    for key, row in sorted(union.items()):
        points = set()
        cited = claims.get(key[:2], [])
        for record_id, proof in cited:
            if proof.get('evidence_format') == 'VANILLA_COMPARISON':
                continue
            evidence = read(proof['evidence_file'])
            for witness in evidence.get('witnesses', []):
                if witness['entry'] != row['entry']:
                    continue
                for method in witness['methods']:
                    if (method['name'], method['descriptor']) == key[1:]:
                        assert method['code_sha256'] == row['code_sha256']
                        points.update((i['offset'], str(i['operand']))
                                      for i in method['instructions'])
        unaccounted = [i for i in row['hits'] if (i['offset'], str(i['operand'])) not in points]
        if cited and not unaccounted:
            counts['CITED_WITH_NATIVE_WITNESS'] += 1
            continue
        result = dict(entry=row['entry'], method=row['method'], descriptor=row['descriptor'],
                      code_sha256=row['code_sha256'], census_groups=sorted(row['groups']))
        if key[:2] in LOCKED:
            note, fact = LOCKED[key[:2]]
            assert fact in read(note)['facts']
            result.update(disposition='LOCKED_CHECKPOINT_BINDING', checkpoint_file=note,
                          evidence_pointer='/facts/' + fact,
                          reason='Existing completed fact reused; do not re-review.')
        elif all(i['operand'] == 'net/neoforged/neoforge/common/ModConfigSpec$Builder.'
                 'push(Ljava/lang/String;)Lnet/neoforged/neoforge/common/ModConfigSpec$Builder;'
                 for i in row['hits']) and '/config/' in row['entry']:
            result.update(disposition='EXCLUDED_SCAN_FALSE_POSITIVE',
                          reason='Only config-builder push(String) hits; these are not entity movement. '
                                 'Real config consumers retain their own semantic records.')
        elif cited and all(i['operand'] == 'net/minecraft/util/profiling/ProfilerFiller.'
                           'push(Ljava/lang/String;)V' for i in unaccounted):
            result.update(disposition='CITED_WITH_NONCOMBAT_SCAN_REMAINDER',
                          mechanic_ids=sorted({x[0] for x in cited}),
                          reason='Uncaptured hit is only profiler push(String),not entity movement.')
        else:
            result.update(disposition='PENDING_TARGETED_RECONCILIATION',
                          reason='A census citation is not a completed semantic review or proof of '
                                 'runtime reachability. Verify only this missing boundary/reachability; '
                                 'reuse any protected fact before inspecting evidence.',
                          hits_to_reconcile=unaccounted if cited else row['hits'])
            if row['entry'].startswith(PREFIX + 'blocks/') or row['entry'].startswith(PREFIX + 'blockentities/') or row['entry'].endswith('/Poison_Dart_Entity.class'):
                result['queue_domain'] = 'R2k33b_BLOCKS_TRAPS_EMP'
            else:
                result['queue_domain'] = 'LATER_BOUNDED_RESIDUAL_RECONCILIATION'
        counts[result['disposition']] += 1
        residual.append(result)
    assert sum(counts.values()) == len(union)
    return dict(schema='tno.external_effects.cataclysm_coverage_audit.v1',
        checkpoint='R2k33a-cataclysm-coverage-reconciliation-checkpoint',
        source_commit=sha, source_checkpoint=review['checkpoint'], mod_key='cataclysm',
        status='PARTIAL', jar_sha256=census['jar_sha256'],
        scope='Deterministic citation/hit-offset reconciliation only. No new semantic review, '
              'JAR scan,Stage policy,production change or premature completion.',
        summary=dict(total_unique_census_methods=len(union),
            original_census_group_counts={group:len(census[group]) for group in GROUPS},
            counts_by_disposition=dict(sorted(counts.items())),
            pending_methods_by_domain=dict(sorted(Counter(r['queue_domain'] for r in residual
                if r['disposition']=='PENDING_TARGETED_RECONCILIATION').items())),
            total_canonical_semantic_records=len(review['effects']),
            total_canonical_numeric_candidates=sum(len(c['parameters']) for r in review['effects']
                for c in r.get('scalable_parameter_candidates',[])),
            material_unresolved_ambiguity_count=None),
        residual_methods=residual,
        limitations=['Cited instruction coverage is structural evidence,not a new semantic classification '
                     'or whole-mod completeness proof.',
                    'Protected early shared/status/Guardian packages remain locked;final publication '
                    'must reconcile those packages without re-research or copying old Stage-policy prose.',
                    'Registry/resource reachability and non-combat exclusions still require targeted '
                    'closure;the census is a finite review queue,not an eligibility decision.'],
        accessory_reconciliation=dict(sticky_gloves='Existing native-evidence/cataclysm-koboleton-family.json '
                'Koboleton_Entity.lambda$tick$0 contains the exact equipped Sticky Gloves predicate. '
                'Reuse that locked disarm family;absence in global event callbacks is not global absence.',
            bone_reptile='Intrinsic defenses/config merge locked in R2k32v. Renderer roots excluded '
                'from gameplay;do not invent a new passive trigger.',
            berserker='Native attack/armor Curios modifiers locked in R2k32w;do not invent low-HP gates.',
            charge_time='Registry declaration is locked;any consumer or absence claim needs exact '
                'targeted existing-evidence/index proof,not inference from the attribute name.'),
        input_files=[dict(file=key,sha256=value) for key,value in sorted(hashes.items())],
        exact_next_task=NEXT_TASK)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-ref', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    data = generate(args.source_ref)
    write_json(args.output, data)
    print(json.dumps(data['summary'],sort_keys=True))
