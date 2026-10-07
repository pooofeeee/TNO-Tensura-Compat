"""Negative source-graph mutations; no package/name grants coverage by itself."""
import copy
import unittest
from native_context_graph import prove, external_allowed


def fixture():
    e='example/client/model/Test.class';name=e[:-6]
    c=dict(mod_key='test',jar_sha256='pin',classes=[dict(entry=e,name=name,
        superclass='java/lang/Object',entry_sha256='class')],registration_bootstraps=[],
        symbols=['java/lang/Object.<init>()V',name+'.valueF',name+'.second()V',name+'.first()V',
                 'net/minecraft/world/entity/Entity.hurt(Lnet/minecraft/world/damagesource/DamageSource;F)Z'],
        methods=[dict(entry=e,method='first',descriptor='()V',access=1,
             code_sha256='first',hits=[],calls=[[0,182,2]]),
             dict(entry=e,method='second',descriptor='()V',access=1,
             code_sha256='second',hits=[],calls=[[0,182,3]])])
    return c


class ContextGraphTests(unittest.TestCase):
    def test_cycle_only_closes_with_independent_side_effect_proof(self):
        c=fixture();self.assertEqual(prove(c)['summary']['methods'],2)
        c['methods'][1]['calls'].append([3,182,4])
        self.assertEqual(prove(c)['summary']['methods'],0)

    def test_external_game_field_write_is_rejected_transitively(self):
        c=fixture();c['symbols'].append('net/minecraft/world/entity/Entity.fallDistanceF')
        c['methods'][1]['hits']=[[5,181,5]]
        self.assertEqual(prove(c)['summary']['methods'],0)

    def test_own_presentation_state_is_distinct_from_game_state(self):
        c=fixture();c['methods'][1]['hits']=[[5,181,1]]
        self.assertEqual(prove(c)['summary']['methods'],2)
        c['methods'][1]['access']=0x100
        self.assertEqual(prove(c)['summary']['methods'],0)

    def test_unknown_dispatch_and_time_controller_are_not_visual(self):
        for op in ('net/minecraft/world/entity/Entity.setXRot(F)V',
                   'net/minecraft/client/multiplayer/ClientLevel.setBlock()V',
                   'com/github/alexthe666/citadel/server/tick/ServerTickRateTracker.add()V',
                   'example/Mystery.getDamage()F'):
            self.assertFalse(external_allowed(op))
        self.assertTrue(external_allowed('net/minecraft/world/entity/Entity.getX()D'))

    def test_checked_game_reader_is_not_itself_dispositioned(self):
        c=fixture();e='example/server/Actor.class'
        c['classes'].append(dict(entry=e,name=e[:-6],superclass='java/lang/Object',entry_sha256='actor'))
        c['symbols'].append(e[:-6]+'.query()I')
        c['methods'].append(dict(entry=e,method='query',descriptor='()I',access=1,
            code_sha256='query',hits=[],calls=[]))
        c['methods'][0]['calls']=[[0,182,5]]
        rows=prove(c)['rows'];self.assertEqual(len(rows),2)
        self.assertFalse(any(r['entry']==e for r in rows))


if __name__=='__main__':unittest.main()
