from contextlib import suppress
from time import sleep

def start(args):
    w = args.w
    with suppress(KeyboardInterrupt):
        for _i in range(args.loop):
            w.click(w.wait("retry", timeout=10*60))
            w.click(w.wait("retry-confirm"), offset="75% 75%")
            sleep(5)
