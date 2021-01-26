import unittest
from unittest.mock import patch
from paramap.fields import Any, Map, Nested, List
from paramap.types import MapObject


class MapTest(unittest.TestCase):
    def test_get_map(self):
        instance = Map(Any)

        self.assertTrue(callable(instance.get_map))
        self.assertTrue(isinstance(instance.get_map(), dict))

    def test_resolve_identity(self):
        instance = Map(Any)

        self.assertEqual(5, instance.resolve(5))
        self.assertEqual('5', instance.resolve('5'))
        self.assertEqual('test_value', instance.resolve('test_value'))

    @patch('paramap.fields.Map.get_map')
    def test_resolve_with_static_map(self, mock_get_map):
        mock_get_map.return_value = {
            '5': 5,
            5: '5',
            'test_value': 'TEST_VALUE',
        }

        instance = Map(Any)

        self.assertEqual(5, instance.resolve('5'))
        self.assertEqual('5', instance.resolve(5))
        self.assertEqual('TEST_VALUE', instance.resolve('test_value'))

    @patch('paramap.fields.Map.get_map')
    def test_resolve_with_function_map(self, mock_get_map):
        mock_get_map.return_value = {
            '5': lambda x: 'five',
            5: lambda x: x + 5,
            'test_value': lambda x: x,
        }

        instance = Map(Any)

        self.assertEqual('five', instance.resolve('5'))
        self.assertEqual(10, instance.resolve(5))
        self.assertEqual('test_value', instance.resolve('test_value'))

    @patch('paramap.fields.Map.get_map')
    def test_resolve_with_mixed_map(self, mock_get_map):
        mock_get_map.return_value = {
            '5': 5,
            5: lambda x: x + 5,
            'test_value': lambda x: x,
        }

        instance = Map(Any)

        self.assertEqual(5, instance.resolve('5'))
        self.assertEqual(10, instance.resolve(5))
        self.assertEqual('test_value', instance.resolve('test_value'))

    def test_multi_inheritance_resolution(self):
        class TestClass(Map, Any):
            def get_map(self):
                return {
                    '0': 'value_1',
                    '1': 'value_2',
                }

        instance = TestClass()
        self.assertEqual(5, instance.resolve(5))
        self.assertEqual('value_1', instance.resolve('0'))
        self.assertEqual('value_2', instance.resolve('1'))


class NestedTest(unittest.TestCase):

    def test_resolve(self):
        class TestMapObject(MapObject):
            test_field_1 = Any()
            test_field_2 = Any(param='test_param_2')

        nested_field = Nested(TestMapObject)

        instance = nested_field.resolve({
            'test_param_2': 'test_param_2_value'
        })

        self.assertTrue(isinstance(instance, MapObject))
        self.assertEqual(None, instance.test_field_1)
        self.assertEqual('test_param_2_value', instance.test_field_2)

        instance = nested_field.resolve(TestMapObject(test_field_1='test_value'))

        self.assertEqual('test_value', instance.test_field_1)
        self.assertEqual(None, instance.test_field_2)


class ListTest(unittest.TestCase):

    def test_resolve_scalars_identity(self):
        instance = List(Any)

        test_scalar_list = [1, 2, 3, 4, 5, 6, 'test_value']
        self.assertEqual(test_scalar_list, instance.resolve(test_scalar_list))

    def test_resolve_map_objects_with_object_list(self):
        class TestMap(MapObject):
            test_field_1 = Any()

        instance = List(TestMap)

        test_nested_list = [
            TestMap(test_field_1=1),
            TestMap(test_field_1=2),
            TestMap(test_field_1=3),
        ]

        self.assertEqual(test_nested_list, instance.resolve(test_nested_list))
