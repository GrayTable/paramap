from collections import OrderedDict


class BaseType(object):
    """
    Represents base type class that resolves values with identity.
    """
    def clean(self, value):
        """
        All values are valid by default
        """
        return value

    def resolve(self, value):
        """
        Resolves literal value
        """
        return self.clean(value)


class BaseField(BaseType):
    """
    Base class for fields
    """
    def __init__(self, type_class, param=None, default=None):
        self.type_class = type_class
        self.param = param
        self.default = default

    def clean(self, value):
        return self.type_class().clean(value)

    def resolve(self, value):
        resolve_with = self.type_class().resolve(value)
        return super(BaseField, self).resolve(resolve_with) or self.default


class DeclarativeFieldsMetaclass(type):
    """
    Collects declared fields in .base_fields attribute.
    """

    def __new__(mcs, name, bases, attrs):
        # Collect fields from current class and remove them from attrs.
        attrs['declared_fields'] = {
            key: attrs.pop(key) for key, value in list(attrs.items())
            if isinstance(value, BaseType)
        }

        new_class = super(DeclarativeFieldsMetaclass, mcs).__new__(mcs, name, bases, attrs)

        # Walk through the MRO.
        declared_fields = {}
        for base in reversed(new_class.__mro__):
            # Collect fields from base class.
            if hasattr(base, 'declared_fields'):
                declared_fields.update(base.declared_fields)

            for attr, value in base.__dict__.items():
                if value is None and attr in declared_fields:
                    declared_fields.pop(attr)

        new_class.base_fields = declared_fields

        return new_class
