.. _esa:

=============================
Embedded Shared Archive (ESA)
=============================

When using Google's Play-Services-Ads Android library, there is a hidden 
JAR-File added to the app since version 10.0.0. These shadowed JAR files
will be called Embedded Shared Archive (ESA) files. The name refers to an
encrypted JAR file stored in a Java-class.

Dynamic DEX-Loading
-------------------

When using the ``play-services-ads`` module directly in an Android app,
a DEX-File with additional compiles Java-Classes will be loaded. The basic
importing and loading process can be summarized to:

1. Phase: Decryption
    Decrypt the stored JAR file (ecrypted as AES-String within the app's source code)

    .. caution:: 
        
        The decryption key as well as the special timestamp is hardcoded in 
        each version of the ``play-services-ads`` module. Therefore, decryption can be
        done by just inspecting the decompiled source code.

2. Phase: Temporary Storage
    If not already present, save the decrypted JAR file content in a file with a special 
    timestamp as its name to the ``/cache`` or ``/dex`` directory. These folders will be 
    created in the private app's directory.

3. Phase: Extraction
    Extract the ``classes.dex`` file stored inside the decrypted JAR file and
    save it with the same special timestamp as its name.

4. Phase: Import
    With an instance of ``DexClassLoader`` the saved DEX-File is loaded into the
    running app.

5. (Last) Phase: Cleanup
    All files that have been saved to the app's private directory will be removed
    afterwards.


Decryption flow
---------------

The internal Google-Cipher is using the a cipher instance of *AES/CBC/PKCS5Padding* for
encryption and decryption.

The following graph illustrates how the custom cipher decrypts an input JAR-file (ESA)
with a SecretKey:
    
>>>         +-----------------------------+
>>>         | encrypted JAR (ESA): byte[] |
>>>         +----------+------------------+
>>>                    |
>>>                    |
>>>                    | Base64.decode()
>>>                    |
>>>                    |
>>>         +----------v---+-----------------------+
>>>         | iv: byte[16] | encrypted JAR: byte[] |
>>>         +----------+---+-----------------------+
>>>                    |
>>>                    | AESCipher.init(secretKey, iv)
>>>                    |
>>>                    | AESCipher.doFinal()
>>>                    |
>>>         +----------v------------+
>>>         | decrypted JAR: byte[] |
>>>         +-----------------------+


Collected Data by Google
------------------------

Below is a list of data that can be collected by Google vie extra classes that have
been loaded at runtime of an Android app. Note that most of the time data is sent 
in an encrypted form or compressed with the ProtoBuf library by Google.

* ``MotionEvent``: Collects information about a given MotionEvent. 
    By default, the following information are extracted:

    - ``elapsedTime``: time since the user has pressed
    - ``pressure``: pressure of the fired event
    - ``windowObscured``: indicates that the window that received this motion event is partlyor wholly obscured by another visible window above it
    - ``historicalPressure``: historical pressure coordinates
    - ``x``: x position in relation to the given metrics
    - ``y``: y position in relation to the given metrics
    - ``touchMajor``: length of the major axis of an ellipse that describes the touch area
    - ``historicalTouchMajor``: historical touch major axis coordinates
    - ``source``: the event's source
    - ``toolType``: the type of tool used to make contact
    - ``deviceId``: id for the device that the motion event came from

* ``uptimeMillis``: Queries information about the uptime since last boot of the device.
* ``availableProcessors``: The amount of available processors
* ``date``: The current date as a timestamp
* ``screen``: (width/height/orientation) The device's screen-width, height and orientation
* ``battery``: (status/level) Information about the current battery status. The returned array contains information about the current battery status, charging level and temperature.
* ``model``: the constant according to the current model (either ``NORMAL_DEVICE``, ``ROOTED_DEVICE`` or ``EMULATOR_DEVICE``)
* ``usbStatus``: Whether the device is connected via a USB-cable.
* ``adbEnabled``: Whether ADB is enabled
* ``android-id``: Android-ID (AAID)
* ``usesProxy``: Whether the running app is using a global HTTP-Proxy
* ``processInfo``: Whether the app is running in foreground
