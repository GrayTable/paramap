.. _Quickstart Overview:

Quickstart
==========

Let's consider you have a following parameter dictionary that gives us some information about a smart house system:


.. code-block:: python

   parameters = {
      'HOME_ID' : 213,
      'HOME_TEMPERATURE': 24.6, # in Celsius
      'HOME_HUMIDITY': 80.6,
      'HOME_GATE_ACTIVE': 1, # can the gate be opened?
      'HOME_GATE_OPENED': 0, # is the gate opened?
   }


Object, or a nested dictionary representation could be a more useful way to represent this data.

Creating data schema
--------------------------------------------

You cloud parse above parameters with ``paramap`` by creating ``Home``, ``Environment``, and ``Gate`` objects:


.. code-block:: python

    from paramap.types import MapObject
    from paramap.fields import Integer, Float, Bool

    class Gate(MapObject):
        opened = Bool(param='HOME_GATE_OPENED')
        active = Bool(param='HOME_GATE_ACTIVE')
    
    class Environment(MapObject):
        temperature = Float(param='HOME_TEMPERATURE')
        humidity = Float(param='HOME_HUMIDITY')
    
    class Home(MapObject):
        id = Integer(param='HOME_ID')



As you can see, all classes inheriting from ``MapObject`` have a set :ref:`Fields Overview`, ie. ``Gate`` has ``opened`` and ``active`` fields. Keyword argument ``param`` passed on field creation determines which parameter should be used to resolve the value.


With the above implementation, we can already create objects with previously defined parameters and access their values:


.. code-block:: python

    >>> home = Home(parameters=parameters)
    >>> home.id
    213
    >>> gate = Gate(parameters=parameters)
    >>> gate.opened
    False
    >>> environment = Environment(parameters=parameters)
    >>> environment.temperature
    24.6
    >>> environment.to_dict()
    { 'temperature': 24.6, 'humidity': 80.6 }


Nesting objects
----------------------------------

The main functionality of Paramap is being able to easily create nested object representations of flat parameter dictionaries. Currently  ``Environment`` and ``Gate`` are not related to ``Home``. We can use :ref:`Fields Nested` to create the relationship:

.. code-block:: python

    from paramap.types import MapObject
    from paramap.fields import Integer, Float, Bool, Nested

    class Gate(MapObject):
        opened = Bool(param='HOME_GATE_OPENED')
        active = Bool(param='HOME_GATE_ACTIVE')
    
    class Environment(MapObject):
        temperature = Float(param='HOME_TEMPERATURE')
        humidity = Float(param='HOME_HUMIDITY')
    
    class Home(MapObject):
        id = Integer(param='HOME_ID')
        gate = Nested(Gate)
        environment = Nested(Environment)

.. code-block:: python

   >>> home = Home(parameters=parameters)
   >>> home.environment.humidity
   80.6
   >>> home.gate.opened
   False
   >>> home.to_dict()
   {
      'id': 213,
      'environment': {
         'temperature': 24.6,
         'humidity': 80.6,
      },
      'gate': {
         'opened': False,
         'active': True,
      }
   }
   >>> home.gate.to_dict()
   {
       'opened': False,
       'active': True,
   }


Temperature conversion with resolvers
----------------------------------------

Sometimes we need to perform some special logic when parsing data. As an example, let's assume our sensors read temperature in Celsius, 
but we need temperature expressed in Fahrenheit in our final result. 

To solve this problem Paramap introduces a useful feature called :ref:`Resolvers Overview`, which will be familiar to people that used ``graphene`` before.

Let's modify our `Environment` class:

.. code-block:: python

    from paramap.types import MapObject
    from paramap.fields import Float

    class Environment(MapObject):
        temperature = Float(param='HOME_TEMPERATURE')
        humidity = Float(param='HOME_HUMIDITY')

        def resolve_temperature(self, value, parameters):
            """
            value - resolved from paramater
            parameters - parameters dict(in case other values are needed)
            """
            # convert value to Fahrenheit
            return (value * 9/5) + 32


As you can see, we've added a ``resolve_temperature`` method. It will be used to determine final value for ``temperature`` field. You can resolve any field this way, you just have to ensure that resolver name matches the field's name(eg. ``resolve_active`` for active field).

Every resolver method gets ``parameters`` object passed as the first argument, which is the same object you've passed in on ``MapObject`` creation.

Resolvers are being called from top to bottom, remember it when trying to access other values using resolvers.


Reusable temperature conversion field
-------------------------------------

If you need a reusable field that implements some special logic, you can create fields with custom resolving method:

.. code-block:: python

    from paramap.types import MapObject
    from paramap.fields import Float

    class Fahrenheit(Float):
        def resolve(self, celsius):
            """
            celsius value comes from parameter value
            """
            fahrenheit = (celsius * 9/5) + 32

            return super(FahrenheitTemp, self).resolve(fahrenheit)

    class Environment(MapObject):
        """
        Now temperature will be automatically converted to Fahrenheit
        """
        temperature = Fahrenheit(param='HOME_TEMPERATURE')
        humidity = Float(param='HOME_HUMIDITY')


Mapping values with Map field
--------------------------------------------

In some cases you could need a way to enumerate/directly map many different values with a dictionary. For example, let's suppose that our `Gate` can have many statuses.

Gate Statuses:

- 0 - CLOSED
- 1 - OPENED
- 10 - CLOSING
- 11 - OPENING
- 99 - ERROR

.. code-block:: python

   from paramap.types import MapObject
   from paramap.fields import String, Bool, Map

   class GateStatus(Map, String):
      def get_map(self):
         return {
            0: 'CLOSED',
            1: 'OPENED',
            10: 'CLOSING',
            11: 'OPENING',
            99: 'ERR',
        }
   
   class Gate(MapObject):
      status = GateStatus(param='HOME_GATE_STATUS')

Now our ``status`` field will resolve to string representation:

.. code-block:: python

    >>> parameters = { 'HOME_GATE_STATUS': 99}
    >>> gate = Gate(parameters=parameters)
    >>> gate.status
    'ERR'
