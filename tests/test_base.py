import unittest
from paramap.base import BaseType, DeclarativeFieldsMetaclass


class BaseTypeTest(unittest.TestCase):

    def test_attrs(self):
        base_type = BaseType()

        self.assertTrue(hasattr(base_type, 'clean'))
        self.assertTrue(hasattr(base_type, 'resolve'))
        self.assertTrue(callable(base_type.clean))
        self.assertTrue(callable(base_type.resolve))

    def test_clean_identity(self):
        test_value = 'test_value'
        base_type = BaseType()

        self.assertEqual(test_value, base_type.clean(test_value))

    def test_resolve_identity(self):
        test_value = 'test_value'
        base_type = BaseType()

        self.assertEqual(test_value, base_type.resolve(test_value))


class DeclarativeFieldsMetaclassTest(unittest.TestCase):

    def test_add_base_types_to_base_fields(self):
        class TestClass(metaclass=DeclarativeFieldsMetaclass):
            not_registered = 'this_field_should_not_be_registered'
            test_field_1 = BaseType()
            test_field_2 = BaseType()

        instance = TestClass()

        self.assertTrue(hasattr(instance, 'base_fields'))
        self.assertFalse('not_registered' in instance.base_fields)
        self.assertTrue('test_field_1' in instance.base_fields)
        self.assertTrue('test_field_2' in instance.base_fields)

    def test_exclude_none_from_base_fields(self):
        class ParentClass(metaclass=DeclarativeFieldsMetaclass):
            not_registered = 'this_field_should_not_be_registered'
            test_field_1 = BaseType()
            test_field_2 = BaseType()

        class ChildClass(ParentClass):
            test_field_1 = None

        instance = ChildClass()

        self.assertTrue(hasattr(instance, 'base_fields'))
        self.assertFalse('not_registered' in instance.base_fields)
        self.assertTrue('test_field_1' not in instance.base_fields)
        self.assertTrue('test_field_2' in instance.base_fields)
