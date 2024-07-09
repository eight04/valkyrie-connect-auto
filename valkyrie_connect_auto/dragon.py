from time import sleep

import pyautogui
from .auto import click, wait, find, wait_all, PopupHandler, NotFound

def start(args):
    h = PopupHandler()

    @h.add("right-arrow")
    def _(r):
        click(r)
        sleep(0.5)

    @h.add("dragon-lv-up-ok")
    def _(r):
        click(r)
        click(r)
        sleep(0.5)

    @h.add("red-level", region=(1/3, 3/4, 2/3, 1))
    def _(r):
        click(r)

    @h.add("battle-join-error")
    @h.add("battle-join-error-2")
    def _(m):
        click(m, y=7/8)

    for _i in range(args.loop):
        try:
            loop(h)
        except NotFound as err:
            # sometimes the starting process will be interrupted by the popup and we have to start from scratch
            if err.image_name == "battle":
                raise
        except KeyboardInterrupt:
            break

def loop(handler):
    click(wait("battle", handler=handler, timeout=300))
    r = wait("dragon-join")
    try:
        find(r, "dragon-create-cd", confidence=0.7)
    except pyautogui.ImageNotFoundException:
        start_create(r)
    else:
        start_join(r)

def start_create(r):
    click(find(r, "dragon-create"))
    r_multi = wait("multi")
    click(find(r_multi, "bonus"))
    third_opt = None
    r_unselect = None
    for r_unselect in wait_all("unselect", key=lambda b: b.top)[1:]:
        click(r_unselect)
        if not third_opt:
            third_opt = wait_all("select", key=lambda b: b.top)[2]
        click(third_opt)
    click(find(r_unselect, "bonus-ok"))
    click(r_multi)
    click(wait("cross-swords"))
    sleep(5)

def center(box):
    return (box.left + box.width / 2, box.top + box.height / 2)

def start_join(r):
    click(r)
    r_last = wait_all("battle-join", key=lambda b: b.top)[-1]
    for _ in range(5):
        pyautogui.moveTo(*center(r_last.box))
        pyautogui.drag(0, -300, 0.25)
    sleep(1)
    click(wait_all("battle-join", key=lambda b: b.top)[-1])

    h = PopupHandler()
    @h.add("battle-join-error")
    @h.add("battle-join-error-2")
    def _(m):
        click(m, y=0.8)
        click(wait_all("battle-join", key=lambda b: b.top)[-1])

    click(wait("join", handler=h))
    click(wait("cross-swords"))
    sleep(5)
