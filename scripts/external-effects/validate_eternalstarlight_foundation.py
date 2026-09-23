"""Reproduce R2h1 witnesses, source/tag scans, registration and bridge ordering."""
from catalog_common import *
from native_evidence import collect
from collect_eternalstarlight_foundation import START,CP,ES,FACTORY,EFFECTS,EVENTS,census,tags,compat_scan
from assemble_eternalstarlight_foundation import STEM,FACTS

def validate_foundation():
    spec=read_json(OUT/'native-specifications/eternalstarlight-foundation.json');e=read_json(OUT/'native-evidence/eternalstarlight-foundation.json')
    assert collect(spec)==e and len(e['witnesses'])==45
    c=read_json(OUT/'eternalstarlight-source-census.json');assert census()==c
    assert c['parsed_classes']==1384 and len(c['factory_callers'])==29 and len(c['damage_key_references'])==31 and len(c['status_references'])==38
    t=read_json(OUT/'eternalstarlight-damage-tags.json');assert tags()==t and len(t['declarations'])==18
    compat=read_json(OUT/'eternalstarlight-direct-compat-census.json');assert compat_scan()==compat and len(compat['archives'])==6 and all(not a['hits'] for a in compat['archives'])
    w={r['entry']:r for r in e['witnesses']}
    def body(entry,method):return next(m['instructions'] for m in w[entry+'.class']['methods'] if m['name']==method)
    def hits(b,s):return [i for i in b if s in str(i.get('operand',''))]
    direct=body(FACTORY,'getEntityDamageSource');assert [x['opcode'] for x in direct[:4]]==['0x2a','0x2b','0x2c','0x2c']
    ownerless=body(FACTORY,'getDamageSource');assert ownerless[2]['opcode']=='0x1'
    indirect=body(FACTORY,'getIndirectEntityDamageSource');assert indirect[0]['operand']=='net/minecraft/world/damagesource/DamageSource'
    assert hits(indirect,'registryOrThrow(')[0]['offset']<hits(indirect,'getHolderOrThrow(')[0]['offset']<hits(indirect,'DamageSource.<init>(')[0]['offset']
    assert [i['opcode'] for i in indirect if i['offset'] in [22,23]]==['0x2c','0x2d']
    assert not any(s in str(indirect) for s in ['.hurt(','.setHealth(','.orElse('])
    constants={i['operand'] for i in body(FACTORY,'<clinit>') if i['opcode'] in ['0x12','0x13']}
    assert constants=={d['id'].split(':')[1] for d in t['declarations']}
    forbidden={'minecraft:is_fire','minecraft:is_freezing','minecraft:is_lightning','minecraft:bypasses_invulnerability','minecraft:bypasses_cooldown'}
    assert all(not (set(d['tags'])&forbidden) for d in t['declarations'])
    assert {d['id'].split(':')[1] for d in t['declarations'] if 'minecraft:is_projectile' in d['tags']}=={'seeds','shattered_blade','wilt'}
    assert {d['id'].split(':')[1] for d in t['declarations'] if 'eternal_starlight:bypasses_crescent_pendant' in d['tags']}=={'numbness'}
    assert {d['id'].split(':')[1] for d in t['declarations'] if d['data'].get('effects')=='burning'}=={'laser','energized_flame'}
    assert all(d['data']['exhaustion']==.1 and d['data']['scaling']=='when_caused_by_living_non_player' for d in t['declarations'])
    registry=body(EFFECTS,'<clinit>');names=[i['operand'] for i in registry if i['opcode'] in ['0x12','0x13']]
    assert names==['eternal_starlight','crystal_infection','dream_catcher','sticky','flammable','brittle','numbness','teary','starfire','oblivion']
    for i,category in enumerate(['HARMFUL','BENEFICIAL','BENEFICIAL','HARMFUL','HARMFUL','BENEFICIAL','HARMFUL','HARMFUL','BENEFICIAL']):
        assert hits(body(EFFECTS,'lambda$static$'+str(i)),'.'+category+'Lnet/minecraft/world/effect/MobEffectCategory;')
    assert hits(body(ES+'common/EternalStarlight','init'),'ESMobEffects.loadClass(')
    entry=body(ES+'neoforge/ESNeoEntrypoint','<init>');assert hits(entry,'EternalStarlight.init(')[0]['offset']<hits(entry,'DeferredRegister.register(')[0]['offset']
    service=w['META-INF/services/cn.leolezury.eternalstarlight.common.platform.ESPlatform']['text'];assert service.strip()=='cn.leolezury.eternalstarlight.neoforge.platform.ESNeoPlatform'
    events=ES+'neoforge/event/CommonEvents';incoming=body(events,'onIncomingDamage')
    order=[hits(incoming,n)[0]['offset'] for n in ['onAllowLivingHurt(','setCanceled(','onModifyLivingHurtDamage(','setAmount(','onModifyPostAttackInvulnerabilityTicks(','setPostAttackInvulnerabilityTicks(']];assert order==sorted(order)
    # The amount/iframe tail contains no cancellation recheck or early return.
    tail=[i for i in incoming if i['offset']>=32];assert not hits(tail,'isCanceled(') and [i['offset'] for i in tail if i['opcode']=='0xb1']==[80]
    death=body(events,'onLivingDeath');assert len(hits(death,'isCanceled('))==2 and hits(death,'isCanceled(')[1]['offset']<hits(death,'ESCommonHandler.onLivingDeath(')[0]['offset']
    assert hits(body(events,'onPreLivingHurt'),'setNewDamage(') and hits(body(events,'onLivingHeal'),'setAmount(')
    annotation=read_json(OUT/'annotation-evidence/eternalstarlight-foundation-javap.json');assert sha256(annotation['tool'])==annotation['tool_sha256'] and sha256(OUT/annotation['output_file'])==annotation['output_sha256']
    text=(OUT/annotation['output_file']).read_text(encoding='utf-8');assert 'EventBusSubscriber' in text and 'SubscribeEvent' in text and 'BootstrapMethods:' in text and 'LivingIncomingDamageEvent' in text
    source=next(r for r in read_json(OUT/'reference-evidence/twilight-equipment-244.json')['witnesses'] if r['entry'].endswith('/DamageSource.class'))
    getters={m['name']:m['instructions'] for m in source['methods'] if m['name'] in {'getDirectEntity','getEntity'}}
    assert hits(getters['getDirectEntity'],'.directEntityL') and hits(getters['getEntity'],'.causingEntityL')
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and d['promoted_mechanics']==0 and not d['whole_mod_complete']
    for ref in d['reference_files']:assert sha256(OUT/ref['file'])==ref['sha256']
    for v in FACTS.values():assert v in (OUT/(STEM+'-review.md')).read_text(encoding='utf-8')
    preserved={}
    views=[('effect-catalog.json','effects'),('effect-sources.json','sources'),('delivery-path-matrix.json','paths'),('vanilla-comparison.json','comparisons'),('behavior-primitives.json','primitives')]
    for name,key in views:
        old=json.loads(git('show',START+':docs/benchmarks/external-effects-catalog/'+name))[key]
        current=read_json(OUT/name)[key];assert [r for r in current if r['mod_key'] in {x['mod_key'] for x in old}]==old;preserved[key]=len(old)
    assert preserved==dict(effects=416,sources=1029,paths=1029,comparisons=416,primitives=553)
    mutable={'docs/external-effects-catalog-research.md','scripts/external-effects/validate.py'}|{'docs/benchmarks/external-effects-catalog/'+n for n in [n for n,_ in views]+['mod-completion-ledger.json','research-decision.json']}
    for line in git('diff','--name-status',START).splitlines():
        status,path=line.split('\t',1);assert status=='A' or (status=='M' and path in mutable),line
    for line in git('diff','--name-status',BASELINE).splitlines():
        status,path=line.split('\t',1);assert status=='A' and path.startswith(('docs/external-effects-catalog-research.md','docs/benchmarks/external-effects-catalog/','scripts/external-effects/')),line
    assert all(not d[k] for k in boundary_flags()) and d['runtime_tests']==0
    git('diff','--check',BASELINE)
    return dict(schema='tno.external_effects.es_foundation_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',native_witnesses=45,classes=1384,custom_damage_types=18,mob_effects=9,factory_caller_methods=29,damage_key_methods=31,status_reference_methods=38,scoped_direct_compat_archives=6,scoped_explicit_name_hits=0,bridge_ordering='PASS',accepted_counts_preserved=preserved,promoted_records=0,whole_eternalstarlight_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_foundation();write_json(OUT/'eternalstarlight-r2h1-integrity.json',d);print(json.dumps(d,indent=2))
