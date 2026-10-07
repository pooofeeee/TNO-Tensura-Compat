"""Native display mutations stay distinct from independent combat payloads."""
import unittest
from catalog_common import OUT, read_json
from assemble_authored_contracts import render
from promote_combat_batch import validate_batch


def body(cls, name, scope='remaining-display-context'):
    w = next(w for w in read_json(OUT/f'native-evidence/alexscaves-{scope}.json')['witnesses']
             if w['entry'].endswith('/'+cls+'.class'))
    return next(m['instructions'] for m in w['methods'] if m['name']==name)


class DisplayContextTests(unittest.TestCase):
    def test_render_and_exact_native_coverage(self):
        batch=read_json(OUT/'alexscaves-r2m8z-remaining-display-context.json')
        self.assertEqual(batch, render(read_json(OUT/'native-findings/alexscaves-remaining-display-context.json')))
        self.assertEqual(validate_batch(batch,read_json(OUT/'mod-reviews/alexscaves.json'),
                         read_json(OUT/'alexscaves-combat-census.json'))['status'],'PASS')

    def test_render_copy_mutates_and_restores_rotation_without_actor_spawn(self):
        for cls, name in [('AmberMonolithBlockRenderer','renderEntityInAmber'),
                          ('NotorRenderer','renderEntityInHologram')]:
            s=str(body(cls,name))
            self.assertGreaterEqual(s.count('.setXRot('),2)
            self.assertGreaterEqual(s.count('.setYRot('),2)
            for marker in ('.addFreshEntity(','.hurt(','.addEffect(','.tick('):
                self.assertNotIn(marker,s)

    def test_mushroom_cloud_native_writes_are_display_counters(self):
        b=body('MushroomCloudParticle','tick','display-cache-context');s=str(b)
        for field,value in [('renderNukeSkyDarkFor',70),('muteNonNukeSoundsFor',50),('renderNukeFlashFor',16)]:
            at=next(n for n,i in enumerate(b) if i['opcode']=='0xb3' and ('.'+field) in str(i['operand']))
            self.assertEqual(b[at-1]['operand'],value)
        for marker in ('.hurt(','.explode(','.addEffect('):self.assertNotIn(marker,s)

    def test_item_frame_posts_native_name_event_not_attack_event(self):
        s=str(body('ItemFrameRendererMixin','ac_renderArmWithItem'))
        self.assertIn('RenderNameTagEvent',s)
        self.assertNotIn('RenderItemInFrameEvent',s)
        self.assertNotIn('AttackEntityEvent',s)

    def test_tutorial_message_preserves_original_native_delivery(self):
        s=str(body('SpelunkeryTableScreen','containerTick'))
        self.assertIn('SpelunkeryTableChangeMessage',s)
        self.assertIn('.setTutorialComplete(',s)
        self.assertNotIn('.hurt(',s)


if __name__=='__main__':unittest.main()
