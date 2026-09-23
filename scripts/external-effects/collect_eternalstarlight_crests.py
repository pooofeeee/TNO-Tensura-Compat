from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from collect_eternalstarlight_foundation import ES,targets
STUBS=['BurstSparkSpell','FlamingAftershockSpell','FlamingArcSpell','FlamingRingSpell','MergedFireballSpell','SurroundingFireballsSpell','FrozenFogSpell','IcySpikesSpell']
CLASSES={
 'common/util/ESCrestUtil':['tickCrests','getCrests','getOwnedCrests','getCrestLevel'],
 'common/util/ESSpellUtil':None,'common/registry/ESSpells':None,
 'common/crest/Crest':None,'common/crest/Crest$LevelBasedAttributeModifier':None,'common/crest/Crest$Instance':None,
 'common/item/magic/OrbOfProphecyItem':['use','onUseTick'],
 'common/item/magic/SimpleSpellItem':None,
 'common/mixin/ItemEntityMixin':['playerTouch'],
 'common/network/UpdateCrestsPacket':['handle'],
 'common/handler/ESCommonHandler':['onEntityTick','onPostLivingHurt'],
 'common/item/misc/ManaCrystalItem':None,
 'common/entity/misc/CrestEntity':['hurt'],
}
for n in STUBS+['AbstractSpell','AbstractSpell$Properties','LaserBeamSpell','GuidanceOfStarsSpell','SpellCastData','SpellCastData$ItemSpellSource','ManaType','SpellCooldown']:CLASSES['common/spell/'+n]=None

def census():
    t=targets()['eternalstarlight'];rows=[]
    needles=['ESSpellUtil.tickSpells','ESCrestUtil.tickCrests','ESDataAttachments.SPELL_SOURCE','ESItems.MANA_CRYSTAL_SHARD','/SimpleSpellItem','/AbstractSpell.start(','/AbstractSpell.canCast(']
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(x for x in z.namelist() if x.endswith('.class')):
            raw=z.read(n);c=ClassFile(raw)
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if any(s in str(i['operand']) for s in needles)]
                if hits:rows.append(dict(entry=n,sha256=byte_hash(raw),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits))
    return dict(jar_sha256=t['sha256'],scope='Whole JAR spell start, SimpleSpellItem construction and mana shard/tick routes. No runtime activation inferred from a class name.',rows=rows)

def save():
    t=targets()['eternalstarlight'];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in CLASSES.items():
            n=ES+short+'.class';c=ClassFile(z.read(n));names=wanted if wanted is not None else sorted({m['name'] for m in c.methods});names=sorted(set(names)|{m['name'] for m in c.methods if any(m['name'].startswith('lambda$'+v+'$') for v in names)})
            rows.append(dict(id='es:crest:'+short,mod_key='eternalstarlight',entry=n,methods=names))
        data=sorted(n for n in z.namelist() if n.endswith('.json') and ('/eternal_starlight/crest/' in n or '/tags/item/' in n and n.endswith('_crystals.json')))
        for n in data:rows.append(dict(id='es:crest:data:'+n,mod_key='eternalstarlight',entry=n))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='All installed spell callbacks and crest definitions; no duplicate laser damage review.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/eternalstarlight-crests.json',s);write_json(OUT/'native-evidence/eternalstarlight-crests.json',collect(s));write_json(OUT/'eternalstarlight-crests-census.json',census())
    print('Crest/spell witnesses saved')
if __name__=='__main__':save()
