"""Reproduce source/admission foundation and protect all accepted owner tables."""
from catalog_common import *
from native_evidence import collect
from collect_bossesrise_foundation import CP,STEM,PKG,census,tags,compat_scan
from assemble_bossesrise_foundation import FACTS
from bossesrise_combat_common import preserve_section

def validate_foundation():
    e=read_json(OUT/'native-evidence/bossesrise-foundation.json');assert collect(read_json(OUT/'native-specifications/bossesrise-foundation.json'))==e
    assert len(e['witnesses'])==34
    c=read_json(OUT/'bossesrise-source-census.json');assert census()==c
    assert c['parsed_classes']==802 and len(c['watched_methods'])==157 and len(c['custom_damage_key_methods'])==6 and len(c['native_effect_reference_methods'])==18
    assert not c['custom_effect_registry_candidates'] and not any('MobEffect' in x['superclass'] for x in c['classes'])
    t=read_json(OUT/'bossesrise-damage-tags.json');assert tags()==t and len(t['declarations'])==2
    expected={'cannonball_hit':{'minecraft:always_kills_armor_stands','minecraft:bypasses_armor','minecraft:bypasses_shield','minecraft:is_projectile','minecraft:panic_causes'},'kraken_tentacle_smash':{'minecraft:bypasses_armor','minecraft:bypasses_shield','minecraft:no_knockback'}}
    for row in t['declarations']:
        key=row['id'].split(':')[1];assert set(row['tags'])==expected[key]
        assert row['data']['exhaustion']==(0 if key=='cannonball_hit' else .1) and row['data']['scaling']=='when_caused_by_living_non_player'
    compat=read_json(OUT/'bossesrise-direct-compat-census.json');assert compat_scan()==compat and len(compat['archives'])==6 and all(not a['hits'] for a in compat['archives'])
    w={x['entry']:x for x in e['witnesses']}
    def body(short,method):return next(m['instructions'] for m in w[PKG+short+'.class']['methods'] if m['name']==method)
    def hits(b,s):return [x for x in b if s in str(x.get('operand',''))]
    for short,method,key in [('entity/projectile/CannonballEntity','onHitEntity','CANNONBALL_HIT'),('entity/boss/kraken/KrakenTentacleEntity','attackEntityWithSlam','KRAKEN_TENTACLE_SMASH')]:
        b=body(short,method);assert hits(b,key) and hits(b,'.source(') and hits(b,'.getOwner(') and hits(b,'.hurt(')
        assert hits(b,'.source(')[0]['offset']<hits(b,'.hurt(')[0]['offset']
    b=body('entity/projectile/CannonballEntity','onHitEntity');assert hits(b,'.hurt(')[0]['offset']<hits(b,'.doPostAttackEffects(')[0]['offset']<hits(b,'.explode(')[0]['offset']
    b=body('entity/boss/kraken/KrakenTentacleEntity','attackEntityWithSlam');assert hits(b,'.hurt(')[0]['offset']<hits(b,'.pushEntity(')[0]['offset'] and any(i['opcode']=='0x57' for i in b)
    b=body('attachment/entity/RollAttachment','preDamage');assert hits(b,'.isInvulnerable(') and hits(b,'.setCanceled(') and not hits(b,'DamageTypeTags')
    assert hits(body('attachment/entity/RollAttachment','preEffect'),'DO_NOT_APPLY')
    assert hits(body('mixins/RollMixin','freshNeverFrozen'),'.cancel(')
    for m in w[PKG+'procedures/BossCancelDie2Procedure.class']['methods']:
        assert not any(s in str(m['instructions']) for s in ['.setCanceled(','.setAmount(','.setHealth(','.hurt('])
    a=read_json(OUT/'annotation-evidence/bossesrise-foundation-javap.json');assert sha256(a['tool'])==a['tool_sha256'] and sha256(OUT/a['output_file'])==a['output_sha256']
    s=(OUT/a['output_file']).read_text(encoding='utf-8');assert all(v in s for v in ['SubscribeEvent','LivingIncomingDamageEvent','setTicksFrozen','isImmobile','HEAD','cancellable=true'])
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and not d['mechanic_packages'] and not d['whole_mod_complete']
    preserved=preserve_section(d);assert preserved==dict(effects=543,sources=1303,paths=1303,comparisons=543,primitives=717)
    return dict(schema='tno.external_effects.bossesrise_foundation_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',native_witnesses=34,classes=802,watched_candidates=157,custom_damage_types=2,custom_effect_registry_candidates=0,native_effect_reference_methods=18,explicit_name_compat_hits=0,accepted_counts_preserved=preserved,promoted_records=0,whole_mod_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_foundation();write_json(OUT/'bossesrise-r2i1-integrity.json',d);print(json.dumps(d,indent=2))
