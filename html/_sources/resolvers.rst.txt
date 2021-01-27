
.. _Resolvers Overview:

Resolvers
=========

Sometimes when parsing data you need to include values that are not directly present in the source data, but can be derived from other available values, they also might need special rules when being resolved.

In Paramap this issue is being solved by the use of ``resolvers``. If you've ever used ``graphene``, you should be familiar with this concept.

.. code-block:: python

    class Person(MapObject):
        first_name = String(param='FIRST_NAME')
        last_name = String(param='LAST_NAME')
        full_name = String()

        def resolve_full_name(self, value, parameters):
            # full_name attribute will be resolved based
            # on other values
            return self.first_name + ' ' + last_name

Looking at the example above, you should be able to notice three things:

- there is a resolver method ``resolve_full_name`` in ``Person`` class
- resolver takes two arguments ``value`` and ``parameters``
- resolver name matches attribute name it corresponds to eg. ``resolver_attr_name``, in this case ``full_name``


Arguments and return value
----------------------------
Each resolver gets two argument passed into it:

- ``value`` - value with which the field resolved with
- ``parameters`` - an entire parameter dictionary passed into the root ``MapObject``

Resolvers should return a value compatible with the field they are resolving.

Naming and resolution order
---------------------------

Resolvers naming is imporant. Name should always start with ``resolve_`` and end with field name. Resolvers will be fired from top to bottom.

.. code-block:: python

    class JohnDoe(MapObject):
        first_name = String()
        lastName = String()     # notice field name is not in snake_case
        full_name = String()

        def resolve_first_name(self, value, parameters):
            # I will be fired first!
            # self.first_name = None
            # self.lastName = None
            # self.full_name = None

            return 'John'
        
        def resolve_lastName(self, value, parameters):
            # I will be fired second! Notice my name is not in snake case.
            # self.first_name = 'John'
            # self.lastName = None
            # self.full_name = None

            return 'Doe'
        
        def resolve_full_name(self, value, paramaters):
            # I will be fired last!
            # self.first_name = 'John'
            # self.lastName = 'Doe'
            # self.full_name = None

            return self.first_name + ' ' + self.last_name
