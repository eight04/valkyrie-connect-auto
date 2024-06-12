import importlib.resources
from time import sleep
from datetime import datetime, timedelta
from collections import namedtuple

import pyautogui
import pyscreeze
from PIL import Image
from pyscreeze import Box

resources = importlib.resources.files("valkyrie_connect_auto.resources")

Match = namedtuple("WaitResult", ["screenshot", "box"])

BOX_KEY = lambda b: (b.left, b.top)

class NotFound(ValueError):
    def __init__(self, msg, image_name=None, origin=None):
        super().__init__(msg)
        self.image_name = image_name
        self.origin = origin

class PopupHandler:
    def __init__(self):
        self.handlers = {}

    def add(self, name):
        def _(f):
            self.handlers[name] = f
            return f
        return _

    def handle(self, r):
        for name, handler in self.handlers.items():
            try:
                r = find(r, name)
            except (pyscreeze.ImageNotFoundException, pyautogui.ImageNotFoundException):
                pass
            else:
                print(f"[PopupHandler] {name}")
                handler(r)
                return True
        return False

def _locate(im, im_screen, confidence):
    return Match(im_screen, pyautogui.locate(im, im_screen, confidence=confidence))

def wait(name, timeout=10, handler=None, confidence=0.9) -> Match:
    """Wait and return a match on the screen"""
    print(f"[wait] {name}")
    return _wait(name, timeout=timeout, handler=handler, confidence=confidence)

def _wait(name, timeout, handler, confidence, _locate=_locate):
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=timeout)
    err = None
    with Image.open(resources / f"{name}.png") as im:
        while datetime.now() < end_time:
            im_screen = pyautogui.screenshot()
            try:
                return _locate(im, im_screen, confidence)
            except (pyscreeze.ImageNotFoundException, pyautogui.ImageNotFoundException) as _err:
                err = _err
                handled = False
                if handler:
                    handled = handler.handle(Match(im_screen, None))
                if not handled:
                    sleep(1)
    raise NotFound(f"Image not found: {name}", origin=err, image_name=name)

def wait_all(name, timeout=10, handler=None, confidence=0.9, key=BOX_KEY) -> list[Match]:
    """Wait and return all matches on the screen"""
    print(f"[wait_all] {name}")
    def _locate_all(im, im_screen, confidence):
        l = list(pyautogui.locateAll(im, im_screen, confidence=confidence))
        l.sort(key=key)
        l = remove_similar_boxes(l)
        return [Match(im_screen, box) for box in l]
    return _wait(name, timeout=timeout, handler=handler, confidence=confidence, _locate=_locate_all)

def click(r, x=0.5, y=0.5, **kwargs):
    """Click on the center of the box"""
    pyautogui.click(r.box.left + r.box.width * x, r.box.top + r.box.height * y, **kwargs)
    sleep(0.25)

def box_to_bound(box: Box, offset, size) -> tuple:
    return (box.left + offset[0], box.top + offset[1], box.left + offset[0] + size[0], box.top + offset[1] + size[1])

def get_text(r, offset=(0, 0), size=None) -> str:
    """Get text from the match"""
    import pytesseract
    if not size:
        size = (r.box.width, r.box.height)
    try:
        text = pytesseract.image_to_string(r.screenshot.crop(box_to_bound(r.box, offset, size)), config="--psm 6")
    except pytesseract.pytesseract.TesseractNotFoundError:
        print("[get_text] Tesseract not available")
        return ""
    print(f"[get_text] {text}")
    return text

def find(r, name, confidence=0.9):
    """Find an image from a matched screen"""
    with Image.open(resources / f"{name}.png") as im:
        box = pyautogui.locate(im, r.screenshot, confidence=confidence)
        return Match(r.screenshot, box)

def remove_similar_boxes(boxes: list[Box]):
    if not boxes:
        return boxes
    result = [boxes[0]]
    for box in boxes[1:]:
        if not has_similar_pos(box, result[-1]):
            result.append(box)
    return result

def has_similar_pos(a, b):
    return abs(a.left - b.left) < 10 and abs(a.top - b.top) < 10

def find_all(r, name, key=BOX_KEY):
    """Find all images from a matched screen"""
    with Image.open(resources / f"{name}.png") as im:
        boxes = []
        for box in sorted(pyautogui.locateAll(im, r.screenshot, confidence=0.9), key=key):
            if boxes and has_similar_pos(box, boxes[-1]):
                continue
            boxes.append(box)
        return [Match(r.screenshot, box) for box in boxes]
