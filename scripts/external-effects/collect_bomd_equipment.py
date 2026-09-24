from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_bomd_foundation import targets,KEY,PKG

CLASSES={**{'item/'+n:None for n in ['BMDItems','BMDFoods','custom/ChargedEnderPearlEntity','custom/ChargedEnderPearlItem','custom/EarthdiveSpear','custom/WallTeleport','custom/CrystalFruitItem','custom/BrimstoneNectarItem','custom/SoulStarEntity','custom/SoulStarItem']},**{'block/custom/'+n:None for n in ['MonolithBlock','MonolithBlockEntity','ChunkCacheBlockEntity','LevitationBlock','LevitationBlockEntity','MobWardBlock','VoidLilyBlockEntity']},'capability/ChunkBlockCache':None,'capability/util/BMDCapabilities':['getChunkBlockCache'],'neoforge/platform/NeoCapabilityHelper':['getChunkBlockCache'],'neoforge/attachment/saved_data/LevelChunkBlockCache':None,'neoforge/event/NeoEvents':None,'mixin/ExplosionMixin':None,'mixin/NaturalSpawnerMixin':None,'mixin/IceBlockMixin':None,'util/VanillaCopiesServer':['travel']}

def save():
    CLASSES['block/custom/VoidLilyBlock']=None
    t=targets()[KEY];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in CLASSES.items():
            n=PKG+short+'.class';c=ClassFile(z.read(n));names=wanted or sorted({m['name'] for m in c.methods})
            rows.append(dict(id='bomd:equipment:'+short,mod_key=KEY,entry=n,methods=names))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Remaining combat equipment/blocks/native hook prerequisites, with bounded exclusions; no rendering or acquisition expansion.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/bomd-equipment.json',s);write_json(OUT/'native-evidence/bomd-equipment.json',collect(s))
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None);a['classes']={'net/minecraft/world/entity/LivingEntity.class':['eat','addEatEffect','heal','getDamageAfterMagicAbsorb','isInvertedHealAndHarm','travel'],'net/minecraft/world/entity/player/Player.class':['eat']}
    r=dict(id='bomd-equipment-244',scope='Food effect application, healing and Resistance/Slow Falling native dependency.',archives=[a]);write_json(OUT/'reference-specifications/bomd-equipment-244.json',r);write_json(OUT/'reference-evidence/bomd-equipment-244.json',reference_collect(r,source_aids=True))
    v=dict(classes={'net/minecraft/world/effect/RegenerationMobEffect':['applyEffectTick','shouldApplyEffectTickThisTick'],'net/minecraft/world/effect/HealOrHarmMobEffect':['applyEffectTick','applyInstantenousEffect'],'net/minecraft/world/level/block/FlowerBlock':['<init>','makeEffectList']},resources=['data/minecraft/tags/entity_type/inverted_healing_and_harm.json'])
    write_json(OUT/'vanilla-specifications/bomd-equipment.json',v);write_json(OUT/'vanilla-evidence/bomd-equipment.json',prepare(v))
    print('Equipment witnesses',len(rows))

if __name__=='__main__':save()
