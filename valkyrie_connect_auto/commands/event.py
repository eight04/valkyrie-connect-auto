from contextlib import suppress
from time import sleep

from pyautogui import ImageNotFoundException
from pyscreeze import Box

from ..auto import get_text, PopupHandler

def start(args):
    w = args.w
    h = PopupHandler()

    @h.add("out-of-ap")
    def _(r):
        raise Exception("Out of AP")

    @h.add("inventory-full", confidence=0.8)
    def _(r):
        raise Exception("Inventory Full")

    @h.add("retry")
    def _(match):
        w.click(match)
        sleep(.5)

    @h.add("battle-start")
    def _(r):
        w.click(r)

        # the button is not cliackable during fade in animation
        h = PopupHandler()
        @h.add("battle-start")
        def _(r):
            w.click(r)

        match = w.wait("start-current-member", handler=h)
        for _ in range(2):
            w.click(match, offset="66% 87%")
        sleep(5)

    with suppress(KeyboardInterrupt):
        for _i in range(args.loop):
            match = w.wait("challenge-again", timeout=10*60, handler=h)
            try:
                double = match.screenshot.find("drop-double")
            except ImageNotFoundException:
                pass
            else:
                text = get_text(double, region=Box(110, 44, 56, 18)).strip()
                if text.endswith("]") or text.endswith(")"):
                    text = text[:-1]
                # breakpoint()
                try:
                    n = int(text)
                except ValueError:
                    pass
                else:
                    if n <= args.double_drop_potion:
                        w.click(double)
            w.click(match)
            sleep(5)
