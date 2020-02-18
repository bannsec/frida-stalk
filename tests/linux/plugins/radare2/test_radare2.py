import logging

logger = logging.getLogger(__name__)

import os
import pytest
import revenge
types = revenge.types

from time import sleep

import r2pipe

here = os.path.dirname(os.path.abspath(__file__))
bin_location = os.path.join(here, "..", "..", "bins")

basic_one_path = os.path.join(bin_location, "basic_one")

def test_radare2_basic():
    process = revenge.Process(basic_one_path, resume=False, verbose=False)

    # r2 should kick off right away
    assert process.radare2._r2 is not None
    assert os.path.basename(process.radare2._r2.cmdj('ij')['core']['file']) == "basic_one"
    assert process.radare2.file == 'basic_one'

    local_r2 = r2pipe.open(basic_one_path)
    local_r2.cmd("=h& 54321")
    sleep(0.2) # Little race condition...
    process.radare2.connect("http://127.0.0.1:54321")
    assert os.path.basename(process.radare2._r2.cmdj('ij')['core']['file']) == "basic_one"
    assert process.radare2.file == 'basic_one'

    # Make sure it's actually connected
    local_r2.cmd('CC hello world @ 0x123')
    assert "hello world" in process.radare2._r2.cmd("CC.@0x123")

    timeless = process.techniques.NativeTimelessTracer()
    timeless.apply()
    t = list(timeless)[0]

    process.memory[process.entrypoint].breakpoint = False
    t.wait_for(process.memory['basic_one:0x692'].address) # ret

    # Send it off
    process.radare2.highlight(t)
    # No real way to test this rn :-(

    # There should be no functions without the analysis
    assert process.radare2._r2.cmd("afl").strip() == ""

    process.radare2.analyze()

    # entry0 and others should now be recognized
    assert "entry0" in process.radare2._r2.cmd("afl").strip()

    local_r2.quit()
    process.quit()
