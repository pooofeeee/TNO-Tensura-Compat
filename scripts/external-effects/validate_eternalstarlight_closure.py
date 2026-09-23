from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_eternalstarlight_closure import ES,census
from assemble_eternalstarlight_closure import CP,STEM,FACTS
from eternalstarlight_combat_common import preserve_section

def validate_closure():
    e=read_json(OUT/'native-evidence/eternalstarlight-closure.json');assert collect(read_json(OUT/'native-specifications/eternalstarlight-closure.json'))==e
    r=read_json(OUT/'reference-evidence/eternalstarlight-closure-244.json');assert reference_collect(read_json(OUT/'reference-specifications/eternalstarlight-closure-244.json'))==r
    v=read_json(OUT/'vanilla-evidence/eternalstarlight-closure.json');assert prepare(read_json(OUT/'vanilla-specifications/eternalstarlight-closure.json'))==v
    route=read_json(OUT/'reference-routing/eternalstarlight-closure.json');assert sha256(route['archive'])==route['sha256']
    with zipfile.ZipFile(route['archive']) as z:assert not(set(route['absent_entries'])&set(z.namelist()))
    c=census();assert c==read_json(OUT/'eternalstarlight-combat-closure-census.json') and c['class_count']==1384 and len(c['watched_methods'])==274
    pinned=set()
    for f in (OUT/'native-evidence').glob('eternalstarlight-*.json'):
        for w in read_json(f)['witnesses']:
            for m in w.get('methods',[]):pinned.add((w['entry'],m['name'],m['descriptor']))
    assert all((x['entry'],x['method'],x['descriptor']) in pinned for x in c['watched_methods'])
    w={x['entry']:x for x in e['witnesses']+r['witnesses']}
    def body(cl,method):return next(m['instructions'] for m in w[cl+'.class']['methods'] if m['name']==method and m.get('instructions'))
    def es(cl,method):return body(ES+cl,method)
    def hit(b,s):return [i for i in b if str(s) in str(i.get('operand',''))]
    def pos(b,s):return hit(b,s)[0]['offset']
    b=es('common/block/entity/AbstractDuskLightBlockEntity','tick');assert pos(b,'.clip(')<pos(b,'.getEntitiesOfClass(')<pos(b,'ItemEntity')<pos(b,'.setRemainingFireTicks(') and not hit(b,'.hurt(')
    b=es('common/block/entity/AlloyFurnaceBlockEntity','tick');assert pos(b,'.destroyBlock(')<pos(b,'.explode(') and hit(b,'ExplosionInteraction.BLOCK') and hit(b,'.explosionRadius(')
    b=es('common/mixin/AbstractArrowMixin','scaleKnockback');assert hit(b,'UNREALIUM_CROSSBOW') and hit(b,0.5)
    b=es('common/mixin/LivingEntityMixin','knockback');assert hit(b,'UNREALIUM_CROSSBOW') and hit(b,0.5)
    b=es('common/mixin/EntityMixin','getGravity');assert hit(b,'bottomInWater') and hit(b,'AIR_SAC_BOOTS') and not hit(b,'.hurt(')
    b=es('common/mixin/ProjectileWeaponItemMixin','getHeldProjectile');assert pos(b,'.isEmpty(')<pos(b,'GALACTIC_QUIVER')<pos(b,'Predicate.test(')<pos(b,'QUIVER_ARROW')
    b=es('common/mixin/ThrowableProjectileMixin','tick');assert hit(b,'WiltedPetal') and hit(b,'EnergySpark')
    b=body('net/minecraft/world/level/block/CampfireBlock','entityInside');assert pos(b,'.LIT')<pos(b,'.campfire(')<pos(b,'.hurt(')
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==8 and len(d['delivery_paths'])==15
    assert all(v in (OUT/(STEM+'-review.md')).read_text(encoding='utf-8') for v in FACTS.values())
    return dict(schema='tno.external_effects.es_closure_integrity.v1',checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),loader_witnesses=len(r['witnesses']),raw_fallback_classes=len(v['classes']),watched_combat_methods=274,all_watched_methods_pinned=True,reviewed_packages=8,reviewed_paths=15,semantic_order_source_admission_checks='PASS',accepted_counts_preserved=preserve_section(d),promoted_records=0,whole_eternalstarlight_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_closure();write_json(OUT/'eternalstarlight-r2h8a-integrity.json',d);print(json.dumps(d,indent=2))
