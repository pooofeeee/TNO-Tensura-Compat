from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from collect_bomd_foundation import targets,KEY,PKG

CLASSES=['entity/custom/lich/LichMovement','entity/custom/gauntlet/GauntletMovement','entity/ai/VelocitySteering','entity/ai/ValidatedTargetSelector','entity/ai/goals/VelocityGoal','entity/ai/goals/CompositeGoal','entity/ai/valid_direction/CanMoveThrough','entity/ai/valid_direction/InDesiredRange','entity/ai/valid_direction/ValidDirectionAnd','entity/util/CompositeEntityTick','entity/custom/void_blossom/LightBlockPlacer','entity/custom/void_blossom/VoidBlossomClientSpikeHandler','packet/custom/SpikeS2CPacket','packet/custom/HealS2CPacket','packet/custom/ChargedEnderPearlS2CPacket']

def save():
    t=targets()[KEY];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for short in CLASSES:
            n=PKG+short+'.class';c=ClassFile(z.read(n));rows.append(dict(id='bomd:closure:'+short,mod_key=KEY,entry=n,methods=sorted({m['name'] for m in c.methods})))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Final native movement helper and packet non-damage boundary witnesses; no new boss research.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/bomd-closure.json',s);write_json(OUT/'native-evidence/bomd-closure.json',collect(s));print('Closure witnesses',len(rows))

if __name__=='__main__':save()
