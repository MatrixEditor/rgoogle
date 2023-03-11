.. _esa_api:

=========
ESA - API
=========

This part of the developer documentation contains usage information and 
implementation hints on the ``esa`` module and its components.

.. automodule:: rgoogle.esa

.. important::

    Decryption keys starting with version *10.0.0* are stored in the 
    ``rgoogle.esa.keys`` module together with their special file names.
    The keys can be retrieved either by accessing them directly or by 
    calling ``get_key(VERSION)``.

Usage
-----

The ``rgoogle.esa`` module is designed to be invoked directly. Therefore with the 
following command you can execute the ``esa`` module:

.. code:: console

    $ python3 -m rgoogle.esa --help

As of version :ref:`release-1.0.0` it is possible to decrypt ESA files directly on the 
command line interface. 

.. code-block:: console
    :caption: Decryption of an ESA file

    $ python3 -m rgoogle.esa -d esa_file.txt -V "10.0.0" -o decrypted.jar

Arguments:

-d                              Indicates whether an input should be decrypted
-o OUTPUT, --output OUTPUT      Specifies the output file
-v, --verbose                   Show console output
-f, --force                     Force override the file
-V VERSION, --version VERSION   The play-services-ads module version
-k KEY, --key KEY               Use the given decryption key instead (base64 encoded)


If you prefer to include the ``esa`` module directly in your project, the following
smaple illustrates its basic usage:

.. code-block:: python
    :linenos:

    from rgoogle.esa import get_key, DefaultCipher

    # First, we need the decryption key
    file_name, key = get_key("20.0.5")

    # Next, the encrypted content is needed (bytes)
    # Why? - see note below
    with open('encrypted.txt', 'rb') as ifp:
        encrypted = ifp.read()
    
    # Lastly, we have to create the cipher instance
    cipher = DefaultCipher(key, is_encoded=True)
    with open(f"{file_name}.jar", 'wb') as ofp:
        ofp.write(cipher.decrypt(encrypted))


.. note::

    Unfortunately, the input file stores the initialization vector used to 
    decrypt the JAR content. As the file is base64 encoded, the whole file 
    content has to be loaded first. 


Functions
---------

.. _get_key_link:

.. autofunction:: rgoogle.esa.get_key