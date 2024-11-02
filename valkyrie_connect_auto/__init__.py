from argparse import ArgumentParser
from importlib import import_module

__version__ = "0.1.0"

STAGES = [
    "event",
    "dragon",
    "summon",
    "crystal",
    "click"
    ]

HEADER_HEIGHT_MAXIMIZED = 29
HEADER_HEIGHT = 38
BORDER = 1
SHADOW = 8

def cli():
    parser = ArgumentParser(prog="valkyrie-connect-auto", description="Valkyrie Connect Automation")
    parser.add_argument("stage", choices=STAGES, help="Stage")
    parser.add_argument("-d", "--double-drop-potion", type=int, default=5, help="Double Drop Potion")
    parser.add_argument("-l", "--loop", type=int, default=999, help="Repeat times")
    args = parser.parse_args()

    mod = import_module(f".{args.stage}", __package__)
    import pyautogui
    w = pyautogui.getWindowsWithTitle("Valkyrie Connect WW")[0]
    w.activate()
    w.resizeTo(1366 + 2*BORDER + 2* SHADOW, 768 - HEADER_HEIGHT_MAXIMIZED + HEADER_HEIGHT + BORDER + SHADOW)
    w.moveTo(0 - SHADOW - BORDER, 0)
    mod.start(args)
