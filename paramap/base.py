from collections import OrderedDict, defaultdict
import warnings


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
    def __init__(self, type_class, param=None, default=None, required=False, 
            verbose_name=None, description=None):
        self.type_class = type_class
        self.param = param
        self.default = default
        self.required = required
        self.verbose_name = verbose_name
        self.description = description

        if self.default and self.required:
            warnings.warn(
                'Warning, you are using both `default` and `required` kwargs on '
                '%s field.' % self.__class__.__name__,
            )

    def clean(self, value):
        return self.type_class().clean(value)

    def resolve(self, value):
        if value is None:
            return self.default

        resolve_with = self.type_class().resolve(value)

        if resolve_with is None:
            return self.default

        return super(BaseField, self).resolve(resolve_with)


class DeclarativeFieldsMetaclass(type):
    """
    Collects declared fields in .base_fields attribute.
    """

    def __new__(mcs, name, bases, attrs):
        # Collect fields from current class and remove them from attrs.
        attrs['base_fields'] = {
            key: attrs.pop(key) for key, value in list(attrs.items())
            if isinstance(value, BaseType)
        }

        new_class = super(DeclarativeFieldsMetaclass, mcs).__new__(mcs, name, bases, attrs)

        # Walk through the MRO.
        base_fields = {}

        for base in reversed(new_class.__mro__):
            # Collect fields from base class.
            if hasattr(base, 'base_fields'):
                base_fields.update(base.base_fields)

            for attr, value in base.__dict__.items():
                if value is None and attr in base_fields:
                    base_fields.pop(attr)

        new_class.base_fields = base_fields

        return new_class
