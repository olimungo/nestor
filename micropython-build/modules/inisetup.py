import uos
from flashbdev import bdev

def check_bootsec():
    buf = bytearray(bdev.SEC_SIZE)
    bdev.readblocks(0, buf)
    empty = True
    for b in buf:
        if b != 0xFF:
            empty = False
            break
    if empty:
        return True
    fs_corrupted()

def fs_corrupted():
    import time

    while 1:
        print(
            """\
The filesystem starting at sector %d with size %d sectors looks corrupt.
You may want to make a flash snapshot and try to recover it. Otherwise,
format it with uos.VfsLfs2.mkfs(bdev), or completely erase the flash and
reprogram MicroPython.
"""
            % (bdev.start_sec, bdev.blocks)
        )
        time.sleep(3)


def setup():
    check_bootsec()
    print("Performing initial setup")
    uos.VfsLfs2.mkfs(bdev)
    vfs = uos.VfsLfs2(bdev)
    uos.mount(vfs, "/")
    with open("boot.py", "w") as f:
        f.write(
            """\
from machine import Pin
from time import sleep_ms

pin = Pin(2, Pin.OUT) # D4

from machine import reset
def rst():
    reset()

while True:
    pin.off()
    sleep_ms(200)
    pin.on()
    sleep_ms(150)
    pin.off()
    sleep_ms(200)
    pin.on()
    sleep_ms(800)
"""
        )
    return vfs
