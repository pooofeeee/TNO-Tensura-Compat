from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_bossesrise_foundation import targets,KEY,PKG
CLASSES={s:None for s in ['item/IceGauntletItem','item/SandwormGauntletItem','attachment/entity/GauntletAttachment','item/component/OperationMode','network/IceGauntletMessage']}
CLASSES['attachment/entity/PlayerAnimationHandler']=['startAnimation']

def census():
    t=targets()[KEY];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(x for x in z.namelist() if x.endswith('.class')):
            raw=z.read(n);c=ClassFile(raw)
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if i['opcode']=='0xb8' and 'PoisonSpitPrEntity.shoot(' in str(i.get('operand',''))]
                if hits:rows.append(dict(entry=n,entry_sha256=byte_hash(raw),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits))
    return dict(jar_sha256=t['sha256'],scope='Distinguish invokestatic convenience-helper use from native invokevirtual projectile launch; no external static-helper caller is inferred from owner-qualified method text.',rows=rows)

def save():
    t=targets()[KEY];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in CLASSES.items():
            n=PKG+short+'.class';c=ClassFile(z.read(n));names=wanted or sorted({m['name'] for m in c.methods});names=sorted(set(names)|{m['name'] for m in c.methods if any(m['name'].startswith('lambda$'+v+'$') for v in names)});rows.append(dict(id='br:gauntlets:'+short,mod_key=KEY,entry=n,methods=names))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Actual Ice/Sandworm Gauntlet input, cost, owner and hazard delivery; reuse protected hazard payloads.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/bossesrise-gauntlets.json',s);write_json(OUT/'native-evidence/bossesrise-gauntlets.json',collect(s));write_json(OUT/'bossesrise-gauntlets-helper-census.json',census())
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None);a['classes']={};raw={}
    wanted={'net/minecraft/world/item/ShieldItem':['use','getUseAnimation','getUseDuration'],'net/minecraft/world/entity/player/Player':['attack'],'net/minecraft/world/item/ItemStack':['hurtEnemy'],'net/minecraft/world/item/Item':['hurtEnemy']}
    with zipfile.ZipFile(a['path']) as z:
        for k,v in wanted.items():
            if k+'.class' in z.namelist():a['classes'][k+'.class']=v
            else:raw[k]=v
    r=dict(id='bossesrise-gauntlets-244',scope='Inherited real shield use and native successful melee callback; no synthetic item use or HP events.',archives=[a]);write_json(OUT/'reference-specifications/bossesrise-gauntlets-244.json',r);write_json(OUT/'reference-evidence/bossesrise-gauntlets-244.json',reference_collect(r,source_aids=True))
    s=dict(classes=raw,resources=[]);write_json(OUT/'vanilla-specifications/bossesrise-gauntlets.json',s);write_json(OUT/'vanilla-evidence/bossesrise-gauntlets.json',prepare(s));write_json(OUT/'reference-routing/bossesrise-gauntlets.json',dict(archive=a['path'],sha256=a['sha256'],absent_entries=[k+'.class' for k in raw]));print('Gauntlet evidence pinned')
if __name__=='__main__':save()
