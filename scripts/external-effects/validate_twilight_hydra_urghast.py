"""R2f6 integrity, prior-checkpoint preservation and installed semantic guardrails."""
from collections import Counter
from catalog_common import *
from classfile import ClassFile
from assemble_twilight_hydra_urghast import START, DECISION, BATCH
from collect_twilight_hydra_urghast import FULL
from validate_twilight_pair import validate_pair


def validate_hydra_urghast():
    previous=validate_pair()
    prefix='docs/benchmarks/external-effects-catalog/'
    mutable={prefix+x for x in ['behavior-primitives.json','delivery-path-matrix.json','effect-catalog.json',
        'effect-sources.json','mod-completion-ledger.json','mod-reviews/twilightforest.json',
        'research-decision.json','vanilla-comparison.json','twilightforest-owner-table.md']}
    protected=[p for p in git('ls-tree','-r','--name-only',START,'--',prefix,'scripts/external-effects/').splitlines()
               if p not in mutable and p!='scripts/external-effects/validate.py']
    for p in protected:
        old=subprocess.check_output(['git','show',START+':'+p],cwd=ROOT)
        assert (ROOT/p).read_bytes().replace(b'\r\n',b'\n')==old.replace(b'\r\n',b'\n'),p
    s=read_json(OUT/'semantic-sections/twilightforest-hydra-urghast.json')
    assert s['subsection_decision']==DECISION and set(s['boss_states'].values())=={'SEMANTIC_REVIEW_COMPLETE'}
    assert len(s['closure_checklist'])==15 and all(s['closure_checklist'].values())
    assert len(s['effects'])==16 and len(s['paths'])==43
    assert s['counts']['per_boss']=={'hydra':{'packages':8,'paths':22},'ur_ghast':{'packages':8,'paths':21}}
    counts=dict(Counter(e['primary_classification'] for e in s['effects']))
    assert counts=={'BINARY_MECHANIC':1,'CUSTOM_RESOURCE':3,'CUSTOM_CONTROL':5,'CUSTOM_DAMAGE':4,'VANILLA_LIKE_EXTENDED':2,'VANILLA_DIRECT':1}
    assert s['counts']['classification_totals']==counts and s['counts']['review_required']==0
    assert all(e['alternate_sources'] and e['primary_test_source'] for e in s['effects'])
    assert all(p['future_controls'] and p['setup'] for p in s['paths'])
    old=read_json(OUT/'partial-drafts/twilightforest-r2f5-partial.json');new=read_json(OUT/'partial-drafts/twilightforest-r2f6-partial.json')
    assert new['effects']==old['effects']+s['effects'] and len(new['effects'])==45
    assert new['paths']==old['paths']+s['paths'] and len(new['paths'])==126
    profiles={p['type']:p for p in s['damage_profiles']}
    wanted=['HYDRA_BITE','HYDRA_FIRE','HYDRA_MORTAR','GHAST_TEAR']
    assert set(profiles)=={'twilightforest:'+x.lower() for x in wanted}
    assert all(p['status']=='USED' for p in profiles.values())
    assert {'minecraft:bypasses_armor','minecraft:bypasses_shield','minecraft:damages_helmet','minecraft:no_knockback'}<=set(profiles['twilightforest:ghast_tear']['tags'])
    for name in ['hydra_fire','hydra_mortar']:
        tags=set(profiles['twilightforest:'+name]['tags'])
        assert 'minecraft:is_fire' in tags and not tags & {'minecraft:is_projectile','minecraft:is_explosion','minecraft:bypasses_armor'}
    assert 'neoforge:is_physical' in profiles['twilightforest:hydra_bite']['tags']
    assert s['damage_census']['reviewed_profiles_after']==13 and s['damage_census']['remaining_profiles']==27
    witnesses={}
    for p in (OUT/'native-evidence').glob('*.json'):
        for w in read_json(p).get('witnesses',[]):
            if w.get('mod_key')=='twilightforest' and w['entry'].endswith('.class'):
                witnesses.setdefault(w['entry'],[]).extend(w['methods'])
    def methods(c):return witnesses['twilightforest/'+c+'.class']
    def ins(c,m):return next(x['instructions'] for x in methods(c) if x['name']==m)
    def pos(i,t):return next(x['offset'] for x in i if t in str(x['operand']))
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest')
    assert sha256(target['path'])==target['sha256']
    actual_hits=[]
    with zipfile.ZipFile(target['path']) as jar:
        for c in FULL:
            actual={(m['name'],m['descriptor']) for m in ClassFile(jar.read('twilightforest/'+c+'.class')).methods}
            assert actual=={(m['name'],m['descriptor']) for m in methods(c)},c
        for entry in jar.namelist():
            if not entry.startswith('twilightforest/') or not entry.endswith('.class'):continue
            data=jar.read(entry)
            if not any(n.encode() in data for n in wanted):continue
            cls=ClassFile(data)
            for m in cls.methods:
                for i in cls.instructions(m.get('code',b'')):
                    if any('TFDamageTypes.'+n+'Lnet/minecraft/resources/ResourceKey;' in str(i['operand']) for n in wanted):
                        actual_hits.append(dict(entry=entry,class_sha256=byte_hash(data),method=m['name'],descriptor=m['descriptor'],instruction=i))
    scan=read_json(OUT/'twilightforest-hydra-urghast-caller-scan.json')
    assert scan['jar_sha256']==target['sha256'] and scan['hits']==actual_hits
    runtime=[x for x in actual_hits if '/entity/' in x['entry']]
    assert Counter((x['entry'],x['method']) for x in runtime)==Counter({
        ('twilightforest/entity/boss/Hydra.class','isInvulnerableTo'):1,
        ('twilightforest/entity/boss/HydraHeadContainer.class','executeAttacks'):2,
        ('twilightforest/entity/boss/HydraMortar.class','detonate'):1,
        ('twilightforest/entity/boss/UrGhast.class','doTantrumDamageEffects'):1})
    H='entity/boss/Hydra';C='entity/boss/HydraHeadContainer';M='entity/boss/HydraMortar';U='entity/boss/UrGhast';F='entity/projectile/UrGhastFireball';T='block/entity/GhastTrapBlockEntity'
    head=ins(H,'attackEntityFromPart')
    assert pos(head,'.destroyBlocksInAABB(')<pos(head,'.calculateRange(')<pos(head,'.getCurrentMouthOpen(')<pos(head,'BaseTFBoss.hurt(')<pos(head,'.addDamage(')
    assert sum('BaseTFBoss.hurt(' in str(i['operand']) for i in head)==2
    assert sum('.addDamage(' in str(i['operand']) for i in head)==2
    assert any(i['opcode']=='0x8b' for i in ins(C,'addDamage'))  # float -> int counter
    assert not any('.getHealth(' in str(i['operand']) for i in ins(C,'addDamage'))
    det=ins(M,'detonate');assert pos(det,'.explode(')<pos(det,'.getEntities(')<pos(det,'.hurt(')<pos(det,'.igniteForSeconds(')<pos(det,'.discard(')
    assert not {'addAdditionalSaveData','readAdditionalSaveData','onDeflection'} & {m['name'] for m in methods(M)}
    assert not {'addAdditionalSaveData','readAdditionalSaveData','hurt'} & {m['name'] for m in methods(F)}
    hit=ins(F,'onHitEntity');h=next(n for n,i in enumerate(hit) if '.hurt(' in str(i['operand']))
    assert hit[h+1]['opcode']=='0x57'  # discarded hurt return
    assert pos(hit,'.hurt(')<pos(hit,'.doPostAttackEffects(')<pos(hit,'.explode(')<pos(hit,'.discard(')
    assert any(int(i['opcode'],16)==1 and pos(hit,'.doPostAttackEffects(')<i['offset']<pos(hit,'.explode(') for i in hit)  # explicit null source
    ur=ins(U,'hurt');assert pos(ur,'.isInTantrum(')<pos(ur,'.getHealth(')<pos(ur,'BaseTFBoss.hurt(')<pos(ur,'.switchPhase(')
    ai=ins(U,'customServerAiStep');assert pos(ai,'.discard(')<pos(ai,'.heal(')
    assert not any('.setHealth(' in str(i['operand']) for i in ai)
    trap=ins(T,'tickActive');assert pos(trap,'.setInTantrum(')<pos(trap,'.setInTrap(')<pos(trap,'.setDeltaMovement(')<pos(trap,'.hurt(')
    assert not {'saveAdditional','loadAdditional','addAdditionalSaveData','readAdditionalSaveData'} & {m['name'] for m in methods(T)}
    assert 'CUSTOM_RESOURCE'==next(e for e in s['effects'] if e['id']=='twilightforest:hydra_head_resource')['primary_classification']
    ledger=read_json(OUT/'mod-reviews/twilightforest.json')
    assert ledger['status']=='PARTIAL' and not ledger['effects'] and not ledger['paths']
    assert ledger['draft_mechanic_count']==45 and ledger['draft_path_count']==126
    return dict(schema='tno.external_effects.hydra_urghast_integrity.v1',status='PASS',starting_sha=START,decision=DECISION,boss_states=s['boss_states'],counts=s['counts'],protected_prior_files=len(protected),full_declared_class_coverage=len(FULL),caller_scan_exact_reproduction=True,combat_producers=4,defensive_type_tests=1,twilight_reviewed_drafts=45,twilight_delivery_drafts=126,accepted_counts_unchanged=previous['accepted_counts_unchanged'],damage_profiles_reviewed=13,damage_profiles_remaining=27,runtime_tests=0,promoted_twilight_records=0,alpha_yeti_snow_queen_started=False,**boundary_flags())


if __name__=='__main__':
    result=validate_hydra_urghast();write_json(OUT/'twilightforest-hydra-urghast-integrity.json',result);print(json.dumps(result,indent=2))
