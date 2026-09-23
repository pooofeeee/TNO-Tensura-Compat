"""Pin Gorgon combat contracts without reopening completed Ice & Fire families."""
from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_iceandfire_foundation import IAF, targets

METHODS = {
 'entity/GorgonEntity':['<init>','bakeAttributes','setConfigurableAttributes','registerGoals','doHurtTarget','setTarget','aiStep','forcePreyToLook','isStoneMob','isBlindfolded','isTargetBlocked','readAdditionalSaveData'],
 'entity/ai/GorgonAIStareAttackGoal':['*'],
 'entity/util/IafEntityUtil':['isEntityLookingAt'],
 'entity/StoneStatueEntity':['*'],
 'item/GorgonHeadItem':['<init>','getUseDuration','use','releaseUsing','onUseTick'],
 'item/StoneStatueItem':['useOn'],
 'event/ServerEvents':['onPlayerAttack'],
 'entity/util/dragon/DragonUtils':['isAlive','getBlockInTargetsViewGorgon'],
}

def census():
    rows=[]; blacklists=[]; tags=[]; classes=0
    t=targets()['iceandfire']
    with zipfile.ZipFile(t['path']) as z:
        for entry in sorted(z.namelist()):
            if entry.endswith('.class'):
                c=ClassFile(z.read(entry));classes+=1
                for m in c.methods:
                    instructions=list(c.instructions(m.get('code',b'')))
                    hits=[i for i in instructions if any(x in str(i.get('operand','')) for x in ['GorgonEntity.isTargetBlocked(', 'getBlockInTargetsViewGorgon(', 'GorgonEntity.isBlindfolded(', 'IafDamageTypes.causeGorgonDamage(', 'StoneStatueEntity.buildStatueEntity(', 'StoneStatueEntity.setCrackAmount(', 'IMMUNE_TO_GORGON_STONE'])]
                    if hits:rows.append(dict(entry=entry,method=m['name'],descriptor=m['descriptor'],hits=hits))
                    if m['name']=='canBeTurnedToStone':blacklists.append(dict(entry=entry,method=m['name'],instructions=instructions))
            elif entry.startswith('data/') and '/tags/entity_type/' in entry and entry.endswith(('/blinded.json','/immune_to_gorgon_stone.json')):
                b=z.read(entry);tags.append(dict(entry=entry,sha256=byte_hash(b),data=json.loads(b)))
    return dict(schema='tno.external_effects.iaf_gorgon_census.v1',jar_sha256=t['sha256'],parsed_classes=classes,rows=rows,blacklist_implementations=blacklists,tag_resources=tags,scope='Installed Iaf declarations and direct callers; runtime merged tags and external overrides remain future tests.')

def save():
    specs=[]
    with zipfile.ZipFile(targets()['iceandfire']['path']) as z:
        for short,wanted in METHODS.items():
            c=ClassFile(z.read(IAF+short+'.class'))
            methods=sorted({m['name'] for m in c.methods}) if wanted==['*'] else wanted+[m['name'] for m in c.methods if m['name'].startswith('lambda$')]
            specs.append(dict(id='iaf:gorgon:'+short,mod_key='iceandfire',entry=IAF+short+'.class',methods=sorted(set(methods))))
        for row in census()['blacklist_implementations']:
            if row['entry']!=IAF+'entity/StoneStatueEntity.class':specs.append(dict(id='iaf:gorgon:predicate:'+row['entry'],mod_key='iceandfire',entry=row['entry'],methods=['canBeTurnedToStone']))
        for row in census()['tag_resources']:specs.append(dict(id='iaf:gorgon:tag:'+row['entry'],mod_key='iceandfire',entry=row['entry']))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Gorgon gaze/head, fallback attack and statue combat persistence/admission. Shared methods do not certify unrelated families.',evidence_specifications=specs)
    write_json(OUT/'native-specifications/iceandfire-gorgon.json',s)
    write_json(OUT/'native-evidence/iceandfire-gorgon.json',collect(s))
    write_json(OUT/'iceandfire-gorgon-census.json',census())
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None)
    a['classes']={'net/minecraft/world/entity/Entity.class':['isInvulnerableTo','isInvulnerable','remove','setRemoved'], 'net/minecraft/world/entity/LivingEntity.class':['hasLineOfSight'], 'net/minecraft/world/entity/player/Player.class':['hurt','canHarmPlayer'], 'net/minecraft/server/level/ServerPlayer.class':['hurt','canHarmPlayer','isPvpAllowed']}
    ref=dict(id='iceandfire-gorgon-244',scope='Gorgon gaze LOS, player source-sensitive admission and actual statue invulnerability dispatch; inherited hurt/poison witnesses reused.',archives=[a])
    write_json(OUT/'reference-specifications/iceandfire-gorgon-244.json',ref)
    write_json(OUT/'reference-evidence/iceandfire-gorgon-244.json',reference_collect(ref))
    print('Gorgon witnesses and narrow admission references saved')

if __name__=='__main__':save()
