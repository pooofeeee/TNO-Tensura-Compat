"""Independent hand-built shape/mutation cases, plus exact finite-queue proofs."""
import copy
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from catalog_common import OUT,read_json,byte_hash
from native_forwarding import forwarding_shape,validate,declared_field_exists
from reconcile_native_census import reconcile
from classfile import ClassFile


def ins(op,operand=None,offset=0,**extra):
    return dict(opcode=op,operand=operand,offset=offset,**extra)


class ForwardingTests(unittest.TestCase):
    def bridge(self):
        return [ins('0x2a'),ins('0x2b'),ins('0xc0','example/Actor'),
                ins('0xb6','example/Renderer.render(Lexample/Actor;)V'),ins('0xb1')]

    def shape(self,body,handlers=()):
        return forwarding_shape('example/Renderer.class','render','(Ljava/lang/Object;)V',0x1041,body,handlers)

    def test_exact_typed_bridge_and_native_cast_retained(self):
        self.assertEqual(self.shape(self.bridge()),dict(kind='EXACT_COMPILER_BRIDGE',
            target=dict(entry='example/Renderer.class',method='render',descriptor='(Lexample/Actor;)V')))
        b=self.bridge();del b[2]
        self.assertIsNone(self.shape(b))

    def test_bridge_flags_owner_and_argument_identity_are_required(self):
        b=self.bridge()
        self.assertIsNone(forwarding_shape('example/Renderer.class','render','(Ljava/lang/Object;)V',1,b))
        for index,new in [(0,ins('0x2b')),(1,ins('0x2c')),
                          (3,ins('0xb6','example/Other.render(Lexample/Actor;)V')),
                          (3,ins('0xb8','example/Renderer.render(Lexample/Actor;)V'))]:
            bad=copy.deepcopy(b);bad[index]=new;self.assertIsNone(self.shape(bad))

    def test_side_effects_constants_branches_and_exception_handlers_refused(self):
        for added in [ins('0xb8','example/Combat.hurt()V'),ins('0x3'),ins('0x99'),ins('0xb5','example/Actor.healthF')]:
            b=self.bridge();b.insert(1,added);self.assertIsNone(self.shape(b))
        self.assertIsNone(self.shape(self.bridge(),[(0,1,2,3)]))

    def test_instance_noop_and_constant_gate_are_not_exclusions(self):
        self.assertIsNone(forwarding_shape('x/Actor.class','die','()V',1,[ins('0xb1')]))
        self.assertIsNone(forwarding_shape('x/Actor.class','canAttack','()Z',9,[ins('0x3'),ins('0xac')]))
        self.assertEqual(forwarding_shape('x/Helper.class','execute','()V',9,[ins('0xb1')]),
                         dict(kind='EMPTY_STATIC_VOID_HELPER'))

    def test_only_object_constructor_is_pure_context(self):
        b=[ins('0x2a'),ins('0xb7','java/lang/Object.<init>()V'),ins('0xb1')]
        self.assertEqual(forwarding_shape('x/H.class','<init>','()V',1,b),dict(kind='OBJECT_ONLY_CONTEXT_CONSTRUCTOR'))
        b[1]['operand']='x/Boss.<init>()V'
        self.assertIsNone(forwarding_shape('x/H.class','<init>','()V',1,b))

    def test_covariant_return_and_wide_parameter_slots_are_not_guessed(self):
        b=[ins('0x2a'),ins('0x1f'),ins('0x2d'),ins('0xc0','example/Actor'),
           ins('0xb6','example/Renderer.copy(JLexample/Actor;)Lexample/Actor;'),ins('0xb0')]
        self.assertIsNotNone(forwarding_shape('example/Renderer.class','copy','(JLjava/lang/Object;)Ljava/lang/Object;',0x1041,b))
        b[2]=ins('0x2c');self.assertIsNone(forwarding_shape('example/Renderer.class','copy','(JLjava/lang/Object;)Ljava/lang/Object;',0x1041,b))


class LeafQueryShapeTests(unittest.TestCase):
    def test_declared_field_transport_preserves_context_without_excluding_readers(self):
        getter=[ins('0x2a'),ins('0xb4','x/Actor.phaseI'),ins('0xac')]
        s=forwarding_shape('x/Actor.class','getPhase','()I',1,getter)
        self.assertEqual(s,dict(kind='RAW_DECLARED_FIELD_QUERY',field_name='phase',field_descriptor='I',field_static=False))
        self.assertTrue(declared_field_exists(s,dict(fields=[dict(name='phase',descriptor='I',access=2)])))
        self.assertFalse(declared_field_exists(s,dict(fields=[])))
        setter=[ins('0x2a'),ins('0x1b',local_index=1),ins('0xb5','x/Actor.phaseI'),ins('0xb1')]
        self.assertEqual(forwarding_shape('x/Actor.class','setPhase','(I)V',1,setter)['kind'],'RAW_DECLARED_FIELD_WRITE')
        for b in [getter+[ins('0xb1')],[ins('0x3',0),ins('0xb5','x/Actor.phaseI'),ins('0xb1')],
                  [ins('0x2a'),ins('0xb4','x/Parent.phaseI'),ins('0xac')]]:
            self.assertIsNone(forwarding_shape('x/Actor.class','method','()I',1,b))
        wrong=copy.deepcopy(setter);wrong[1]['local_index']=2
        self.assertIsNone(forwarding_shape('x/Actor.class','setPhase','(I)V',1,wrong))

    def test_abstract_declarations_do_not_close_native_or_concrete_code(self):
        self.assertEqual(forwarding_shape('x/I.class','tick','()V',0x401,[]),dict(kind='ABSTRACT_DECLARATION_CONTEXT'))
        self.assertIsNone(forwarding_shape('x/I.class','tick','()V',0x101,[]))
        self.assertIsNone(forwarding_shape('x/I.class','tick','()V',0x401,[ins('0xb1')]))

    def test_constant_true_requires_static_synthetic_reference_predicate(self):
        body=[ins('0x4',1),ins('0xac')]
        shape=lambda desc,flags,b:forwarding_shape('x/Q.class','anyName',desc,flags,b)
        self.assertEqual(shape('(Lx/Actor;)Z',0x100a,body),dict(kind='EXACT_SYNTHETIC_TRUE_PREDICATE'))
        for desc,flags,b in [('()Z',0x100a,body),('(I)Z',0x100a,body),
                             ('(Lx/Actor;)Z',0xa,body),('(Lx/Actor;)Z',0x1002,body),
                             ('(Lx/Actor;)Z',0x100a,[ins('0x3',0),ins('0xac')]),
                             ('(Lx/Actor;)Z',0x100a,[ins('0xb5','x/Actor.healthF')]+body)]:
            self.assertIsNone(shape(desc,flags,b))

    def test_vec3_distance_requires_exact_receiver_argument_and_api(self):
        desc='(Lnet/minecraft/world/phys/Vec3;Lnet/minecraft/world/entity/Entity;)D'
        body=[ins('0x2b',local_index=1),ins('0x2a',local_index=0),
              ins('0xb6','net/minecraft/world/entity/Entity.distanceToSqr(Lnet/minecraft/world/phys/Vec3;)D'),ins('0xaf')]
        shape=lambda b:forwarding_shape('x/Q.class','anyName',desc,0xa,b)
        self.assertEqual(shape(body),dict(kind='EXACT_NATIVE_VEC3_DISTANCE_QUERY'))
        for index,field,value in [(0,'local_index',0),(1,'local_index',1),
                                  (2,'operand','x/Actor.damage(Lnet/minecraft/world/phys/Vec3;)D')]:
            bad=copy.deepcopy(body);bad[index][field]=value;self.assertIsNone(shape(bad))
        self.assertIsNone(shape(body+[ins('0xb1')]))

    @unittest.skipUnless(shutil.which('javac'),'Requires JDK parser fixture')
    def test_independent_compiled_predicate_does_not_hide_a_state_gate(self):
        source='''import java.util.function.Predicate;
class QueryFixture {
  static boolean gate;
  static Predicate<Object> constant() { return entity -> true; }
  static Predicate<Object> state() { return entity -> gate; }
  static boolean callback(Object entity) { return true; }
}'''
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'QueryFixture.java').write_text(source)
            subprocess.run(['javac','-d',d,str(root/'QueryFixture.java')],check=True,capture_output=True)
            c=ClassFile((root/'QueryFixture.class').read_bytes(),retain_code_metadata=True)
            accepted=[]
            for m in c.methods:
                shape=forwarding_shape('QueryFixture.class',m['name'],m['descriptor'],m['access'],list(c.instructions(m.get('code',b''))))
                if shape and shape['kind']=='EXACT_SYNTHETIC_TRUE_PREDICATE':accepted.append(m['name'])
            self.assertEqual(accepted,['lambda$constant$0'])


class PresentationLeafShapeTests(unittest.TestCase):
    def test_sound_query_is_exact_registry_return_not_hurt_payload(self):
        b=[ins('0xb2','net/minecraft/core/registries/BuiltInRegistries.SOUND_EVENTLnet/minecraft/core/Registry;'),
           ins('0x12','example:hurt'),ins('0xb8','net/minecraft/resources/ResourceLocation.parse(Ljava/lang/String;)Lnet/minecraft/resources/ResourceLocation;'),
           ins('0xb9','net/minecraft/core/Registry.get(Lnet/minecraft/resources/ResourceLocation;)Ljava/lang/Object;'),
           ins('0xc0','net/minecraft/sounds/SoundEvent'),ins('0xb0')]
        shape=lambda b:forwarding_shape('x/Actor.class','getHurtSound','(Lnet/minecraft/world/damagesource/DamageSource;)Lnet/minecraft/sounds/SoundEvent;',1,b)
        self.assertEqual(shape(b),dict(kind='EXACT_NATIVE_SOUND_REGISTRY_QUERY',sound_identifier='example:hurt'))
        for extra in (ins('0xb6','x/Actor.hurt()Z'),ins('0xb5','x/Actor.healthF')):
            self.assertIsNone(shape([extra]+b))
        bad=copy.deepcopy(b);bad[0]['operand']='x/Actor.GAMEPLAY_REGISTRYLnet/minecraft/core/Registry;';self.assertIsNone(shape(bad))

    def test_cache_query_requires_own_field_exact_gecko_type(self):
        t='Lsoftware/bernie/geckolib/animatable/instance/AnimatableInstanceCache;'
        b=[ins('0x2a'),ins('0xb4','x/Actor.cache'+t),ins('0xb0')]
        shape=lambda b:forwarding_shape('x/Actor.class','getAnimatableInstanceCache','()'+t,1,b)
        self.assertEqual(shape(b),dict(kind='EXACT_GECKO_ANIMATION_CACHE_QUERY',cache_field='x/Actor.cache'+t))
        for value in ('x/Other.cache'+t,'x/Actor.attackStateI'):
            bad=copy.deepcopy(b);bad[1]['operand']=value;self.assertIsNone(shape(bad))

    def test_death_rotation_requires_literal_renderer_api_not_physical_getter(self):
        b=[ins('0xb',0.0),ins('0xae')];parent='software/bernie/geckolib/renderer/GeoEntityRenderer'
        self.assertEqual(forwarding_shape('x/R.class','getDeathMaxRotation','(Lx/Actor;)F',1,b,superclass=parent),
                         dict(kind='EXACT_GECKO_DEATH_RENDER_ROTATION',render_degrees=0.0))
        self.assertIsNone(forwarding_shape('x/R.class','getDeathMaxRotation','(Lx/Actor;)F',1,b,superclass='x/Combat'))
        self.assertIsNone(forwarding_shape('x/R.class','getRotation','(Lx/Actor;)F',1,b,superclass=parent))

    def test_literal_tooltip_preserves_native_parent_and_only_mutates_text_list(self):
        desc='(Lnet/minecraft/world/item/ItemStack;Lnet/minecraft/world/item/Item$TooltipContext;Ljava/util/List;Lnet/minecraft/world/item/TooltipFlag;)V'
        parent='net/minecraft/world/item/Item'
        b=[ins(op,local_index=n) for n,op in enumerate(('0x2a','0x2b','0x2c','0x2d','0x19'))]
        b += [ins('0xb7',parent+'.appendHoverText'+desc),ins('0x2d',local_index=3),ins('0x12','Tooltip claim is not evidence of damage'),
              ins('0xb8','net/minecraft/network/chat/Component.literal(Ljava/lang/String;)Lnet/minecraft/network/chat/MutableComponent;'),
              ins('0xb9','java/util/List.add(Ljava/lang/Object;)Z'),ins('0x57'),ins('0xb1')]
        shape=lambda b:forwarding_shape('x/I.class','appendHoverText',desc,1,b,superclass=parent)
        # One parent call and one five-instruction literal line, then return.
        self.assertEqual(shape(b),dict(kind='EXACT_NATIVE_LITERAL_TOOLTIP',tooltip_lines=['Tooltip claim is not evidence of damage']))
        bad=copy.deepcopy(b);bad[6]['local_index']=1;self.assertIsNone(shape(bad))
        bad=copy.deepcopy(b);bad[8]['operand']='x/Item.damage(Ljava/lang/String;)Lnet/minecraft/network/chat/MutableComponent;';self.assertIsNone(shape(bad))


class DistanceQueryShapeTests(unittest.TestCase):
    def query(self):
        return [ins('0x19',local_index=6),ins('0x26',local_index=0),
                ins('0x28',local_index=2),ins('0x18',local_index=4),
                ins('0xb6','net/minecraft/world/entity/Entity.distanceToSqr(DDD)D'),ins('0xaf')]

    def factory(self):
        return [ins('0x27',local_index=1),ins('0x29',local_index=3),ins('0x18',local_index=5),
                ins('0xba','bootstrap#3:applyAsDouble(DDD)Ljava/util/function/ToDoubleFunction;'),
                ins('0xb8','java/util/Comparator.comparingDouble(Ljava/util/function/ToDoubleFunction;)Ljava/util/Comparator;'),ins('0xb0')]

    def bootstrap(self):
        return {'3':dict(handle=dict(tag=15,value='java/lang/invoke/LambdaMetafactory.metafactory(Ljava/lang/invoke/MethodHandles$Lookup;Ljava/lang/String;Ljava/lang/invoke/MethodType;Ljava/lang/invoke/MethodType;Ljava/lang/invoke/MethodHandle;Ljava/lang/invoke/MethodType;)Ljava/lang/invoke/CallSite;',reference_kind=6),arguments=[
            dict(tag=16,value='(Ljava/lang/Object;)D'),
            dict(tag=15,value='SELF.lambda$ordered$0(DDDLnet/minecraft/world/entity/Entity;)D',reference_kind=6),
            dict(tag=16,value='(Lnet/minecraft/world/entity/Entity;)D')])}

    def test_query_preserves_exact_xyz_recipient_and_native_squared_distance(self):
        descriptor='(DDDLnet/minecraft/world/entity/Entity;)D'
        self.assertEqual(forwarding_shape('x/Q.class','arbitrary',descriptor,4106,self.query()),
                         dict(kind='EXACT_NATIVE_DISTANCE_QUERY'))
        for n,field,value in [(0,'local_index',4),(1,'local_index',2),
                              (4,'operand','net/minecraft/world/entity/Entity.distanceTo(DDD)D')]:
            b=self.query();b[n][field]=value
            self.assertIsNone(forwarding_shape('x/Q.class','arbitrary',descriptor,4106,b))
        for i in [ins('0xb6','x/Combat.hurt()V'),ins('0xb4','x/Q.stateI'),ins('0x99')]:
            b=self.query();b.insert(0,i)
            self.assertIsNone(forwarding_shape('x/Q.class','arbitrary',descriptor,4106,b))

    def test_factory_requires_exact_typed_static_same_class_bootstrap(self):
        shape=lambda b: forwarding_shape('x/Q.class','arbitrary','(DDD)Ljava/util/Comparator;',0,self.factory(),bootstraps=b)
        self.assertEqual(shape(self.bootstrap()),dict(kind='EXACT_NATIVE_DISTANCE_COMPARATOR_FACTORY',
                         target=dict(entry='x/Q.class',method='lambda$ordered$0',descriptor='(DDDLnet/minecraft/world/entity/Entity;)D')))
        self.assertIsNone(shape({}))
        for field,value in [('reference_kind',5),('tag',16),('value','x/Other.lambda$ordered$0(DDDLnet/minecraft/world/entity/Entity;)D')]:
            b=self.bootstrap();b['3']['arguments'][1][field]=value;self.assertIsNone(shape(b))
        b=self.bootstrap();b['3']['arguments'][2]['value']='(Ljava/lang/Object;)D';self.assertIsNone(shape(b))

    def test_handlers_and_changed_factory_locals_are_not_pure_proofs(self):
        b=self.factory();b[2]['local_index']=3
        self.assertIsNone(forwarding_shape('x/Q.class','x','(DDD)Ljava/util/Comparator;',0,b,bootstraps=self.bootstrap()))
        self.assertIsNone(forwarding_shape('x/Q.class','x','(DDD)Ljava/util/Comparator;',0,self.factory(),[(0,1,2,3)],self.bootstrap()))

    def test_independent_jdk_lambda_and_side_effect_fixture(self):
        from native_evidence import annotate_local_operands
        from compare_native_methods import bootstrap_signature,referenced_bootstraps
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);e=root/'net/minecraft/world/entity/Entity.java';e.parent.mkdir(parents=True)
            e.write_text('package net.minecraft.world.entity; public class Entity { public double distanceToSqr(double x,double y,double z) { return x*x+y*y+z*z; } public void hurt() {} }')
            q=root/'QueryFixture.java';q.write_text('import java.util.Comparator; import net.minecraft.world.entity.Entity; public class QueryFixture { Comparator<Entity> ordered(double x,double y,double z) { return Comparator.comparingDouble(e -> e.distanceToSqr(x,y,z)); } Comparator<Entity> harmful(double x,double y,double z) { return Comparator.comparingDouble(e -> { e.hurt(); return e.distanceToSqr(x,y,z); }); } }')
            subprocess.run([shutil.which('javac'),str(e),str(q)],check=True,capture_output=True)
            c=ClassFile(q.with_suffix('.class').read_bytes(),retain_code_metadata=True)
            shapes={}
            for m in c.methods:
                body=annotate_local_operands(list(c.instructions(m.get('code',b''))),m.get('code',b''))
                bs={str(n):bootstrap_signature(c,n) for n in referenced_bootstraps(body)}
                shapes[m['name']]=forwarding_shape('QueryFixture.class',m['name'],m['descriptor'],m['access'],body,m['exception_handlers'],bs)
            self.assertEqual(shapes['ordered']['kind'],'EXACT_NATIVE_DISTANCE_COMPARATOR_FACTORY')
            self.assertEqual(next(v['kind'] for k,v in shapes.items() if k.startswith('lambda$ordered$')),'EXACT_NATIVE_DISTANCE_QUERY')
            self.assertIsNone(next(v for k,v in shapes.items() if k.startswith('lambda$harmful$')))


class ModelAssetShapeTests(unittest.TestCase):
    def body(self):
        return [ins('0x12','arphex:geo/native_actor.geo.json'),
                ins('0xb8','net/minecraft/resources/ResourceLocation.parse(Ljava/lang/String;)Lnet/minecraft/resources/ResourceLocation;'),ins('0xb0')]

    def shape(self,body=None,name='getModelResource',superclass='software/bernie/geckolib/model/GeoModel'):
        return forwarding_shape('x/Model.class',name,'(Lx/Actor;)Lnet/minecraft/resources/ResourceLocation;',1,body or self.body(),superclass=superclass)

    def test_exact_constant_asset_selector_requires_native_api_superclass(self):
        self.assertEqual(self.shape(),dict(kind='EXACT_GECKO_MODEL_ASSET_QUERY',asset_identifier='arphex:geo/native_actor.geo.json'))
        self.assertIsNone(self.shape(superclass='x/Combat'))
        self.assertIsNone(self.shape(name='getDamageType'))

    def test_stateful_missing_namespace_or_nonasset_queries_remain_pending(self):
        for identifier in ['arphex:damage_type/attack.json','arphex:geo/../attack.geo.json','geo/native_actor.geo.json']:
            b=self.body();b[0]['operand']=identifier;self.assertIsNone(self.shape(b))
        b=self.body();b.insert(0,ins('0xb5','x/Actor.stateI'));self.assertIsNone(self.shape(b))
        b=self.body();b[1]['operand']='x/Combat.registry(Ljava/lang/String;)Lnet/minecraft/resources/ResourceLocation;';self.assertIsNone(self.shape(b))

    def test_independent_compiled_selector_has_no_actor_or_state_access(self):
        from native_evidence import annotate_local_operands
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);r=root/'net/minecraft/resources/ResourceLocation.java';r.parent.mkdir(parents=True)
            r.write_text('package net.minecraft.resources; public class ResourceLocation { public static ResourceLocation parse(String s) { return new ResourceLocation(); } }')
            g=root/'software/bernie/geckolib/model/GeoModel.java';g.parent.mkdir(parents=True)
            g.write_text('package software.bernie.geckolib.model; public abstract class GeoModel<T> { public abstract net.minecraft.resources.ResourceLocation getModelResource(T t); }')
            m=root/'AssetFixture.java';m.write_text('import software.bernie.geckolib.model.GeoModel; import net.minecraft.resources.ResourceLocation; public class AssetFixture extends GeoModel<String> { public ResourceLocation getModelResource(String t) { return ResourceLocation.parse("fixture:geo/actor.geo.json"); } }')
            subprocess.run([shutil.which('javac'),str(r),str(g),str(m)],check=True,capture_output=True)
            c=ClassFile(m.with_suffix('.class').read_bytes(),retain_code_metadata=True)
            method=next(m for m in c.methods if m['name']=='getModelResource' and not m['access']&0x40)
            b=annotate_local_operands(list(c.instructions(method['code'])),method['code'])
            shape=forwarding_shape('AssetFixture.class',method['name'],method['descriptor'],method['access'],b,method['exception_handlers'],superclass=c.super)
            self.assertEqual(shape['asset_identifier'],'fixture:geo/actor.geo.json')


class NativeModelAssetRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.census=read_json(OUT/'arphex-combat-census.json')
        cls.document=read_json(OUT/'arphex-native-model-asset-registry.json')

    def test_exact_selector_and_bridge_counts_without_native_payloads(self):
        rows=validate(self.document,self.census,set())
        self.assertEqual(self.document['summary']['counts_by_kind'],
                         {'EXACT_COMPILER_BRIDGE':251,'EXACT_GECKO_MODEL_ASSET_QUERY':251})
        self.assertEqual(len(rows),502)
        self.assertFalse(any('scalable_parameter_candidates' in r for r in rows))

    def test_forged_asset_identity_or_parent_is_rejected(self):
        for field,value in [('asset_identifier','arphex:geo/other.geo.json'),('superclass','x/Combat')]:
            d=copy.deepcopy(self.document);r=next(r for r in d['rows'] if r['kind']=='EXACT_GECKO_MODEL_ASSET_QUERY');r[field]=value
            with self.assertRaises(AssertionError):validate(d,self.census,set())

    def test_bridge_requires_its_actual_selector_not_a_capture_label(self):
        d=copy.deepcopy(self.document);r=next(r for r in d['rows'] if r['kind']=='EXACT_GECKO_MODEL_ASSET_QUERY');d['rows'].remove(r)
        remaining={r['instruction_template'] for r in d['rows']};d['instruction_templates']={k:v for k,v in d['instruction_templates'].items() if k in remaining}
        with self.assertRaisesRegex(AssertionError,'Bridge target lacks prior'):
            validate(d,self.census,set())


class NativeForwardingRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.census=read_json(OUT/'arphex-combat-census.json')
        cls.review=read_json(OUT/'mod-reviews/arphex.json')
        cls.document=read_json(OUT/'arphex-native-forwarding-registry.json')
        prior=copy.deepcopy(cls.review)
        prior['reviewed_batches']=[f for f in prior['reviewed_batches'] if f!='arphex-r2m6w-exact-native-forwarding.json']
        cls.index,_=reconcile(prior,cls.census)
        cls.covered={(m['entry'],m['method'],m['descriptor']) for m in cls.index['methods']}

    def test_exact_finite_context_counts_and_method_hashes(self):
        rows=validate(self.document,self.census,self.covered)
        self.assertEqual(len(rows),1383)
        self.assertEqual(self.document['summary']['counts_by_kind'],
                         {'EMPTY_STATIC_VOID_HELPER':18,'EXACT_COMPILER_BRIDGE':2,'OBJECT_ONLY_CONTEXT_CONSTRUCTOR':1363})
        self.assertTrue(all(byte_hash(bytes.fromhex(r['code_hex']))==r['code_sha256'] for r in rows))

    def test_bridge_cannot_self_prove_from_capture_or_cyclic_targets(self):
        with self.assertRaisesRegex(AssertionError,'Bridge target lacks prior'):
            validate(self.document,self.census,set())

    def test_forged_method_class_hash_or_duplicate_row_is_rejected(self):
        for field in ['code_sha256','entry_sha256','code_hex']:
            d=copy.deepcopy(self.document);d['rows'][0][field]='00'
            with self.assertRaises(AssertionError):validate(d,self.census,self.covered)
        d=copy.deepcopy(self.document);d['rows'].append(d['rows'][0])
        with self.assertRaises(AssertionError):validate(d,self.census,self.covered)

    def test_queue_reduction_grants_no_new_semantic_record_or_scalar(self):
        rows=validate(self.document,self.census,self.covered)
        self.assertFalse(any('scalable_parameter_candidates' in r for r in rows))
        self.assertFalse(any('effects' in r for r in rows))
        self.assertTrue(all(r['kind']!='FIELD_ACCESS_CONTEXT' for r in rows))

    def test_audit_index_uses_one_canonical_relative_file_identity(self):
        from audit_catalog_integrity import EvidenceIndex
        i=EvidenceIndex();name='arphex-native-forwarding-registry.json'
        self.assertIs(i.read(name),i.read(OUT/name))
        self.assertEqual(set(i.file_hashes),{name})


class NativeDistanceOrderingRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.census=read_json(OUT/'arphex-combat-census.json')
        cls.document=read_json(OUT/'arphex-native-distance-ordering-registry.json')

    def test_every_factory_has_exact_pure_query_and_no_new_scalar(self):
        rows=validate(self.document,self.census,set())
        self.assertEqual(len(rows),1026)
        self.assertEqual(self.document['summary']['counts_by_kind'],
                         {'EXACT_NATIVE_DISTANCE_COMPARATOR_FACTORY':513,'EXACT_NATIVE_DISTANCE_QUERY':513})
        self.assertEqual(len(self.document['instruction_templates']),2)
        for r in rows:
            self.assertNotIn('effects',r);self.assertNotIn('scalable_parameter_candidates',r)
            if r['kind']=='EXACT_NATIVE_DISTANCE_QUERY':
                b=self.document['instruction_templates'][r['instruction_template']]
                self.assertEqual([i['operand'] for i in b if i['opcode'].startswith('0xb')],
                                 ['net/minecraft/world/entity/Entity.distanceToSqr(DDD)D'])

    def test_factory_cannot_borrow_coverage_or_captured_harmful_target(self):
        d=copy.deepcopy(self.document)
        query=next(r for r in d['rows'] if r['kind']=='EXACT_NATIVE_DISTANCE_QUERY')
        d['rows'].remove(query)
        with self.assertRaisesRegex(AssertionError,'lacks exact pure-query'):
            validate(d,self.census,{(query['entry'],query['method'],query['descriptor'])})

    def test_bootstrap_cannot_be_replaced_by_foreign_or_instance_consumer(self):
        for value in [('reference_kind',5),('value','OTHER.lambda$compareDistOf$0(DDDLnet/minecraft/world/entity/Entity;)D')]:
            d=copy.deepcopy(self.document)
            r=next(r for r in d['rows'] if r['kind']=='EXACT_NATIVE_DISTANCE_COMPARATOR_FACTORY')
            next(iter(r['bootstraps'].values()))['arguments'][1][value[0]]=value[1]
            with self.assertRaises(AssertionError):validate(d,self.census,set())

    def test_finite_census_exclusions_leave_all_caller_methods_separate(self):
        review=read_json(OUT/'mod-reviews/arphex.json')
        index,pending=reconcile(review,self.census)
        batch='arphex-r2m6y-exact-native-distance-ordering.json'
        if batch not in review['reviewed_batches']:
            review['reviewed_batches'].append(batch);index,pending=reconcile(review,self.census)
        keys={(m['entry'],m['method'],m['descriptor']) for m in self.document['rows']}
        indexed={ (m['entry'],m['method'],m['descriptor']):m for m in index['methods']}
        self.assertTrue(keys<=set(indexed))
        self.assertTrue(all(m['method'] in ('compareDistOf','lambda$compareDistOf$0') for m in self.document['rows']))
        self.assertTrue(all(not indexed[k]['record_ids'] for k in keys))
        self.assertTrue(all(p['kind']=='REVIEWED_EXCLUSION' for k in keys for p in indexed[k]['proofs']))


class JdkCodeMetadataTests(unittest.TestCase):
    def test_exception_table_matches_independent_compiled_fixture(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'ContextFixture.java'
            p.write_text('public class ContextFixture { public int guarded(int n) { '
                         'try { return 8/n; } catch (ArithmeticException e) { return 0; } } }')
            subprocess.run([shutil.which('javac'),str(p)],check=True,capture_output=True)
            raw=p.with_suffix('.class').read_bytes()
            default=ClassFile(raw)
            self.assertTrue(all('exception_handlers' not in m for m in default.methods))
            parsed=ClassFile(raw,retain_code_metadata=True)
            m=next(m for m in parsed.methods if m['name']=='guarded')
            self.assertEqual(len(m['exception_handlers']),1)
            start,end,target,cp=m['exception_handlers'][0]
            self.assertTrue(0<=start<end<=len(m['code']))
            self.assertTrue(0<=target<len(m['code']))
            self.assertEqual(parsed.resolve(cp),'java/lang/ArithmeticException')


if __name__=='__main__':unittest.main()
