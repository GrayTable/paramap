
.. _Registry Overview:

Schema Registry
===============

Paramap offers an option to track existing ``MapObject`` classes through ``Registry`` class and ``register(registry=None)`` class decorator.


Register decorator
------------------
To register ``MapObject`` class, decorate it with ``register(registry=None)`` decorator.

.. code-block:: python

    from paramap import registry

    @registry.register(registry=None)
    class Person(MapObject):
        first_name = String(param='FIRST_NAME')
        last_name = String(param='LAST_NAME')


By default, ``register`` uses global paramap registry.

Global Registry
---------------

You can get global registry instance by using ``get_global_registry`` function.

.. code-block:: python

    from paramap import registry

    global_paramap_registry = registry.get_global_registry()

    print(global_paramap_registry.schemas)
    # output:
    # {
    #   'Person': <__main__.Person object at ...>
    # }


Custom Registry
---------------

You can define your own registries with `paramap.registry.Registry` class.

.. code-block:: python

    from paramap import registry

    global_registry = registry.get_global_registry()
    local_registry = registry.Registry()


    registry.register(registry=local_registry)
    class Person(MapObject):
        pass


    print(global_registry.schemas)
    # output: {}

    print(local_registry.schemas)
    # output:
    # {
    #   'Person': <__main__.Person object at ...>
    # }