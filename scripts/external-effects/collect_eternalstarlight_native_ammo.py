from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from collect_eternalstarlight_foundation import ES,targets

CLASSES={}
PROJECTILES=['AshenSnowball','FrozenBomb','GlaciteArrow','MalariteArrow','AethersentArrow','AirSacArrow','ThrownSpear','ThrownMalariteSpear','ThrownPungencyFruitSpear']
for n in PROJECTILES:CLASSES['common/entity/projectile/'+n]=None
for n in ['AshenSnowball','FrozenBomb','GlaciteArrow','MalariteArrow','AethersentArrow','AirSacArrow','Spear','MalariteSpear','PungencyFruitSpear']:CLASSES['common/item/combat/'+n+'Item']=None
CLASSES['common/handler/ESCommonSetupHandler']=['commonSetup']
CLASSES['common/entity/living/monster/Stranghoul']=['performRangedAttack','getProjectile']
def census():
    t=targets()['eternalstarlight'];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(x for x in z.namelist() if x.endswith('.class')):
            raw=z.read(n);c=ClassFile(raw)
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if i['opcode']=='0xbb' and any(str(i['operand']).endswith('/'+s) for s in PROJECTILES)]
                if hits:rows.append(dict(entry=n,sha256=byte_hash(raw),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits))
    return dict(jar_sha256=t['sha256'],scope='Whole JAR native snowball/bomb/arrows/spears constructor producers; registry factories alone are not extra paths.',rows=rows)
def save():
    t=targets()['eternalstarlight'];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in CLASSES.items():
            n=ES+short+'.class';c=ClassFile(z.read(n));names=wanted if wanted is not None else sorted({m['name'] for m in c.methods});names=sorted(set(names)|{m['name'] for m in c.methods if any(m['name'].startswith('lambda$'+v+'$') for v in names)})
            rows.append(dict(id='es:ammo:'+short,mod_key='eternalstarlight',entry=n,methods=names))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Remaining native damage ammo: snowball/bomb, arrow variants and common spear damage/delivery. Reuse prior Tearing and boomerang review.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/eternalstarlight-native-ammo.json',s);write_json(OUT/'native-evidence/eternalstarlight-native-ammo.json',collect(s));write_json(OUT/'eternalstarlight-native-ammo-census.json',census())
    print('Native ammo witnesses saved')
if __name__=='__main__':save()
