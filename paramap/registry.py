
class Registry:
    def __init__(self):
        self.schemas = {}

    def __iter__(self):
        for schema in self.schemas.values():
            yield schema

    def register(self, schema_class):
        key = schema_class.__name__

        if key in self.schemas.keys():
            raise ValueError('Schema with name %s already exists in the registry.' % key)
        self.schemas[schema_class.__name__] = schema_class

    @property
    def parameters(self):
        all_parameters = {}

        for schema in self.schemas.values():
            schema_parameters = {
                parameter.name: parameter for parameter in schema().parameters.values()
                if not all_parameters.get(parameter.name) or parameter.required
            }

            all_parameters.update(schema_parameters)

        return all_parameters

    @property
    def required_parameters(self):
        return {
            parameter.name: parameter
            for parameter in self.parameters.values()
            if parameter.required
        }

    @property
    def optional_parameters(self):
        return {
            parameter.name: parameter
            for parameter in self.parameters.values()
            if not parameter.required
        }


registry = None


def get_global_registry():
    """
    Returns a global schema registry
    """
    global registry
    if not registry:
        registry = Registry()

    return registry


def register(registry=None):
    """
    Registers schema
    """
    if not registry:
        registry = get_global_registry()

    def wrapper(schema_class):
        registry.register(schema_class)

        return schema_class

    return wrapper