MapObject
=========

MapObject is the most important component of Paramap. It's used as an entrypoint for parameters, and defines how to resolve them into objects.

Data Schema Definition
----------------------

Imagine we have the following flat parameter dictionary:

.. code-block:: python

    my_parameters = {
        'FIRST_NAME': 'John',
        'LAST_NAME': 'Doe',
        'AGE': 32,
        'ADDRESS_CITY': 'Warsaw',
        'ADDRESS_POST_CODE': '00-000',
        'ADDRESS_STREET': 'Royal',
    }

We could define two objects ``Address`` and ``Person`` to represent the above parameters as an object:

.. code-block:: python

    from paramap.types import MapObject
    from paramap import fields

    class Address(MapObject):
        city = fields.String(param='ADRESS_CITY')
        post_code = fields.String(param='ADDRESS_POST_CODE')
        street = fields.String(param='ADDRESS_STREET')

    class Person(MapObject):
        first_name = fields.String(param='FIRST_NAME', required=True)
        last_name = fields.String(param='LAST_NAME', required=True)
        age = fields.Integer(param='AGE', default=0)
        address = fields.Nested(Address)
    
    
    person = Person(parameters=my_parameters)

    print(person.first_name)
    # output: 'John'

    print(person.address.street)
    # output: 'Royal'

    print(person.to_dict())
    # output:
    # {
    #     'first_name': 'John',
    #     'last_name': 'Doe',
    #     'age': 32,
    #     'address': {
    #         'city': 'Warsaw',
    #        'street': 'Royal',
    #         'post_code': '00-000',
    #      }
    # }

MapObject is essentially a collection of fields which can use passed parameters to resolve their value.

Required and optional fields
----------------------------

You can use ``parameters``, ``required_parameters``, and ``optional_parameters`` properties to determine required and optional parameters in the data schema.

.. code-block:: python

    print(Person().parameters)
    # output:
    # {
    #     'FIRST_NAME': True,  # this parameter is required
    #     'LAST_NAME': True,   # this parameter is required
    #     'AGE': False,
    #     'ADDRESS_CITY': False,
    #     'ADDRESS_POST_CODE': False,
    #     'ADDRESS_STREET': False,
    # }

    print(Person().required_parameters) # <- returns a set of required parameter names
    # output:
    # { 'FIRST_NAME', 'LAST_NAME' }

    print(Person().optional_parameters) # <- returns a set of optional parameter names
    # output:
    # { 'AGE', 'ADDRESS_CITY', 'ADDRESS_POST_CODE', 'ADDRESS_STREET', }

MapObject determines which parameters are required by looking up ``required`` attribute of ``Field(type_class, param=None, default=None, required=False)``.