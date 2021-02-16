import unittest
from unittest.mock import patch

from paramap import registry, fields
from paramap.types import MapObject, StringType


class RegistryTest(unittest.TestCase):

    def test_get_global_registry(self):
        global_registry = registry.get_global_registry()

        class TestMap(MapObject):
            pass

        global_registry.register(TestMap)

        self.assertIn(TestMap, global_registry.schemas.values())

    def test_create_registry(self):
        local_registry = registry.Registry()

        class TestMap(MapObject):
            pass

        local_registry.register(TestMap)

        self.assertIn(TestMap, local_registry.schemas.values())
        self.assertEqual(len(local_registry.schemas), 1)

    def test_register_schema(self):
        global_registry = registry.get_global_registry()

        @registry.register()
        class TestMap2(MapObject):
            pass

        self.assertIn(TestMap2, global_registry.schemas.values())

        local_registry = registry.Registry()

        @registry.register(registry=local_registry)
        class LocalTestMap(MapObject):
            pass

        self.assertIn(LocalTestMap, local_registry.schemas.values())
        self.assertEqual(len(local_registry.schemas), 1)

    def test_registry_iterator(self):
        local_registry = registry.Registry()

        @registry.register(registry=local_registry)
        class LocalTestMap(MapObject):
            pass

        @registry.register(registry=local_registry)
        class LocalTestMap2(MapObject):
            pass

        for schema in local_registry:
            self.assertIn(schema, [LocalTestMap, LocalTestMap2])

    def test_registry_parameters(self):
        local_registry = registry.Registry()

        common_parameter = fields.Parameter(StringType, param='TEST_PARAMETER', required=True)

        @registry.register(local_registry)
        class TestOne(MapObject):
            common = common_parameter
            test_field = fields.String(param='TEST_TWO_PARAMETER', required=True)

        @registry.register(local_registry)
        class TestTwoNested(MapObject):
            test_field = fields.String(param='TEST_TWO_PARAMETER', required=False)
            test_field_not_required = fields.String(param='TEST_THREE_PARAMETER', required=False)

        @registry.register(local_registry)
        class TestTwo(MapObject):
            common = common_parameter

        parameters = local_registry.parameters
        required_parameters = local_registry.required_parameters
        optional_parameters = local_registry.optional_parameters

        print('REQUIRED_PARAMETERS', required_parameters)

        self.assertTrue({
            'TEST_PARAMETER',
            'TEST_TWO_PARAMETER',
            'TEST_THREE_PARAMETER',
        } == set(parameters))

        self.assertTrue({
            'TEST_PARAMETER',
            'TEST_TWO_PARAMETER',
        } == set(required_parameters))

        self.assertTrue({
            'TEST_THREE_PARAMETER',
        } == set(optional_parameters))
