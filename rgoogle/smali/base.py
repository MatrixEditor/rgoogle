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
import re

from enum import Enum, IntFlag

__all__ = [
    'AccessType', 'Token', 'Line', 'Type',
    'smali_value', 'SmaliType'
]

class AccessType(IntFlag):
    PUBLIC = 0x1
    PRIVATE = 0x2
    PROTECTED = 0x4
    STATIC = 0x8
    FINAL = 0x10
    SYNCHRONIZED = 0x20
    VOLATILE = 0x40
    BRIDGE = 0x80
    TRANSIENT = 0x100
    VARARGS = 0x200
    NATIVE = 0x400
    INTERFACE = 0x800
    ABSTRACT = 0x1000
    STRICTFP = 0x2000
    SYNTHETIC = 0x4000
    ANNOTATION = 0x8000
    ENUM = 0x10000
    CONSTRUCTOR = 0x20000
    DECLARED_SYNCHRONIZED = 0x40000
    SYSTEM = 0x80000
    RUNTIME = 0x100000

    @staticmethod
    def get_flags(values: list) -> int:
        result = 0
        for element in values:
            for val in AccessType:
                if val.name.lower().replace('_', '-') == element:
                    result |= val.value
        return result

    @staticmethod
    def get_names(flags: int) -> list:
        result = []
        for val in AccessType:
            if flags in val:
                result.append(val.name.lower().replace('_', '-'))
        return result

    @staticmethod
    def find(value: str) -> bool:
        for val in AccessType:
            name = val.name.lower().replace('_', '-')
            if name == value:
                return True
        return False

    def __contains__(self, other: int) -> bool:
        if isinstance(other, self.__class__):
            return super().__contains__(other)
        if isinstance(other, int):
            return self.value & other != 0
        raise TypeError(f"Unsupported type: {type(other)}")

class Token(Enum):
    ANNOTATION = 'annotation'
    ARRAYDATA = 'array-data'
    CATCH = 'catch'
    CATCHALL = 'catchall'
    CLASS = 'class'
    END = 'end'
    ENUM = 'enum'
    FIELD = 'field'
    IMPLEMENTS = 'implements'
    LINE = 'line'
    LOCAL = 'local'
    LOCALS = 'locals'
    METHOD = 'method'
    PACKEDSWITCH = 'packed-switch'
    PARAM = 'param'
    PROLOGUE = 'prologue'
    REGISTERS = 'registers'
    RESTART = 'restart'
    SOURCE = 'source'
    SPARSESWITCH = 'sparse-switch'
    SUBANNOTATION = 'subannotation'
    SUPER = 'super'

    def __eq__(self, other: str) -> bool:
        if isinstance(other, self.__class__):
            return super().__eq__(other)
        return self.value == other

    def __ne__(self, other: str) -> bool:
        if isinstance(other, self.__class__):
            return super().__ne__(other)
        return self.value != other

    def __len__(self) -> int:
        return len(str(self.value))

    def __str__(self) -> str:
        return self.value

class Line:
    """Simple peekable Iterator implementation."""

    RE_EOL_COMMENT = re.compile(r"\s*#.*")
    """PAttern for EOL (end of line) comments"""

    _default = object()
    """The default object which is returned to indicate the
    end of the current line has been reached."""

    raw: str
    """The raw line as it was passed through the constructor."""

    cleaned: str
    """The cleaned line without any leading and trailing whitespace"""

    eol_comment: str
    """The removed trailing EOL comment (if present)"""

    def __init__(self, line: str) -> None:
        if isinstance(line, (bytearray, bytes)):
            line = line.decode()

        self._it = None
        self._head = self._default
        self.reset(line)

    def _get_next(self) -> str:
        try:
            return next(self._it)
        except StopIteration:
            return self._default

    def __next__(self) -> str:
        value = self._head
        if value == self._default:
            raise StopIteration()

        self._head = self._get_next()
        return value

    def reset(self, line: str = None) -> None:
        """Resets this line and/or initialized it with the new value.

        :param line: the next line, defaults to None
        :type line: str, optional
        """
        if not line:
            self._head = self._default
            self._it = None
            return

        self.eol_comment = None
        self.raw = line.rstrip()
        self.cleaned = self.raw.lstrip()
        eol_match = Line.RE_EOL_COMMENT.search(self.cleaned)
        if eol_match is not None:
            start, end = eol_match.span()
            # Remove the EOL comment and save it in a variable. Note
            # that the visitor will be notified when StopIteration is
            # raised.
            self.eol_comment = eol_match.group(0).lstrip('# ')
            self.cleaned = self.cleaned[:start] + self.cleaned[end:]

        self._it = iter(self.cleaned.split(' '))
        self._head = self._get_next()

    def peek(self, default: str = _default) -> str:
        """Returns the current element if this line.

        This method won't move forwards.

        :param default: the default value to return, defaults to _default
        :type default: str, optional
        :raises StopIteration: if the end of this line has been reached
        :return: the current value
        :rtype: str
        """
        if self._head == self._default:
            if default != self._default:
                return default
            raise StopIteration()
        return self._head

    def last(self) -> str:
        """Returns the last element of this line without modifying the iterator.

        :return: the last element
        :rtype: str
        """
        return self.cleaned.split(' ')[-1]

    def has_eol(self) -> bool:
        """Returns whether this line contains an EOL comment

        :return: True, if the line contains an EOL comment
        :rtype: bool
        """
        return self.eol_comment is not None

    def __bool__(self) -> bool:
        return self._head != self._default

    def has_next(self) -> bool:
        """Returns whether there as a following element.

        :return: True if next() can be called safely
        :rtype: bool
        """
        return self.__bool__()

    def __len__(self) -> int:
        return len(self.cleaned)

class Type:
    """Basic type definition that can handle both class and method types.
    """

    CLINIT = '<clinit>'
    """Static block initializer"""
    
    INIT = '<init>'
    """Constructor method"""

    def __init__(self, signature: str) -> None:
        self.__signature = signature

    @property
    def internal_name(self) -> str:
        """Returns the internal name of this type.

        :return: the internal name used in the DVM (e.g. "Lcom/example/ABC;")
        :rtype: str
        """
        return self.__signature

    @property
    def type_name(self) -> str:
        """Returns the type name without 'L' and ';'

        :return: the type name
        :rtype: str
        """
        if ';' not in self.__signature and 'L' not in self.__signature:
            return self.__signature
        return self.__signature[1:-1]

    @property
    def class_name(self) -> str:
        """Returns the Smali class name equivalent to Smali class names.

        :return: the class name (e.g. "com.example.ABC")
        :rtype: str
        """
        return self.type_name.replace('/', '.')

    def get_method_name(self) -> str:
        """Returns the method name

        :return: the absolute method name
        :rtype: str
        """
        idx = self.__signature.find('(')
        if idx == -1:
            raise TypeError(
                f'Invalid method signature: could not find name ({self.__signature})')

        # Handle bracket names if not <clinit> or <init>
        name = self.__signature[:idx]
        if name in (Type.INIT, Type.CLINIT):
            return name
        return name.rstrip('>').lstrip('<')

    def get_method_params(self) -> list:
        """Returns the method parameter internal names.

        :return: the method parameters
        :rtype: list
        """
        start = self.__signature.find('(')
        end = self.__signature.find(')')
        if start == -1 or end == -1:
            raise TypeError('Invalid method signature')

        params = self.__signature[start+1:end]
        if not params:
            return []

        param_list = []
        idx = 0
        is_type = False
        current = ""
        while idx < len(params):
            if params[idx] == 'L':
                is_type = True
            elif params[idx] == ';':
                is_type = False
                current += ';'
                param_list.append(current)
                current = ""
                idx += 1
                continue
            elif params[idx] == '[':
                current += '['
                idx += 1
                continue

            if is_type:
                current += params[idx]
            else:
                param_list.append(params[idx])
            idx += 1

        return param_list

    def get_method_return_type(self) -> str:
        end = self.__signature.find(')')
        if end == -1:
            raise TypeError('Invalid method signature')
        return self.__signature[end+1:]

def smali_value(value: str) -> 'SmaliType':
    sm_value = SmaliType()
    sm_value.value = value
    sm_value.actual_value = None
    for i, entry in enumerate(SmaliType.TYPE_MAP):
        matcher, wrapper = entry
        if matcher.match(sm_value.value):
            if i <= 3: # hex value possible
                hex_val = SmaliType.RE_HEX_VALUE.match(value) is not None
                if not hex_val:
                    sm_value.actual_value = wrapper(value)
                else:
                    sm_value.actual_value = wrapper(value, base=16)
            else:
                sm_value.actual_value = wrapper(value)
            break

    # Handling of null values is not implemented yet
    if not sm_value.actual_value:
        raise ValueError(f"Could not find any matching primitive type for {value}")

    sm_locals = {}
    for key in __smali_builtins__:
        if hasattr(sm_value.actual_value, key):
            sm_locals[key] = getattr(sm_value.actual_value, key)

    vars(sm_value).update(sm_locals)
    return sm_value

class SmaliType:
    """Wrapper class for primitives in Smali.

    Use this class to retrieve the actual primitiva value for a parsed
    source code snippet. As this class overrides most of the internal
    special functions, objects of this class can be used as regualar
    strings or numeric values:

    >>> value = SmaliValue("1234")
    1234
    >>> value += 1
    1235

    The same behaviour applies to parsed strings (note that you need
    quotation marks):

    >>> string = SmaliValue('"Hello World"')
    'Hello World'
    >>> len(string)
    11
    """

    RE_INT_VALUE = re.compile(r"[\-\+]?(0x)?\d+")
    RE_BYTE_VALUE = re.compile(r"[\-\+]?(0x)?\d+t$")
    RE_SHORT_VALUE = re.compile(r"[\-\+]?(0x)?\d+s$")
    RE_FLOAT_VALUE = re.compile(r"[\-\+]?(0x)?\d+\.\d+f$")
    RE_DOUBLE_VALUE = re.compile(r"[\-\+]?(0x)?\d+\.\d+")
    RE_LONG_VALUE = re.compile(r"[\-\+]?(0x)?\d+l$")
    RE_CHAR_VALUE = re.compile(r"^'\w*'$")
    RE_STRING_VALUE = re.compile(r'^"\w*"$')
    RE_TYPE_VALUE = re.compile(r"\[*((L\S*;$)|([ZCBSIFJD])$)") # NOQA
    RE_BOOL_VALUE = re.compile(r"true|false")

    RE_HEX_VALUE = re.compile(r"0x\d+")

    TYPE_MAP: list = [
        (RE_SHORT_VALUE, int),
        (RE_LONG_VALUE, int),
        (RE_BYTE_VALUE, int),
        (RE_INT_VALUE, int),
        (RE_BOOL_VALUE, lambda x: x == 'true'),
        (RE_FLOAT_VALUE, float),
        (RE_DOUBLE_VALUE, float),
        (RE_CHAR_VALUE, lambda x: str(x[1:-1])),
        (RE_STRING_VALUE, lambda x: str(x[1:-1])),
        (RE_TYPE_VALUE, Type)
    ]

    value: str
    """The initial source code value (string)"""

    actual_value = None
    """The actual value of any type"""
    
    @staticmethod
    def is_type_descriptor(value: str) -> bool:
        return SmaliType.RE_TYPE_VALUE.match(value) is not None

__smali_builtins__ = [
    "__contains__", "__eq__", "__ne__", "__len__", "__str__",
    "__next__", "__bool__", "__repr__", "__str__", "__bytes__",
    "__format__", "__lt__", "__le__", "__eq__", "__ne__", "__gt__", "__ge__",
    "__hash__", "__bool__", "__len__", "__length_hint__", "__getitem__",
    "__setitem__", "__delitem__", "__missing__", "__iter__", "__reversed__",
    "__contains__", "__add__", "__sub__", "__mul__", "__truediv__",
    "__floordiv__", "__mod__", "__divmod__", "__lshift__", "__rshift__",
    "__and__", "__xor__", "__or__", "__radd__", "__rsub__", "__rmul__",
    "__rtruediv__", "__rfloordiv__", "__rmod__", "__rdivmod__", "__rlshift__",
    "__rrshift__", "__rand__", "__rxor__", "__ror__", "__neg__", "__pos__",
    "__abs__", "__invert__", "__complex__", "__int__", "__float__", "__index__",
    "__trunc__", "__floor__", "__ceil__",
]

__smali_specials__ = [
    ("__iadd__", lambda x,y: x+y),
    ("__isub__", lambda x,y: x-y),
    ("__imul__", lambda x,y: x*y),
    ("__itruediv__", lambda x,y: x/y),
    ("__ifloordiv__", lambda x,y: x//y),
    ("__imod__", lambda x,y: x%y),
    ("__ilshift__", lambda x,y: x<<y),
    ("__irshift__", lambda x,y: x>>y),
    ("__iand__", lambda x,y: x&y),
    ("__ixor__", lambda x,y: x^y),
    ("__ior__", lambda x,y: x|y)
]

for method in __smali_builtins__:
    setattr(SmaliType, method,
        lambda self, *args, method=method: self.__dict__[method](*args)
    )

for method, func in __smali_specials__:
    setattr(SmaliType, method,
        lambda self, val, func=func: func(self.actual_value, val))

del method
del func
