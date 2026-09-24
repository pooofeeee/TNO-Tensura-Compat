"""Reproduce BOMD foundation and preserve accepted catalog rows."""
from catalog_common import *
from native_evidence import collect
from collect_bomd_foundation import CP,STEM,PKG,census,tags,compat_scan,installed_config
from assemble_bomd_foundation import FACTS
from bomd_combat_common import preserve_section

def validate_foundation():
    e=read_json(OUT/'native-evidence/bomd-foundation.json');assert collect(read_json(OUT/'native-specifications/bomd-foundation.json'))==e
    assert len(e['witnesses'])==25
    c=read_json(OUT/'bomd-source-census.json');assert census()==c
    assert c['parsed_classes']==287 and len(c['watched_methods'])==37 and len(c['custom_damage_key_methods'])==1 and len(c['native_effect_reference_methods'])==8
    assert len(c['custom_effect_registry_candidates'])==4 and not any('MobEffect' in x['superclass'] for x in c['classes'])
    assert {x['method'] for x in c['custom_effect_registry_candidates']}=={'performVolley','lambda$getMissileThrower$2','lambda$getMissileThrower$1'}
    t=read_json(OUT/'bomd-damage-tags.json');assert tags()==t and len(t['declarations'])==1
    row=t['declarations'][0];assert row['id']=='bosses_of_mass_destruction:shield_piercing' and row['tags']==[] and row['data']==dict(exhaustion=.1,message_id='mob',scaling='when_caused_by_living_non_player')
    compat=read_json(OUT/'bomd-direct-compat-census.json');assert compat_scan()==compat and len(compat['archives'])==6 and all(not a['hits'] for a in compat['archives'])
    cfg=read_json(OUT/'bomd-installed-config.json');assert installed_config()==cfg
    assert [cfg['values'][k]['health'] for k in ['lichConfig','obsidilithConfig','gauntletConfig','voidBlossomConfig']]==[300,300,250,350]
    w={x['entry']:x for x in e['witnesses']}
    def body(short,method):return next(m['instructions'] for m in w[PKG+short+'.class']['methods'] if m['name']==method)
    def hits(b,s):return [x for x in b if s in str(x.get('operand',''))]
    b=body('util/VanillaCopiesServer','create');assert hits(b,'.getHolderOrThrow(') and hits(b,'DamageSource.<init>(Lnet/minecraft/core/Holder;Lnet/minecraft/world/entity/Entity;)V')
    b=body('util/BMDUtils','shieldPiercing');assert hits(b,'SHIELD_PIERCING') and hits(b,'VanillaCopiesServer.create(')
    calls=[(x['entry'],x['method']) for x in c['watched_methods'] if hits(x['hits'],'.shieldPiercing(')]
    assert set(calls)=={(PKG+s+'.class',m) for s,m in [('entity/custom/obsidilith/BurstAction','damageEntity'),('entity/custom/obsidilith/SpikeAction','damageEntity'),('entity/custom/obsidilith/WaveAction','damageEntity'),('entity/custom/void_blossom/Spikes','damageEntity'),('projectile/SporeBallProjectile','lambda$doExplosion$2')]}
    b=body('projectile/SporeBallProjectile','lambda$doExplosion$2');assert hits(b,'.hurt(')[0]['offset']<hits(b,'.addEffect(')[0]['offset'] and hits(b,'POISON') and any(i['opcode']=='0x57' for i in b)
    b=body('projectile/SporeBallProjectile','entityHit');assert hits(b,'.thrown(') and hits(b,'.getOwner(') and hits(b,'.hurt(')
    b=body('mixin/LivingEntityMixin','bmd_makeShieldPiercingUnshieldable');assert hits(b,'SHIELD_PIERCING') and hits(b,'.setReturnValue(')
    assert not hits(b,'DamageTypeTags')
    b=body('entity/util/BaseEntity','hurt');assert hits(b,'.beforeDamage(')[0]['offset']<hits(b,'.shouldDamage(')[0]['offset']<hits(b,'.hurt(')[0]['offset']<hits(b,'.afterDamage(')[0]['offset']
    b=body('entity/util/EffectsImmunity','canBeAffected');assert hits(b,'getEffect()Lnet/minecraft/core/Holder;') and hits(b,'List.contains(')
    mix=w['bosses_of_mass_destruction-common.mixins.json']['data'];assert mix['required'] and {'LivingEntityMixin','ExplosionMixin'}<=set(mix['mixins'])
    ref=read_json(OUT/'reference-evidence/twilight-equipment-244.json');ds=next(x for x in ref['witnesses'] if x['entry'].endswith('/DamageSource.class'))
    ctor=next(m for m in ds['methods'] if m['name']=='<init>' and m['descriptor']=='(Lnet/minecraft/core/Holder;Lnet/minecraft/world/entity/Entity;)V')
    assert any('DamageSource.<init>(Lnet/minecraft/core/Holder;Lnet/minecraft/world/entity/Entity;Lnet/minecraft/world/entity/Entity;)V' in str(i.get('operand','')) for i in ctor['instructions'])
    a=read_json(OUT/'annotation-evidence/bomd-foundation-javap.json');assert sha256(a['tool'])==a['tool_sha256'] and sha256(OUT/a['output_file'])==a['output_sha256']
    s=(OUT/a['output_file']).read_text(encoding='utf-8');assert all(v in s for v in ['SubscribeEvent','LivingDeathEvent','isDamageSourceBlocked','HEAD','cancellable=true','ModifyVariable'])
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and not d['mechanic_packages'] and not d['whole_mod_complete']
    preserved=preserve_section(d);assert preserved==dict(effects=625,sources=1535,paths=1535,comparisons=625,primitives=827)
    return dict(schema='tno.external_effects.bomd_foundation_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',native_witnesses=25,classes=287,watched_candidates=37,custom_damage_types=1,custom_factory_callers=5,registry_lookup_candidates=4,native_effect_reference_methods=8,explicit_name_compat_hits=0,accepted_counts_preserved=preserved,promoted_records=0,whole_mod_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_foundation();write_json(OUT/'bomd-r2j1-integrity.json',d);print(json.dumps(d,indent=2))
