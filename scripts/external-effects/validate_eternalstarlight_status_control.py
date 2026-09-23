from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_eternalstarlight_foundation import ES
from collect_eternalstarlight_status_control import data_census
from assemble_eternalstarlight_status_control import CP,STEM,FACTS
from eternalstarlight_combat_common import preserve_section

def validate_status_control():
    e=read_json(OUT/'native-evidence/eternalstarlight-status-control.json');assert collect(read_json(OUT/'native-specifications/eternalstarlight-status-control.json'))==e
    r=read_json(OUT/'reference-evidence/eternalstarlight-status-control-244.json');assert reference_collect(read_json(OUT/'reference-specifications/eternalstarlight-status-control-244.json'))==r
    v=read_json(OUT/'vanilla-evidence/eternalstarlight-status-control.json');assert prepare(read_json(OUT/'vanilla-specifications/eternalstarlight-status-control.json'))==v
    routing=read_json(OUT/'reference-routing/eternalstarlight-status-control.json');assert sha256(routing['archive'])==routing['sha256']
    with zipfile.ZipFile(routing['archive']) as z:assert not(set(routing['absent_entries'])&set(z.namelist()))
    dc=read_json(OUT/'eternalstarlight-status-data-census.json');assert data_census()==dc
    assert [x['entry'] for x in dc['rows'] if x['disposition']=='STATUS_DELIVERY']==['data/eternal_starlight/enchantment/tearing.json']
    w={x['entry']:x for x in e['witnesses']+r['witnesses']}
    w.update({x['class_name']+'.class':x for x in v['classes']})
    def body(entry,method):return next(m['instructions'] for m in w[entry+'.class']['methods'] if m['name']==method)
    def hit(b,s):return [i for i in b if s in str(i.get('operand',''))]
    def pos(b,s):return hit(b,s)[0]['offset']
    def after(b,s):return b[b.index(hit(b,s)[0])+1]
    h=ES+'common/handler/ESCommonHandler'
    post=body(h,'onPostLivingHurt');star=[i for i in post if i['offset']>=pos(post,'ESDamageTypes.STARFIRE')]
    assert pos(post,'ESMobEffects.STARFIRE')<pos(post,'ESDamageTypes.STARFIRE')<pos(star,'getIndirectEntityDamageSource(')<pos(star,'.hurt(')
    assert hit(star,'getDirectEntity(') and hit(star,'getEntity(') and hit(star,'3.0') and any(i['opcode']=='0x6e' for i in star) and after(star,'.hurt(')['opcode']=='0x57'
    target=body(h,'onLivingChangeTarget');assert hit(target,'TEARY_TICKS') and hit(target,'mobMaxTearyTicks') and not hit(target,'TEARY_IMMUNE')
    tick=body(h,'onEntityTick');assert pos(tick,'TEARY_IMMUNE')<pos(tick,'TEARY_TICKS')<pos(tick,'MemoryModuleType.ATTACK_TARGET')
    counter=read_json(OUT/'eternalstarlight-status-attachment-census.json');assert {x['method'] for x in counter['rows'] if any('TEARY_TICKS' in str(i['operand']) for i in x['hits'])}=={'<clinit>','onLivingChangeTarget','onEntityTick'}
    assert hit(body(ES+'common/entity/living/monster/Stranghoul','canBeAffected'),'ESMobEffects.TEARY')
    boss=body(ES+'common/entity/living/boss/monstrosity/LunarMonstrosity','hurt');assert hit(boss,'ESMobEffects.STARFIRE') and not hit(boss,'ESDamageTypes.STARFIRE') and hit(boss,'3.0')
    spit=body(ES+'common/entity/projectile/PermafrostSpit','onHitEntity');assert hit(spit,'Attributes.ATTACK_SPEED') and not hit(spit,'Attributes.ATTACK_DAMAGE') and after(spit,'.hurt(')['opcode']=='0x57'
    assert pos(spit,'.hurt(')<pos(spit,'.canFreeze(')<pos(spit,'.addEffect(')
    cloud=body(ES+'common/entity/attack/PermafrostCloud','tick');assert len(hit(cloud,'.invulnerableTimeI'))==3 and pos(cloud,'.invulnerableTimeI')<pos(cloud,'.hurt(')<hit(cloud,'.invulnerableTimeI')[-1]['offset']<pos(cloud,'.setTicksFrozen(')
    assert not hit(cloud,'ESMobEffects.BRITTLE')
    whip=body(ES+'common/entity/attack/Whip','tick');assert pos(whip,'.shouldHarm(')<pos(whip,'.hurt(')<pos(whip,'.doPostHurtEffects(') and after(whip,'.hurt(')['opcode']=='0x99'
    assert hit(whip,'.playerAttack(') and hit(whip,'Attributes.ATTACK_DAMAGE')
    client=body(ES+'common/mixin/client/MinecraftMixin','getHitResultType');assert pos(client,'swing_attack')<pos(client,'WHIPS')<pos(client,'HitResult$Type.MISS')
    cold=body(ES+'common/item/combat/ColdsnapItem','doPostHurtEffects');assert pos(cold,'.canFreeze(')<pos(cold,'.setTicksFrozen(')<pos(cold,'.isCloudSpawned(')<pos(cold,'.setCooldown(')
    cap=w['data/eternal_starlight/enchantment/tearing.json']['data'];effect=cap['effects']['minecraft:post_attack'][0];assert effect['enchanted']=='attacker' and effect['affected']=='victim' and effect['requirements']['predicate']['type']=='eternal_starlight:pungency_fruit_spear'
    assert effect['effect']['min_duration']==2.5 and effect['effect']['max_duration']['per_level_above_first']==.5
    helper=body('net/minecraft/world/item/enchantment/EnchantmentHelper','doPostAttackEffectsWithItemSource');assert hit(helper,'.getEntity(') and hit(helper,'net/minecraft/world/entity/LivingEntity')
    for cl in ['TearBomb','TearBombMinecart']:
        b=body(ES+'common/entity/misc/'+cl,'explode');assert pos(b,'.explode(')<pos(b,'net/minecraft/world/entity/AreaEffectCloud') and not hit(b,'.setOwner(')
        assert len([i for i in b if i['operand']==120])==3
    ac=body('net/minecraft/world/entity/AreaEffectCloud','tick');assert hit(ac,'isAffectedByPotions') and hit(ac,'noneMatch') and hit(ac,'.customEffects(') and hit(ac,'.addEffect(')
    collision=body(ES+'common/mixin/BlockStateBaseMixin','getCollisionShape');assert pos(collision,'Operation.call(')<pos(collision,'UNAFFECTED_BY_OBLIVION')<pos(collision,'isAbove(')<pos(collision,'isDescending(')<pos(collision,'Shapes.empty(')
    inwall=body(ES+'common/mixin/EntityMixin','isInWall');assert hit(inwall,'net/minecraft/world/entity/player/Player')
    visibility=body('net/neoforged/neoforge/event/entity/living/LivingEvent$LivingVisibilityEvent','modifyVisibility');assert any(i['opcode']=='0x6b' for i in visibility)
    tags={x['id']:set(x['tags']) for x in read_json(OUT/'eternalstarlight-damage-tags.json')['declarations']}
    assert 'minecraft:is_freezing' not in tags['eternal_starlight:freeze'] and 'minecraft:is_fire' not in tags['eternal_starlight:starfire']
    a=read_json(OUT/'annotation-evidence/eternalstarlight-status-control-javap.json');assert sha256(a['tool'])==a['tool_sha256'] and sha256(OUT/a['output_file'])==a['output_sha256']
    annotations=(OUT/a['output_file']).read_text(encoding='utf-8');assert all(s in annotations for s in ['WrapMethod','getCollisionShape','isInWall()Z','startAttack()Z','SubscribeEvent','LivingVisibilityEvent'])
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and d['status_effects_reviewed_total']==9 and len(d['mechanic_packages'])==15 and len(d['delivery_paths'])==32 and len(d['status_field_reference_dispositions'])==38
    assert not next(x for x in d['mechanic_packages'] if x['id']=='es:starfire_status')['stage_scaling_needed']
    assert all(v in (OUT/(STEM+'-review.md')).read_text(encoding='utf-8') for v in FACTS.values())
    preserved=preserve_section(d)
    return dict(schema='tno.external_effects.es_status_control_integrity.v1',checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),loader_witnesses=len(r['witnesses']),raw_fallback_classes=len(v['classes']),reviewed_packages=15,reviewed_paths=32,nine_statuses_semantically_reviewed=True,status_field_references_dispositioned=38,semantic_order_source_admission_checks='PASS',accepted_counts_preserved=preserved,promoted_records=0,whole_eternalstarlight_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_status_control();write_json(OUT/'eternalstarlight-r2h2b-integrity.json',d);print(json.dumps(d,indent=2))
