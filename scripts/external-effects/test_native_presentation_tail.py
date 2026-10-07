"""Exact native geometry consumers, render arguments and client registrations."""
import copy
import unittest
from catalog_common import OUT,read_json
from reconcile_native_census import reconcile
from promote_combat_batch import validate_batch


class NativePresentationTailTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b=read_json(OUT/'arphex-r2m7l-native-presentation-tail.json')
        cls.e=read_json(OUT/'native-evidence/arphex-native-presentation-tail.json')
        cls.c=read_json(OUT/'arphex-combat-census.json')
        cls.w={w['entry']:w for w in cls.e['witnesses']}

    def method(self,entry,name):
        return next(m for m in self.w[entry]['methods'] if m['name']==name)

    def test_minimum_scope_changes_no_gameplay_semantic_or_scalar_record(self):
        self.assertEqual(len(self.w),39)
        self.assertEqual(sum(len(w['methods']) for w in self.w.values()),138)
        self.assertEqual(self.b['effects'],[]);self.assertEqual(self.b['paths'],[])
        self.assertEqual(len(self.b['native_geometry_models']),14)
        self.assertEqual(len(self.b['native_entity_renderer_bindings']),23)
        self.assertEqual(len(self.b['native_item_render_context']),1)
        d=read_json(OUT/self.b['native_forwarding_registry_file'])
        self.assertEqual(d['summary'],dict(methods=40,counts_by_kind={'EXACT_COMPILER_BRIDGE':40}))
        r=read_json(OUT/'mod-reviews/arphex.json')
        r['reviewed_batches']=[f for f in r['reviewed_batches'] if f!='arphex-r2m7l-native-presentation-tail.json']
        self.assertEqual(validate_batch(self.b,r,self.c)['semantic_records'],len(r['effects']))

    def test_mesh_geometry_calls_only_native_visual_builders(self):
        allowed={
            'net/minecraft/client/model/geom/PartPose.offset(FFF)Lnet/minecraft/client/model/geom/PartPose;',
            'net/minecraft/client/model/geom/PartPose.offsetAndRotation(FFFFFF)Lnet/minecraft/client/model/geom/PartPose;',
            'net/minecraft/client/model/geom/builders/CubeDeformation.<init>(F)V',
            'net/minecraft/client/model/geom/builders/CubeListBuilder.addBox(FFFFFFLnet/minecraft/client/model/geom/builders/CubeDeformation;)Lnet/minecraft/client/model/geom/builders/CubeListBuilder;',
            'net/minecraft/client/model/geom/builders/CubeListBuilder.create()Lnet/minecraft/client/model/geom/builders/CubeListBuilder;',
            'net/minecraft/client/model/geom/builders/CubeListBuilder.mirror()Lnet/minecraft/client/model/geom/builders/CubeListBuilder;',
            'net/minecraft/client/model/geom/builders/CubeListBuilder.mirror(Z)Lnet/minecraft/client/model/geom/builders/CubeListBuilder;',
            'net/minecraft/client/model/geom/builders/CubeListBuilder.texOffs(II)Lnet/minecraft/client/model/geom/builders/CubeListBuilder;',
            'net/minecraft/client/model/geom/builders/LayerDefinition.create(Lnet/minecraft/client/model/geom/builders/MeshDefinition;II)Lnet/minecraft/client/model/geom/builders/LayerDefinition;',
            'net/minecraft/client/model/geom/builders/MeshDefinition.<init>()V',
            'net/minecraft/client/model/geom/builders/MeshDefinition.getRoot()Lnet/minecraft/client/model/geom/builders/PartDefinition;',
            'net/minecraft/client/model/geom/builders/PartDefinition.addOrReplaceChild(Ljava/lang/String;Lnet/minecraft/client/model/geom/builders/CubeListBuilder;Lnet/minecraft/client/model/geom/PartPose;)Lnet/minecraft/client/model/geom/builders/PartDefinition;'}
        for model in self.b['native_geometry_models']:
            entry=model['entry'];w=self.w[entry]
            self.assertEqual(w['superclass'],'net/minecraft/client/model/EntityModel')
            b=self.method(entry,'createBodyLayer')['instructions']
            self.assertFalse(any(i['opcode'] in ('0xb3','0xb5') for i in b))
            self.assertTrue(all(i['operand'] in allowed for i in b if i['opcode'] in ('0xb6','0xb7','0xb8','0xb9')))
            self.assertEqual([i['opcode'] for i in self.method(entry,'setupAnim')['instructions']],['0xb1'])

    def test_model_fields_and_draw_calls_are_model_parts_not_entity_state(self):
        for model in self.b['native_geometry_models']:
            entry=model['entry'];init=self.method(entry,'<init>')['instructions']
            writes=[i['operand'] for i in init if i['opcode']=='0xb5']
            self.assertTrue(writes)
            self.assertTrue(all(s.startswith(entry[:-6]+'.') and s.endswith('Lnet/minecraft/client/model/geom/ModelPart;') for s in writes))
            b=self.method(entry,'renderToBuffer')['instructions']
            self.assertFalse(any(i['opcode'] in ('0xb3','0xb5') for i in b))
            self.assertTrue(all(i['operand']=='net/minecraft/client/model/geom/ModelPart.render(Lcom/mojang/blaze3d/vertex/PoseStack;Lcom/mojang/blaze3d/vertex/VertexConsumer;III)V' for i in b if i['opcode'] in ('0xb6','0xb7','0xb8','0xb9')))

    def test_client_registration_references_all_exact_mesh_suppliers(self):
        entry='net/arphex/init/ArphexModModels.class';w=self.w[entry]
        self.assertTrue(any(a['values'].get('value')==[{'enum_type':'Lnet/neoforged/api/distmarker/Dist;','constant':'CLIENT'}]
                            and a['values'].get('bus',{}).get('constant')=='MOD' for a in w['annotations']))
        m=self.method(entry,'registerLayerDefinitions')
        self.assertTrue(any('SubscribeEvent' in a['descriptor'] for a in m['annotations']))
        self.assertEqual(sum('registerLayerDefinition(' in str(i['operand']) for i in m['instructions']),14)
        original=[dict(entry=b['entry'],index=b['index'],handle=b['handle'],arguments=b['arguments']) for b in self.c['registration_bootstraps'] if b['entry']==entry]
        self.assertEqual(original,self.b['native_model_layer_registration_handles'])
        suppliers={a.split('.createBodyLayer')[0]+'.class' for b in original for a in b['arguments']
                   if isinstance(a,str) and '.createBodyLayer' in a}
        self.assertEqual(suppliers,{x['entry'] for x in self.b['native_geometry_models']})

    def test_projectile_model_draw_reads_actor_rotation_but_never_writes_it(self):
        draws=0
        for renderer in self.b['native_entity_renderer_bindings']:
            entry=renderer['entry'];methods=self.w[entry]['methods']
            ctor=self.method(entry,'<init>')['instructions']
            actual=[i['operand'] for i in ctor if i['opcode']=='0xb7' and '/model/' in str(i['operand']) and '.<init>' in str(i['operand'])]
            self.assertEqual(actual,renderer['native_model_constructors'])
            for m in methods:
                if m['name']!='render':continue
                draws+=1;b=m['instructions']
                self.assertFalse(any(i['opcode'] in ('0xb3','0xb5') for i in b))
                self.assertEqual(sum('PoseStack.pushPose()' in str(i['operand']) for i in b),1)
                self.assertEqual(sum('PoseStack.popPose()' in str(i['operand']) for i in b),1)
                self.assertEqual(sum('PoseStack.mulPose(' in str(i['operand']) for i in b),2)
                self.assertEqual([i.get('local_index') for i in b[-9:-2]],list(range(7)))
                self.assertTrue(b[-2]['operand'].startswith('net/minecraft/client/renderer/entity/EntityRenderer.render('))
        self.assertEqual(draws,4)

    def test_item_renderer_forwards_original_arguments_and_only_caches_draw_state(self):
        entry=self.b['native_item_render_context'][0]['entry']
        b=self.method(entry,'actuallyRender')['instructions']
        at=next(n for n,i in enumerate(b) if i['opcode']=='0xb7')
        self.assertEqual([i.get('local_index') for i in b[at-12:at]],list(range(12)))
        fields={i['operand'] for i in b if i['opcode']=='0xb5'}
        self.assertTrue(all(f.startswith(entry[:-6]+'.') for f in fields))
        self.assertEqual({f[len(entry[:-6])+1:] for f in fields},{'currentBufferLnet/minecraft/client/renderer/MultiBufferSource;',
            'renderTypeLnet/minecraft/client/renderer/RenderType;','animatableLnet/arphex/item/SingularityScytheItem;','renderArmsZ'})
        b=self.method(entry,'renderByItem')['instructions']
        self.assertEqual([i.get('local_index') for i in b[-9:-2]],list(range(7)))
        self.assertTrue(b[-2]['operand'].startswith('software/bernie/geckolib/renderer/GeoItemRenderer.renderByItem('))

    def test_missing_target_proof_or_changed_native_hash_cannot_close(self):
        r=read_json(OUT/'mod-reviews/arphex.json');r['reviewed_batches']=[f for f in r['reviewed_batches'] if f!='arphex-r2m7l-native-presentation-tail.json']
        b=copy.deepcopy(self.b);b['exclusions']=[]
        with self.assertRaisesRegex(AssertionError,'target lacks prior'):validate_batch(b,r,self.c)
        r['reviewed_batches'].append('arphex-r2m7l-native-presentation-tail.json')
        e=copy.deepcopy(self.e);e['witnesses'][0]['methods'][0]['code_sha256']='0'*64
        def read(path):
            return e if str(path.relative_to(OUT))=='native-evidence/arphex-native-presentation-tail.json' else read_json(path)
        with self.assertRaisesRegex(AssertionError,'hash mismatch'):reconcile(r,self.c,read=read)


if __name__=='__main__':unittest.main()
