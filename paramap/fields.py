from .base import BaseType, BaseField
from paramap import types


class Field(BaseField):
    """
    Basic field
    """
    pass


class Nested(BaseField):
    """
    Field that resolves with MapObject
    """
    def __init__(self, type_class, *args, **kwargs):
        assert issubclass(type_class, types.MapObject), 'Nested fields must resolve with `MapObject` type_class'

        super(Nested, self).__init__(type_class, *args, **kwargs)


class Any(Field):
    """
    Field resolving with any value
    """
    def __init__(self, *args, **kwargs):
        super(Any, self).__init__(types.AnyType, **kwargs)


class String(Field):
    """
    Field resolving with sting value
    """
    def __init__(self, **kwargs):
        super(String, self).__init__(types.StringType, **kwargs)


class Integer(Field):
    """
    Field resolving with integer value
    """
    def __init__(self, **kwargs):
        super(Integer, self).__init__(types.IntegerType, **kwargs)


class Float(Field):
    """
    Field resolving with float value

    """
    def __init__(self, **kwargs):
        super(Float, self).__init__(types.FloatType, **kwargs)


class Bool(Field):
    """
    Field resolving with boolean value
    """
    def __init__(self, **kwargs):
        super(Bool, self).__init__(types.BoolType, **kwargs)


class List(Field):
    """
    Represents a collection of objects
    """
    def resolve(self, value):
        if value is None: return value

        return [
            super(List, self).resolve(item)
            for item in value
        ]


class Map(Field):
    """
    Resolves values with a map
    """
    def __init__(self, *args, **kwargs):
        self.map = kwargs.pop('map', {})

        super(Map, self).__init__(*args, **kwargs)

    def get_map(self):
        return self.map

    def resolve(self, value):
        mapping = self.get_map().get(value)

        if mapping:
            value = mapping(value) if callable(mapping) else mapping

        return super(Map, self).resolve(value)
