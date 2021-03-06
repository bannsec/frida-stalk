.. _techniques-page:

==========
Techniques
==========

In ``revenge`` parlance, a :class:`~revenge.techniques.Technique` is a high
level set of actions that should be performed on the running binary. For
instance, instead of manually deciding how you need to hide yourself from
debugging checks, a technique could be applied that specifically attempts to do
that. They're effectively high level batches of actions to be parformed with a
single goal in mind.

Types of Techniques
===================

There are two main types of techniques, due to how these techniques may be
implemented:

Stalk Techniques
----------------

These techniques require the use of per-thread stalking. The important thing to
note here is that you can only have one stalker running on a thread at a time.
That means, you can only use one of these techniques at a time.

Replace Techniques
------------------

These techniques utilize binary re-writing prior to thread execution. The
important thing to realize here is that these changes will affect all threads,
since they are not thread specific. You can, however, have as many of these
techniques running at a time as you like, since they do not take up a stalker
context.

General Technique Usage
=======================

Specifics of technique usage may vary from technique to technique, the general
usage remains the same. The steps are:

#. Start your process
#. Select the technique from ``process.techniques.<technique>()``
#. :meth:`~revenge.techniques.Technique.apply` your technique

   a. If it is a stalking technique, you may want to provide the threads to the
   apply function
#. (optionally) :meth:`~revenge.techniques.Technique.remove` the technique at some point.

Techniques for specific calls
-----------------------------

It's possible to apply a technique for specific calls. For instance, where you
would use a native call to a function like ``time(0)``, you can also provide a
``techniques`` argument with a single (or list) of techniques to apply to the
specific call.

Details can be found under :class:`~revenge.memory.MemoryBytes` documentation.

Implemented Techniques
======================

For a list of techniques and more information, see :ref:`techniques`.

How To Create a Technique
=========================

Creating a new technique is relatively strait forward:

#. Create a new submodule in ``revenge/techniques``
#. Create your technique class by extending ``revenge.techniques.Technique``
#. Implement ``apply`` and ``remove`` methods
#. Make sure ``TYPE`` is defined in your class
#. In the ``__init__.py``, be sure that you expose the ``Technique`` you
   created. It can be any name, so long as the class instantiator is visible.
#. docs and tests

``revenge`` will auto-discover the technique at runtime and expose it.
