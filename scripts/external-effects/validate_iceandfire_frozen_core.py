"""Reproduce bounded Frozen evidence and protect all prior accepted records."""
from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as collect_reference
from collect_iceandfire_frozen import census,FULL,IAF
from collect_iceandfire_foundation import targets
from assemble_iceandfire_frozen_core import START,CP,FACTS

def validate_frozen_core():
    spec=read_json(OUT/'native-specifications/iceandfire-frozen.json');evidence=read_json(OUT/'native-evidence/iceandfire-frozen.json')
    assert collect(spec)==evidence and len(evidence['witnesses'])==17
    assert census()==read_json(OUT/'iceandfire-frozen-callers.json')
    w={r['entry']:r for r in evidence['witnesses']}
    def body(short,method):return next(m['instructions'] for m in w[IAF+short+'.class']['methods'] if m['name']==method)
    def offsets(ins,needle):return [i['offset'] for i in ins if needle in str(i.get('operand'))]
    core=body('effect/FrozenStatusEffect','applyEffectTick')
    order=[offsets(core,n)[0] for n in ['IceDragonEntity','isDeadOrDying(','isOnFire(','clearFire(','isCreative(','Vec3.multiply(','onGround(','Vec3.add(']]
    assert order==sorted(order)
    assert any(i['operand']==0.25 for i in core) and any(i['operand']==-0.2 for i in core)
    assert not any(n in str(core) for n in ['.hurt(','.setHealth(','.setTicksFrozen(','.setNoAi('])
    payload=body('item/ability/FrozenTargetAbility','active')
    order=[offsets(payload,n)[0] for n in ['MOVEMENT_SLOWDOWN','DIG_SLOWDOWN','IafStatusEffects.FROZEN']];assert order==sorted(order)
    assert len(offsets(payload,'.addEffect('))==3
    assert all(payload[j+1]['opcode']=='0x57' for j,i in enumerate(payload) if '.addEffect(' in str(i['operand']))
    for tool in ['Sword','Axe','Pickaxe','Shovel','Hoe']:
        b=body('item/tool/ActivePostHit'+tool+'Item','hurtEnemy')
        assert offsets(b,'.isEnable(')[0]<offsets(b,'.active(')[0]<offsets(b,'.hurtEnemy(')[0]
    bonus=body('item/ability/DamageBonusAbility','active')
    assert offsets(bonus,'getAttackStrengthScale')[0]<offsets(bonus,'EntityType.is(')[0]<offsets(bonus,'bonusDamage(')[0]<offsets(bonus,'.hurt(')[0]
    assert all(bonus[j+1]['opcode']=='0x57' for j,i in enumerate(bonus) if '.hurt(' in str(i['operand']))
    assert w['data/iceandfire/tags/entity_type/fire_dragon.json']['data']['values']==['iceandfire:fire_dragon']
    with zipfile.ZipFile(targets()['iceandfire']['path']) as z:
        for short in FULL:
            actual=ClassFile(z.read(IAF+short+'.class'))
            assert {(m['name'],m['descriptor']) for m in actual.methods}=={(m['name'],m['descriptor']) for m in w[IAF+short+'.class']['methods']}
    refs=[]
    for name in ['iceandfire-frozen-tensura','iceandfire-frozen-244']:
        s=read_json(OUT/'reference-specifications'/f'{name}.json')
        for a in s['archives']:
            if 'nested_entry' in a:
                assert sha256(a['parent_path'])==a['parent_sha256']
                with zipfile.ZipFile(a['parent_path']) as z:assert byte_hash(z.read(a['nested_entry']))==a['sha256']
        r=read_json(OUT/'reference-evidence'/f'{name}.json');assert collect_reference(s)==r;refs+=r['witnesses']
    # Preserve the actual resistance override rather than substituting the generic gate.
    r=next(r for r in refs if r.get('entry','').endswith('/resist/ResistSkill.class'))
    can=next(m for m in r['methods'] if m['name']=='canInteractSkill')['instructions']
    assert offsets(can,'isInSleepMode(') and offsets(can,'isAffectedByStatus(') and offsets(can,'canActivateInArea(')
    assert not offsets(can,'getMastery(') and not offsets(can,'isSpectator(')
    bridge=next(r for r in refs if r.get('entry','').endswith('/skill/mixin/MixinLivingEntity.class'))
    assert any('CallbackInfoReturnable.setReturnValue' in str(i['operand']) for m in bridge['methods'] for i in m['instructions'])
    inherited=next(r for r in refs if r.get('entry','').endswith('/TensuraSkillInstance.class'))
    assert not inherited['methods']
    # Player item callback precedes cooldown reset in the installed patched class.
    prior=read_json(OUT/'reference-evidence/twilight-frosted-244.json')
    p=next(r for r in prior['witnesses'] if r['entry'].endswith('/player/Player.class'))
    b=next(m for m in p['methods'] if m['name']=='attack')['instructions']
    assert offsets(b,'ItemStack.hurtEnemy(')[0]<offsets(b,'resetAttackStrengthTicker(')[0]
    annotation=read_json(OUT/'annotation-evidence/iceandfire-frozen-javap.json')
    assert sha256(annotation['tool'])==annotation['tool_sha256']
    for a in annotation['entries']:assert sha256(OUT/a['output_file'])==a['output_sha256'] and sha256(a['archive']['path'])==a['archive']['sha256']
    text=(OUT/annotation['entries'][0]['output_file']).read_text(encoding='utf-8')
    assert 'addEffect(Lnet/minecraft/world/effect/MobEffectInstance;Lnet/minecraft/world/entity/Entity;)Z' in text and 'cancellable=true' in text and 'value="HEAD"' in text
    config=read_json(OUT/'iceandfire-frozen-config-snapshot.json');assert sha256(config['path'])==config['sha256'] and read_json(config['path'])==config['data']
    assert config['data']['tools']['dragonIceAbility'] and config['data']['tools']['dragonBloodFrozenDuration']==100 and config['data']['tools']['dragonsteelFrozenDuration']==300
    d=read_json(OUT/'iceandfire-r2g2a-frozen-core.json');assert d['facts']==FACTS
    assert d['status']=='CORE_WEAPONS_COMPLETE_DRAGON_DELIVERY_PENDING' and len(d['reviewed_weapon_paths'])==6 and len(d['future_runtime_fixtures'])==18
    for ref in d['reference_files']:assert sha256(OUT/ref['file'])==ref['sha256']
    preserved={}
    for name,key in [('effect-catalog.json','effects'),('effect-sources.json','sources'),('delivery-path-matrix.json','paths'),('vanilla-comparison.json','comparisons'),('behavior-primitives.json','primitives')]:
        old=json.loads(git('show',START+':docs/benchmarks/external-effects-catalog/'+name))[key]
        assert read_json(OUT/name)[key]==old;preserved[key]=len(old)
    mutable={'docs/external-effects-catalog-research.md','scripts/external-effects/validate.py'}|{'docs/benchmarks/external-effects-catalog/'+n for n in ['effect-catalog.json','effect-sources.json','delivery-path-matrix.json','vanilla-comparison.json','behavior-primitives.json','mod-completion-ledger.json','research-decision.json','mod-reviews/iceandfire.json']}
    for line in git('diff','--name-status',START).splitlines():
        status,path=line.split('\t',1);assert status=='A' or (status=='M' and path in mutable),line
    for line in git('diff','--name-status',BASELINE).splitlines():
        status,path=line.split('\t',1);assert status=='A' and path.startswith(('docs/external-effects-catalog-research.md','docs/benchmarks/external-effects-catalog/','scripts/external-effects/')),line
    assert all(not d[k] for k in boundary_flags()) and not d['runtime_tests']
    git('diff','--check',BASELINE)
    return dict(schema='tno.external_effects.iaf_frozen_core_integrity.v1',checkpoint=CP,status='PASS',native_witnesses=17,new_reference_witnesses=len(refs),caller_methods=18,reviewed_weapon_paths=6,future_unexecuted_fixtures=18,accepted_counts_preserved=preserved,protected_evidence_unchanged=True,dragon_delivery_complete=False,promoted_iceandfire_records=0,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_frozen_core();write_json(OUT/'iceandfire-r2g2a-integrity.json',d);print(json.dumps(d,indent=2))
