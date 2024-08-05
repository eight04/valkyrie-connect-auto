from contextlib import suppress
from time import sleep

from pyautogui import ImageNotFoundException
from .auto import click, wait, get_text, find, PopupHandler

def start(args):
    h = PopupHandler()

    @h.add("out-of-ap")
    def _(r):
        raise Exception("Out of AP")

    @h.add("retry")
    def _(r):
        click(r)
        sleep(.5)

    @h.add("battle-start")
    def _(r):
        click(r)

        # the button is not cliackable during fade in animation
        h = PopupHandler()
        @h.add("battle-start")
        def _(r):
            click(r)

        click(wait("start-current-member", handler=h), x=2/3, y=7/8, clicks=2)
        sleep(5)

    with suppress(KeyboardInterrupt):
        for _i in range(args.loop):
            r = wait("challenge-again", timeout=10*60, handler=h)
            try:
                double = find(r, "drop-double")
            except ImageNotFoundException:
                pass
            else:
                text = get_text(double, offset=(110, 44), size=(56, 18))
                # breakpoint()
                try:
                    n = int(text)
                except ValueError:
                    pass
                else:
                    if n <= args.double_drop_potion:
                        click(double)
            click(r)
            sleep(5)
