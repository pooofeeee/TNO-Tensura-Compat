from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_iceandfire_ghost_troll import census
from assemble_iceandfire_ghost_troll import CP,STEM,FACTS
from iceandfire_combat_common import preserve_section
def validate_ghost_troll():
    e=read_json(OUT/'native-evidence/iceandfire-ghost-troll.json');assert collect(read_json(OUT/'native-specifications/iceandfire-ghost-troll.json'))==e
    r=read_json(OUT/'reference-evidence/iceandfire-ghost-troll-244.json');assert reference_collect(read_json(OUT/'reference-specifications/iceandfire-ghost-troll-244.json'))==r
    assert prepare(read_json(OUT/'vanilla-specifications/iceandfire-ghost-troll.json'))==read_json(OUT/'vanilla-evidence/iceandfire-ghost-troll.json')
    c=read_json(OUT/'iceandfire-ghost-troll-census.json');assert census()==c and not c['myrmex_named_entries'] and not c['myrmex_class_constants']
    a=read_json(OUT/'annotation-evidence/iceandfire-ghost-troll-javap.json');assert sha256(a['tool'])==a['tool_sha256'] and sha256(OUT/a['output_file'])==a['output_sha256']
    assert subprocess.check_output([a['tool'],*a['arguments']],encoding='utf-8')==(OUT/a['output_file']).read_text(encoding='utf-8')
    def body(doc,cls,name):return next(m['instructions'] for w in doc['witnesses'] if w['entry'].endswith(cls+'.class') for m in w['methods'] if m['name']==name)
    def hits(b,n):return [i for i in b if n in str(i.get('operand',''))]
    sword=body(e,'GhostSwordEntity','onHitEntity');assert hits(sword,'.magic(') and hits(sword,'.indirectMagic(') and not hits(sword,'.arrow(')
    assert not hits(sword,'doPostAttackEffects') and hits(sword,'.igniteForSeconds(')[0]['offset']<hits(sword,'.hurt(')[0]['offset']
    tick=body(e,'GhostSwordEntity','tick');assert not hits(tick,'.onProjectileImpact(') and hits(tick,'.onHit(')
    troll=body(e,'TrollEntity','aiStep');assert len(hits(troll,'.hurt('))==2 and hits(troll,'.remove(') and hits(troll,'.explode(')
    armor=body(r,'player/Player','actuallyHurt');maxes=hits(armor,'Math.max(FF)F');assert len(maxes)==1
    i=armor.index(maxes[0]);assert '.setAbsorptionAmount(' in str(armor[i+1]['operand'])
    assert hits(body(r,'PlayerEntityMixin','livingDamageEvent'),'LivingEntityEvents.DAMAGE')
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['delivery_paths'])==18 and len(d['mechanic_packages'])==8
    assert all(v in (OUT/(STEM+'-review.md')).read_text(encoding='utf-8') for v in FACTS.values())
    preserved=preserve_section(d)
    return dict(checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),reference_witnesses=len(r['witnesses']),caller_methods=len(c['rows']),packages=8,paths=18,fixtures=len(d['unexecuted_future_fixtures']),accepted_counts_preserved=preserved,source_and_actual_absorption_hook_checks='PASS',myrmex='ABSENT_IN_INSTALLED_JAR',runtime_tests=0,whole_iceandfire_complete=False,**boundary_flags())
if __name__=='__main__':
    d=validate_ghost_troll();write_json(OUT/'iceandfire-r2g8a-integrity.json',d);print(json.dumps(d,indent=2))
