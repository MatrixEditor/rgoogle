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

from rgoogle.esa.cipher import *
from rgoogle.esa import keys

def get_key(version: str) -> tuple:
    """Returns the key and file name for the given version

    :param version: the version string
    :type version: str
    :raises ValueError: if the version string is invalid
    :raises ValueError: if no key could be found
    :return: the file name and decryption key
    :rtype: tuple
    """
    parts = version.split('.')
    if len(parts) < 2:
        raise ValueError('Version must contain at least 2 numbers')
    
    for name, value in keys.__dict__.items():
        if not name.startswith('v'):
            continue
        
        name_parts = name[1:].split('_')
        if name_parts[0] == parts[0] and name_parts[1] == parts[1]:
            return value
    
    raise ValueError(f"Key for version '{version}' not found!")

