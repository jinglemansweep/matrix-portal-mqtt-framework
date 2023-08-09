import gc
import supervisor

supervisor.runtime.autoreload = False
gc.collect()

print("BOOT [mem:{}]".format(gc.mem_free()))

import displayio
displayio.release_displays()
gc.collect()

import app
