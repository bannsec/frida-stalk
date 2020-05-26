
from revenge import Colorer

import logging
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

import os
import random
import pytest

import revenge

types = revenge.types

here = os.path.dirname(os.path.abspath(__file__))
bin_location = os.path.join(here, "bins")

basic_one_path = os.path.join(bin_location, "basic_one")
basic_one_ia32_path = os.path.join(bin_location, "basic_one_ia32")
basic_struct_path = os.path.join(bin_location, "basic_struct")


def test_ctypes():
    process = revenge.Process(basic_struct_path, resume=False, verbose=False)

    assert types.Int8.ctype == "char"
    assert types.UInt8.ctype == "unsigned char"
    assert types.Char.ctype == "char"
    assert types.UChar.ctype == "unsigned char"
    assert types.Int16.ctype == "short"
    assert types.UInt16.ctype == "unsigned short"
    assert types.Short.ctype == "short"
    assert types.UShort.ctype == "unsigned short"
    assert types.Int32.ctype == "int"
    assert types.UInt32.ctype == "unsigned int"
    assert types.Int.ctype == "int"
    assert types.UInt.ctype == "unsigned int"
    assert types.Int64.ctype == "long"
    assert types.UInt64.ctype == "unsigned long"
    assert types.Long.ctype == "long"
    assert types.ULong.ctype == "unsigned long"
    assert types.Float.ctype == "float"
    assert types.Double.ctype == "double"
    assert types.Pointer.ctype == "void *"
    assert types.StringUTF8.ctype == "char *"

    process.quit()


def test_struct_calling():
    basic_struct = revenge.Process(basic_struct_path, resume=False, verbose=False)
    basic_struct_module = basic_struct.modules['basic_struct']

    struct = types.Struct()
    struct['d'] = types.Double
    struct['f'] = types.Float
    struct['i32'] = types.Int32
    struct['i8'] = types.Int8
    struct['pad1'] = types.Padding(1)
    struct['i16'] = types.Int16
    struct['pad2'] = types.Padding(4)
    struct['p'] = types.Pointer

    basic_struct_module.symbols['MyStructSizeOf'].memory.int32
    existing_instance = basic_struct_module.symbols['MyStructInstance'].memory
    struct.memory = existing_instance

    assert struct['d'] == 1.234
    assert struct['f'] == 1.2339999675750732
    assert struct['i32'] == -55
    assert struct['i8'] == 4
    assert struct['i16'] == -17
    assert struct['p'] == 0x123456

    #
    # Let the program return the value
    #

    basic_struct.memory.alloc_struct(struct)
    assert struct.memory.size == struct.sizeof

    return_double = basic_struct_module.symbols['return_double'].memory
    return_double.return_type = types.Double
    struct['d'] = 3.1415
    assert struct['d'] == 3.1415
    assert return_double(types.Pointer(struct)) == struct['d']

    return_float = basic_struct_module.symbols['return_float'].memory
    return_float.return_type = types.Float
    struct['f'] = 3.141592
    assert abs(struct['f'] - 3.141592) < 0.000001
    assert return_float(types.Pointer(struct)) == struct['f']

    return_i32 = basic_struct_module.symbols['return_i32'].memory
    return_i32.return_type = types.Int32
    struct['i32'] = 45124
    assert struct['i32'] == 45124
    assert return_i32(types.Pointer(struct)) == struct['i32']

    return_i8 = basic_struct_module.symbols['return_i8'].memory
    return_i8.return_type = types.Int8
    struct['i8'] = 11
    assert struct['i8'] == 11
    assert return_i8(types.Pointer(struct)) == struct['i8']

    return_i16 = basic_struct_module.symbols['return_i16'].memory
    return_i16.return_type = types.Int8
    struct['i16'] = -64
    assert struct['i16'] == -64
    assert return_i16(types.Pointer(struct)) == struct['i16']

    return_p = basic_struct_module.symbols['return_p'].memory
    return_p.return_type = types.Pointer
    struct['p'] = 0xcaf3bab3
    assert struct['p'] == 0xcaf3bab3
    assert return_p(types.Pointer(struct)) == struct['p']

    basic_struct.quit()


def test_struct_read_write():
    basic_one = revenge.Process(basic_one_path, resume=False, verbose=False, load_symbols='basic_one')

    struct = types.Struct()
    struct.add_member('test1', types.Int32(-5))
    struct.add_member('test2', types.Int8(-12))
    struct.add_member('test3', types.UInt16(16))
    struct.add_member('test4', types.Pointer(4444))
    struct.add_member('test5', types.Int16)  # This should cause warning
    struct.add_member('test6', types.Pointer(5555))

    assert struct['test1'] == -5
    assert struct['test2'] == -12
    assert struct['test3'] == 16
    assert struct['test4'] == 4444
    assert struct['test5'] == types.Int16
    assert struct['test6'] == 5555

    # writable = next(x for x in basic_one.memory.maps if x.writable)
    writable = basic_one.memory.alloc(1024)
    basic_one.memory[writable.address] = struct

    # Make it generic so we don't accidentally re-read our defined struct
    struct = types.Struct()
    struct.add_member('test1', types.Int32)
    struct.add_member('test2', types.Int8)
    struct.add_member('test3', types.UInt16)
    struct.add_member('test4', types.Pointer)
    struct.add_member('test5', types.Int16)  # This should cause warning
    struct.add_member('test6', types.Pointer)

    # Bind it to the memory address
    struct.memory = basic_one.memory[writable.address]

    assert struct['test1'] == -5
    assert struct['test2'] == -12
    assert struct['test3'] == 16
    assert struct['test4'] == 4444
    assert struct['test6'] == 5555

    struct['test1'] = -18
    assert struct['test1'] == -18
    struct['test2'] = 3
    assert struct['test2'] == 3
    struct['test3'] = 26
    assert struct['test3'] == 26
    struct['test4'] = 4545
    assert struct['test4'] == 4545
    struct['test6'] = 5454
    assert struct['test6'] == 5454

    struct = types.Struct()
    assert struct.name is None
    struct.name = "MyStruct"
    assert struct.name == "MyStruct"

    struct['test1'] = types.Int32
    struct['test2'] = types.Int8
    struct['test3'] = types.UInt16
    struct['test4'] = types.Pointer
    struct['test5'] = types.Int16  # This should cause warning
    struct['test6'] = types.Pointer

    str(struct)
    repr(struct)

    # Bind it to the memory address
    struct.memory = basic_one.memory[writable.address]

    assert struct['test1'] == -18
    assert struct['test2'] == 3
    assert struct['test3'] == 26
    assert struct['test4'] == 4545
    assert struct['test6'] == 5454

    # Just make sure it works...
    repr(struct)
    str(struct)

    basic_one.quit()


def test_struct_get_member_offset(caplog):
    basic_one = revenge.Process(basic_one_path, resume=False, verbose=False, load_symbols='basic_one')

    struct = types.Struct()
    struct.add_member('test1', types.Int32(-5))
    struct.add_member('test2', types.Int8(-12))
    struct.add_member('test3', types.UInt16(16))
    struct.add_member('test4', types.Pointer(4444))
    struct.add_member('test5', types.Int16)  # This should cause warning
    struct.add_member('test6', types.Pointer(5555))

    struct._process = basic_one

    assert struct._get_member_offset('test1') == 0
    assert struct._get_member_offset('test2') == 4
    assert struct._get_member_offset('test3') == 4 + 1
    assert struct._get_member_offset('test4') == 4 + 1 + 2
    assert struct._get_member_offset('test5') == 4 + 1 + 2 + 8
    assert struct._get_member_offset('test6') == 4 + 1 + 2 + 8 + 2

    basic_one.quit()


def test_sizeof():
    basic_one = revenge.Process(basic_one_path, resume=False, verbose=False, load_symbols='basic_one')
    basic_one_ia32 = revenge.Process(basic_one_ia32_path, resume=False, verbose=False, load_symbols='basic_one_ia32')

    assert types.Int8.sizeof == 1
    assert types.Int8(0).sizeof == 1
    assert types.UInt8.sizeof == 1
    assert types.UInt8(0).sizeof == 1
    assert types.Char.sizeof == 1
    assert types.Char(0).sizeof == 1
    assert types.UChar.sizeof == 1
    assert types.UChar(0).sizeof == 1

    assert types.Int16.sizeof == 2
    assert types.Int16(0).sizeof == 2
    assert types.UInt16.sizeof == 2
    assert types.UInt16(0).sizeof == 2
    assert types.Short.sizeof == 2
    assert types.Short(0).sizeof == 2
    assert types.UShort.sizeof == 2
    assert types.UShort(0).sizeof == 2

    assert types.Int32.sizeof == 4
    assert types.Int32(0).sizeof == 4
    assert types.UInt32.sizeof == 4
    assert types.UInt32(0).sizeof == 4
    assert types.Int.sizeof == 4
    assert types.Int(0).sizeof == 4
    assert types.UInt.sizeof == 4
    assert types.UInt(0).sizeof == 4

    assert types.Int64.sizeof == 8
    assert types.Int64(0).sizeof == 8
    assert types.UInt64.sizeof == 8
    assert types.UInt64(0).sizeof == 8
    assert types.Long.sizeof == 8
    assert types.Long(0).sizeof == 8
    assert types.ULong.sizeof == 8
    assert types.ULong(0).sizeof == 8

    assert types.Float.sizeof == 4
    assert types.Float(0).sizeof == 4
    assert types.Double.sizeof == 8
    assert types.Double(0).sizeof == 8

    with pytest.raises(revenge.exceptions.RevengeProcessRequiredError):
        types.Pointer().sizeof

    x = types.Pointer()
    x._process = basic_one
    assert x.sizeof == 8
    x._process = basic_one_ia32
    assert x.sizeof == 4

    with pytest.raises(revenge.exceptions.RevengeProcessRequiredError):
        types.StringUTF8().sizeof

    x = types.StringUTF8()
    x._process = basic_one
    assert x.sizeof == 8
    x._process = basic_one_ia32
    assert x.sizeof == 4

    with pytest.raises(revenge.exceptions.RevengeProcessRequiredError):
        types.StringUTF16().sizeof

    x = types.StringUTF16()
    x._process = basic_one
    assert x.sizeof == 8
    x._process = basic_one_ia32
    assert x.sizeof == 4

    with pytest.raises(revenge.exceptions.RevengeProcessRequiredError):
        types.Struct().sizeof

    #
    # Struct sizeof
    #

    x = types.Struct()
    x._process = basic_one
    assert x.sizeof == 0
    x._process = basic_one_ia32
    assert x.sizeof == 0

    x.add_member('test', types.Int32)
    assert x.sizeof == 4
    x.add_member('test2', types.Int8(4))
    assert x.sizeof == 5
    x.add_member('test3', types.Pointer)
    x._process = basic_one
    assert x.sizeof == 13
    x._process = basic_one_ia32
    assert x.sizeof == 9

    basic_one.quit()
    basic_one_ia32.quit()


def test_js_attr():

    for t in types.frida_types:
        i = random.randint(1, 0xff)
        x = t(i)

        if issubclass(type(x), types.Pointer):
            assert x.js == 'ptr("{}")'.format(hex(int(x)))

        elif issubclass(type(x), types.Int64):
            assert x.js == "int64('{}')".format(hex(int(x)))

        elif issubclass(type(x), types.UInt64):
            assert x.js == "uint64('{}')".format(hex(int(x)))

        else:
            assert x.js == str(x)


def test_types_attr():

    for t in types.frida_types:

        i = random.randint(1, 0xff)
        x = t(i)
        assert type(x + 3) == type(x)

        # Not sure exactly what to do with this rn
        print("Type: " + x.type)

    for t in [types.StringUTF8, types.StringUTF16]:
        x = t("something here")
