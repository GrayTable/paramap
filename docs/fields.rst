.. _Fields Overview:

Fields
===========

Paramap uses ``fields`` as a way to represent data. Every subclass of ``paramap.base.BaseType`` is treated like a field by ``MapObject``. Currently there are 9 field classes, 7 of which are pretty obvious like ``String``, ``Bool``, ``Float``, but there are others that may need some insight to use them.


**Paramap offers following basic fields**:

- ``Any`` - generic field that resolves as any value
- ``String`` - resolves as string
- ``Integer`` - resolves as Integer
- ``Bool`` - resolves as bool
- ``Float`` - resolves as float

**and following complex fields**:

- ``Map`` - resolves to chosen data type with dictionary based value resolution
- ``Nested`` - resolves as ``MapObject``
- ``List`` - resolves as list

Field
------

``Field(type_class, param=None, default=None)`` is the most basic respresentation of field functionality. All other, type specific fields are simply an abstraction on top of it. It takes mandatory ``type_class`` argument when being initialized, which designates what type class it should use when resolving final value.

.. code-block:: python

    from param import fields
    from param.types import IntegerType

    integer_field = fields.Field(type_class=IntegerType)

    # is an equivalent to

    integer_field = fields.Integer()

Argument ``type_class`` is only mandatory for ``Field``, ``Nested``, ``Map`` and ``List`` classes.



Basic Fields
------------------

Basic fields perform type casting and validation when resolving values. Therefore when trying to resolve an ``Integer(param=None, default=None)`` field with ``value='5'`` it will automatically cast it to integer, otherwise error will be raised:


.. code-block:: python

    from paramap.fields import Integer

    integer_field = Integer()

    print(integer_field.resolve('5'))
    # output: 5

    integer_field.resolve('error_raising_value')
    # raises Exception: ValueError


.. _Fields Nested:

Nested Field
------------------

It is useful to be able to represent data as a tree of objects and values. In cases like that ``Nested`` field comes in handy.

.. code-block:: python

    from paramap.fields import String, Float, Nested

    class Wallet(MapObject):
        currency = String(param='WALLET_CURRENCY_ABBR', default='USD')
        balance = Float(param='WALLET_BALANCE', default=0)

    class Person(MapObject):
        id = Integer(param='PERSON_ID')
        wallet = Nested(Wallet)

When creating an object with our flat dictionary:

.. code-block:: python

    parameters = {
        'PERSON_ID',
        'WALLET_CURRENCY_ABBR': 'EUR',
        'WALLET_BALANCE': 4560.23,
    }

    person = Person(parameters=parameters)

we can access the ``Wallet`` owned by a ``Person`` directly from the ``person`` s instance:

.. code-block:: python

    print(person.wallet.balance)
    # output: 4560.23
    print(person.wallet.currecy)
    # output: 'EUR'


List Field
------------------

``List(type_class, param=None, default=None)`` field resolves to a list of any given type. For example we could use ``List`` like this:

.. code-block:: python

    from param.types import MapObject
    from param.fields import List, Integer, String


    class Wallet(MapObject):
        id = Integer(param='WALLET_ID')
        currencies = List(String)

        def resolve_currencies(self, parameters):
            currency_list = parameters.get('WALLET_CURRENCIES')

            return currency_list.split(',')


    parameters = {
        'WALLET_ID': 142,
        'WALLET_CURRENCIES': 'USD,EUR,PLN',
    }

    wallet = Wallet(parameters=parameters)

    print(wallet.id)
    # output: 142
    print(wallet.currencies)
    # output: ['USD', 'EUR', 'PLN']


Map Field
------------------

``Map(type_class, param=None, default=None)`` field, as the name suggests, uses a map to resolve values. Let's say that our wallet has a single `currency` that we want to translate to its full name:

.. code-block:: python

    from param.types import MapObject
    from param.fields import Integer, String, Map

    class FullNameCurrency(Map, String):
        def get_map(self):
            return {
                'EUR': 'Euro',
                'PLN': 'Polish Zloty',
                'USD': 'United States Dollar',
            }

    class Wallet(MapObject):
        id = Integer(param='WALLET_ID')
        currency = FullNameCurrency(String)


    parameters = {
        'WALLET_ID': 142,
        'WALLET_CURRENCY': 'PLN',
    }

    wallet = Wallet(parameters=parameters)

    print(wallet.id)
    # output: 142
    print(wallet.currency)
    # output: Polish Zloty

Or we could use a shorthand:

.. code-block:: python

    class Wallet(MapObject):
        id = Integer(param='WALLET_ID')
        currency = Map(String, map={
            'EUR': 'Euro',
            'PLN': 'Polish Zloty',
            'USD': 'United States Dollar',
        })
