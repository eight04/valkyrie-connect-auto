from contextlib import suppress
from time import sleep

from pyautogui import ImageNotFoundException
from .auto import click, wait, get_text, find, PopupHandler

def start(args):
    h = PopupHandler()
    @h.add("retry")
    def _(r):
        click(r)
        sleep(.5)

    @h.add("battle-start")
    def _(r):
        click(r)
        click(wait("start-current-member"), x=2/3, y=7/8, clicks=2)
        sleep(5)

    with suppress(KeyboardInterrupt):
        for _i in range(args.loop):
            r = wait("challenge-again", timeout=300, handler=h)
            try:
                double = find(r, "drop-double")
            except ImageNotFoundException:
                pass
            else:
                text = get_text(double, offset=(110, 44), size=(56, 18))
                try:
                    n = int(text)
                except ValueError:
                    pass
                else:
                    if n <= args.double_drop_potion:
                        click(r)
            click(r)
            sleep(5)
