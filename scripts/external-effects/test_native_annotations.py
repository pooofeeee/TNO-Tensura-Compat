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


if __name__=='__main__':unittest.main()
