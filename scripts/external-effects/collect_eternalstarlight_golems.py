from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from collect_eternalstarlight_foundation import ES,targets

CLASSES={
 'common/entity/living/boss/ESBoss':['hurt','tick','canBossMove','setActivated','defineSynchedData','readAdditionalSaveData','addAdditionalSaveData','canChangeDimensions','startRiding'],
 'common/entity/living/boss/golem/StarlightGolem':['<init>','createAttributes','isInvulnerableTo','hurt','aiStep','getNearbyEnergyBlocks','turnOnEnergyBlocks','canBossMove','isAlliedTo','clearChargeHurtCountAndAmount','readAdditionalSaveData'],
 'common/entity/living/boss/golem/StarlightGolemChargeStartPhase':None,
 'common/entity/living/boss/golem/StarlightGolemChargePhase':None,
 'common/entity/living/boss/golem/StarlightGolemChargeEndPhase':None,
 'common/block/EnergyBlock':['<init>','onProjectileHit','useWithoutItem'],
 'common/entity/living/phase/BehaviorManager':None,
 'common/entity/living/phase/BehaviorPhase':None,
 'common/entity/living/boss/golem/Permafrost':['<init>','createAttributes','doHurtTarget','aiStep','causeFallDamage','isAlliedTo'],
 'common/entity/living/boss/golem/PermafrostMeleePhase':None,
 'common/entity/living/boss/golem/PermafrostMeleeTransitionPhase':None,
 'common/entity/living/boss/golem/PermafrostMeleeEndPhase':None,
 'common/entity/living/boss/golem/PermafrostRangedPhase':None,
 'common/entity/projectile/FrozenTube':['onHit','onHitEntity'],
 'common/item/combat/FrozenTubeItem':['use','asProjectile'],
 'common/entity/living/monster/Freeze':['registerGoals','performRangedAttack','tick','createAttributes','isAlliedTo','causeFallDamage'],
 'common/entity/attack/ray/RayAttack':['tick','update','getRadius','onHit','doHurtTarget','getAttackDamage','hurt','getCaster','setCaster','readAdditionalSaveData','addAdditionalSaveData'],
 'common/entity/attack/ray/GolemLaserBeam':['getAttackDamage','updatePosition','getPositionForCaster'],
 'common/spell/LaserBeamSpell':None,
 'common/spell/AbstractSpell':['canCast','canContinueToCast','hasNeededCrystal','start','damageCrystal','tick','stop'],
 'common/spell/SpellCastData$ItemSpellSource':['canContinue'],
 'common/util/ESSpellUtil':None,
 'common/util/ESCrestUtil':['getCrestLevel','getOwnedCrests'],
 'common/item/magic/OrbOfProphecyItem':['use'],
 'common/registry/ESSpells':None,
 'common/registry/ESPoiTypes':None,
 'common/mixin/PlayerMixin':[],
}

def producer_census():
    t=targets()['eternalstarlight'];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(x for x in z.namelist() if x.endswith('.class')):
            raw=z.read(n);c=ClassFile(raw)
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if (i['opcode']=='0xbb' and any(str(i['operand']).endswith('/'+s) for s in ['FrozenTube','GolemLaserBeam'])) or (i['opcode']=='0xb2' and any(s in str(i['operand']) for s in ['ESSpells.LASER_BEAM','ESEntities.FROZEN_TUBE','ESEntities.GOLEM_LASER_BEAM']))]
                if hits:rows.append(dict(entry=n,sha256=byte_hash(raw),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits))
    return dict(jar_sha256=t['sha256'],scope='Whole ES-JAR exact producer/factory-key census; registry/render/datagen entries are not extra combat delivery.',rows=rows)

def save():
    t=targets()['eternalstarlight'];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in CLASSES.items():
            n=ES+short+'.class';c=ClassFile(z.read(n));names=wanted if wanted is not None else sorted({m['name'] for m in c.methods});names=sorted(set(names)|{m['name'] for m in c.methods if any(m['name'].startswith('lambda$'+v+'$') for v in names)})
            rows.append(dict(id='es:golems:'+short,mod_key='eternalstarlight',entry=n,methods=names))
        for n in ['data/eternal_starlight/tags/entity_type/starlight_golem_allies.json','data/eternal_starlight/eternal_starlight/crest/blazing_beam.json']:
            rows.append(dict(id='es:golems:data:'+n,mod_key='eternalstarlight',entry=n))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Golem protection/charge, Permafrost and Freeze, Frozen Tube, LASER ray and legitimate Orb spell path; not other spells/bosses.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/eternalstarlight-golems.json',s);write_json(OUT/'native-evidence/eternalstarlight-golems.json',collect(s));write_json(OUT/'eternalstarlight-golems-producer-census.json',producer_census())
    javap=Path('C:/Program Files/Java/jdk-21/bin/javap.exe');args=['-p','-c','-v','-classpath',t['path'],ES.replace('/','.')+'common.entity.projectile.FrozenTube']
    output=subprocess.check_output([str(javap),*args],encoding='utf-8');p=OUT/'annotation-evidence/eternalstarlight-frozen-tube-javap.txt';p.write_text('\n'.join(line.rstrip() for line in output.splitlines())+'\n',encoding='utf-8')
    write_json(OUT/'annotation-evidence/eternalstarlight-frozen-tube-javap.json',dict(tool=str(javap),tool_sha256=sha256(javap),jar_sha256=t['sha256'],arguments=args,output_file=p.relative_to(OUT).as_posix(),output_sha256=sha256(p),scope='Resolve malformed source-aid pattern-switch receiver: native owner typeSwitch and branches are authority.'))
    print('Golem family witnesses saved')
if __name__=='__main__':save()
