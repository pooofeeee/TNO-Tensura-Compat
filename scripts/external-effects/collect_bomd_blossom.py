from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_bomd_foundation import targets,KEY,PKG,tags

CLASSES={**{'entity/custom/void_blossom/'+n:None for n in ['VoidBlossomEntity','VoidBlossomAttacks','VoidBlossomMoveLogic','VoidBlossomSpikeTick','SpikeAction','SpikeWaveAction','Spikes','SporeAction','BladeAction','BlossomAction','LightBlockRemover','VoidBlossomDropExpDeathTick','hitbox/VoidBlossomHitboxes','hitbox/VoidBlossomHitboxes$1','hitbox/VoidBlossomCompoundHitbox','hitbox/NetworkedHitboxManager','hitbox/HitboxId']},'projectile/SporeBallProjectile':None,'projectile/PetalBladeProjectile':None,'block/custom/VoidBlossomBlock':None,'block/custom/VineWallBlock':None}

def source_tags():
    table={}
    for r in tags()['resources']:
        n=r['entry'];tag=n.split('/')[1]+':'+n.split('/tags/damage_type/')[1][:-5];d=r['data']
        if d.get('replace'):table[tag]=[]
        table.setdefault(tag,[]).extend(d.get('values',[]))
    def members(tag,seen=()):
        if tag in seen:return set()
        result=set()
        for v in table.get(tag,[]):
            v=v['id'] if isinstance(v,dict) else v
            result|=members(v[1:],seen+(tag,)) if v.startswith('#') else {v}
        return result
    return dict(scope='Pinned Minecraft/NeoForge/BOMD closure, not every pack override.',types={n:sorted(k for k in table if n in members(k)) for n in ['minecraft:thorns','minecraft:thrown','neoforge:poison','minecraft:magic','bosses_of_mass_destruction:shield_piercing']})

def save():
    t=targets()[KEY];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in CLASSES.items():
            n=PKG+short+'.class';c=ClassFile(z.read(n));names=wanted or sorted({m['name'] for m in c.methods})
            rows.append(dict(id='bomd:blossom:'+short,mod_key=KEY,entry=n,methods=names))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Void Blossom native combat, multipart retaliation, distinct projectile/ground damage and bounded healing-block/death semantics.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/bomd-blossom.json',s);write_json(OUT/'native-evidence/bomd-blossom.json',collect(s))
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None);a['classes']={'net/minecraft/world/effect/PoisonMobEffect.class':['applyEffectTick','shouldApplyEffectTickThisTick']}
    b=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][1]);b.pop('semantic_review',None);b['classes']={};b['resources']=['data/neoforge/damage_type/poison.json']
    r=dict(id='bomd-blossom-244',scope='Installed patched Poison source and tick amount/admission; no raw-vanilla magic substitution.',archives=[a,b]);write_json(OUT/'reference-specifications/bomd-blossom-244.json',r);write_json(OUT/'reference-evidence/bomd-blossom-244.json',reference_collect(r,source_aids=True))
    v=dict(classes={'net/minecraft/world/damagesource/DamageSources':['thorns','source']},resources=['data/minecraft/damage_type/thorns.json'])
    write_json(OUT/'vanilla-specifications/bomd-blossom.json',v);write_json(OUT/'vanilla-evidence/bomd-blossom.json',prepare(v));write_json(OUT/'bomd-blossom-source-tags.json',source_tags())
    print('Void Blossom witnesses',len(rows))

if __name__=='__main__':save()
