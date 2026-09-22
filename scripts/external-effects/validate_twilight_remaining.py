"""Later Twilight subset integrity; preserves R2f7 and every published subset input."""
from collections import Counter
from catalog_common import *
from classfile import ClassFile
from validate_twilight_yeti_queen import validate_yeti_queen

START='cb929fb7833eb27ddc3c16126f281cc62247421a'


def validate_remaining():
    previous=validate_yeti_queen();prefix='docs/benchmarks/external-effects-catalog/'
    mutable={prefix+x for x in ['behavior-primitives.json','delivery-path-matrix.json','effect-catalog.json','effect-sources.json','mod-completion-ledger.json','mod-reviews/twilightforest.json','research-decision.json','vanilla-comparison.json','twilightforest-owner-table.md']}
    mutable.add('scripts/external-effects/validate.py')
    protected=[p for p in git('ls-tree','-r','--name-only',START,'--',prefix,'scripts/external-effects/').splitlines() if p not in mutable]
    for p in protected:
        old=subprocess.check_output(['git','show',START+':'+p],cwd=ROOT)
        assert (ROOT/p).read_bytes().replace(b'\r\n',b'\n')==old.replace(b'\r\n',b'\n'),p
    witnesses={}
    for p in (OUT/'native-evidence').glob('*.json'):
        for w in read_json(p).get('witnesses',[]):
            if w.get('mod_key')=='twilightforest' and w['entry'].endswith('.class'):witnesses.setdefault(w['entry'],[]).extend(w['methods'])
    def methods(c):return witnesses['twilightforest/'+c+'.class']
    def ins(c,m):return next(x['instructions'] for x in methods(c) if x['name']==m)
    def pos(i,t):return next(x['offset'] for x in i if t in str(x['operand']))
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest')
    assert sha256(target['path'])==target['sha256']
    results=[]
    for sp in sorted((OUT/'semantic-sections').glob('twilightforest-*.json')):
        s=read_json(sp)
        if not s.get('remaining_content_subsection'):continue
        r=s['review_input'];assert sha256(OUT/r['evidence_file'])==r['sha256'];d=read_json(OUT/r['evidence_file'])
        assert s['counts']==d['expected_counts'] and s['semantic_closure']==d['facts']
        assert s['subsection_decision']==d['decision'] and all(s['closure_checklist'].values())
        assert set(s['closure_checklist'])==set(d['closure_checklist'])
        assert Counter(e['primary_classification'] for e in s['effects'])==s['counts']['classification_totals']
        assert len(s['effects'])==s['counts']['mechanic_packages'] and len(s['paths'])==s['counts']['delivery_cases']
        for e,row in zip(s['effects'],d['packages']):
            assert e['id']==row['id'] and e['actual_behavior']==[d['facts'][k] for k in row['facts']]
            assert e['alternate_sources'] and e['primary_test_source'] and e['components']
            assert e['components'][0]['numerical_parameters']==row['parameters'] and e['components'][0]['binary_parameters']==row['gates']
        for p,row in zip(s['paths'],d['paths']):
            assert p['id']==row['id'] and p['native_delivery']==' '.join(d['facts'][k] for k in row['facts'])
            assert p['setup'] and p['future_controls'] and set(p['labels'])<=set(DELIVERIES)
        old=read_json(OUT/d['previous_draft']);new=read_json(OUT/('partial-drafts/twilightforest-'+d['checkpoint_short']+'-partial.json'))
        assert new['effects']==old['effects']+s['effects'] and new['paths']==old['paths']+s['paths']
        assert len({e['id'] for e in new['effects']})==len(new['effects']) and len({p['id'] for p in new['paths']})==len(new['paths'])
        with zipfile.ZipFile(target['path']) as jar:
            for c in d['full_classes']:
                actual={(m['name'],m['descriptor']) for m in ClassFile(jar.read('twilightforest/'+c+'.class')).methods}
                assert actual=={(m['name'],m['descriptor']) for m in methods(c)},c
        if d['slug']=='ranged-mobs':
            from collect_twilight_ranged_mobs import scan_callers,FIELDS
            scan=read_json(OUT/'twilightforest-ranged-mobs-caller-scan.json');assert scan==scan_callers(target)
            runtime=[x for x in scan['hits'] if '/data/' not in x['entry'] and '/init/' not in x['entry']]
            assert Counter(x['entry'] for x in runtime)==Counter({'twilightforest/entity/monster/FireBeetle.class':2,'twilightforest/entity/projectile/NatureBolt.class':1,'twilightforest/entity/projectile/TomeBolt.class':2,'twilightforest/entity/projectile/IceSnowball.class':1})
            profiles={p['type']:p for p in s['damage_profiles']};assert set(profiles)=={'twilightforest:'+f.lower() for f in FIELDS}
            assert all(p['status']=='USED' for p in profiles.values())
            for name in ['leaf_brain','lost_words','schooled']:
                assert {'minecraft:bypasses_armor','minecraft:bypasses_shield','minecraft:is_projectile','neoforge:is_magic'}<=set(profiles['twilightforest:'+name]['tags'])
            assert 'minecraft:bypasses_armor' not in profiles['twilightforest:snowball_fight']['tags']
            assert 'minecraft:is_freezing' not in profiles['twilightforest:snowball_fight']['tags']
            M='entity/monster/';P='entity/projectile/';G='entity/ai/goal/BreathAttackGoal'
            use=ins(G,'canUse');assert any('.getLastHurtByMob(' in str(x['operand']) for x in use) and not any('.getTarget(' in str(x['operand']) for x in use)
            select=ins(G,'getHeadLookTarget');assert not any('ClipContext' in str(x['operand']) for x in select)
            winter=ins(M+'WinterWolf','doBreathAttack');assert any('.mobAttack(' in str(x['operand']) for x in winter) and not any('TFDamageTypes' in str(x['operand']) for x in winter)
            fire=ins(M+'FireBeetle','doBreathAttack');assert pos(fire,'.fireImmune(')<pos(fire,'.hurt(')<pos(fire,'.igniteForSeconds(')
            assert not any('.igniteForSeconds(' in str(x['operand']) for x in ins(M+'FireBeetle','doHurtTarget'))
            for c in ['NatureBolt','TomeBolt']:
                hit=ins(P+c,'onHitEntity');assert pos(hit,'.hurt(')<pos(hit,'.addEffect(')
            for c in ['SlimeProjectile','IceSnowball']:
                hit=ins(P+c,'onHitEntity');i=next(n for n,x in enumerate(hit) if '.hurt(' in str(x['operand']));assert int(hit[i+1]['opcode'],16)==0x57
                hurt=ins(P+c,'hurt');assert pos(hurt,'TFThrowable.hurt(')<pos(hurt,'.die(')
                assert not any('.addEffect(' in str(x['operand']) for x in hit)
            for c in ['NatureBolt','TomeBolt','SlimeProjectile','IceSnowball']:assert not {'addAdditionalSaveData','readAdditionalSaveData'} & {m['name'] for m in methods(P+c)}
            death=ins(M+'UnstableIceCore','tickDeath');assert pos(death,'.explode(')<pos(death,'.transformBlocks(')<pos(death,'BaseIceMob.tickDeath(')
            assert not any('.setHealth(' in str(x['operand']) for x in death)
            mist=ins(M+'MistWolf','doHurtTarget');assert pos(mist,'HostileWolf.doHurtTarget(')<pos(mist,'.getMaxLocalRawBrightness(')<pos(mist,'.addEffect(')
            assert d['damage_census']['reviewed_profiles_after']==22 and d['damage_census']['remaining_profiles']==18
        if d['slug']=='mounted-mobs':
            from collect_twilight_mounted_mobs import scan_callers
            scan=read_json(OUT/'twilightforest-mounted-mobs-caller-scan.json');assert scan==scan_callers(target)
            runtime=[x for x in scan['hits'] if '/data/' not in x['entry'] and '/init/' not in x['entry']]
            assert Counter((x['entry'].split('/')[-1],x['method']) for x in runtime)==Counter({('Yeti.class','hurt'):1,('Yeti.class','readAdditionalSaveData'):1,('PinchBeetle.class','doHurtTarget'):1,('HeavySpearAttackGoal.class','tick'):1})
            p=s['damage_profiles'][0];assert p['type']=='twilightforest:clamped' and p['status']=='USED'
            assert set(p['tags'])=={'minecraft:no_knockback','neoforge:is_physical'}
            M='entity/monster/';G='entity/ai/goal/'
            upper=ins(M+'UpperGoblinKnight','hurt');assert pos(upper,'.getEntity(')<pos(upper,'.takeHitOnShield(')<pos(upper,'Monster.hurt(')
            assert not any('.getDirectEntity(' in str(x['operand']) for x in upper)
            for c in ['UpperGoblinKnight','LowerGoblinKnight']:
                h=ins(M+c,'hurt');assert pos(h,'.breakArmor(')<pos(h,'Monster.hurt(')
            shield=ins(M+'UpperGoblinKnight','takeHitOnShield');assert pos(shield,'AxeItem')<pos(shield,'.damageShield(')<pos(shield,'.knockback(')
            cl=ins(M+'UpperGoblinKnight','<clinit>');assert any('ADD_MULTIPLIED_BASE' in str(x['operand']) for x in cl)
            assert any(x['operand']==12.0 for x in cl)
            heavy=ins(G+'HeavySpearAttackGoal','tick');assert any(x['operand']==25 for x in heavy)
            assert 'requiresUpdateEveryTick' not in {m['name'] for m in methods(G+'HeavySpearAttackGoal')}
            area=ins(M+'UpperGoblinKnight','landHeavySpearAttack');assert any('Monster.doHurtTarget(' in str(x['operand']) for x in area)
            pinch=ins(M+'PinchBeetle','doHurtTarget');assert pos(pinch,'.startRiding(')<pos(pinch,'TFDamageTypes.CLAMPED')<pos(pinch,'.properlyApplyCustomDamageSource(')
            boat=ins(M+'PinchBeetle','startRiding');assert any('Boat.kill(' in str(x['operand']) for x in boat) and not any('.hurt(' in str(x['operand']) for x in boat)
            yh=ins(M+'Yeti','hurt');assert pos(yh,'.setAngry(')<pos(yh,'Monster.hurt(')
            assert s['effects'][-1]['reuses_protected_effect_ids']==['twilightforest:alpha_yeti_throw','twilightforest:alpha_yeti_thrown_fall']
            assert d['damage_census']['reviewed_profiles_after']==23 and d['damage_census']['remaining_profiles']==17
        result=dict(schema='tno.external_effects.remaining_subsection_integrity.v1',status='PASS',checkpoint=d['checkpoint'],decision=d['decision'],starting_sha=d['starting_sha'],counts=s['counts'],protected_prior_files=len(protected),full_declared_class_coverage=len(d['full_classes']),twilight_reviewed_drafts=len(new['effects']),twilight_delivery_drafts=len(new['paths']),damage_profiles_reviewed=d['damage_census']['reviewed_profiles_after'],damage_profiles_remaining=d['damage_census']['remaining_profiles'],accepted_counts_unchanged=previous['accepted_counts_unchanged'],runtime_tests=0,promoted_twilight_records=0,**boundary_flags())
        results.append((d['slug'],result))
    assert results
    return results


if __name__=='__main__':
    for slug,result in validate_remaining():
        path=OUT/('twilightforest-'+slug+'-integrity.json')
        if path.exists():assert read_json(path)==result,'Protected integrity changed: '+slug
        else:write_json(path,result)
        print(json.dumps(result,indent=2))
