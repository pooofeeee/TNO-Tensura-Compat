"""Evaluate exact native armor predicates with explicit static input fixtures.

Only the bounded armor interval is interpreted. Unsupported calls/opcodes fail;
no Minecraft classes execute and this is not a simulated game/runtime test.
"""
import re,math,unittest
from copy import deepcopy
from catalog_common import OUT,read_json
W=next(w for w in read_json(OUT/'native-evidence/arphex-global-hooks.json')['witnesses'] if w['entry'].endswith('/DwellerLifestealProcedure.class'))
M=next(m for m in W['methods'] if m['name']=='execute' and 'Lnet/neoforged/bus/api/Event;' in m['descriptor'])
B={i['offset']:i for i in M['instructions']};offsets=sorted(B);following=dict(zip(offsets,offsets[1:]))

def types(s):
    return re.findall(r'\[*L[^;]+;|\[*[ZBCSIJFD]',s)

def trace(armor,amount=6):
    victim=dict(kind='Entity',role='victim',armor=armor);source=dict(kind='Entity',role='source',armor={})
    locals={0:dict(kind='Event'),1:dict(kind='World'),2:0.,4:0.,6:0.,9:victim,11:source,12:amount}
    stack=[];actions=[];pc=17342;steps=0
    def invoke(operand,args,receiver=None):
        owner,name=operand.split('(')[0].rsplit('.',1)
        if name=='<init>':receiver['args']=args;return None
        if name=='getItemBySlot':return dict(kind='ItemStack',item=receiver['armor'].get(args[0],'AIR'))
        if name=='getItem':return receiver['item']
        if name=='get':return receiver
        if name in ('level','getServer','getCommands'):return dict(kind='World')
        if name=='isClientSide':return False
        if name=='nextInt':return args[-1]
        if name=='create' and owner=='net/minecraft/util/RandomSource':return dict(kind='Random')
        if name in ('getYRot','getXRot','getX','getY','getZ'):return 0.
        if name=='hasEffect':return False
        if name=='setDeltaMovement':actions.append((pc,'movement',receiver['role'],args[0]['args']));return None
        if name=='addEffect':actions.append((pc,'effect',receiver['role'],args[0]['args']));return True
        if name=='igniteForSeconds':actions.append((pc,'burn',receiver['role'],args[0]));return None
        if name=='setCanceled':actions.append((pc,'cancel',args[0]));return None
        if name in ('parse','containing','literal'):return dict(kind=name,args=args)
        if name in ('playSound','playLocalSound'):return None
        if owner=='java/lang/Math' and name in ('sin','cos','abs'):return getattr(math,name)(*args)
        raise AssertionError(('unsupported native call',pc,operand))
    while pc<22300:
        steps+=1;assert steps<4000
        i=B[pc];op=int(i['opcode'],16);nextpc=following[pc];value=i['operand']
        if op==1:stack.append(None)
        elif 2<=op<=0x14:stack.append(value)
        elif 0x15<=op<=0x19:stack.append(locals[i['local_index']])
        elif 0x1a<=op<=0x2d:stack.append(locals[(op-0x1a)%4])
        elif 0x36<=op<=0x3a:locals[i['local_index']]=stack.pop()
        elif 0x3b<=op<=0x4e:locals[(op-0x3b)%4]=stack.pop()
        elif op==0x57:stack.pop()
        elif op==0x59:stack.append(stack[-1])
        elif op in (0x60,0x62,0x63,0x64,0x66,0x67,0x68,0x6a,0x6b,0x6c,0x6e,0x6f):
            b=stack.pop();a=stack.pop()
            stack.append(a+b if op<=0x63 else a-b if op<=0x67 else a*b if op<=0x6b else a/b)
        elif op in (0x85,0x86,0x87,0x89,0x8a,0x8b,0x8c,0x8d,0x8e,0x8f,0x90):pass
        elif op in (0x95,0x96,0x97,0x98):
            b=stack.pop();a=stack.pop();stack.append((a>b)-(a<b))
        elif 0x99<=op<=0x9e:
            a=stack.pop();condition=[a==0,a!=0,a<0,a>=0,a>0,a<=0][op-0x99]
            if condition:nextpc=i['branch_target']
        elif 0x9f<=op<=0xa6:
            b=stack.pop();a=stack.pop();condition=[a==b,a!=b,a<b,a>=b,a>b,a<=b,a==b,a!=b][op-0x9f]
            if condition:nextpc=i['branch_target']
        elif op==0xa7:nextpc=i['branch_target']
        elif op==0xb2:
            owner,field=value.rsplit('.',1);name=field.partition('Lnet/')[0]
            if owner=='net/minecraft/world/entity/EquipmentSlot':stack.append(name)
            elif owner=='net/minecraft/world/item/ItemStack':stack.append(dict(kind='ItemStack',item='AIR'))
            elif owner=='net/minecraft/core/registries/BuiltInRegistries':stack.append(dict(kind='Registry'))
            else:stack.append(value)
        elif op==0xb4:
            obj=stack.pop();stack.append(dict(kind='World') if '.connection' in value else obj[value])
        elif op in (0xb6,0xb7,0xb8,0xb9):
            descriptor=value[value.index('('):];n=len(types(descriptor.split(')')[0][1:]));args=stack[-n:] if n else []
            if n:del stack[-n:]
            receiver=None if op==0xb8 else stack.pop()
            result=invoke(value,args,receiver)
            if descriptor.split(')')[1]!='V':stack.append(result)
        elif op==0xbb:stack.append(dict(kind=value))
        elif op==0xc0:pass
        elif op==0xc1:
            obj=stack.pop();stack.append(bool(obj) and ((value.endswith('/LivingEntity') and obj['kind']=='Entity') or (value.endswith('/ICancellableEvent') and obj['kind']=='Event') or (value.endswith('/Level') and obj['kind']=='World')))
        else:raise AssertionError(('unsupported opcode',pc,i))
        pc=nextpc
    return actions


class ArmorReactionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m2h-incoming-armor-state.json')

    def outfit(self,family,mask=15):
        return {slot:f'net/arphex/init/ArphexModItems.{family}_{item}Lnet/neoforged/neoforge/registries/DeferredItem;'
                for n,(slot,item) in enumerate(zip(['HEAD','CHEST','LEGS','FEET'],['HELMET','CHESTPLATE','LEGGINGS','BOOTS'])) if mask&(1<<n)}

    def test_all_sixteen_infernal_predicates_against_native_branches(self):
        for mask in range(16):
            with self.subTest(mask=mask):
                moves=[a for a in trace(self.outfit('INFERNAL',mask)) if a[1]=='movement']
                count=mask.bit_count()
                if not count:self.assertEqual(moves,[]);continue
                divisor={1:8,2:6,3:4,4:2}[count]
                self.assertEqual(len(moves),1)
                self.assertEqual(moves[0][2],'source')
                self.assertAlmostEqual(moves[0][3][2],-1/divisor)
                self.assertEqual(moves[0][3][1],.6)

    def test_full_eternal_immortal_preserve_two_independent_reactions(self):
        for family in ['ETERNAL','IMMORTAL']:
            actions=trace(self.outfit(family))
            self.assertEqual([a[0] for a in actions if a[1]=='movement'],[17724,20939])
            self.assertEqual([a[0] for a in actions if a[1]=='burn'],[17777,20742])
            self.assertTrue(any(a[1]=='effect' and a[2]=='source' and a[3][1:]==[30,1] for a in actions))
        for family in ['UMBRAL','SPECTRAL','SPACETIME']:
            self.assertEqual([a[0] for a in trace(self.outfit(family)) if a[1]=='movement'],[20939])

    def test_small_request_cancellation_and_native_reactions_both_continue(self):
        actions=trace(self.outfit('IMMORTAL'),amount=1)
        self.assertEqual(sum(a[1]=='cancel' for a in actions),3)
        self.assertEqual(sum(a[1]=='movement' for a in actions),2)
        self.assertTrue(any(a[1]=='effect' and a[2]=='victim' and a[3][1:]==[10,1,0,0] for a in actions))

    def test_effect_recipients_and_order_are_native_local_bindings(self):
        from promote_combat_batch import effect_receiver_binding
        for offset,local in [(17765,11),(17829,9),(20393,11),(20604,11),(20832,11),
                             (22603,9),(22788,9),(22888,9),(22933,9),(23729,11),
                             (24495,11),(24554,11),(24613,11)]:
            self.assertEqual(effect_receiver_binding(M,offset)['origin_local_index'],local)
        self.assertLess(23017,23225)
        self.assertEqual(B[23225]['operand'],'net/minecraft/world/entity/Entity.setDeltaMovement(Lnet/minecraft/world/phys/Vec3;)V')
        row=next(r for r in self.batch['effects'] if r['id']=='arphex:fly_festerer_incoming_dodge')
        self.assertEqual(row['scalable_parameter_candidates'][0]['parameters'],['horizontal_min','horizontal_max'])
        self.assertEqual(row['superseded_native_contributions'][0]['overwriter_offset'],23225)

    def test_first_teleport_is_followed_by_a_fresh_position_read(self):
        for first,second in [(18331,18381),(18739,18789),(19147,19197),(19555,19605)]:
            window=[i for i in M['instructions'] if first<i['offset']<second]
            self.assertTrue(any('Entity.getX()' in str(i['operand']) for i in window))
            self.assertTrue(any('Entity.getZ()' in str(i['operand']) for i in window))
            self.assertIn('teleportTo(DDD)',B[first]['operand'])
            self.assertIn('teleport(DDDFF)',B[second]['operand'])

    def test_raw_native_markers_are_not_mistaken_for_active_callbacks(self):
        w=next(w for w in read_json(OUT/'native-evidence/arphex-status-core.json')['witnesses'] if w['entry'].endswith('/SpiderSilkTouchMobEffect.class'))
        self.assertEqual(w['superclass'],'net/minecraft/world/effect/InstantenousMobEffect')
        self.assertEqual({m['name'] for m in w['methods']},{'<init>','registerMobEffectExtensions'})
        marker=next(r for r in self.batch['effects'] if r['id']=='arphex:goliath_funnel_incoming_silk_marker')
        self.assertEqual(marker['scalable_parameter_candidates'],[])

    def test_resume_boundary_is_a_real_instruction_not_an_operand_byte(self):
        from classfile import ClassFile
        import zipfile,hashlib
        from pathlib import Path
        jar=Path('/workspace/.cache/large-mod-campaign/ArPhEx-5.0.2-neoforge-1.21.1.jar')
        if not jar.exists():self.skipTest('Pinned archive not available')
        with zipfile.ZipFile(jar) as z:data=z.read(W['entry'])
        self.assertEqual(hashlib.sha256(data).hexdigest(),W['entry_sha256'])
        method=next(m for m in ClassFile(data).methods if m['name']=='execute' and 'Lnet/neoforged/bus/api/Event;' in m['descriptor'])
        self.assertEqual(method['code'][17342:17344],bytes([0x19,9]))
        self.assertNotIn(17343,B)
        self.assertEqual(B[24620]['local_index'],11)
        self.assertIn('offset17342',read_json(OUT/'arphex-r2m2g-reactive-arrow-control.json')['exact_next_task'])
        self.assertIn('offset24620',self.batch['exact_next_task'])

    def test_batch_uses_exact_consumers_without_recounting_old_records(self):
        from promote_combat_batch import validate_batch
        review=deepcopy(read_json(OUT/'mod-reviews/arphex.json'));ids={r['id'] for r in self.batch['effects']}
        review['effects']=[r for r in review['effects'] if r['id'] not in ids]
        review['paths']=[p for p in review['paths'] if not set(p['effect_ids'])&ids]
        self.assertEqual(len(ids),10)
        validate_batch(self.batch,review,read_json(OUT/'arphex-combat-census.json'))


if __name__=='__main__':
    unittest.main()
