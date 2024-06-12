from contextlib import suppress
from time import sleep
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
            r = wait("drop-double", timeout=300, handler=h)
            text = get_text(r, offset=(110, 44), size=(56, 18))
            try:
                n = int(text)
            except ValueError:
                pass
            else:
                if n <= args.double_drop_potion:
                    click(r)
            click(find(r, "challenge-again"))
            sleep(5)
