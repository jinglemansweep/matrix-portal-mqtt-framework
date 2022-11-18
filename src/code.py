import gc

gc.collect()

print("BOOT [mem:{}]".format(gc.mem_free()))

import displayio

displayio.release_displays()

import app
