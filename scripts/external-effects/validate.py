"""Validate research scope, pinned JARs and catalog referential integrity; no runtime."""
import argparse
from catalog_common import *

def validate():
    inventory=read_json(OUT/'jar-inventory.json')
    assert inventory['baseline']==BASELINE
    assert len(inventory['targets'])==23
    assert {(t['key'],t['filename']) for t in inventory['targets']}==set(TARGETS)
    for target in inventory['targets']+inventory['compat_candidates']:
        if target['status']=='UNAVAILABLE': continue
        assert Path(target['path']).name==target['filename']
        assert sha256(target['path'])==target['sha256'], 'Installed JAR changed: '+target['filename']
        with zipfile.ZipFile(target['path']) as jar:
            for meta in target['metadata']:
                assert byte_hash(jar.read(meta['entry']))==meta['sha256']
    decision=read_json(OUT/'research-decision.json')
    for key in boundary_flags(): assert decision[key] is False, key
    assert decision['baseline']==BASELINE
    files=['effect-catalog.json','effect-sources.json','delivery-path-matrix.json','vanilla-comparison.json','behavior-primitives.json']
    records={name:read_json(OUT/name) for name in files}
    for obj in records.values(): assert obj['baseline']==BASELINE
    catalog=records['effect-catalog.json']
    for ref in catalog['existing_tno_coverage']:
        assert ref['coverage']=='TENSURA_NATIVE_EXISTING_TNO_COVERAGE' and ref['repeat_research'] is False
        assert git('rev-parse',ref['revision']+':'+ref['path'])==ref['git_blob']
    ids=[e['id'] for e in catalog['effects']]
    assert len(ids)==len(set(ids)), 'Duplicate effect id'
    for effect in catalog['effects']:
        if effect.get('primary_classification') is not None:
            assert effect['primary_classification'] in CLASSIFICATIONS
        assert effect['mod_key'] in {key for key,_ in TARGETS if key!='tensura'}
    if (OUT/'discovery-scan.json').exists():
        from audit_discovery import audit
        assert audit()==read_json(OUT/'discovery-audit.json'), 'Discovery audit stale'
        from native_evidence import collect
        from assemble_native import assemble
        for spec_path in (OUT/'native-specifications').glob('*.json'):
            assert collect(read_json(spec_path))==read_json(OUT/'native-evidence'/spec_path.name), 'Native specification witness changed: '+spec_path.name
        for draft_path in (OUT/'partial-drafts').glob('*.json'):
            draft=read_json(draft_path)
            assert draft['baseline']==BASELINE and draft['status']=='PARTIAL'
            assert draft['semantic_coverage_complete'] is False
            assert draft['promoted_to_catalog'] is False
            draft_ids={e['id'] for e in draft['effects']}
            draft_paths={p['id'] for p in draft['paths']}
            assert len(draft_ids)==len(draft['effects']) and len(draft_paths)==len(draft['paths'])
            for row in draft['effects']+draft['paths']:
                for ref in row['implementation']:
                    witnesses=read_json(OUT/ref['evidence_file'])['witnesses']
                    witness=next(w for w in witnesses if w['id']==ref['witness_id'])
                    assert witness['entry']==ref['entry']
                    assert set(ref['methods'])<={m['name'] for m in witness.get('methods',[])}
            for e in draft['effects']:
                assert e['inspection_status']=='DRAFT' and e['primary_classification'] in CLASSIFICATIONS
                assert e['pending'] and e['unresolved_ambiguities'] is None
                assert set(e['delivery_paths'])<=draft_paths
            for p in draft['paths']:
                assert p['status']=='DRAFT' and set(p['effect_ids'])<=draft_ids
                assert set(p['labels'])<=set(DELIVERIES)
        for path in (OUT/'native-findings').glob('*.json'):
            document=read_json(path)
            assert collect(document)==read_json(OUT/'native-evidence'/path.name), 'Native witness changed: '+path.name
            known={e['id'] for e in document['evidence_specifications']}
            for finding in document['findings']:
                assert set(finding['evidence_ids'])<=known
        assert catalog['effects']==assemble(), 'Catalog does not match native findings'
        compat_path=OUT/'compat-findings'/'antarchy-tensura-data.json'
        if compat_path.exists():
            compat=read_json(compat_path)
            target=next(t for t in inventory['compat_candidates'] if t['key']==compat['mod_key'])
            assert target['sha256']==compat['compat_jar_sha256']
            assert compat['definitions']==len(compat['entries'])
            with zipfile.ZipFile(target['path']) as jar:
                for entry in compat['entries']:
                    raw=jar.read(entry['entry'])
                    assert byte_hash(raw)==entry['sha256'] and json.loads(raw)==entry['data']
        parser=read_json(OUT/'parser-validation.json')
        assert parser['status']=='PASS' and parser['tests']==5 and not parser['failures'] and not parser['errors']
        notes=OUT/'partial-notes'/'cultofazazel.json'
        if notes.exists():
            assert collect(read_json(notes))==read_json(OUT/'native-evidence'/'cultofazazel-partial.json')
        for notes in (OUT/'partial-notes').glob('*-r2c*.json'):
            document=read_json(notes)
            assert collect(document)==read_json(OUT/'native-evidence'/notes.name)
            known={e['id'] for e in document['evidence_specifications']}
            for finding in document['findings']:
                assert set(finding.get('source_witness_ids',[]))<=known
        for config_path in (OUT/'config-evidence').glob('*.json'):
            import tomllib
            config=read_json(config_path)
            assert config['baseline']==BASELINE
            assert sha256(config['path'])==config['sha256'], 'Installed config changed: '+config['path']
            assert Path(config['path']).read_bytes().decode('utf-8-sig')==config['text']
            assert tomllib.loads(config['text'])==config['values']
        cult_continuation=OUT/'native-evidence/cultofazazel-r2c2.json'
        if cult_continuation.exists():
            witnesses=read_json(cult_continuation)['witnesses']
            config=next(w for w in witnesses if w['id']=='coa2-config')
            instructions=config['methods'][0]['instructions']
            builds=[i['offset'] for i in instructions if 'ModConfigSpec$Builder.build(' in str(i.get('operand'))]
            defines=[i['offset'] for i in instructions if 'ModConfigSpec$Builder.define' in str(i.get('operand'))]
            assert len(builds)==1 and defines and max(defines)<builds[0], 'Use actual bytecode initialization order'
        vanilla_spec=OUT/'vanilla-specifications'/'variants-prerequisites.json'
        if vanilla_spec.exists():
            from vanilla_reference import prepare
            raw=read_json(OUT/'vanilla-evidence'/'variants-prerequisites.json')
            assert prepare(read_json(vanilla_spec))==raw, 'Raw vanilla witness changed'
            poison=next(c for c in raw['classes'] if c['class_name'].endswith('/PoisonMobEffect'))
            tick=next(m for m in poison['methods'] if m['name']=='applyEffectTick')
            assert any(i['operand']=='net/minecraft/world/damagesource/DamageSources.magic()Lnet/minecraft/world/damagesource/DamageSource;' for i in tick['instructions'])
            loader=read_json(OUT/'instance-loader-reference.json')
            assert sha256(loader['manifest_path'])==loader['manifest_sha256']
            for artifact in loader['artifacts']: assert sha256(artifact['path'])==artifact['sha256']
        for spec_path in (OUT/'reference-specifications').glob('*.json'):
            from selected_reference import collect as collect_reference
            assert collect_reference(read_json(spec_path))==read_json(OUT/'reference-evidence'/spec_path.name)
        for spec_path in (OUT/'vanilla-specifications').glob('*.json'):
            assert prepare(read_json(spec_path))==read_json(OUT/'vanilla-evidence'/spec_path.name)
        reviews=[read_json(p) for p in (OUT/'mod-reviews').glob('*.json')]
        paths=records['delivery-path-matrix.json']['paths']
        assert len({p['id'] for p in paths})==len(paths)
        path_ids={p['id'] for p in paths}
        for review in reviews:
            assert review['baseline']==BASELINE
            if review['status']=='COMPLETE':
                assert all(review[k] for k in ('semantic_discovery_complete','special_damage_discovery_complete','source_mapping_complete','delivery_mapping_complete'))
                for e in review['effects']:
                    assert e['inspection_status']=='VERIFIED' and e['primary_classification'] in CLASSIFICATIONS
                    assert e['components'] and e['implementation'] and e['primary_test_source']
                    assert set(e['delivery_paths'])<=path_ids
            for p in review['paths']:
                assert set(p['labels'])<=set(DELIVERIES) and set(p['effect_ids'])<=set(ids)
        if reviews:
            ledger=read_json(OUT/'mod-completion-ledger.json')
            assert {t['mod_key'] for t in ledger['targets']}=={k for k,_ in TARGETS}
            assert len(ledger['targets'])==23
        if (OUT/'mod-reviews/cultofazazel.json').exists():
            from validate_cult_review import validate_cult
            assert validate_cult()['status']=='PASS'
        if (OUT/'mod-reviews/royalvariations.json').exists():
            from validate_royal_review import validate_royal
            assert validate_royal()['status']=='PASS'
        if (OUT/'mod-reviews/friendsandfoes.json').exists():
            from validate_friends_review import validate_friends
            assert validate_friends()['status']=='PASS'
        if (OUT/'semantic-sections/twilightforest-lich.json').exists():
            from validate_twilight_lich import validate_lich
            assert validate_lich()['status']=='PASS'
        if (OUT/'semantic-sections/twilightforest-naga.json').exists():
            from validate_twilight_naga import validate_naga
            assert validate_naga()['status']=='PASS'
        if (OUT/'semantic-sections/twilightforest-minoshroom-knight.json').exists():
            from validate_twilight_pair import validate_pair
            assert validate_pair()['status']=='PASS'
        if (OUT/'semantic-sections/twilightforest-hydra-urghast.json').exists():
            from validate_twilight_hydra_urghast import validate_hydra_urghast
            assert validate_hydra_urghast()['status']=='PASS'
        if (OUT/'semantic-sections/twilightforest-yeti-queen.json').exists():
            from validate_twilight_yeti_queen import validate_yeti_queen
            assert validate_yeti_queen()['status']=='PASS'
        if (OUT/'semantic-sections/twilightforest-ranged-mobs.json').exists():
            from validate_twilight_remaining import validate_remaining
            assert all(r['status']=='PASS' for _,r in validate_remaining())
        if (OUT/'twilightforest-global-source-closure.json').exists():
            from validate_twilight_global_closure import validate_global_closure
            assert validate_global_closure()['status']=='PASS'
        if (OUT/'twilightforest-final-promotion-map.json').exists():
            from validate_twilight_final import validate_final
            assert validate_final()['status']=='PASS'
        if (OUT/'iceandfire-r2g1-source-foundation.json').exists():
            from validate_iceandfire_foundation import validate_foundation
            assert validate_foundation()['status']=='PASS'
        if (OUT/'iceandfire-r2g2a-frozen-core.json').exists():
            from validate_iceandfire_frozen_core import validate_frozen_core
            assert validate_frozen_core()['status']=='PASS'
        if (OUT/'iceandfire-r2g2b-frozen-dragons.json').exists():
            from validate_iceandfire_frozen_dragons import validate_frozen_dragons
            assert validate_frozen_dragons()['status']=='PASS'
        if (OUT/'iceandfire-r2g3a-siren-song.json').exists():
            from validate_iceandfire_siren import validate_siren
            assert validate_siren()['status']=='PASS'
        if (OUT/'iceandfire-r2g3b-siren-flute-attacks.json').exists():
            from validate_iceandfire_siren_flute import validate_siren_flute
            assert validate_siren_flute()['status']=='PASS'
        if (OUT/'iceandfire-r2g4-gorgon.json').exists():
            from validate_iceandfire_gorgon import validate_gorgon
            assert validate_gorgon()['status']=='PASS'
        if (OUT/'iceandfire-r2g5a-dragon-elements.json').exists():
            from validate_iceandfire_dragon_elements import validate_dragon_elements
            assert validate_dragon_elements()['status']=='PASS'
        if (OUT/'iceandfire-r2g5b-dragon-combat.json').exists():
            from validate_iceandfire_dragon_combat import validate_dragon_combat
            assert validate_dragon_combat()['status']=='PASS'
        if (OUT/'iceandfire-r2g6-cockatrice.json').exists():
            from validate_iceandfire_cockatrice import validate_cockatrice
            assert validate_cockatrice()['status']=='PASS'
        if (OUT/'iceandfire-r2g7-worm-cyclops.json').exists():
            from validate_iceandfire_worm_cyclops import validate_worm_cyclops
            assert validate_worm_cyclops()['status']=='PASS'
        if (OUT/'iceandfire-r2g8a-ghost-troll.json').exists():
            from validate_iceandfire_ghost_troll import validate_ghost_troll
            assert validate_ghost_troll()['status']=='PASS'
        if (OUT/'iceandfire-r2g8b-hydra-serpent.json').exists():
            from validate_iceandfire_hydra_serpent import validate_hydra_serpent
            assert validate_hydra_serpent()['status']=='PASS'
        if (OUT/'iceandfire-r2g8c-avian-mounts.json').exists():
            from validate_iceandfire_avian_mounts import validate_avian_mounts
            assert validate_avian_mounts()['status']=='PASS'
        if (OUT/'iceandfire-r2g8d-dread.json').exists():
            from validate_iceandfire_dread import validate_dread
            assert validate_dread()['status']=='PASS'
        if (OUT/'iceandfire-r2g9a-weapons.json').exists():
            from validate_iceandfire_weapons import validate_weapons
            assert validate_weapons()['status']=='PASS'
        if (OUT/'iceandfire-r2g9b-control.json').exists():
            from validate_iceandfire_control import validate_control
            assert validate_control()['status']=='PASS'
        if (OUT/'iceandfire-r2g10a-closure.json').exists():
            from validate_iceandfire_closure import validate_closure
            assert validate_closure()['status']=='PASS'
    # All pre-existing files, including Phase 6 and the readiness assessment, are immutable here.
    allowed=('docs/external-effects-catalog-research.md','docs/benchmarks/external-effects-catalog/','scripts/external-effects/')
    for line in git('diff','--name-status',BASELINE).splitlines():
        status,path=line.split('\t',1)
        assert status=='A' and path.startswith(allowed), 'Out-of-scope change: '+line
    for path in git('ls-files','--others','--exclude-standard').splitlines():
        assert path.startswith(allowed), 'Out-of-scope untracked file: '+path
    git('diff','--check',BASELINE)
    if decision['status']=='COMPLETE':
        assert decision['decision']=='EXTERNAL_EFFECT_CATALOG_READY_FOR_OWNER_REVIEW'
        assert decision['effect_coverage_complete'] and decision['delivery_coverage_complete']
        assert all(obj['status']=='COMPLETE' for obj in records.values())
        assert all(e.get('inspection_status')=='VERIFIED' for e in catalog['effects'])
    return dict(schema='tno.external_effects.validation.v1',status='PASS',checkpoint=decision['checkpoint'],
        target_jars=len(inventory['targets']),available=inventory['inspected_inventory_count'],
        unavailable=inventory['unavailable_count'],compat_candidates=len(inventory['compat_candidates']),
        catalog_effects=len(ids),complete=decision['status']=='COMPLETE',**boundary_flags())

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--report',required=True); args=parser.parse_args()
    report=validate(); write_json(OUT/args.report,report); print(json.dumps(report,indent=2))
