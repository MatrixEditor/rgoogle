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

import os
import sys
import argparse

from rgoogle.esa.cipher import DefaultCipher
from rgoogle.esa import get_key

def esa_decrypt(**kwargs):
    verbose = kwargs.get('verbose', False)
    key = kwargs.get('key', None)
    out_path = kwargs.get('output', None)
    if not out_path:
        print('WARN  - No output file specified - quitting...')
        sys.exit(1)

    if not key:
        version = kwargs.get('version', None)
        if verbose:
            print(f'INFO  - Getting key for version "{version}"')
        if not version:
            print('ERROR - A version must be specified')
            sys.exit(1)

        try:
            _, key = get_key(version)
        except ValueError as err:
            print(f'ERROR - {str(err)}')
            sys.exit(1)

    if not key:
        raise ValueError('Could not initialize secret key!')

    path = kwargs.get('file')
    if not path or not os.path.exists(path):
        raise FileNotFoundError(f'Could not locate file at {path}')

    if verbose:
        print('INFO  - Decrypting content...')
    try:
        cipher = DefaultCipher(key, is_encoded=True)
        with open(path, 'rb') as ifp:
            content = cipher.decrypt(ifp.read())
    except (ValueError, TypeError) as err:
        print(f'ERROR - [{type(err).__name__}] {str(err)}')
        sys.exit(1)

    if os.path.exists(out_path) and not kwargs.get('force', False):
        raise FileExistsError(f'File already exists at {out_path} (use -f to force override)')

    with open(out_path, 'wb') as ofp:
        ofp.write(content)
        if verbose:
            print('INFO  - Success!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--decrypt', action='store_true',
        help="Indicates whether an input should be decrypted")
    parser.add_argument('-v', '--verbose', help="Show console output", action='store_true')
    parser.add_argument('-o', '--output', help="Specifies the output file")

    d_group = parser.add_argument_group("Decryption Context")
    d_group.add_argument('file', help="The input file")
    d_group.add_argument('-f', '--force', help="Force override the file", action='store_true')

    dme_group = d_group.add_mutually_exclusive_group()
    dme_group.add_argument('-V', '--version', help="The play-services-ads module version",
        default=None)
    dme_group.add_argument('-k', '--key', help="Use the given key instead (base64 encoded)",
        default=None)

    args = parser.parse_args().__dict__

    if args['decrypt']:
        esa_decrypt(**args)