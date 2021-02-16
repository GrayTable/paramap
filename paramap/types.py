from functools import partial
from collections import OrderedDict

from .base import BaseType, DeclarativeFieldsMetaclass


class AnyType(BaseType):
    """
    Resolves with any value
    """
    pass


class StringType(BaseType):
    """
    Resolves to string
    """
    def clean(self, value):
        """
        Casts value to string
        """
        return str(value)


class IntegerType(BaseType):
    """
    Resolves to integer
    """
    def clean(self, value):
        """
        Casts value to integer
        """
        if isinstance(value, float):
            raise ValueError('Value `{}` can not be cast to type `Integer`'.format(value))

        try:
            value = int(value)
        except ValueError:
            raise ValueError('Value `{}` can not be cast to type `Integer`'.format(value))

        return value


class FloatType(BaseType):
    """
    Resolves to float
    """
    def clean(self, value):
        """
        Casts value to float
        """
        try:
            value = float(value)
        except ValueError:
            raise ValueError('Value `{}` can not be cast to type `Float`'.format(value))

        return value


class BoolType(BaseType):
    """
    Resolves to bool
    """
    def clean(self, value):
        """
        Casts value to bool
        """
        return bool(value)


class DateStringType(StringType):
    """
    Resolves to date string
    """
    pass


class Parameter:
    """
    Comparable parameter object used for parameter resolving
    """
    def __init__(self, name, type_class=None, required=False, description=None):
        self.name = name
        self.type_class = type_class
        self.required = required
        self.description = description

    def __repr__(self):
        return (f'Parameter(name={self.__class__.__name__}, required={self.required}, '
                'description={self.description})')

    def __eq__(self, other):
        return self.name == other.name


class MapObject(metaclass=DeclarativeFieldsMetaclass):
    """
    Main map type class meant to be inherited by other classes
    to represent domain objects.

    Resolvers work similar to graphene type classes, and have to follow
    resolve_attributename convention. Resolvers will only be called for
    BaseType(field) attributes.

    Example:
        ::

            class Person(MapObject):
                first_name = 'John'
                last_name = 'Doe'
                full_name = String()

                def resolve_full_name(self, parameters):
                    # parameters variable is a dict passed to constructor
                    # you can access other attributes to build values here
                    return self.first_name + ' ' + self.last_name

                def resolve_first_name(self, parameters):
                    # this method will not be called, because the self.first_name
                    # attribute is a str and not a BaseType
                    return None

    Each resolver gets full access to parameters passed to __init__ method.

    Resolve methods will be called only after all fields without resolvers are set.
    After that, when there is more than one resolver in the class, each of them will
    be called from top to bottom. Remember about it when accessing other attributes.

    Each non nested field can have a default value set in type definition.

    Example:
        ::

            class Person(MapObject):
                # Represents a person
                firstName = String(param='person_first_name')
                lastName = String(param='person_last_name')
                fullName = String()

                def resolve_fullName(self, parameters):
                    # custom resolve method for fullName field
                    # that uses other fields to build the value
                    return self.firstName + ' ' + self.lastName

            # create person instance with parameters
            person = Person(parameters={
                'person_first_name': 'John',
                'person_last_name': 'Doe',
            })

            # as you can see, fullName field is present in the result
            print(person.to_dict())
            {
                'firstName': 'John',
                'lastName': 'Doe',
                'fullName': 'John Doe',
                'age': 24,
            }

            # create person instance with kwargs directly
            person = Person(firstName='Bobby', lastName='Bob')

            # as you can see, fullName field is present in the result
            print(person.to_dict())
            {
                'firstName': 'Bobby',
                'lastName': 'Bob',
                'fullName': 'Bobby Bob',
                'age': 24,
            }

    """
    def __init__(self, parameters=None, **kwargs):
        """Initializes map type instance

        Args:
            parameters (dict, optional): a dictionary with { field: value } pairs. Defaults to {}.
            kwargs (dict): directly initialized fields
        """

        if not parameters:
            parameters = {}

        self._init_with_fields(parameters=parameters, initial=kwargs)

    def _init_with_fields(self, parameters, initial={}):
        """Initializes field values based on passed parameters

        Args:
            parameters (dict): a dictionary with { field: value } pairs.
            initial (dict, optional): initial values passed as kwargs SomeType(field_1='some_value').

        """
        # Pending resolvers are used after all other values
        # have been set, to make it possible to use them
        # in the resolver function body
        pending_resolvers = OrderedDict()

        for key, field in self.base_fields.items():
            # traverse base fields and initialize values
            value = initial.get(key, None)

            if value:
                # if value is set through kwargs, simply set attribute
                setattr(self, key, field.resolve(value))
                continue

            if issubclass(field.type_class, MapObject) and not field.param:
                value = field.resolve(parameters)
            else:
                value = field.resolve(parameters.get(field.param))

            resolver = getattr(self, 'resolve_' + key, None)

            if resolver:
                # keep resolvers for later execution
                pending_resolvers[key] = partial(resolver, value, parameters)
                continue

            setattr(self, key, value)

        # execute delayed resolvers
        for attr, resolver in pending_resolvers.items():
            # inject parameters argument to the resolver
            resolved_value = resolver()
            setattr(self, attr, resolved_value)

    def to_dict(self, skip_none=True):
        """Deep casts current object to a dictionary

        Returns:
            dict: dictionary with { field: value } pairs
        """
        def recursive_to_dict(obj=None):
            """Recursively casts object to a dictionary

            Args:
                obj (any): object to be casted. Defaults to None.

            Returns:
                dict: dictionary with { field: value } pairs
            """
            result = {}

            if isinstance(obj, list) or isinstance(obj, tuple):
                # cast iterable members to dict
                return [recursive_to_dict(obj=o) for o in obj]

            if not isinstance(obj, MapObject):
                # if not a map type, return literal value
                return obj

            for name, field in obj.base_fields.items():
                # if map type, traverse all fields
                value = getattr(obj, name, None)

                if skip_none and value is None:
                    continue

                key = field.verbose_name or name
                result[key] = recursive_to_dict(obj=value)

            return result

        return recursive_to_dict(obj=self)


    def resolve(self, value):
        """Returns a new class instance

        Args:
            value (Union[MapObject, dict]): map object or dictionary to resolve with

        Returns:
            MapObject: new MapObject instance
        """
        if issubclass(value.__class__, MapObject):
            return value

        return self.__class__(parameters=value)

    def clean(self, value):
        """Cleans value

        Args:
            value (MapObject): value to clean

        Returns:
            MapObject: cleaned value
        """
        return value

    @property
    def parameters(self):
        """
        Returns all parameters used in MapObject definition including nested objects.

        Returns:
            dict({ String: Parameter }): a dictionary containing { parameter_name: Parameter } key and value pairs.
        """
        result = {}

        for field in self.base_fields.values():

            if issubclass(field.type_class, MapObject):
                # resolve nested map objects required parameters
                # and update result
                nested_parameters = {
                    parameter.name: parameter for parameter in
                    field.type_class().parameters.values()
                    if result.get(parameter.name) is None or parameter.required
                }

                result.update(nested_parameters)
                continue

            field_parameter = field.parameter

            if field_parameter:
                result[field_parameter.name] = field_parameter

        return result

    @property
    def required_parameters(self):
        """
        Returns a set of required parameters

        Returns:
            dict: required parameters
        """
        return { parameter.name: parameter for parameter in self.parameters.values() if parameter.required }

    @property
    def optional_parameters(self):
        """
        Returns a set of optional parameters

        Returns:
            dict: optional parameters
        """
        return { parameter.name: parameter for parameter in self.parameters.values() if not parameter.required }
