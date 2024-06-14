from .auto import click, wait, PopupHandler

def start(args):
    h = PopupHandler()

    @h.add("summon-reward")
    def _(r):
        click(r, 0, 0)

    @h.add("skip", region=(0.8, 0, 1, 0.2))
    def _(r):
        click(r)

    for _i in range(args.loop):
        try:
            loop(h)
        except KeyboardInterrupt:
            break

def loop(handler):
    click(wait("summon-again", handler=handler, timeout=300))
    click(wait("summon-confirm"), x=2/3, y=7/8)
