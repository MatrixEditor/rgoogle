# Copyright (C) 2023 MatrixEditor

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Decryption algorithm implementation.

Use this module to decrypt embedded shared archive files (ESA) that
have been placed into your Android application.
"""

import base64

from cryptography.hazmat.primitives.ciphers import (
    Cipher,
    algorithms,
    modes
)

__all__ = [
    'decode_key', 'DefaultCipher'
]


def decode_key(content) -> bytes:
    """Decodes the given input bytes with base64.

    Applies a simple XOR mechanism on the returned byte array afterwards.

    :param content: the encoded key
    :type content: str | bytes
    :raises ValueError: if the decoded input does not match a length of 32 bytes.
    :raises TypeError: if the input type is not bytes or str
    :raises ValueError: if the input content is null
    :return: the decoded content with a length of 16 bytes
    :rtype: bytes
    """
    if not content:
        raise ValueError('Invalid content (nullptr)')

    if isinstance(content, str):
        encoded_key = content.encode()
    elif isinstance(content, (bytearray, bytes)):
        encoded_key = content
    else:
        raise TypeError(f'Unexpected input type: {type(content)}')

    decoded_key = base64.b64decode(encoded_key)
    if len(decoded_key) != 32:
        raise ValueError(f'Invalid key length, got {len(decoded_key)} - expected 32')

    decoded_key = decoded_key[4:20]
    result = [0 for _ in range(16)]
    for i, val in enumerate(decoded_key):
        result[i] = val ^ 68
    return bytes(result)


class DefaultCipher:
    """Basic implementation of a cipher engine.

    Is it using the default cipher instance of `AES/CBC/PKCS5Padding` for
    decryption and encryption.


    The following workflow illustrates how this cipher engine decrypts an input
    JAR-file with a SecretKey:
    
    >>>         +-----------------------+
    >>>         | encrypted JAR: byte[] |
    >>>         +----------+------------+
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

    """

    def __init__(self, key: bytes = None, is_encoded=False) -> None:
        self.__key: algorithms.AES = None
        if key:
            self.set_key(key, is_encoded)

    def set_key(self, key: bytes, is_encoded=False):
        """Sets a new secret key.

        :param key: the new key
        :type key: bytes
        :param is_encoded: whether the key should be decoded first, defaults to False
        :type is_encoded: bool, optional
        :raises ValueError: if the key is null
        :raises TypeError: if the key is not a string or bytes object
        """
        if not key:
            raise ValueError('Invalid key (nullptr)')

        if not isinstance(key, (str, bytes, bytearray)):
            raise TypeError(f'Invalid key type: {type(key)}')

        if isinstance(key, str):
            key = key.encode()

        self.__key = algorithms.AES(decode_key(key) if is_encoded else key)

    @property
    def key(self) -> algorithms.AES:
        """Returns the SecretKey instance of this cipher.

        :return: the secret key
        :rtype: algorithms.AES
        """
        return self.__key

    def decrypt(self, content: bytes) -> bytes:
        """Decrypts the given bytes by applying the stored `SecretKey`.

        :param content: the file content
        :type content: bytes
        :raises ValueError: if the decoded buffer is not at least 17 bytes long
        :return: the decrypted content
        :rtype: bytes
        """
        decoded = base64.decodebytes(content)
        if len(decoded) <= 16:
            raise ValueError(
                f'Invalid buffer length, got {len(decoded)} - expected at least 17 bytes')

        ivector = decoded[:16]
        content_buffer = decoded[16:]

        cipher = Cipher(self.key, modes.CBC(ivector)) # NOQA
        decryptor = cipher.decryptor()

        return decryptor.update(content_buffer) + decryptor.finalize()
