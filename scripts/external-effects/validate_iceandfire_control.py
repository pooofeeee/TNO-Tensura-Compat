from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_iceandfire_control import census
from assemble_iceandfire_control import CP,STEM,FACTS
from iceandfire_combat_common import preserve_section

def validate_control():
    e=read_json(OUT/'native-evidence/iceandfire-control.json');assert collect(read_json(OUT/'native-specifications/iceandfire-control.json'))==e
    r=read_json(OUT/'reference-evidence/iceandfire-control-244.json');assert reference_collect(read_json(OUT/'reference-specifications/iceandfire-control-244.json'))==r
    assert prepare(read_json(OUT/'vanilla-specifications/iceandfire-control.json'))==read_json(OUT/'vanilla-evidence/iceandfire-control.json')
    route=read_json(OUT/'reference-routing/iceandfire-control.json');assert sha256(route['archive'])==route['sha256']
    with zipfile.ZipFile(route['archive']) as z:assert all(n not in z.namelist() for n in route['absent_entries'])
    ann=read_json(OUT/'annotation-evidence/iceandfire-control-javap.json');assert sha256(ann['tool'])==ann['tool_sha256'] and sha256(OUT/ann['output_file'])==ann['output_sha256']
    assert subprocess.check_output([ann['tool'],*ann['arguments']],encoding='utf-8')==(OUT/ann['output_file']).read_text(encoding='utf-8')
    c=read_json(OUT/'iceandfire-control-census.json');assert census()==c
    def body(cls,name):return next(m['instructions'] for w in e['witnesses'] if w['entry'].endswith('/'+cls+'.class') for m in w['methods'] if m['name']==name)
    def hits(b,n):return [i for i in b if n in str(i.get('operand',''))]
    b=body('PixieChargeEntity','onHit');assert len(hits(b,'.addEffect('))==2 and hits(b,'.addEffect(')[-1]['offset']<hits(b,'.hurt(')[0]['offset'] and hits(b,'.indirectMagic(')
    assert not hits(body('ChainData','tick'),'.knockback(') and hits(body('ChainData','tick'),'.setDeltaMovement(')
    assert hits(body('DragonBaseEntity','onHearFlute'),'.isOwnedBy(') and not hits(body('AmphithereEntity','onHearFlute'),'.isOwnedBy(')
    armor=body('ServerEvents','onLivingHurt');assert hits(armor,'DamageTypes.LIGHTNING_BOLT') and len([i for i in hits(armor,'IafItems.DRAGONSTEEL_LIGHTNING_')])==4
    bridge=[m['instructions'] for w in r['witnesses'] if w['entry'].endswith('/EventHandlerImplCommon.class') for m in w['methods'] if 'LivingIncomingDamageEvent' in m['descriptor']];assert len(bridge)==1 and hits(bridge[0],'.setCanceled(')
    cfg=read_json(OUT/'iceandfire-frozen-config-snapshot.json')['data'];assert cfg['pixie']['stealItems'] is False and cfg['ghost']['fromPlayerDeaths'] is True
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['delivery_paths'])==26 and len(d['mechanic_packages'])==9
    assert all(v in (OUT/(STEM+'-review.md')).read_text(encoding='utf-8') for v in FACTS.values())
    preserved=preserve_section(d)
    return dict(checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),reference_witnesses=len(r['witnesses']),caller_methods=len(c['rows']),packages=9,paths=26,fixtures=len(d['unexecuted_future_fixtures']),accepted_counts_preserved=preserved,source_owner_and_control_admission_checks='PASS',runtime_tests=0,whole_iceandfire_complete=False,**boundary_flags())
if __name__=='__main__':
    d=validate_control();write_json(OUT/'iceandfire-r2g9b-integrity.json',d);print(json.dumps(d,indent=2))
