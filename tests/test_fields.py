import unittest
from unittest.mock import patch

from paramap.types import MapObject, StringType, Parameter
from paramap.fields import (
    Field,
    Any,
    String,
    Bool,
    Integer,
    Float,
    Map,
    List,
    Nested,
)


class FieldTest(unittest.TestCase):

    def test_parameter_property(self):
        field = Field(
            StringType,
            param='TEST_PARAM',
            required=True,
            description='Parmeter description',
        )

        parameter = field.parameter

        self.assertEqual(field.param, parameter.name)
        self.assertEqual(StringType, parameter.type_class)
        self.assertTrue(parameter.required)
        self.assertEqual(field.description, parameter.description)

    def test_init_with_parameter(self):
        parameter = Parameter(name='TEST_PARAMETER')

        field = Field(StringType, param=parameter)

        self.assertEqual(field.param, parameter.name)
        self.assertFalse(field.required)

        field = Field(StringType, param=parameter, required=True)
        self.assertEqual(field.param, parameter.name)
        self.assertTrue(field.required)

        parameter.required = True
        field = Field(StringType, param=parameter, required=False)
        self.assertEqual(field.param, parameter.name)
        self.assertTrue(field.required)

        parameter.type_class = Any

        with self.assertRaises(ValueError):
            Field(StringType, param=parameter)


class AnyFieldTest(unittest.TestCase):

    def test_attrs(self):
        field = Any()

        self.assertTrue(hasattr(field, 'param'))
        self.assertTrue(hasattr(field, 'default'))

    def test_create(self):
        field = Any(param='test_param', default='test_default')

        self.assertTrue('test_param', field.param)
        self.assertTrue('test_default', field.default)

    def test_resolve_identity(self):
        field = Any()

        self.assertEqual(5, field.resolve(5))
        self.assertEqual('test_value', field.resolve('test_value'))

    def test_resolve_to_default(self):
        field = Any(default='test_default')

        self.assertEqual('5', field.resolve('5'))
        self.assertEqual('test_default', field.resolve(None))


class StringFieldTest(unittest.TestCase):

    def test_clean(self):
        field = String()

        self.assertEqual('5', field.clean(5))
        self.assertEqual('5.251', field.clean(5.251))
        self.assertEqual('test_value', field.clean('test_value'))

    def test_resolve_to_default(self):
        field = String(default='test_default')

        self.assertEqual('5', field.resolve('5'))
        self.assertEqual('test_default', field.resolve(None))


class BoolFieldTest(unittest.TestCase):

    def test_clean(self):
        field = Bool()

        self.assertTrue(field.clean(5))
        self.assertTrue(field.clean(5.251))
        self.assertTrue(field.clean('test_value'))

    def test_resolve_to_default(self):
        field = Bool(default=False)

        self.assertEqual(False, field.resolve(False))
        self.assertEqual(True, field.resolve(True))
        self.assertEqual(False, field.resolve(None))

        field = Bool(default=True)

        self.assertEqual(False, field.resolve(False))
        self.assertEqual(True, field.resolve(True))
        self.assertEqual(True, field.resolve(None))


class IntegerFieldTest(unittest.TestCase):

    def test_clean(self):
        field = Integer()

        self.assertEqual(5, field.clean(5))
        self.assertEqual(5, field.clean('5'))


        with self.assertRaises(ValueError):
            field.clean(5.251)

        with self.assertRaises(ValueError):
            field.clean('test_value')

    def test_resolve_to_default(self):
        field = Integer(default=256)

        self.assertEqual(256, field.resolve(256))
        self.assertEqual(123, field.resolve(123))
        self.assertEqual(256, field.resolve(None))

        field = Integer(default=-256)

        self.assertEqual(-256, field.resolve(-256))
        self.assertEqual(256, field.resolve(256))
        self.assertEqual(-256, field.resolve(None))


class FloatFieldTest(unittest.TestCase):

    def test_clean(self):
        field = Float()

        self.assertEqual(5.0, field.clean(5))
        self.assertEqual(5.251, field.clean(5.251))

        with self.assertRaises(ValueError):
            field.clean('test_value')

    def test_resolve_to_default(self):
        field = Float(default=256.25)

        self.assertEqual(256.15, field.resolve(256.15))
        self.assertEqual(123.00, field.resolve(123.00))
        self.assertEqual(256.25, field.resolve(None))

        field = Float(default=-256.25)

        self.assertEqual(-256.00, field.resolve(-256.00))
        self.assertEqual(256.00, field.resolve(256.00))
        self.assertEqual(-256.25, field.resolve(None))


class MapFieldTest(unittest.TestCase):

    def test_get_map(self):
        field = Map(Any)

        self.assertTrue(callable(field.get_map))
        self.assertTrue(isinstance(field.get_map(), dict))

    def test_resolve_identity(self):
        field = Map(Any)

        self.assertEqual(5, field.resolve(5))
        self.assertEqual('5', field.resolve('5'))
        self.assertEqual('test_value', field.resolve('test_value'))

    @patch('paramap.fields.Map.get_map')
    def test_resolve_with_static_map(self, mock_get_map):
        mock_get_map.return_value = {
            '5': 5,
            5: '5',
            'test_value': 'TEST_VALUE',
        }

        field = Map(Any)

        self.assertEqual(5, field.resolve('5'))
        self.assertEqual('5', field.resolve(5))
        self.assertEqual('TEST_VALUE', field.resolve('test_value'))

    @patch('paramap.fields.Map.get_map')
    def test_resolve_with_function_map(self, mock_get_map):
        mock_get_map.return_value = {
            '5': lambda x: 'five',
            5: lambda x: x + 5,
            'test_value': lambda x: x,
        }

        field = Map(Any)

        self.assertEqual('five', field.resolve('5'))
        self.assertEqual(10, field.resolve(5))
        self.assertEqual('test_value', field.resolve('test_value'))

    @patch('paramap.fields.Map.get_map')
    def test_resolve_with_mixed_map(self, mock_get_map):
        mock_get_map.return_value = {
            '5': 5,
            5: lambda x: x + 5,
            'test_value': lambda x: x,
        }

        field = Map(Any)

        self.assertEqual(5, field.resolve('5'))
        self.assertEqual(10, field.resolve(5))
        self.assertEqual('test_value', field.resolve('test_value'))

    def test_multi_inheritance_resolution(self):
        class TestClass(Map, Any):
            def get_map(self):
                return {
                    '0': 'value_1',
                    '1': 'value_2',
                }

        field = TestClass()
        self.assertEqual(5, field.resolve(5))
        self.assertEqual('value_1', field.resolve('0'))
        self.assertEqual('value_2', field.resolve('1'))


class NestedFieldTest(unittest.TestCase):

    def test_resolve(self):
        class TestMapObject(MapObject):
            test_field_1 = Any()
            test_field_2 = Any(param='test_param_2')

        nested_field = Nested(TestMapObject)

        field = nested_field.resolve({
            'test_param_2': 'test_param_2_value'
        })

        self.assertTrue(isinstance(field, MapObject))
        self.assertEqual(None, field.test_field_1)
        self.assertEqual('test_param_2_value', field.test_field_2)

        field = nested_field.resolve(TestMapObject(test_field_1='test_value'))

        self.assertEqual('test_value', field.test_field_1)
        self.assertEqual(None, field.test_field_2)


class ListFieldTest(unittest.TestCase):

    def test_resolve_scalars_identity(self):
        field = List(Any)

        test_scalar_list = [1, 2, 3, 4, 5, 6, 'test_value']
        self.assertEqual(test_scalar_list, field.resolve(test_scalar_list))

    def test_resolve_with_none(self):
        field = List(Any)
        self.assertIsNone(field.resolve(None))

    def test_resolve_to_default(self):
        field = List(Any, default=[])
        self.assertEqual(field.resolve(None), [])

    def resolve_with_non_iterable(self):
        field = List(Any)
        resolved_with = field.resolve(5)

        self.assertIsInstance(resolved_with, list)
        self.assertIn(5, resolved_with)
        self.assertEqual(1, resolved_with)

    def test_resolve_map_objects_with_object_list(self):
        class TestMap(MapObject):
            test_field_1 = Any()

        field = List(TestMap)

        test_nested_list = [
            TestMap(test_field_1=1),
            TestMap(test_field_1=2),
            TestMap(test_field_1=3),
        ]

        self.assertEqual(test_nested_list, field.resolve(test_nested_list))

    def test_nested_list_with_param(self):
        class NestedListItem(MapObject):
            test_field_1 = Any(param='test_param_1')
            test_field_2 = Any(param='test_param_2')

        class TestMap(MapObject):
            nested_list = List(NestedListItem)

        test_map = TestMap()
        self.assertEqual(len(test_map.nested_list), 1)

        class TestMap(MapObject):
            nested_list = List(NestedListItem, param='nested_list_param')

        params = {
            'nested_list_param': [
            ]
        }

        test_map = TestMap(parameters=params)
        self.assertEqual(len(test_map.nested_list), 0)

        params = {
            'nested_list_param': [
                {
                    'test_param_1': 'first_item_param_value_1',
                    'test_param_2': 'first_item_param_value_2',
                }
            ]
        }

        test_map = TestMap(parameters=params)
        self.assertEqual(len(test_map.nested_list), 1)
        self.assertEqual(test_map.nested_list[0].test_field_1, params['nested_list_param'][0]['test_param_1'])
        self.assertEqual(test_map.nested_list[0].test_field_2, params['nested_list_param'][0]['test_param_2'])

        params = {
            'nested_list_param': [
                {
                    'test_param_1': 'first_item_param_value_1',
                    'test_param_2': 'first_item_param_value_2',
                },
                {
                    'test_param_1': 'second_item_param_value_1',
                    'test_param_2': 'second_item_param_value_2',
                },
            ]
        }

        test_map = TestMap(parameters=params)
        self.assertEqual(len(test_map.nested_list), 2)

        self.assertEqual(test_map.nested_list[0].test_field_1, params['nested_list_param'][0]['test_param_1'])
        self.assertEqual(test_map.nested_list[0].test_field_2, params['nested_list_param'][0]['test_param_2'])
        self.assertEqual(test_map.nested_list[1].test_field_1, params['nested_list_param'][1]['test_param_1'])
        self.assertEqual(test_map.nested_list[1].test_field_2, params['nested_list_param'][1]['test_param_2'])
