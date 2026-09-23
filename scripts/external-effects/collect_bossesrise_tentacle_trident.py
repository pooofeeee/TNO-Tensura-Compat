from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_bossesrise_foundation import targets,KEY,PKG
CLASSES={s:None for s in ['item/UndyingTentacleItem','entity/boss/kraken/summons/GhostTentacleEntity','entity/boss/kraken/summons/GhostTentacleEntity$1','item/KrakenTridentItem','entity/projectile/ThrownKrakenTridentEntity','mixins/KrakenTridentTridentItemMixin']}
CLASSES['init/BossesRiseItems']=['<clinit>']

def support():
    t=targets()[KEY];resources=[];calls=[]
    with zipfile.ZipFile(t['path']) as z:
        for n in ['block_factorys_bosses.mixins.json','META-INF/accesstransformer.cfg']:
            raw=z.read(n);resources.append(dict(entry=n,sha256=byte_hash(raw),text=raw.decode('utf-8')))
        for n in sorted(x for x in z.namelist() if x.endswith('.class')):
            raw=z.read(n);c=ClassFile(raw)
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if (i['opcode']=='0xbb' and str(i.get('operand','')).endswith('/ThrownKrakenTridentEntity')) or (i['opcode'] in ['0xb6','0xb7','0xb8','0xb9'] and any(s in str(i.get('operand','')) for s in ['DispenserBlock.registerBehavior(', 'DispenserBlock.registerProjectileBehavior(', 'KrakenTridentItem.asProjectile(']))]
                if hits:calls.append(dict(entry=n,entry_sha256=byte_hash(raw),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits))
    return dict(jar_sha256=t['sha256'],resources=resources,calls=calls,scope='Installed trident redirect/access transformer and constructor/dispenser-registration census; factory override is not automatically a delivered dispenser path.')

def save():
    t=targets()[KEY];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in CLASSES.items():
            n=PKG+short+'.class';c=ClassFile(z.read(n));names=wanted or sorted({m['name'] for m in c.methods});names=sorted(set(names)|{m['name'] for m in c.methods if any(m['name'].startswith('lambda$'+v+'$') for v in names)})
            if short=='init/BossesRiseItems':names+= [m['name'] for m in c.methods if any('KrakenTridentItem.<init>' in str(i.get('operand','')) for i in c.instructions(m.get('code',b'')))]
            rows.append(dict(id='br:tentacle_trident:'+short,mod_key=KEY,entry=n,methods=names))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Undying Tentacle genuine pull/summon and Ghost combat; Kraken Trident inherited throw and added area hit.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/bossesrise-tentacle-trident.json',s);write_json(OUT/'native-evidence/bossesrise-tentacle-trident.json',collect(s));write_json(OUT/'bossesrise-tentacle-trident-support.json',support())
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None);a['classes']={};raw={}
    wanted={'net/minecraft/world/item/TridentItem':['use','releaseUsing','getUseDuration'],'net/minecraft/world/entity/projectile/ThrownTrident':['<init>','onHitEntity','tick','findHitEntity','getLoyaltyFromItem','getWeaponItem','hitBlockEnchantmentEffects','readAdditionalSaveData','addAdditionalSaveData','playerTouch','tryPickup','isAcceptibleReturnOwner'],'net/minecraft/world/entity/LivingEntity':['kill'],'net/minecraft/core/dispenser/DispenseItemBehavior':['bootStrap'],'net/minecraft/world/damagesource/DamageSources':['trident']}
    with zipfile.ZipFile(a['path']) as z:
        for k,v in wanted.items():
            if k+'.class' in z.namelist():a['classes'][k+'.class']=v
            else:raw[k]=v
    r=dict(id='bossesrise-tentacle-trident-244',scope='Native release/Riptide/Trident hurt, terminal summon lifetime and actual dispenser registration distinction.',archives=[a]);write_json(OUT/'reference-specifications/bossesrise-tentacle-trident-244.json',r);write_json(OUT/'reference-evidence/bossesrise-tentacle-trident-244.json',reference_collect(r,source_aids=True))
    s=dict(classes=raw,resources=['data/minecraft/damage_type/trident.json']);write_json(OUT/'vanilla-specifications/bossesrise-tentacle-trident.json',s);write_json(OUT/'vanilla-evidence/bossesrise-tentacle-trident.json',prepare(s));write_json(OUT/'reference-routing/bossesrise-tentacle-trident.json',dict(archive=a['path'],sha256=a['sha256'],absent_entries=[k+'.class' for k in raw]));print('Tentacle/Trident evidence pinned')
if __name__=='__main__':save()
