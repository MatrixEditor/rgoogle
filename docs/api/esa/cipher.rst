.. _esa_cipher:

==========
ESA Cipher
==========

.. automodule:: rgoogle.esa.cipher

.. autoclass:: rgoogle.esa.DefaultCipher
    :members:

To decode default keys provided in ``rgoogle.esa.keys``, the following function can be used:

.. autofunction:: rgoogle.esa.cipher.decode_key


    A sample usage would be

    .. code-block:: python
        :linenos:

        from rgoogle.esa import keys, decode_key

        # Keys are stored in tuples
        file_name, key = keys.v15_0

        real_key = decode_key(key)
