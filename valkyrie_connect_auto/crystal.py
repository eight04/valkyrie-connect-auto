from contextlib import suppress
from time import sleep

from .auto import click, wait

def start(args):
    with suppress(KeyboardInterrupt):
        for _i in range(args.loop):
            click(wait("retry", timeout=10*60))
            click(wait("retry-confirm"), x=3/4, y=3/4)
            sleep(5)
