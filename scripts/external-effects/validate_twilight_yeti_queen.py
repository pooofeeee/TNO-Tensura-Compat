"""R2f7 integrity, preservation and installed-bytecode semantic guardrails."""
from collections import Counter
from catalog_common import *
from classfile import ClassFile
from assemble_twilight_yeti_queen import START,DECISION,BATCH
from collect_twilight_yeti_queen import FULL,FIELDS,scan_callers
from validate_twilight_hydra_urghast import validate_hydra_urghast


def validate_yeti_queen():
    previous=validate_hydra_urghast()
    prefix='docs/benchmarks/external-effects-catalog/'
    mutable={prefix+x for x in ['behavior-primitives.json','delivery-path-matrix.json','effect-catalog.json','effect-sources.json','mod-completion-ledger.json','mod-reviews/twilightforest.json','research-decision.json','vanilla-comparison.json','twilightforest-owner-table.md']}
    # Earlier validator retains exact archived45/126 section checks, permits subsequent ledger growth.
    mutable.update(['scripts/external-effects/validate.py','scripts/external-effects/validate_twilight_hydra_urghast.py'])
    protected=[p for p in git('ls-tree','-r','--name-only',START,'--',prefix,'scripts/external-effects/').splitlines() if p not in mutable]
    for p in protected:
        old=subprocess.check_output(['git','show',START+':'+p],cwd=ROOT)
        assert (ROOT/p).read_bytes().replace(b'\r\n',b'\n')==old.replace(b'\r\n',b'\n'),p
    old_validator=subprocess.check_output(['git','show',START+':scripts/external-effects/validate_twilight_hydra_urghast.py'],cwd=ROOT).decode().replace('\r\n','\n')
    allowed_validator=old_validator.replace("ledger['draft_mechanic_count']==45 and ledger['draft_path_count']==126","ledger['draft_mechanic_count']>=45 and ledger['draft_path_count']>=126")
    assert (ROOT/'scripts/external-effects/validate_twilight_hydra_urghast.py').read_text()==allowed_validator
    s=read_json(OUT/'semantic-sections/twilightforest-yeti-queen.json')
    assert s['subsection_decision']==DECISION and set(s['boss_states'].values())=={'SEMANTIC_REVIEW_COMPLETE'}
    assert len(s['closure_checklist'])==18 and all(s['closure_checklist'].values())
    assert len(s['effects'])==15 and len(s['paths'])==41
    assert s['counts']['per_boss']=={'alpha_yeti':{'packages':7,'paths':22},'snow_queen':{'packages':8,'paths':19}}
    counts=dict(Counter(e['primary_classification'] for e in s['effects']))
    assert counts=={'BINARY_MECHANIC':2,'CUSTOM_RESOURCE':2,'CUSTOM_CONTROL':5,'CUSTOM_DAMAGE':4,'VANILLA_LIKE_EXTENDED':2}
    assert s['counts']['classification_totals']==counts and s['counts']['review_required']==0
    assert all(e['alternate_sources'] and e['primary_test_source'] for e in s['effects'])
    assert all(p['future_controls'] and p['setup'] for p in s['paths'])
    old=read_json(OUT/'partial-drafts/twilightforest-r2f6-partial.json');new=read_json(OUT/'partial-drafts/twilightforest-r2f7-partial.json')
    assert new['effects']==old['effects']+s['effects'] and len(new['effects'])==60
    assert new['paths']==old['paths']+s['paths'] and len(new['paths'])==167
    reused=set()
    for r in s['protected_effect_links']:
        assert sha256(OUT/r['evidence_file'])==r['sha256']
        assert set(r['effect_ids'])<={e['id'] for e in read_json(OUT/r['evidence_file'])['effects']}
        reused.update(r['effect_ids'])
    assert reused=={'twilightforest:frosted_package','twilightforest:ice_bomb_package'}
    assert not reused & {e['id'] for e in s['effects']}
    links=[p for p in s['paths'] if p.get('reuses_protected_effect_ids')]
    assert len(links)==2 and all(set(p['reuses_protected_effect_ids'])==reused for p in links)
    profiles={p['type']:p for p in s['damage_profiles']}
    assert set(profiles)=={'twilightforest:'+x.lower() for x in FIELDS}
    assert all(p['status']=='USED' for p in profiles.values())
    assert set(profiles['twilightforest:chilling_breath']['tags'])=={'neoforge:is_magic'}
    assert set(profiles['twilightforest:squish']['tags'])=={'neoforge:is_physical'}
    assert {'minecraft:bypasses_armor','minecraft:bypasses_shield','minecraft:is_fall'}<=set(profiles['twilightforest:yeeted']['tags'])
    assert set(profiles['twilightforest:falling_ice']['tags'])=={'minecraft:bypasses_enchantments','neoforge:is_environment','neoforge:is_physical'}
    assert s['damage_census']['reviewed_profiles_after']==17 and s['damage_census']['remaining_profiles']==23
    witnesses={}
    for p in (OUT/'native-evidence').glob('*.json'):
        for w in read_json(p).get('witnesses',[]):
            if w.get('mod_key')=='twilightforest' and w['entry'].endswith('.class'):witnesses.setdefault(w['entry'],[]).extend(w['methods'])
    def methods(c):return witnesses['twilightforest/'+c+'.class']
    def ins(c,m):return next(x['instructions'] for x in methods(c) if x['name']==m)
    def pos(i,t):return next(x['offset'] for x in i if t in str(x['operand']))
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest')
    assert sha256(target['path'])==target['sha256']
    with zipfile.ZipFile(target['path']) as jar:
        for c in FULL:
            actual={(m['name'],m['descriptor']) for m in ClassFile(jar.read('twilightforest/'+c+'.class')).methods}
            assert actual=={(m['name'],m['descriptor']) for m in methods(c)},c
    scan=read_json(OUT/'twilightforest-yeti-queen-caller-scan.json');assert scan==scan_callers(target)
    runtime=[x for x in scan['hits'] if '/data/' not in x['entry'] and '/init/' not in x['entry']]
    assert Counter(x['entry'] for x in runtime)==Counter({'twilightforest/entity/projectile/FallingIce.class':1,'twilightforest/events/HostileMountEvents.class':1,'twilightforest/entity/boss/SnowQueen.class':2})
    A='entity/boss/AlphaYeti';Q='entity/boss/SnowQueen';F='entity/projectile/FallingIce';T='entity/ai/goal/ThrowRiderGoal';E='events/HostileMountEvents';Y='components/entity/YetiThrowAttachment';S='entity/boss/SnowQueenIceShield';B='entity/ai/goal/HoverBeamGoal';I='entity/monster/IceCrystal'
    ah=ins(A,'hurt');assert pos(ah,'DamageTypeTags.IS_PROJECTILE')<pos(ah,'BaseTFBoss.hurt(')<max(x['offset'] for x in ah if '.canRampageZ' in str(x['operand']))
    fall=ins(A,'causeFallDamage');assert pos(fall,'.hitNearbyEntities(')<pos(fall,'BaseTFBoss.causeFallDamage(')
    assert not any('canEntityGrief' in str(x['operand']) for x in ins(A,'makeBlockAboveTargetFall'))
    assert any('canEntityGrief' in str(x['operand']) for x in ins(A,'makeRandomBlockFall'))
    grab=ins(T,'checkAndPerformAttack');assert any('.startRiding(' in str(x['operand']) for x in grab)
    assert not any('.hurt(' in str(x['operand']) or '.doHurtTarget(' in str(x['operand']) for x in grab)
    event=ins(E,'handleMountDamage');assert pos(event,'DamageTypes.FALL')<pos(event,'.getAmount(')<pos(event,'TFDamageTypes.YEETED')<pos(event,'.hurt(')
    assert not any('.setHealth(' in str(x['operand']) for x in event)
    qhurt=ins(Q,'hurt');assert pos(qhurt,'BaseTFBoss.hurt(')<pos(qhurt,'.getCurrentPhase(')
    assert any(int(x['opcode'],16)==0x8b for x in qhurt) and not any('.getHealth(' in str(x['operand']) for x in qhurt)
    shield=ins(S,'hurt');assert any('AbstractArrow.getPierceLevel(' in str(x['operand']) for x in shield)
    assert not any('.hurt(' in str(x['operand']) or '.setHealth(' in str(x['operand']) or '.discard(' in str(x['operand']) for x in shield)
    contact=ins(Q,'applyShieldCollision');assert pos(contact,'.push(')<pos(contact,'.doHurtTarget(')<pos(contact,'.setDeltaMovement(')
    breath=ins(Q,'doBreathAttack');i=next(n for n,x in enumerate(breath) if '.hurt(' in str(x['operand']));assert int(breath[i+1]['opcode'],16)==0x57
    ray=ins(B,'doRayAttack');assert not any('ClipContext' in str(x['operand']) or 'Level.clip(' in str(x['operand']) for x in ray)
    assert sum('.doBreathAttack(' in str(x['operand']) for x in ray)==2
    summon=ins(Q,'summonMinionAt');assert pos(summon,'.addFreshEntity(')<pos(summon,'.randomTeleport(')<pos(summon,'.setTarget(')<pos(summon,'.setToDieIn30Seconds(')
    for c in [A,Q,I,Y]:assert not {'addAdditionalSaveData','readAdditionalSaveData','serializeNBT','deserializeNBT'} & {m['name'] for m in methods(c)}
    save=ins(F,'addAdditionalSaveData');assert not any('hangTime' in str(x['operand']) for x in save)
    ledger=read_json(OUT/'mod-reviews/twilightforest.json')
    assert ledger['status']=='PARTIAL' and not ledger['effects'] and not ledger['paths']
    assert ledger['draft_mechanic_count']>=60 and ledger['draft_path_count']>=167
    return dict(schema='tno.external_effects.yeti_queen_integrity.v1',status='PASS',starting_sha=START,decision=DECISION,boss_states=s['boss_states'],counts=s['counts'],protected_prior_files=len(protected),full_declared_class_coverage=len(FULL),caller_scan_exact_reproduction=True,protected_frosted_packages_reused=len(reused),twilight_reviewed_drafts=60,twilight_delivery_drafts=167,accepted_counts_unchanged=previous['accepted_counts_unchanged'],damage_profiles_reviewed=17,damage_profiles_remaining=23,runtime_tests=0,promoted_twilight_records=0,**boundary_flags())


if __name__=='__main__':
    result=validate_yeti_queen();write_json(OUT/'twilightforest-yeti-queen-integrity.json',result);print(json.dumps(result,indent=2))
