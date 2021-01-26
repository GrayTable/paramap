import unittest
from paramap.fields import Any, String, Bool, Integer, Float


class FieldTest(unittest.TestCase):

    def test_attrs(self):
        field = Any()

        self.assertTrue(hasattr(field, 'param'))
        self.assertTrue(hasattr(field, 'default'))

    def test_create(self):
        string = Any(param='test_param', default='test_default')

        self.assertTrue('test_param', string.param)
        self.assertTrue('test_default', string.default)

    def test_resolve_identity(self):
        field = Any()

        self.assertEqual(5, field.resolve(5))
        self.assertEqual('test_value', field.resolve('test_value'))

    def test_resolve_to_default(self):
        field = Any(default='test_default')

        self.assertEqual('5', field.resolve('5'))
        self.assertEqual('test_default', field.resolve(None))


class StringTest(unittest.TestCase):

    def test_clean(self):
        string = String()

        self.assertEqual('5', string.clean(5))
        self.assertEqual('5.251', string.clean(5.251))
        self.assertEqual('test_value', string.clean('test_value'))


class BoolTest(unittest.TestCase):

    def test_clean(self):
        boolean = Bool()

        self.assertTrue(boolean.clean(5))
        self.assertTrue(boolean.clean(5.251))
        self.assertTrue(boolean.clean('test_value'))


class IntegerTest(unittest.TestCase):

    def test_clean(self):
        integer = Integer()

        self.assertEqual(5, integer.clean(5))
        self.assertEqual(5, integer.clean('5'))


        with self.assertRaises(ValueError):
            integer.clean(5.251)

        with self.assertRaises(ValueError):
            integer.clean('test_value')


class FloatTest(unittest.TestCase):

    def test_clean(self):
        float_ = Float()

        self.assertEqual(5.0, float_.clean(5))
        self.assertEqual(5.251, float_.clean(5.251))

        with self.assertRaises(ValueError):
            float_.clean('test_value')