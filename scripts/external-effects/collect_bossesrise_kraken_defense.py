from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from collect_bossesrise_foundation import targets,KEY,PKG
KRAKEN='entity/boss/kraken/KrakenEntity'
TENTACLE='entity/boss/kraken/KrakenTentacleEntity'
CLASSES={KRAKEN:None,KRAKEN+'$TentacleRespawnTimer':None,'entity/boss/kraken/KrakenCinematicEntity':None,TENTACLE:['<init>','hurt','reallyHurt','killQuietly','die','remove','tickDeath','getOwnerUUID','getOwnerKraken','setOwner','updateOwnerReference','baseTick','addAdditionalSaveData','readAdditionalSaveData','isPushable','setDeltaMovement','pushEntities','getPistonPushReaction','createAttributes','isInWall','isAttacking'],'block/entity/KrakenSpawnerBlockEntity':['tick','<clinit>'],'block/entity/KrakenSpawnerBlockEntity$PiratePoint':['trySummon','onDied'],'entity/projectile/CannonballEntity':['hasCausedDamage'],'configuration/ServerConfiguration':['<clinit>']}

def save():
    t=targets()[KEY];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in CLASSES.items():
            n=PKG+short+'.class';c=ClassFile(z.read(n));names=wanted or sorted({m['name'] for m in c.methods});names=sorted(set(names)|{m['name'] for m in c.methods if any(m['name'].startswith('lambda$'+v+'$') for v in names)})
            rows.append(dict(id='br:kraken_defense:'+short,mod_key=KEY,entry=n,methods=names))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Kraken and tentacle incoming admission, phase/death/resources and genuine spawn callbacks; outgoing goals remain next subsection.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/bossesrise-kraken-defense.json',s);write_json(OUT/'native-evidence/bossesrise-kraken-defense.json',collect(s));print('Kraken defense pinned')
if __name__=='__main__':save()
