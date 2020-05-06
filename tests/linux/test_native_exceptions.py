
import os
import revenge
import logging
logging.basicConfig(level=logging.WARN)

logger = logging.getLogger(__name__)

types = revenge.types

here = os.path.dirname(os.path.abspath(__file__))
bin_location = os.path.join(here, "bins")

exceptions_path = os.path.join(bin_location, "exceptions")
exceptions_path_x86 = os.path.join(bin_location, "exceptions_x86")
dvb_path_x86 = os.path.join(bin_location, "dvb_i386_nocanary_nopie_elf")
dvb_path_x86_64 = os.path.join(bin_location, "dvb_x86_64_nocanary_nopie_elf")

#######
# x86 #
#######


def test_access_violation_x86_main_thread(caplog):
    p = revenge.Process(dvb_path_x86, resume=True, verbose=False)

    p.stdout("?> ")
    p.stdin("1\n")
    p.stdout("input: ")
    p.stdin("A"*128 + "\n")

    assert isinstance(list(p.threads)[0].exceptions, list)

    while list(p.threads)[0].exceptions == []:
        pass

    e = list(p.threads)[0].exceptions[0]
    str(e)
    repr(e)
    assert isinstance(e.context.pc, types.Telescope)
    assert e.type == 'access-violation'
    assert e.address.thing == 0x41414141

    while "Caught exception in thread" not in caplog.text:
        pass

    p.quit()


def test_arithmetic_x86():
    p = revenge.Process(exceptions_path_x86, resume=False, verbose=False)

    do_arithmetic = p.memory['exceptions_x86:do_arithmetic']
    do_good = p.memory['exceptions_x86:do_good']

    e = do_arithmetic()
    assert isinstance(e, revenge.native_exception.NativeException)
    str(e)
    repr(e)
    assert isinstance(e.context.pc, types.Telescope)
    assert e.type == 'arithmetic'
    # This abort is run by throwing the signal from libc
    assert p.modules[e.address].name == 'exceptions_x86'
    assert p.memory.describe_address(e.address).startswith("exceptions_x86:do_arithmetic")
    assert isinstance(e.backtrace, revenge.native_exception.NativeBacktrace)
    assert isinstance(e.context, revenge.cpu.contexts.x86.X86Context)

    # If we handled exception correctly, process should still be in good state
    assert not isinstance(do_good, revenge.native_exception.NativeException)

    p.quit()


def test_illegal_instruction_x86():
    p = revenge.Process(exceptions_path_x86, resume=False, verbose=False)

    do_ill = p.memory['exceptions_x86:do_ill']
    do_good = p.memory['exceptions_x86:do_good']

    e = do_ill()
    assert isinstance(e, revenge.native_exception.NativeException)
    str(e)
    repr(e)
    assert isinstance(e.context.pc, types.Telescope)
    assert e.type == 'illegal-instruction'
    # This abort is run by throwing the signal from libc
    assert 'linux-vdso' in p.modules[e.address].name
    assert isinstance(e.backtrace, revenge.native_exception.NativeBacktrace)
    assert isinstance(e.context, revenge.cpu.contexts.x86.X86Context)

    # If we handled exception correctly, process should still be in good state
    assert not isinstance(do_good, revenge.native_exception.NativeException)

    p.quit()


def test_abort_x86():
    p = revenge.Process(exceptions_path_x86, resume=False, verbose=False)

    do_abort = p.memory['exceptions_x86:do_abort']
    do_good = p.memory['exceptions_x86:do_good']

    e = do_abort()
    assert isinstance(e, revenge.native_exception.NativeException)
    str(e)
    repr(e)
    assert isinstance(e.context.pc, types.Telescope)
    assert e.type == 'abort'
    # This abort is run by throwing the signal from libc
    assert 'linux-vdso' in p.modules[e.address].name
    assert isinstance(e.backtrace, revenge.native_exception.NativeBacktrace)
    assert isinstance(e.context, revenge.cpu.contexts.x86.X86Context)

    # If we handled exception correctly, process should still be in good state
    assert not isinstance(do_good, revenge.native_exception.NativeException)

    p.quit()


def test_access_violation_x86():
    p = revenge.Process(exceptions_path_x86, resume=False, verbose=False)

    do_access_violation = p.memory['exceptions_x86:do_access_violation']
    do_good = p.memory['exceptions_x86:do_good']

    e = do_access_violation()
    assert isinstance(e, revenge.native_exception.NativeException)
    str(e)
    repr(e)
    assert isinstance(e.context.pc, types.Telescope)
    assert e.type == 'access-violation'
    # This abort is run by throwing the signal from libc
    assert 'exceptions' in p.modules[e.address].name
    assert p.memory.describe_address(e.address).startswith("exceptions_x86:do_access_violation")
    assert isinstance(e.backtrace, revenge.native_exception.NativeBacktrace)
    assert isinstance(e.context, revenge.cpu.contexts.x86.X86Context)

    # If we handled exception correctly, process should still be in good state
    assert not isinstance(do_good, revenge.native_exception.NativeException)

    p.quit()


def test_access_violation_read_x86():
    p = revenge.Process(exceptions_path_x86, resume=False, verbose=False)

    do_access_read_violation = p.memory['exceptions_x86:do_access_read_violation']
    do_good = p.memory['exceptions_x86:do_good']

    e = do_access_read_violation()
    assert isinstance(e, revenge.native_exception.NativeException)
    str(e)
    repr(e)
    assert isinstance(e.context.pc, types.Telescope)
    assert e.type == 'access-violation'
    # This abort is run by throwing the signal from libc
    assert p.modules[e.address].name == 'exceptions_x86'
    assert p.memory.describe_address(e.address).startswith("exceptions_x86:do_access_read_violation")
    assert isinstance(e.backtrace, revenge.native_exception.NativeBacktrace)
    assert isinstance(e.context, revenge.cpu.contexts.x86.X86Context)

    assert e.memory_address == 0x666
    assert e.memory_operation == 'read'

    # If we handled exception correctly, process should still be in good state
    assert not isinstance(do_good, revenge.native_exception.NativeException)

    p.quit()


def test_access_violation_execute_x86():
    p = revenge.Process(exceptions_path_x86, resume=False, verbose=False)

    do_access_exec_violation = p.memory['exceptions_x86:do_access_exec_violation']
    do_good = p.memory['exceptions_x86:do_good']

    e = do_access_exec_violation()
    assert isinstance(e, revenge.native_exception.NativeException)
    str(e)
    repr(e)
    assert isinstance(e.context.pc, types.Telescope)
    assert e.type == 'access-violation'
    # 0x666 shouldn't be in any module
    assert p.modules[e.address] is None
    assert p.memory.describe_address(e.address) == "0x666"
    assert isinstance(e.backtrace, revenge.native_exception.NativeBacktrace)
    assert isinstance(e.context, revenge.cpu.contexts.x86.X86Context)

    assert e.memory_address == 0x666
    assert e.memory_operation == 'execute'

    # If we handled exception correctly, process should still be in good state
    assert not isinstance(do_good, revenge.native_exception.NativeException)

    p.quit()


def test_int3_x86():
    p = revenge.Process(exceptions_path_x86, resume=False, verbose=False)

    do_int3 = p.memory['exceptions_x86:do_int3']
    do_good = p.memory['exceptions_x86:do_good']

    e = do_int3()
    assert isinstance(e, revenge.native_exception.NativeException)
    str(e)
    repr(e)
    assert isinstance(e.context.pc, types.Telescope)
    assert e.type == 'breakpoint'

    assert p.modules[e.address].name == 'exceptions_x86'
    assert p.memory.describe_address(e.address).startswith("exceptions_x86:do_int3")
    assert isinstance(e.backtrace, revenge.native_exception.NativeBacktrace)
    assert isinstance(e.context, revenge.cpu.contexts.x86.X86Context)

    # If we handled exception correctly, process should still be in good state
    assert not isinstance(do_good, revenge.native_exception.NativeException)

    p.quit()


def test_sigsys_x86():
    p = revenge.Process(exceptions_path_x86, resume=False, verbose=False)

    do_sigsys = p.memory['exceptions_x86:do_sigsys']
    do_good = p.memory['exceptions_x86:do_good']

    e = do_sigsys()
    assert isinstance(e, revenge.native_exception.NativeException)
    str(e)
    repr(e)
    assert isinstance(e.context.pc, types.Telescope)
    assert e.type == 'system'

    assert 'linux-vdso' in p.modules[e.address].name
    assert p.memory.describe_address(e.address).startswith("linux-vdso")
    assert isinstance(e.backtrace, revenge.native_exception.NativeBacktrace)
    assert isinstance(e.context, revenge.cpu.contexts.x86.X86Context)

    # If we handled exception correctly, process should still be in good state
    assert not isinstance(do_good, revenge.native_exception.NativeException)

    p.quit()

#########
# amd64 #
#########


def test_arithmetic_amd64():
    p = revenge.Process(exceptions_path, resume=False, verbose=False)

    do_arithmetic = p.memory[p.modules['exceptions'].symbols['do_arithmetic']]
    do_good = p.memory[p.modules['exceptions'].symbols['do_good']]

    e = do_arithmetic()
    assert isinstance(e, revenge.native_exception.NativeException)
    str(e)
    repr(e)
    assert isinstance(e.context.pc, types.Telescope)
    assert e.type == 'arithmetic'
    # This abort is run by throwing the signal from libc
    assert p.modules[e.address].name == 'exceptions'
    assert p.memory.describe_address(e.address).startswith("exceptions:do_arithmetic")
    assert isinstance(e.backtrace, revenge.native_exception.NativeBacktrace)
    assert isinstance(e.context, revenge.cpu.contexts.x64.X64Context)

    # If we handled exception correctly, process should still be in good state
    assert not isinstance(do_good, revenge.native_exception.NativeException)

    p.quit()


def test_illegal_instruction_amd64():
    p = revenge.Process(exceptions_path, resume=False, verbose=False)

    do_ill = p.memory[p.modules['exceptions'].symbols['do_ill']]
    do_good = p.memory[p.modules['exceptions'].symbols['do_good']]

    e = do_ill()
    assert isinstance(e, revenge.native_exception.NativeException)
    str(e)
    repr(e)
    assert isinstance(e.context.pc, types.Telescope)
    assert e.type == 'illegal-instruction'
    # This abort is run by throwing the signal from libc
    assert 'libc' in p.modules[e.address].name
    assert isinstance(e.backtrace, revenge.native_exception.NativeBacktrace)
    assert isinstance(e.context, revenge.cpu.contexts.x64.X64Context)

    # If we handled exception correctly, process should still be in good state
    assert not isinstance(do_good, revenge.native_exception.NativeException)

    p.quit()


def test_abort_amd64():
    p = revenge.Process(exceptions_path, resume=False, verbose=False)

    do_abort = p.memory[p.modules['exceptions'].symbols['do_abort']]
    do_good = p.memory[p.modules['exceptions'].symbols['do_good']]

    e = do_abort()
    assert isinstance(e, revenge.native_exception.NativeException)
    str(e)
    repr(e)
    assert isinstance(e.context.pc, types.Telescope)
    assert e.type == 'abort'
    # This abort is run by throwing the signal from libc
    assert 'libc' in p.modules[e.address].name
    assert isinstance(e.backtrace, revenge.native_exception.NativeBacktrace)
    assert isinstance(e.context, revenge.cpu.contexts.x64.X64Context)

    # If we handled exception correctly, process should still be in good state
    assert not isinstance(do_good, revenge.native_exception.NativeException)

    p.quit()


def test_access_violation_amd64():
    p = revenge.Process(exceptions_path, resume=False, verbose=False)

    do_access_violation = p.memory[p.modules['exceptions'].symbols['do_access_violation']]
    do_good = p.memory[p.modules['exceptions'].symbols['do_good']]

    e = do_access_violation()
    assert isinstance(e, revenge.native_exception.NativeException)
    str(e)
    repr(e)
    assert isinstance(e.context.pc, types.Telescope)
    assert e.type == 'access-violation'
    # This abort is run by throwing the signal from libc
    assert 'exceptions' in p.modules[e.address].name
    assert p.memory.describe_address(e.address).startswith("exceptions:do_access_violation")
    assert isinstance(e.backtrace, revenge.native_exception.NativeBacktrace)
    assert isinstance(e.context, revenge.cpu.contexts.x64.X64Context)

    # If we handled exception correctly, process should still be in good state
    assert not isinstance(do_good, revenge.native_exception.NativeException)

    p.quit()


def test_access_violation_amd64_main_thread(caplog):
    p = revenge.Process(dvb_path_x86_64, resume=True, verbose=False)

    p.stdout("?> ")
    p.stdin("1\n")
    p.stdout("input: ")
    p.stdin("A"*128 + "\n")

    assert isinstance(list(p.threads)[0].exceptions, list)

    while list(p.threads)[0].exceptions == []:
        pass

    e = list(p.threads)[0].exceptions[0]
    str(e)
    repr(e)
    assert isinstance(e.context.pc, types.Telescope)
    assert e.type == 'access-violation'
    assert e.context.ip.next.thing.mnemonic == "ret"
    assert e.context.rbp.thing == 0x4141414141414141

    while "Caught exception in thread" not in caplog.text:
        pass

    p.quit()


def test_access_violation_read_amd64():
    p = revenge.Process(exceptions_path, resume=False, verbose=False)

    do_access_read_violation = p.memory[p.modules['exceptions'].symbols['do_access_read_violation']]
    do_good = p.memory[p.modules['exceptions'].symbols['do_good']]

    e = do_access_read_violation()
    assert isinstance(e, revenge.native_exception.NativeException)
    str(e)
    repr(e)
    assert isinstance(e.context.pc, types.Telescope)
    assert e.type == 'access-violation'
    # This abort is run by throwing the signal from libc
    assert p.modules[e.address].name == 'exceptions'
    assert p.memory.describe_address(e.address).startswith("exceptions:do_access_read_violation")
    assert isinstance(e.backtrace, revenge.native_exception.NativeBacktrace)
    assert isinstance(e.context, revenge.cpu.contexts.x64.X64Context)

    assert e.memory_address == 0x666
    assert e.memory_operation == 'read'

    # If we handled exception correctly, process should still be in good state
    assert not isinstance(do_good, revenge.native_exception.NativeException)

    p.quit()


"""
def test_access_violation_write():
    # Frida bug: https://github.com/frida/frida/issues/987

    do_access_write_violation = p.memory[p.modules['exceptions'].symbols['do_access_write_violation']]
    do_good = p.memory[p.modules['exceptions'].symbols['do_good']]

    e = do_access_write_violation()
    assert isinstance(e, revenge.native_exception.NativeException)
    str(e)
    repr(e)
    assert e.type == 'access-violation'
    # This abort is run by throwing the signal from libc
    assert p.modules[e.address].name == 'exceptions'
    assert p.memory.describe_address(e.address).startswith("exceptions:do_access_write_violation")
    assert isinstance(e.backtrace, revenge.native_exception.NativeBacktrace)
    assert isinstance(e.context, revenge.cpu.contexts.x64.X64Context)

    assert e.memory_address == 0x666
    assert e.memory_operation == 'write'

    # If we handled exception correctly, process should still be in good state
    assert not isinstance(do_good, revenge.native_exception.NativeException)
"""


def test_access_violation_execute_amd64():
    p = revenge.Process(exceptions_path, resume=False, verbose=False)

    do_access_exec_violation = p.memory[p.modules['exceptions'].symbols['do_access_exec_violation']]
    do_good = p.memory[p.modules['exceptions'].symbols['do_good']]

    e = do_access_exec_violation()
    assert isinstance(e, revenge.native_exception.NativeException)
    str(e)
    repr(e)
    assert isinstance(e.context.pc, types.Telescope)
    assert e.type == 'access-violation'
    # 0x666 shouldn't be in any module
    assert p.modules[e.address] is None
    assert p.memory.describe_address(e.address) == "0x666"
    assert isinstance(e.backtrace, revenge.native_exception.NativeBacktrace)
    assert isinstance(e.context, revenge.cpu.contexts.x64.X64Context)

    assert e.memory_address == 0x666
    assert e.memory_operation == 'execute'

    # If we handled exception correctly, process should still be in good state
    assert not isinstance(do_good, revenge.native_exception.NativeException)

    p.quit()


def test_int3_amd64():
    p = revenge.Process(exceptions_path, resume=False, verbose=False)

    do_int3 = p.memory[p.modules['exceptions'].symbols['do_int3']]
    do_good = p.memory[p.modules['exceptions'].symbols['do_good']]

    e = do_int3()
    assert isinstance(e, revenge.native_exception.NativeException)
    str(e)
    repr(e)
    assert isinstance(e.context.pc, types.Telescope)
    assert e.type == 'breakpoint'

    assert p.modules[e.address].name == 'exceptions'
    assert p.memory.describe_address(e.address).startswith("exceptions:do_int3")
    assert isinstance(e.backtrace, revenge.native_exception.NativeBacktrace)
    assert isinstance(e.context, revenge.cpu.contexts.x64.X64Context)

    # If we handled exception correctly, process should still be in good state
    assert not isinstance(do_good, revenge.native_exception.NativeException)

    p.quit()


def test_sigsys_amd64():
    p = revenge.Process(exceptions_path, resume=False, verbose=False)

    do_sigsys = p.memory[p.modules['exceptions'].symbols['do_sigsys']]
    do_good = p.memory[p.modules['exceptions'].symbols['do_good']]

    e = do_sigsys()
    assert isinstance(e, revenge.native_exception.NativeException)
    str(e)
    repr(e)
    assert isinstance(e.context.pc, types.Telescope)
    assert e.type == 'system'

    assert 'libc' in p.modules[e.address].name
    assert p.memory.describe_address(e.address).startswith("libc")
    assert isinstance(e.backtrace, revenge.native_exception.NativeBacktrace)
    assert isinstance(e.context, revenge.cpu.contexts.x64.X64Context)

    # If we handled exception correctly, process should still be in good state
    assert not isinstance(do_good, revenge.native_exception.NativeException)

    p.quit()
