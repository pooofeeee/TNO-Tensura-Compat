from catalog_common import *
from native_evidence import collect
from collect_eternalstarlight_crests import ES,STUBS,census
from assemble_eternalstarlight_crests import CP,STEM,FACTS
from eternalstarlight_combat_common import preserve_section

def validate_crests():
    e=read_json(OUT/'native-evidence/eternalstarlight-crests.json');assert collect(read_json(OUT/'native-specifications/eternalstarlight-crests.json'))==e
    c=census();assert c==read_json(OUT/'eternalstarlight-crests-census.json')
    assert not any(i['opcode']=='0xbb' and str(i['operand']).endswith('/SimpleSpellItem') for r in c['rows'] for i in r['hits'])
    assert all(r['entry']==ES+'common/item/magic/SimpleSpellItem.class' for r in c['rows'] if any('/SimpleSpellItem' in str(i['operand']) for i in r['hits']))
    w={x['entry']:x for x in e['witnesses']}
    def body(cl,method):return next(m['instructions'] for m in w[ES+cl+'.class']['methods'] if m['name']==method and m.get('instructions'))
    def hit(b,s):return [i for i in b if str(s) in str(i.get('operand',''))]
    def pos(b,s):return hit(b,s)[0]['offset']
    for n in STUBS:
        for method in ['onPreparationTick','onSpellTick','onStart','onStop']:
            assert [i['opcode'] for i in body('common/spell/'+n,method)]==['0xb1']
    b=body('common/spell/AbstractSpell','canContinueToCast');assert not hit(b,'.hasNeededCrystal(')
    b=body('common/spell/AbstractSpell','damageCrystal');assert pos(b,'.getInventory(')<pos(b,'.hurtAndBreak(')
    b=body('common/util/ESSpellUtil','tickSpells');assert pos(b,'.canContinueToCast(')<pos(b,'.stop(')<pos(b,'.tick(')
    b=body('common/mixin/ItemEntityMixin','playerTouch');assert pos(b,'MANA_CRYSTAL_SHARD')<pos(b,'.cancel(')<pos(b,'.discard(')<pos(b,'MANA_CRYSTALS')<pos(b,'.isDamaged(')<pos(b,'.setDamageValue(')
    b=body('common/network/UpdateCrestsPacket','handle');assert pos(b,'.getOwnedCrests(')<pos(b,'.setCrests(') and not hit(b,'.maxLevel(')
    b=body('common/util/ESCrestUtil','tickCrests');assert pos(b,'OLD_ACTIVE_CRESTS')<pos(b,'.removeAll(')
    # Repeated field access: cleanup follows first read and final state write follows cleanup.
    assert len(hit(b,'OLD_ACTIVE_CRESTS'))==2 and pos(b,'.removeAll(')<hit(b,'OLD_ACTIVE_CRESTS')[1]['offset']
    crest=[x for x in e['witnesses'] if '/eternal_starlight/crest/' in x['entry']];assert len(crest)==11
    passive=[x['data'] for x in crest if 'mob_effects' in x['data']];assert len(passive)==1 and passive[0]['max_level']==2 and passive[0]['mob_effects']==[dict(effect='minecraft:resistance',level=0,level_addition=1)]
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==3 and len(d['delivery_paths'])==5
    assert all(v in (OUT/(STEM+'-review.md')).read_text(encoding='utf-8') for v in FACTS.values())
    return dict(schema='tno.external_effects.es_crests_integrity.v1',checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),empty_spell_callbacks_proven=32,installed_crests=11,reviewed_packages=3,reviewed_paths=5,semantic_order_source_admission_checks='PASS',accepted_counts_preserved=preserve_section(d),promoted_records=0,whole_eternalstarlight_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_crests();write_json(OUT/'eternalstarlight-r2h6-integrity.json',d);print(json.dumps(d,indent=2))
