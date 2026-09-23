"""Validate R2g1 source facts and preserve the completed five-mod catalog."""
from catalog_common import *
from native_evidence import collect
from classfile import ClassFile
from collect_iceandfire_foundation import START,CP,IAF,COMPAT,FULL,LIMITED,targets,caller_census,tag_census
from assemble_iceandfire_foundation import FACTS


def validate_foundation():
    ts=targets();spec=read_json(OUT/'native-specifications/iceandfire-foundation.json');native=read_json(OUT/'native-evidence/iceandfire-foundation.json')
    assert collect(spec)==native and len(native['witnesses'])==54
    census=read_json(OUT/'iceandfire-source-census.json');assert census==caller_census()
    assert census['parsed_classes']==726 and len(census['factory_callers'])==7 and len(census['status_references'])==6
    tags=read_json(OUT/'iceandfire-damage-tag-census.json');assert tags==tag_census()
    expected={'bonus':['minecraft:bypasses_cooldown'],'gorgon':['minecraft:bypasses_armor','minecraft:bypasses_shield'],**{k:['minecraft:always_hurts_ender_dragons'] for k in ['dragon_fire','dragon_ice','dragon_lightning']}}
    assert {d['id'].split(':')[1]:d['tags'] for d in tags['declarations']}==expected
    W={w['entry']:w for w in native['witnesses']}
    def ins(short,method):return next(m['instructions'] for m in W[IAF+short+'.class']['methods'] if m['name']==method)
    factory='registry/IafDamageTypes';keys={
        'bonusDamage':'BONUS','causeGorgonDamage':'GORGON_DMG_TYPE','causeDragonFireDamage':'DRAGON_FIRE_TYPE','causeIndirectDragonFireDamage':'DRAGON_FIRE_TYPE','causeDragonIceDamage':'DRAGON_ICE_TYPE','causeIndirectDragonIceDamage':'DRAGON_ICE_TYPE','causeDragonLightningDamage':'DRAGON_LIGHTNING_TYPE','causeIndirectDragonLightningDamage':'DRAGON_ICE_TYPE'}
    for method,key in keys.items():
        body=ins(factory,method);fields=[i for i in body if i['opcode']=='0xb2']
        assert len(fields)==1 and fields[0]['operand']==IAF+factory+'.'+key+'Lnet/minecraft/resources/ResourceKey;',method
        if 'Indirect' in method:assert body[2]['opcode']=='0x2b' and [i['opcode'] for i in body if i['offset'] in [11,12]]==['0x2a','0x2b']
    assert next(i for i in ins(factory,'causeIndirectDragonLightningDamage') if i['opcode']=='0xb2')['offset']==5
    get=ins(factory,'get');positions={needle:next(i['offset'] for i in get if needle in str(i.get('operand'))) for needle in ['Registry.getHolder(','FELL_OUT_OF_WORLD','Registry.getHolderOrThrow(','Optional.orElse(']}
    assert list(positions.values())==sorted(positions.values())
    for suffix in ['$CustomEntityDamageSource','$CustomIndirectEntityDamageSource']:
        w=W[IAF+factory+suffix+'.class'];assert w['superclass']=='net/minecraft/world/damagesource/DamageSource'
        assert {m['name'] for m in w['methods']}=={'<init>','getLocalizedDeathMessage'}
        assert any('net/minecraft/world/damagesource/DamageSource.<init>' in str(i['operand']) for i in ins(factory+suffix,'<init>'))
    status=ins('registry/IafStatusEffects','<clinit>')
    assert {i['operand'] for i in status if i['opcode'] in ['0x12','0x13']} >= {'frozen','siren_charm'}
    assert any('IafStatusEffects.REGISTRY' in str(i['operand']) for i in ins('IceAndFire','init'))
    assert any('IceAndFire.init(' in str(i['operand']) for i in ins('neoforge/IceAndFireNeoForge','<init>'))
    manager=ins('entity/util/dragon/IafDragonDestructionManager','getDamageSource')
    assert any('getRidingPlayer' in str(i['operand']) for i in manager)
    assert sum('causeIndirectDragon' in str(i['operand']) for i in manager)==3
    charge=ins('entity/DragonChargeEntity','onHit')
    assert any('.causeDamage(' in str(i['operand']) for i in charge) and any('getRidingPlayer' in str(i['operand']) for i in charge)
    assert any('.causeDragonLightningDamage(' in str(i['operand']) for i in ins('entity/LightningDragonChargeEntity','causeDamage'))
    with zipfile.ZipFile(ts['iceandfire']['path']) as jar:
        for short in FULL:
            actual=ClassFile(jar.read(IAF+short+'.class'))
            assert {(m['name'],m['descriptor']) for m in actual.methods}=={(m['name'],m['descriptor']) for m in W[IAF+short+'.class']['methods']},short
    compatconfig=W['tensura_iaf.mixins.json']['data'];assert compatconfig['required'] and len(compatconfig['mixins'])==11
    assert all(compatconfig['package'].replace('.','/')+'/'+n+'.class' in W for n in compatconfig['mixins'])
    helper=W['io/github/manasmods/tensura_iaf/mixin/MixinTensuraDamageHelper.class']
    for method,key in [('isAbnormal','GORGON_DMG_TYPE'),('isCold','DRAGON_ICE_TYPE'),('isFireDamage','DRAGON_FIRE_TYPE'),('isLightningDamage','DRAGON_LIGHTNING_TYPE')]:
        body=next(m['instructions'] for m in helper['methods'] if m['name']==method)
        assert any('.'+key+'L' in str(i['operand']) for i in body)
        assert any('CallbackInfoReturnable.setReturnValue' in str(i['operand']) for i in body)
    physical=next(m['instructions'] for m in helper['methods'] if m['name']=='isPhysicalAttack')
    assert sum(i['opcode']=='0xb2' and 'IafDamageTypes.' in str(i['operand']) for i in physical)==4
    annotation=read_json(OUT/'annotation-evidence/iceandfire-compat-javap.json')
    assert annotation['jar_sha256']==ts[COMPAT]['sha256'] and sha256(annotation['tool'])==annotation['tool_sha256']
    assert sha256(OUT/annotation['output_file'])==annotation['output_sha256']
    javap=(OUT/annotation['output_file']).read_text(encoding='utf-8')
    assert 'RuntimeVisibleAnnotations' in javap and 'isPhysicalAttack(Lnet/minecraft/world/damagesource/DamageSource;)Z' in javap
    assert 'cancellable=true' in javap and 'value="HEAD"' in javap and 'value="RETURN"' in javap
    foundation=read_json(OUT/'iceandfire-r2g1-source-foundation.json');assert foundation['facts']==FACTS
    for r in foundation['reference_files']:assert sha256(OUT/r['file'])==r['sha256']
    preserved={}
    for name,key in [('effect-catalog.json','effects'),('effect-sources.json','sources'),('delivery-path-matrix.json','paths'),('vanilla-comparison.json','comparisons'),('behavior-primitives.json','primitives')]:
        old=json.loads(git('show',START+':docs/benchmarks/external-effects-catalog/'+name))[key]
        assert read_json(OUT/name)[key]==old,name
        preserved[key]=len(old)
    assert preserved==dict(effects=335,sources=801,paths=801,comparisons=335,primitives=465)
    for mod in ['twilightforest','variantsandventures','cultofazazel','royalvariations','friendsandfoes']:
        path='docs/benchmarks/external-effects-catalog/mod-reviews/'+mod+'.json'
        assert read_json(ROOT/path)==json.loads(git('show',START+':'+path)),mod
    r=read_json(OUT/'mod-reviews/iceandfire.json');assert r['status']=='PARTIAL' and not r['effects'] and not r['paths']
    assert not r['semantic_discovery_complete'] and not r['special_damage_discovery_complete']
    ledger={x['mod_key']:x for x in read_json(OUT/'mod-completion-ledger.json')['targets']}
    assert ledger['twilightforest']['state']=='COMPLETE' and ledger['iceandfire']['state']=='PARTIAL'
    allowed={'docs/external-effects-catalog-research.md','scripts/external-effects/validate.py'}|{'docs/benchmarks/external-effects-catalog/'+n for n in ['effect-catalog.json','effect-sources.json','delivery-path-matrix.json','vanilla-comparison.json','behavior-primitives.json','research-decision.json','mod-completion-ledger.json']}
    for line in git('diff','--name-status',START).splitlines():
        status,path=line.split('\t',1)
        assert status=='A' or (status=='M' and path in allowed),line
    for line in git('diff','--name-status',BASELINE).splitlines():
        status,path=line.split('\t',1)
        assert status=='A' and path.startswith(('docs/external-effects-catalog-research.md','docs/benchmarks/external-effects-catalog/','scripts/external-effects/')),line
    assert all(not foundation[k] for k in boundary_flags())
    git('diff','--check',BASELINE)
    return dict(schema='tno.external_effects.iaf_foundation_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',native_witnesses=54,parsed_classes=726,registered_custom_statuses=2,damage_declarations=5,reviewed_factory_methods=8,factory_caller_methods=7,status_reference_methods=6,declared_compat_mixins=11,lightning_indirect_ice_holder_proven=True,fully_reviewed_damage_profiles=0,promoted_iceandfire_records=0,accepted_counts_preserved=preserved,runtime_tests=0,**boundary_flags())


if __name__=='__main__':
    r=validate_foundation();write_json(OUT/'iceandfire-r2g1-integrity.json',r);print(json.dumps(r,indent=2))
