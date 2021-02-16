from .base import BaseType, BaseField
from paramap import types
import warnings


class Field(BaseField):
    """
    Basic field
    """
    def resolve(self, value):
        if not issubclass(self.type_class, types.MapObject):
            return super(Field, self).resolve(value)

        if isinstance(value, self.type_class):
            return value

        if not isinstance(value, dict):
            raise TypeError('Nested fields can only resolve with `dict` or `MapObject` values.')

        return self.type_class(parameters=value)

    @property
    def parameter(self):
        """
        If the field relies on parameter, returns Parameter object
        """
        if not self.param: return None

        return types.ParameterType(
            name=self.param,
            type_class=self.type_class,
            required=self.required,
            description=self.description,
        )


class Parameter(Field):
    """
    Field that requires param keyword argument. The use case would be defining
    parameters outside of MapObject definition, to be able to quickly swap
    type classes and parameter names across the whole data schema.

    Ofcourse it could be done with other fields, but this class allows you to avoid
    mistakes and clearly states its purpose.

    Example:
        ::

        # parameters.py

        from paramap.fields import Parameter
        from paramap.types import StringType

        first_name_parameter_field = fields.Parameter(StringType, param='FIRST_NAME', default='John Doe')

        # schema.py

        from parameters import first_name_parameter_field

        class Person(MapObject):
            firstName = first_name_parameter_field

    """
    def __init__(self, *args, param=None, **kwargs):
        if not param:
            raise ValueError('`param` keyword argument is required for parameter fields')

        super(Parameter, self).__init__(*args, param, **kwargs)


class Nested(Field):
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
    def __init__(self, *args, **kwargs):
        super(List, self).__init__(*args, **kwargs)

        if self.default is not None and not isinstance(self.default, list):
            raise TypeError('List field default value has to be a list or None.')

    def resolve(self, value):
        """Resolves list field value

        If value is None, field will resolve with default value.
        If value is not iterable, field will resolve with single item list with value inside
        Otherwise resolve each item of a list

        Args:
            value (any): value to resolve with

        Returns:
            list or None
        """
        if value is None:
            return super(List, self).resolve(value)

        if not isinstance(value, list):
            return [super(List, self).resolve(value)]

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
