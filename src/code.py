import gc
import supervisor

supervisor.disable_autoreload()
gc.collect()

print("BOOT [mem:{}]".format(gc.mem_free()))

import displayio
displayio.release_displays()
gc.collect()

import app
