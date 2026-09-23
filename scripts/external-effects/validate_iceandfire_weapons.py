from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_iceandfire_weapons import census
from assemble_iceandfire_weapons import CP,STEM,FACTS
from iceandfire_combat_common import preserve_section

def validate_weapons():
    e=read_json(OUT/'native-evidence/iceandfire-weapons.json');assert collect(read_json(OUT/'native-specifications/iceandfire-weapons.json'))==e
    spec=read_json(OUT/'reference-specifications/iceandfire-weapons-244.json');r=read_json(OUT/'reference-evidence/iceandfire-weapons-244.json');assert reference_collect(spec)==r
    with zipfile.ZipFile(spec['archives'][0]['path']) as z:assert all(n not in z.namelist() for n in spec['raw_fallback_absent_classes'])
    assert prepare(read_json(OUT/'vanilla-specifications/iceandfire-weapons.json'))==read_json(OUT/'vanilla-evidence/iceandfire-weapons.json')
    c=read_json(OUT/'iceandfire-weapons-census.json');assert census()==c
    def body(cls,name):return next(m['instructions'] for w in e['witnesses'] if w['entry'].endswith('/'+cls+'.class') for m in w['methods'] if m['name']==name)
    def hits(b,n):return [i for i in b if n in str(i.get('operand',''))]
    for cls in ['Sword','Axe','Pickaxe','Shovel','Hoe']:
        b=body('ActivePostHit'+cls+'Item','hurtEnemy');assert hits(b,'.isEnable(') and hits(b,'.active(')
    chain=body('LightningMultihitAbility','active');assert hits(chain,'.mobAttack(') and not hits(chain,'EntityType.LIGHTNING_BOLT') and not hits(chain,'Attributes.ATTACK_DAMAGE')
    bolt=body('SummonLightningAbility','active');assert hits(bolt,'EntityType.LIGHTNING_BOLT') and not hits(bolt,'.setCause(')
    tide=body('TideTridentEntity','onHitEntity');assert hits(tide,'.entitiesHitI')[0]['offset']<hits(tide,'.hurt(')[0]['offset']<hits(tide,'.isThundering(')[0]['offset']
    assert not hits(tide,'piercingIgnoreEntityIds') and not hits(tide,'.setDeltaMovement(')
    assert hits(body('DragonArrowItem','asProjectile'),'DragonArrowEntity.<init>')
    g=body('DeathwormGauntletItem','finishUsingItem');assert hits(g,'.hasLineOfSight(') and hits(g,'.hurt(')[0]['offset']<hits(g,'.knockback(')[0]['offset']
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['delivery_paths'])==19 and len(d['mechanic_packages'])==8
    assert all(v in (OUT/(STEM+'-review.md')).read_text(encoding='utf-8') for v in FACTS.values())
    preserved=preserve_section(d)
    return dict(checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),reference_witnesses=len(r['witnesses']),caller_methods=len(c['combat_callers']),packages=8,paths=19,fixtures=len(d['unexecuted_future_fixtures']),accepted_counts_preserved=preserved,source_identity_and_hurt_order_checks='PASS',runtime_tests=0,whole_iceandfire_complete=False,**boundary_flags())
if __name__=='__main__':
    d=validate_weapons();write_json(OUT/'iceandfire-r2g9a-integrity.json',d);print(json.dumps(d,indent=2))
