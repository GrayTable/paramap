import unittest
from unittest.mock import patch

from paramap import registry
from paramap.types import MapObject


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