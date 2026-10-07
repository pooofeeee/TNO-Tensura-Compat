"""Transport proof accepts original typed values, never state interpretation."""
import copy
import unittest
from native_forwarding import forwarding_shape, declared_field_exists, bind_parent_relay


def i(op, operand=None, slot=None):
    return dict(opcode=op, operand=operand, offset=0,
                **({'local_index': slot} if slot is not None else {}))


class StateTransportTests(unittest.TestCase):
    def query(self):
        return [i('0x2a', slot=0), i('0xb4', 'x/Actor.entityDataLnet/minecraft/network/syncher/SynchedEntityData;'),
                i('0xb2', 'x/Actor.STATE Lnet/minecraft/network/syncher/EntityDataAccessor;'.replace(' ', '')),
                i('0xb6', 'net/minecraft/network/syncher/SynchedEntityData.get(Lnet/minecraft/network/syncher/EntityDataAccessor;)Ljava/lang/Object;'),
                i('0xc0', 'java/lang/Integer'), i('0xb6', 'java/lang/Integer.intValue()I'), i('0xac')]

    def setter(self):
        return self.query()[:3] + [i('0x1b', slot=1), i('0xb8', 'java/lang/Integer.valueOf(I)Ljava/lang/Integer;'),
                i('0xb6', 'net/minecraft/network/syncher/SynchedEntityData.set(Lnet/minecraft/network/syncher/EntityDataAccessor;Ljava/lang/Object;)V'), i('0xb1')]

    def shape(self, body, descriptor='()I', flags=1):
        return forwarding_shape('x/Actor.class', 'anyName', descriptor, flags, body)

    def test_original_synched_accessor_query_and_write_require_declared_field(self):
        shape = self.shape(self.query())
        self.assertEqual(shape['kind'], 'RAW_DECLARED_FIELD_SYNCHED_QUERY')
        self.assertTrue(declared_field_exists(shape, {'fields': [dict(name='STATE',
                         descriptor='Lnet/minecraft/network/syncher/EntityDataAccessor;', access=0x1a)]}))
        self.assertFalse(declared_field_exists(shape, {'fields': []}))
        self.assertEqual(self.shape(self.setter(), '(I)V')['kind'], 'RAW_DECLARED_FIELD_SYNCHED_WRITE')

    def test_defaults_arithmetic_wrong_receiver_and_wrong_boxing_are_not_transport(self):
        for at, replacement in [(0, i('0x2b', slot=1)),
                                (1, i('0xb4', 'x/Other.entityDataLnet/minecraft/network/syncher/SynchedEntityData;')),
                                (2, i('0xb2', 'x/Other.STATELnet/minecraft/network/syncher/EntityDataAccessor;')),
                                (5, i('0xb6', 'java/lang/Integer.hashCode()I'))]:
            body = self.query(); body[at] = replacement
            self.assertIsNone(self.shape(body))
        for replacement in [i('0x3', 0), i('0x1c', slot=2), i('0xb8', 'x/Source.get()I')]:
            body = self.setter(); body[3] = replacement
            self.assertIsNone(self.shape(body, '(I)V'))
        body = self.setter(); body.insert(4, i('0x60'))
        self.assertIsNone(self.shape(body, '(I)V'))
        body = self.setter(); body[4]['operand'] = 'java/lang/Float.valueOf(F)Ljava/lang/Float;'
        self.assertIsNone(self.shape(body, '(I)V'))

    def test_object_query_retains_native_cast_and_original_value(self):
        body = self.query()[:4] + [i('0xc0', 'x/Mode'), i('0xb0')]
        self.assertEqual(self.shape(body, '()Lx/Mode;')['kind'], 'RAW_DECLARED_FIELD_SYNCHED_QUERY')
        body[4]['operand'] = 'x/Other'
        self.assertIsNone(self.shape(body, '()Lx/Mode;'))

    def test_compiler_field_access_requires_synthetic_typed_argument(self):
        body = [i('0x2a', slot=0), i('0xb4', 'x/Actor.cooldownI'), i('0xac')]
        self.assertEqual(self.shape(body, '(Lx/Actor;)I', 0x100a)['kind'], 'RAW_DECLARED_FIELD_ACCESS_QUERY')
        self.assertIsNone(self.shape(body, '(Lx/Actor;)I', 0xa))
        self.assertIsNone(self.shape(body, '(Lx/Other;)I', 0x100a))
        body = [i('0x2a', slot=0), i('0x1b', slot=1), i('0xb5', 'x/Actor.cooldownI'), i('0xb1')]
        self.assertEqual(self.shape(body, '(Lx/Actor;I)V', 0x100a)['kind'], 'RAW_DECLARED_FIELD_ACCESS_WRITE')
        body[1] = i('0x3', 0)
        self.assertIsNone(self.shape(body, '(Lx/Actor;I)V', 0x100a))

    def test_any_exception_branch_or_callback_refuses_transport(self):
        body = self.query()
        for extra in [i('0x99'), i('0xb8', 'x/Combat.hurt()V'), i('0xb5', 'x/Actor.healthF')]:
            changed = copy.deepcopy(body); changed.insert(2, extra)
            self.assertIsNone(self.shape(changed))
        self.assertIsNone(forwarding_shape('x/Actor.class', 'anyName', '()I', 1, body, [(0, 1, 2, 0)]))

    def test_parent_relay_preserves_wide_original_arguments_and_return(self):
        body=[i('0x2a',slot=0),i('0x1f',slot=1),i('0x2d',slot=3),
              i('0xb7','x/Parent.copy(JLx/Input;)Z'),i('0xac')]
        shape=forwarding_shape('x/Child.class','copy','(JLx/Input;)Z',1,body,superclass='x/Parent')
        self.assertEqual(shape['kind'],'ORIGINAL_ARGUMENT_PARENT_RELAY')
        for at,replacement in [(1,i('0x20',slot=2)),(2,i('0x3',0)),
                               (3,i('0xb6','x/Parent.copy(JLx/Input;)Z')),
                               (3,i('0xb7','x/Other.copy(JLx/Input;)Z'))]:
            wrong=copy.deepcopy(body);wrong[at]=replacement
            self.assertIsNone(forwarding_shape('x/Child.class','copy','(JLx/Input;)Z',1,wrong,superclass='x/Parent'))

    def test_constructor_or_callback_extra_state_is_not_a_parent_relay(self):
        body=[i('0x2a',slot=0),i('0x2b',slot=1),i('0xb7','net/minecraft/Parent.<init>(Lx/Input;)V'),i('0xb1')]
        shape=forwarding_shape('x/Child.class','<init>','(Lx/Input;)V',1,body,superclass='net/minecraft/Parent')
        self.assertEqual(bind_parent_relay(shape,dict(classes=[],methods=[])),shape)
        wrong=copy.deepcopy(body);wrong.insert(2,i('0xb5','x/Child.healthF'))
        self.assertIsNone(forwarding_shape('x/Child.class','<init>','(Lx/Input;)V',1,wrong,superclass='net/minecraft/Parent'))
        shape['parent_method_symbol']='missing/library/Parent.<init>(Lx/Input;)V'
        self.assertIsNone(bind_parent_relay(shape,dict(classes=[],methods=[])))

    def test_internal_parent_target_is_bound_not_self_proved(self):
        shape=dict(kind='ORIGINAL_ARGUMENT_PARENT_RELAY',parent_method_symbol='x/Parent.tick()V')
        census=dict(classes=[dict(name='x/Parent',superclass='net/minecraft/Parent')],
                    methods=[dict(entry='x/Parent.class',method='tick',descriptor='()V')])
        bound=bind_parent_relay(shape,census)
        self.assertEqual(bound['target'],dict(entry='x/Parent.class',method='tick',descriptor='()V'))


if __name__ == '__main__':
    unittest.main()
