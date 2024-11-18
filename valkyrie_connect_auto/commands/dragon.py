from time import sleep

import pyautogui
from ..auto import PopupHandler, NotFound

def start(args):
    w = args.w
    h = PopupHandler()

    @h.add("right-arrow")
    def _(r):
        w.click(r)
        sleep(0.5)

    @h.add("dragon-lv-up-ok")
    def _(r):
        w.click(r)
        w.click(r)
        sleep(0.5)

    @h.add("red-level", region=(1/3, 3/4, 2/3, 1))
    def _(r):
        w.click(r)

    @h.add("battle-join-error")
    @h.add("battle-join-error-2")
    def _(m):
        w.click(m, offset="50% 87%")

    for _i in range(args.loop):
        try:
            loop(w, h)
        except NotFound as err:
            # sometimes the starting process will be interrupted by the popup and we have to start from scratch
            if err.image_name == "battle":
                raise
        except KeyboardInterrupt:
            break

def loop(w, handler):
    w.click(w.wait("battle", handler=handler, timeout=300))
    match = w.wait("dragon-join")
    try:
        match.screenshot.find("dragon-create-cd", confidence=0.7)
    except pyautogui.ImageNotFoundException:
        start_create(w, match, handler)
    else:
        start_join(w, match)

def start_create(w, match, handler):
    w.click(match.screenshot.find("dragon-create"))
    r_multi = w.wait("multi", handler=handler)
    w.click(r_multi.screenshot.find("bonus"))
    third_opt = None
    r_unselect = None
    all_unselect = list(w.wait_all("unselect"))
    all_unselect.sort(key=lambda b: b.top)
    for r_unselect in all_unselect[1:]:
        click(r_unselect)
        if not third_opt:
            options = list(w.wait_all("select"))
            options.sort(key=lambda b: b.top)
            third_opt = options[2]
        w.click(third_opt)
    w.click(r_unselect.screenshot.find("bonus-ok"))
    w.click(r_multi)
    w.click(w.wait("cross-swords"))
    sleep(5)

def center(box):
    return (box.left + box.width / 2, box.top + box.height / 2)

def start_join(r):
    w.click(r)
    join_buttons = w.wait_all("battle-join")
    join_buttons.sort(key=lambda b: b.top)
    r_last = join_buttons[-1]
    for _ in range(5):
        pyautogui.moveTo(*center(r_last.box))
        w.drag(0, -300, 0.25)
    sleep(1)
    w.click(r_last)

    h = PopupHandler()
    @h.add("battle-join-error")
    @h.add("battle-join-error-2")
    def _(m):
        w.click(m, offset="50% 80%")
        buttons = w.wait_all("battle-join")
        buttons.sort(key=lambda b: b.top)
        w.click(buttons[-1])

    # if the previous click clicked on the level up screen, we have to click again 
    # FIXME: this is not the last battle
    @h.add("battle-join")
    def _(m):
        w.click(m)

    w.click(w.wait("join", handler=h))
    w.click(w.wait("cross-swords"))
    sleep(5)
