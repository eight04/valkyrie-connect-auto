from contextlib import suppress

def start(args):
    with suppress(KeyboardInterrupt):
        for _i in range(args.loop):
            args.w.click()
