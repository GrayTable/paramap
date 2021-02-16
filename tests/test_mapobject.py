import unittest
from unittest.mock import patch
from paramap.types import MapObject
from paramap.fields import Field, Any, List, Nested


class MapObjectTest(unittest.TestCase):

    def test_create(self):
        MapObject()

    def test_resolve(self):
        parameters = {
            'param_1': 1,
            'param_2': 2,
        }

        instance = MapObject()
        resolve = instance.resolve(parameters)

    def test_field_resolving_with_parameters(self):
        class TestMap(MapObject):
            test_field_1 = Any(default='test_default_1')
            test_field_2 = Any(param='test_param_2')
            test_field_3 = Any(param='test_param_3', default='test_default_3')

        instance = TestMap()

        self.assertEqual('test_default_1', instance.test_field_1)
        self.assertEqual(None, instance.test_field_2)
        self.assertEqual('test_default_3', instance.test_field_3)

        instance = TestMap({
            'test_param_1': 'test_param_1_value',
            'test_param_2': 'test_param_2_value',
            'test_param_3': 'test_param_3_value',
        })

        self.assertEqual('test_default_1', instance.test_field_1)
        self.assertEqual('test_param_2_value', instance.test_field_2)
        self.assertEqual('test_param_3_value', instance.test_field_3)

        instance = TestMap(
            test_field_1 = 1,
            test_field_2 = 2,
            test_field_3 = 3,
       )

    def test_field_resolving_with_kwargs(self):
        class TestMap(MapObject):
            test_field_1 = Any(default='test_default_1')
            test_field_2 = Any(param='test_param_2')
            test_field_3 = Any(param='test_param_3', default='test_default_3')

        instance = TestMap(
            test_field_1 = 1,
            test_field_2 = 2,
            test_field_3 = 3,
       )

        self.assertEqual(1, instance.test_field_1)
        self.assertEqual(2, instance.test_field_2)
        self.assertEqual(3, instance.test_field_3)

        instance = TestMap(
            test_field_2 = 2,
        )

        self.assertEqual('test_default_1', instance.test_field_1)
        self.assertEqual(2, instance.test_field_2)
        self.assertEqual('test_default_3', instance.test_field_3)

    def test_mixed_field_resolving(self):
        class TestMap(MapObject):
            test_field_1 = Any(default='test_default_1')
            test_field_2 = Any(param='test_param_2')
            test_field_3 = Any(param='test_param_3', default='test_default_3')

        instance = TestMap(
            parameters={
                'test_param_2': 'test_param_2_value',
                'test_param_3': 'test_param_3_value'
            },
            test_field_2 = 'kwarg values should be prioritized'
        )

        self.assertEqual('test_default_1', instance.test_field_1)
        self.assertEqual('kwarg values should be prioritized', instance.test_field_2)
        self.assertEqual('test_param_3_value', instance.test_field_3)

    def test_nested_field_resolving(self):
        class NestedMap(MapObject):
            test_field_1 = Any(default='test_default_1')
            test_field_2 = Any(param='test_param_2')
            test_field_3 = Any(param='test_param_3', default='test_default_3')

        class TestMap(MapObject):
            test_nested = Nested(NestedMap)

        instance = TestMap().test_nested

        self.assertTrue(isinstance(instance, MapObject))
        self.assertEqual('test_default_1', instance.test_field_1)
        self.assertEqual(None, instance.test_field_2)
        self.assertEqual('test_default_3', instance.test_field_3)

        instance = TestMap({
            'test_param_1': 'test_param_1_value',
            'test_param_2': 'test_param_2_value',
            'test_param_3': 'test_param_3_value',
        }).test_nested

        self.assertEqual('test_default_1', instance.test_field_1)
        self.assertEqual('test_param_2_value', instance.test_field_2)
        self.assertEqual('test_param_3_value', instance.test_field_3)

    def test_any_resolvers(self):
        class NestedMap(MapObject):
            test_field_1 = Any(default='test_default_1')
            test_field_2 = Any(param='test_param_2')
            test_field_3 = Any(param='test_param_3', default='test_default_3')

            def resolve_test_field_2(self, value, parameters):
                # resolvers should have access to other fields
                return self.test_field_1

            def resolve_test_field_3(self, value, parameters):
                return parameters.get('test_param_3') + '_the_resolver'

        class TestMap(MapObject):
            test_nested = Nested(NestedMap)

        instance = TestMap({
            'test_param_3': 'modified_by'
        })

        self.assertEqual('test_default_1', instance.test_nested.test_field_2)
        self.assertEqual('modified_by_the_resolver', instance.test_nested.test_field_3)

    def test_resolvers_mro_top_to_bottom(self):
        mro = []

        class TestMap(MapObject):
            test_field_1 = Any()
            test_field_2 = Any()
            test_field_3 = Any()
            test_field_4 = Any()

            def resolve_test_field_2(self, value, parameters):
                mro.append(2)

            def resolve_test_field_3(self, value, parameters):
                mro.append(3)

            def resolve_test_field_4(self, value, parameters):
                mro.append(4)

        instance = TestMap()

        self.assertEqual(mro, [2,3,4])

    def test_nested_resolvers(self):
        class NestedMap(MapObject):
            test_field_1 = Any(default='test_default_1')
            test_field_2 = Any(param='test_param_2')
            test_field_3 = Any(param='test_param_3', default='test_default_3')

            def resolve_test_field_3(self, value, parameters):
                return parameters.get('test_param_3') + '_the_resolver'

        class TestMap(MapObject):
            test_nested = Nested(NestedMap)

        instance = TestMap({
            'test_param_3': 'modified_by'
        })

        self.assertEqual('modified_by_the_resolver', instance.test_nested.test_field_3)

    def test_to_dict(self):
        class DoubleNested(MapObject):
            test_field_1 = Any(default='test_default_1')
            test_field_2 = Any(param='test_param_2', default='test_default_2')


        class NestedMap(MapObject):
            test_field_1 = Any(default='test_default_1')
            test_field_2 = Any(param='test_param_2', verbose_name='verbose_test_field_2_name')
            test_field_3 = Any(param='test_param_3', default='test_default_3')
            test_field_4 = List(Any)
            test_double_nested = Nested(DoubleNested)

            def resolve_test_field_2(self, value, parameters):
                # resolvers should have access to other fields
                return self.test_field_1

            def resolve_test_field_3(self, value, parameters):
                return parameters.get('test_param_3') + '_the_resolver'

            def resolve_test_field_4(self, value, parameters):
                return [
                    'list_item_1',
                    'list_item_2',
                    'list_item_3',
                ]

        class TestMap(MapObject):
            test_nested = Nested(NestedMap)

            def resolve_test_nested(self, value, parameters):
                return NestedMap(
                    parameters=parameters,
                    test_field_1='test_field_1_resolved'
                )

        dictionary = TestMap({
            'test_param_2': 'test_param_2_value',
            'test_param_3': 'modified_by',
        }).to_dict()

        self.assertEqual(dictionary, {
            'test_nested': {
                'test_field_1': 'test_field_1_resolved',
                'verbose_test_field_2_name': 'test_field_1_resolved',
                'test_field_3': 'modified_by_the_resolver',
                'test_field_4': ['list_item_1', 'list_item_2', 'list_item_3'],
                'test_double_nested': {
                    'test_field_1': 'test_default_1',
                    'test_field_2': 'test_param_2_value',
                }
            }
        })

    def test_to_dict_skip_none(self):
        class TestMap(MapObject):
            test_field_1 = Any()
            test_field_2 = Any()

            def resolve_test_field_2(self, *args, **kwargs):
                return 'not_none'

        test_map = TestMap()

        self.assertTrue(hasattr(test_map, 'test_field_1'))
        self.assertTrue(hasattr(test_map, 'test_field_2'))

        dictionary = test_map.to_dict()

        self.assertNotIn('test_field_1', dictionary.keys())
        self.assertIn('test_field_2', dictionary.keys())
        self.assertEqual(dictionary.get('test_field_2'), 'not_none')


        dictionary = test_map.to_dict(skip_none=True)

        self.assertNotIn('test_field_1', dictionary.keys())
        self.assertIn('test_field_2', dictionary.keys())
        self.assertEqual(dictionary.get('test_field_2'), 'not_none')


        dictionary = test_map.to_dict(skip_none=False)

        self.assertIn('test_field_1', dictionary.keys())
        self.assertIsNone(dictionary.get('test_field_1'))
        self.assertIn('test_field_2', dictionary.keys())
        self.assertEqual(dictionary.get('test_field_2'), 'not_none')

    def test_required_fields(self):
        class DoubleNested(MapObject):
            test_field_1 = Any(default='test_default_1')
            test_field_2 = Any(param='test_param_2', default='test_default_2', required=True)
            test_field_3 = Any(param='test_param_3', required=True)
            test_field_4 = Any(param='test_param_4', required=True)
            test_field_5 = Any(param='test_param_5', required=True)
            test_field_6 = Any(param='test_param_6')


        class NestedMap(MapObject):
            test_field_1 = Any(default='test_default_1')
            test_field_2 = Any(param='test_param_2', required=True)
            test_field_3 = Any(param='test_param_3', default='test_default_3')
            test_field_4 = List(Any)
            test_double_nested = Nested(DoubleNested)

            def resolve_test_field_2(self, value, parameters):
                # resolvers should have access to other fields
                return self.test_field_1

            def resolve_test_field_4(self, value, parameters):
                return [
                    'list_item_1',
                    'list_item_2',
                    'list_item_3',
                ]

        class TestMap(MapObject):
            test_nested = Nested(NestedMap)
            test_field_change_required_status = Any(param='test_param_not_required', required=True)

            def __init__(self, *args, **kwargs):
                super(TestMap, self).__init__(*args, **kwargs)

                # conditional requirement change
                self.base_fields['test_field_change_required_status'].required = False

            def resolve_test_nested(self, value, parameters):
                return NestedMap(
                    parameters=parameters,
                    test_field_1='test_field_1_resolved'
                )


        all_parameters = set(TestMap().parameters.keys())

        self.assertEqual({
            'test_param_2',
            'test_param_3',
            'test_param_4',
            'test_param_5',
            'test_param_6',
            'test_param_not_required',
        }, all_parameters)

        required_parameters = set(TestMap().required_parameters.keys())

        self.assertEqual({
            'test_param_2',
            'test_param_3',
            'test_param_4',
            'test_param_5',
        }, required_parameters)

        optional_parameters = set(TestMap().optional_parameters.keys())

        self.assertEqual({
            'test_param_6',
            'test_param_not_required',
        }, optional_parameters)

        self.assertEqual(required_parameters.union(optional_parameters), all_parameters)

    def test_define_common_field_outside_of_mapobject(self):
        common_field = Any(default='test')

        class TestMapOne(MapObject):
            common = common_field

        class TestMapTwo(MapObject):
            common = common_field

        test_one = TestMapOne()
        test_two = TestMapTwo()

        self.assertEqual(test_one.common, 'test')
        self.assertEqual(test_one.common, test_two.common)

    def test_define_common_field_with_param_outside_of_mapobject(self):
        common_field = Any(param='TEST_PARAM')

        class TestMapOne(MapObject):
            common = common_field

        class TestMapTwo(MapObject):
            common = common_field

        parameters = {
            'TEST_PARAM': 'test',
        }

        test_one = TestMapOne(parameters=parameters)
        test_two = TestMapTwo(parameters=parameters)

        self.assertEqual(test_one.common, 'test')
        self.assertEqual(test_one.common, test_two.common)

        test_one = TestMapOne(parameters=parameters)
        test_two = TestMapTwo(parameters={})

        self.assertEqual(test_one.common, 'test')
        self.assertNotEqual(test_one.common, test_two.common)