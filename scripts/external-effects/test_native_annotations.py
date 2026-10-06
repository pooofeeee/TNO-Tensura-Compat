"""Verify optional annotation decoding against compiled JVM metadata, not names."""
import pathlib
import shutil
import subprocess
import tempfile
import unittest
from classfile import ClassFile


class AnnotationTests(unittest.TestCase):
    def test_explicit_annotations_match_javap_and_defaults_are_not_invented(self):
        with tempfile.TemporaryDirectory() as folder:
            root=pathlib.Path(folder)
            (root/'Fixture.java').write_text('''import java.lang.annotation.*;
@Retention(RetentionPolicy.RUNTIME) @interface Mark {
 String value(); boolean active() default false; int[] counts() default {};
 Class<?> type() default Object.class; RetentionPolicy mode() default RetentionPolicy.CLASS;
}
@Mark(value="registered", active=true, counts={2,7}, type=String.class, mode=RetentionPolicy.RUNTIME)
public class Fixture { @Mark("callback") public static void event(Object event) {} }
''')
            subprocess.run([shutil.which('javac'),str(root/'Fixture.java')],check=True,capture_output=True)
            data=(root/'Fixture.class').read_bytes();parsed=ClassFile(data,retain_annotations=True)
            native=subprocess.check_output([shutil.which('javap'),'-v',str(root/'Fixture.class')],text=True)
            self.assertIn('value="registered"',native)
            self.assertIn('counts=[2,7]',native)
            values=parsed.annotations(parsed.attributes)[0]['values']
            self.assertEqual(values,{'value':'registered','active':True,'counts':[2,7],
                'type':{'class':'Ljava/lang/String;'},'mode':{'enum_type':'Ljava/lang/annotation/RetentionPolicy;','constant':'RUNTIME'}})
            callback=next(m for m in parsed.methods if m['name']=='event')
            self.assertEqual(callback['annotations'][0]['values'],{'value':'callback'})
            self.assertNotIn('active',callback['annotations'][0]['values'])
            legacy=ClassFile(data)
            self.assertTrue(all('annotations' not in m for m in legacy.methods))

    def test_native_recipient_cast_binding_matches_independent_javap_locals(self):
        from promote_combat_batch import effect_receiver_binding
        from collect_cataclysm_ignited_revenant_offense import instructions
        with tempfile.TemporaryDirectory() as folder:
            root=pathlib.Path(folder)
            sources={
                'net/minecraft/world/effect/MobEffectInstance.java':
                    'package net.minecraft.world.effect; public class MobEffectInstance { public MobEffectInstance() {} }',
                'net/minecraft/world/entity/LivingEntity.java':
                    'package net.minecraft.world.entity; import net.minecraft.world.effect.MobEffectInstance; public class LivingEntity { public boolean addEffect(MobEffectInstance e) {return true;} }',
                'Fixture.java':'''import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.effect.MobEffectInstance;
public class Fixture { public static void hit(Object victim,Object source) {
 if(victim instanceof LivingEntity e) e.addEffect(new MobEffectInstance());
 if(source instanceof LivingEntity e) e.addEffect(new MobEffectInstance());
} }'''}
            for file,text in sources.items():
                p=root/file;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
            subprocess.run([shutil.which('javac'),*[str(root/f) for f in sources]],check=True,capture_output=True)
            native=subprocess.check_output([shutil.which('javap'),'-c',str(root/'Fixture.class')],text=True)
            self.assertIn('aload_0',native);self.assertIn('aload_1',native)
            parsed=ClassFile((root/'Fixture.class').read_bytes());method=next(m for m in parsed.methods if m['name']=='hit')
            body=instructions(parsed,method['code']);model=dict(instructions=body)
            sites=[i['offset'] for i in body if 'MobEffectInstance.<init>(' in str(i['operand'])]
            self.assertEqual([effect_receiver_binding(model,s)['origin_local_index'] for s in sites],[0,1])
            bad={**model,'instructions':[dict(i) for i in body]}
            receiver=effect_receiver_binding(model,sites[0])
            origin=next(i for i in bad['instructions'] if i['offset']==receiver['origin_load_offset'])
            origin.update(opcode='0xb6',operand='an arbitrary expression result')
            with self.assertRaises(AssertionError):effect_receiver_binding(bad,sites[0])


if __name__=='__main__':unittest.main()
