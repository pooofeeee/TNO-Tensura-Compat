"""Validate native Frozen dragon closure without modifying protected core evidence."""
from catalog_common import *
from iceandfire_promotion_migration import protected_rows, permitted_tool_change
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as collect_reference
from vanilla_reference import prepare
from collect_iceandfire_foundation import IAF,targets
from assemble_iceandfire_frozen_dragons import START,CP,FACTS

def validate_frozen_dragons():
    n='iceandfire-frozen-dragons';s=read_json(OUT/'native-specifications'/f'{n}.json');e=read_json(OUT/'native-evidence'/f'{n}.json');assert collect(s)==e
    refs=read_json(OUT/'reference-evidence'/f'{n}-244.json');assert collect_reference(read_json(OUT/'reference-specifications'/f'{n}-244.json'))==refs
    raw=read_json(OUT/'vanilla-evidence'/f'{n}.json');assert prepare(read_json(OUT/'vanilla-specifications'/f'{n}.json'))==raw
    route=read_json(OUT/'reference-routing'/f'{n}.json');assert sha256(route['archive'])==route['sha256']
    with zipfile.ZipFile(route['archive']) as z:assert all(entry not in z.namelist() for entry in route['absent_entries'])
    assert {r['class_name']+'.class' for r in raw['classes']}==set(route['absent_entries'])
    w={r['entry']:r for r in e['witnesses']}
    def body(short,method):return next(m['instructions'] for m in w[IAF+short+'.class']['methods'] if m['name']==method)
    def hits(b,needle):return [i for i in b if needle in str(i.get('operand'))]
    charge=body('entity/DragonChargeEntity','onHit');tick=body('entity/DragonChargeEntity','tick')
    # Capture the native self-owner check, rather than mistakenly assigning target.
    own=hits(charge,'.isOwnedBy(');assert len(own)==1
    index=charge.index(own[0]);assert '.getOwner(' in str(charge[index-1]['operand']) and 'DragonBaseEntity' in str(charge[index-1]['operand'])
    assert own[0]['offset']<hits(charge,'.causeDamage(')[0]['offset']<hits(charge,'.destroyArea(')[0]['offset']
    for j,i in enumerate(charge):
        if '.hurt(' in str(i['operand']):assert charge[j+1]['opcode']=='0x57'
    assert hits(tick,'.baseTick(') and hits(tick,'.onHit(')
    assert not hits(tick,'onProjectileImpact(') and not hits(tick,'hitTargetOrDeflectSelf(') and not hits(tick,'AbstractHurtingProjectile.tick(')
    assert hits(charge,'DragonUtils.canGrief(')[0]['offset']>hits(charge,'.hurt(')[0]['offset']
    native=next(r for r in refs['witnesses'] if r['entry'].endswith('/TamableAnimal.class'))
    ownbody=next(m['instructions'] for m in native['methods'] if m['name']=='isOwnedBy')
    assert [i['opcode'] for i in ownbody][:4]==['0x2b','0x2a','0xb6','0xa6']
    assert '.getOwner(' in str(ownbody[2]['operand'])
    with zipfile.ZipFile(targets()['iceandfire']['path']) as z:
        for cls in ['DragonBaseEntity','IceDragonEntity']:
            c=ClassFile(z.read(IAF+'entity/'+cls+'.class'));assert not ({'getOwner','isOwnedBy'} & {m['name'] for m in c.methods})
    manager=next(r for r in read_json(OUT/'native-evidence/iceandfire-frozen.json')['witnesses'] if r['entry'].endswith('/IafDragonDestructionManager.class'))
    payloads=[m for m in manager['methods'] if m['name'].startswith('lambda$destroyArea') and any('.applyDragonEffect(' in str(i['operand']) for i in m['instructions'])]
    assert len(payloads)==2
    for m in payloads:
        b=m['instructions'];h=hits(b,'.hurt(');assert len(h)==1 and h[0]['offset']<hits(b,'.applyDragonEffect(')[0]['offset']
        assert b[b.index(h[0])+1]['opcode']=='0x57'
    for m,needle in [('performNormalBreathAttack','destroyAreaBreath('),('performChargeAttack','.createCharge('),('updateRider','.riderShootFire('),('updateBurnTarget','.breathFireAtPos(')]:assert hits(body('entity/DragonBaseEntity',m),needle)
    assert hits(body('entity/IceDragonEntity','riderShootFire'),'IceDragonChargeEntity.<init>')
    assert hits(body('entity/IceDragonEntity','shootIceAtMob'),'IceDragonChargeEntity.<init>')
    assert hits(body('entity/util/dragon/IafDragonFlightManager','update'),'.breathAttack(')
    d=read_json(OUT/'iceandfire-r2g2b-frozen-dragons.json');assert d['facts']==FACTS and d['frozen_semantic_complete'] and d['frozen_delivery_complete']
    assert len(d['dragon_entry_routes'])==7 and len(d['payload_contracts'])==3 and all(not x['executed'] for x in d['dragon_entry_routes'])
    for p in d['reference_files']:assert sha256(OUT/p['file'])==p['sha256']
    preserved={}
    for name,key in [('effect-catalog.json','effects'),('effect-sources.json','sources'),('delivery-path-matrix.json','paths'),('vanilla-comparison.json','comparisons'),('behavior-primitives.json','primitives')]:
        old=json.loads(git('show',START+':docs/benchmarks/external-effects-catalog/'+name))[key];preserved[key]=len(protected_rows(read_json(OUT/name)[key],old))
    mutable={'docs/external-effects-catalog-research.md','scripts/external-effects/validate.py'}|{'docs/benchmarks/external-effects-catalog/'+x for x in ['effect-catalog.json','effect-sources.json','delivery-path-matrix.json','vanilla-comparison.json','behavior-primitives.json','mod-completion-ledger.json','research-decision.json','mod-reviews/iceandfire.json']}
    for line in git('diff','--name-status',START).splitlines():
        status,path=line.split('\t',1);assert status=='A' or (status=='M' and (path in mutable or permitted_tool_change(path))),line
    for line in git('diff','--name-status',BASELINE).splitlines():
        status,path=line.split('\t',1);assert status=='A' and path.startswith(('docs/external-effects-catalog-research.md','docs/benchmarks/external-effects-catalog/','scripts/external-effects/')),line
    assert not any(d[k] for k in boundary_flags())
    git('diff','--check',BASELINE)
    return dict(schema='tno.external_effects.iaf_frozen_dragon_integrity.v1',checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),exact_loader_witnesses=len(refs['witnesses']),raw_fallback_classes=len(raw['classes']),frozen_native_family_complete=True,weapon_paths_reused=6,dragon_entry_routes=7,payload_contracts=3,native_tamable_self_owner_guard_proven=True,independent_area_hurt_status_proven=True,accepted_counts_preserved=preserved,whole_iceandfire_complete=False,promoted_iceandfire_records=0,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    r=validate_frozen_dragons();write_json(OUT/'iceandfire-r2g2b-integrity.json',r);print(json.dumps(r,indent=2))
