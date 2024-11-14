from contextlib import suppress

import pyautogui

def start(args):
    with suppress(KeyboardInterrupt):
        for _i in range(args.loop):
            pyautogui.click()
