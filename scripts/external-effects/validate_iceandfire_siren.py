"""Validate song-map semantics and keep completed native checkpoints immutable."""
from catalog_common import *
from iceandfire_promotion_migration import protected_rows, permitted_tool_change
from classfile import ClassFile
from native_evidence import collect
from collect_iceandfire_siren import census,FULL
from collect_iceandfire_foundation import IAF,targets
from assemble_iceandfire_siren import START,CP,FACTS

def validate_siren():
    s=read_json(OUT/'native-specifications/iceandfire-siren.json');e=read_json(OUT/'native-evidence/iceandfire-siren.json');assert collect(s)==e
    c=read_json(OUT/'iceandfire-siren-callers.json');assert census()==c and c['parsed_classes']==726 and not c['siren_data_classes']
    w={r['entry']:r for r in e['witnesses']};siren=w[IAF+'entity/SirenEntity.class']
    def body(name):return next(m['instructions'] for m in siren['methods'] if m['name']==name)
    b=body('tickCharm');players=[i for i in b if i['opcode']=='0xc1' and i['operand']=='net/minecraft/world/entity/player/Player'];assert [i['offset'] for i in players]==[100,356]
    assert next(i for i in b if i['offset']==93)['operand'].startswith(IAF+'entity/SirenEntity.charmingEntities')
    assert next(i for i in b if i['offset']==353)['operand'].startswith(IAF+'entity/SirenEntity.charmingEntities')
    assert any(i['opcode']=='0xbb' and i['operand']=='it/unimi/dsi/fastutil/objects/Object2IntOpenHashMap' for i in body('<init>'))
    assert not any(x in str(b) for x in ['.hasEffect(','.getEffect(','.hurt(','.setHealth('])
    effect=body('lambda$tickMovement$8');call=next(j for j,i in enumerate(effect) if '.addEffect(' in str(i['operand']));assert effect[call+1]['opcode']=='0x57'
    assert '(Lnet/minecraft/world/effect/MobEffectInstance;Lnet/minecraft/world/entity/Entity;)Z' in effect[call]['operand']
    assert any(i['operand']==30 for i in effect)
    assert any('.tickCharm(' in str(i['operand']) for i in body('aiStep')) and not any(m['name']=='tickMovement' for m in siren['methods'])
    stop=body('stopCharm');assert any('removeInt(' in str(i['operand']) for i in stop) and not any('.removeEffect(' in str(i['operand']) for i in stop)
    for m in ['addAdditionalSaveData','readAdditionalSaveData']:assert not any(i.get('operand')=='singCooldown' for i in body(m))
    marker=w[IAF+'effect/SirenCharmStatusEffect.class'];assert {m['name'] for m in marker['methods']}=={'<init>'} and 'MobEffectCategory.HARMFUL' in str(marker)
    assert w['data/iceandfire/tags/entity_type/siren_charmable.json']['data']['values']==['minecraft:villager','minecraft:wandering_trader']
    with zipfile.ZipFile(targets()['iceandfire']['path']) as z:
        for cls in FULL:
            raw=ClassFile(z.read(IAF+cls+'.class'));assert {(m['name'],m['descriptor']) for m in raw.methods}=={(m['name'],m['descriptor']) for m in w[IAF+cls+'.class']['methods']}
    d=read_json(OUT/'iceandfire-r2g3a-siren-song.json');assert d['facts']==FACTS and len(d['delivery_paths'])==2 and len(d['future_fixtures'])==13 and all(not f['executed'] for f in d['future_fixtures'])
    for f in d['reference_files']:assert sha256(OUT/f['file'])==f['sha256']
    config=read_json(OUT/'iceandfire-frozen-config-snapshot.json');assert sha256(config['path'])==config['sha256'];assert config['data']['siren']==dict(maxHealth=50.0,maxSingTime=12000,timeBetweenSongs=2000)
    preserved={}
    for name,key in [('effect-catalog.json','effects'),('effect-sources.json','sources'),('delivery-path-matrix.json','paths'),('vanilla-comparison.json','comparisons'),('behavior-primitives.json','primitives')]:
        old=json.loads(git('show',START+':docs/benchmarks/external-effects-catalog/'+name))[key];preserved[key]=len(protected_rows(read_json(OUT/name)[key],old))
    mutable={'docs/external-effects-catalog-research.md','scripts/external-effects/validate.py'}|{'docs/benchmarks/external-effects-catalog/'+n for n in ['effect-catalog.json','effect-sources.json','delivery-path-matrix.json','vanilla-comparison.json','behavior-primitives.json','mod-completion-ledger.json','research-decision.json','mod-reviews/iceandfire.json']}
    for line in git('diff','--name-status',START).splitlines():
        status,path=line.split('\t',1);assert status=='A' or (status=='M' and (path in mutable or permitted_tool_change(path))),line
    for line in git('diff','--name-status',BASELINE).splitlines():
        status,path=line.split('\t',1);assert status=='A' and path.startswith(('docs/external-effects-catalog-research.md','docs/benchmarks/external-effects-catalog/','scripts/external-effects/')),line
    assert all(not d[k] for k in boundary_flags());git('diff','--check',BASELINE)
    return dict(schema='tno.external_effects.iaf_siren_integrity.v1',checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),parsed_classes=726,caller_methods=len(c['rows']),song_delivery_paths=2,unexecuted_fixtures=13,map_player_guard_proven=True,marker_return_ignored_proven=True,accepted_counts_preserved=preserved,promoted_iceandfire_records=0,whole_iceandfire_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    r=validate_siren();write_json(OUT/'iceandfire-r2g3a-integrity.json',r);print(json.dumps(r,indent=2))
