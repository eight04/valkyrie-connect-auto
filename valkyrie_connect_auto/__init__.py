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

CLIENT_SIZE = (1366, 745)

def cli():
    parser = ArgumentParser(prog="valkyrie-connect-auto", description="Valkyrie Connect Automation")
    parser.add_argument("stage", choices=STAGES, help="Stage")
    parser.add_argument("-d", "--double-drop-potion", type=int, default=5, help="Double Drop Potion")
    parser.add_argument("-l", "--loop", type=int, default=999, help="Repeat times")
    args = parser.parse_args()

    mod = import_module(f".commands.{args.stage}", __package__)
    from .window import Window
    with Window("Valkyrie Connect WW", size=CLIENT_SIZE) as w:
        args.w = w
        mod.start(args)
