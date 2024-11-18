from ..auto import PopupHandler

def start(args):
    w = args.w
    h = PopupHandler()

    @h.add("summon-reward")
    def _(r):
        w.click(r, offset="0 0")

    @h.add("skip", padding="0 0 80% 80%")
    def _(r):
        w.click(r)

    for _i in range(args.loop):
        try:
            loop(w, h)
        except KeyboardInterrupt:
            break

def loop(w, handler):
    w.click(w.wait("summon-again", handler=handler, timeout=300))
    w.click(w.wait("summon-confirm"), offset="66% 87%")
