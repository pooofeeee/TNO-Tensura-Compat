from catalog_common import *
from native_evidence import collect
from collect_cataclysm_foundation import CP,STEM,PKG,census,registries,tags,compat_scan
from assemble_cataclysm_foundation import FACTS
from cataclysm_combat_common import preserve_section

def validate_foundation():
    e=read_json(OUT/'native-evidence/cataclysm-foundation.json');assert collect(read_json(OUT/'native-specifications/cataclysm-foundation.json'))==e and len(e['witnesses'])==81
    c=read_json(OUT/'cataclysm-source-census.json');assert census()==c and c['parsed_classes']==1310 and len(c['watched_methods'])==538 and len(c['custom_damage_key_methods'])==26 and len(c['custom_source_factory_methods'])==32 and len(c['effect_reference_methods'])==95 and len(c['boss_tag_reader_methods'])==6
    reg=read_json(OUT/'cataclysm-native-registries.json');assert registries()==reg and len(reg['damage_keys'])==20 and len(reg['mob_effects'])==12
    t=read_json(OUT/'cataclysm-damage-tags.json');assert tags()==t and len(t['declarations'])==15 and len(t['code_keys_without_bundled_json'])==5
    assert all(d['disposition']=='PENDING_CALLER_SEMANTICS' for d in t['declarations'])
    cmp=read_json(OUT/'cataclysm-direct-compat-census.json');assert compat_scan()==cmp and len(cmp['archives'])==6 and not any(r['hits'] for r in cmp['archives'])
    import tomllib
    cfg=read_json(OUT/'cataclysm-installed-common-config.json');raw=Path(cfg['path']).read_bytes();assert byte_hash(raw)==cfg['sha256'] and raw.decode('utf-8-sig')==cfg['text'] and tomllib.loads(cfg['text'])==cfg['values']
    w={x['entry']:x for x in e['witnesses']}
    def b(short,name):return next(m['instructions'] for m in w[PKG+short+'.class']['methods'] if m['name']==name)
    def hits(ins,s):return [x for x in ins if s in str(x.get('operand',''))]
    ins=b('util/CMDamageTypes','getIndirectEntityDamageSource');assert hits(ins,'EntityExcludedDamageSource.<init>') and hits(ins,'getHolderOrThrow') and hits(ins,'DamageSource.<init>(Lnet/minecraft/core/Holder;Lnet/minecraft/world/entity/Entity;Lnet/minecraft/world/entity/Entity;)V')
    ins=b('util/EntityExcludedDamageSource','<init>');assert hits(ins,'DamageSource.<init>(Lnet/minecraft/core/Holder;)V')
    assert {m['name'] for m in w[PKG+'util/EntityExcludedDamageSource.class']['methods']}=={'<init>','getLocalizedDeathMessage'}
    ins=b('Cataclysm','<init>');assert hits(ins,'ModEffect.EFFECTS') and hits(ins,'ModAttribute.ATTRIBUTES') and hits(ins,'COMMON_SPEC') and any(i.get('operand')=='%s-common.toml' for i in ins)
    a=read_json(OUT/'annotation-evidence/cataclysm-foundation-javap.json');assert sha256(a['tool'])==a['tool_sha256'] and sha256(OUT/a['output_file'])==a['output_sha256']
    s=(OUT/a['output_file']).read_text(encoding='utf-8');assert all(v in s for v in ['SubscribeEvent','LivingIncomingDamageEvent','LivingShieldBlockEvent','WrapOperation','HEAD','cancellable=true'])
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and not d['mechanic_packages'] and not d['whole_mod_complete']
    p=preserve_section(d);assert p==dict(effects=669,sources=1620,paths=1620,comparisons=669,primitives=882)
    return dict(schema='tno.external_effects.cataclysm_foundation_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',native_witnesses=81,classes=1310,watched_candidates=538,code_damage_keys=20,bundled_damage_types=15,registered_effects=12,explicit_name_compat_hits=0,accepted_counts_preserved=p,promoted_records=0,whole_mod_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_foundation();write_json(OUT/'cataclysm-r2k1-integrity.json',d);print(json.dumps(d,indent=2))
