from argparse import ArgumentParser

__VERSION__ = "0.0.0"

def cli():
    parser = ArgumentParser(prog="valkyrie-connect-auto", description="Valkyrie Connect Automation")
    parser.add_argument("stage", choices=["event", "dragon"], help="Stage")
    parser.add_argument("-d", "--double-drop-potion", type=int, default=5, help="Double Drop Potion")
    parser.add_argument("-l", "--loop", type=int, default=999, help="Repeat times")
    args = parser.parse_args()

    if args.stage == "event":
        from .event import start
        start(args)

    elif args.stage == "dragon":
        from .dragon import start
        start(args)
