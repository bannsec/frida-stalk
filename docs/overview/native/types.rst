=====
Types
=====

``revenge`` defines it's own types to better understand what data it is
looking at. This means, while in many cases you can pass native python
types to methods and fields, sometimes you will need to pass an instantiated
type instead.

See :doc:`types doc <../../api/native/types>`.

Examples
========

.. code-block:: python3

    from revenge import types

    # Create some ints
    i = types.Int32(0)
    i2 = types.UInt64(12)

    # You can optionally read memory as a type instead of using memory attributes
    assert process.memory[0x12345].cast(types.Int32) ==  process.memory[0x12345].int32


Structs
=======
The :class:`~revenge.types.Struct` type is a little different from the rest of
the types. Specifically, it defines a C structure, rather than a specific type.
A struct can be defined by itself first, and then "bound" to a memory address.

The behavior of structs is to be used like dictionary objects.

.. note::
    
    Compilers have NO standardization for struct padding. If your struct is not
    displaying correctly, check if you need to add type.Padding in between
    some elements.

Examples
--------

.. code-block:: python3
    
    # Create a struct
    my_struct = types.Struct()
    my_struct.add_member('member_1', types.Int)
    my_struct.add_member('member_2', types.Pointer)

    # Alternatively, add them IN ORDER via dict setter
    my_struct = types.Struct()
    my_struct['member_1'] = types.Int
    my_struct['member_2'] = types.Pointer

    # Use cast to bind your struct to a location
    my_struct = process.memory[0x12345].cast(my_struct)

    # Or set memory property directly
    my_struct.memory = process.memory[0x12345]

    # Read out the values
    my_struct['member_1']
    my_struct['member_2']

    # Write in some new values (this will auto-cast based on struct def)
    my_struct['member_1'] = 12

    # Print out some detail about it
    print(my_struct)
    """
    struct {
      test1 = -18;
      test2 = 3;
      test3 = 26;
      test4 = 4545;
      test5 = 3;
      test6 = 5454;
    }
    """

    # There's also a short-hand way to get space for your struct on the heap
    struct = process.memory.alloc_struct(struct)
    
    # It's bound to that address now, use it as above.
    # Using this struct as an argument to a function call, you will likely
    # want to wrap it as a pointer.
    func = process.memory[<something>]
    func(types.Pointer(my_struct))

Telescope
=========
The :class:`~revenge.types.Telescope` class is a meta-ish class that holds
other types. Specifically, it's goal is to address the question of how to
describe and handle the concept of "telescoping" variables. With this in mind,
often you do not create this directly, but will get it from certain tracer
techniques.

Interaction with this class is effectively using the ``thing`` and ``next``
properties. Where ``thing`` is a holder for whatever the current thing is and
``next`` is the next one. Also, ``type`` will help inform you what to expect in
the variable.

Example
-------

.. code-block:: python3
    
    # Telescope down into address 0x12345
    scope = revenge.types(process, 0x12345)
    scope.thing
    scope.next
