import importlib.resources
from time import sleep
from datetime import datetime, timedelta
from collections import namedtuple
from typing import Callable, Any

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
        self.handlers = []

    def add(self, name, **kwargs):
        def _(f):
            self.handlers.append((name, f, kwargs))
            return f
        return _

    def handle(self, r):
        for (name, f, kwargs) in self.handlers:
            try:
                r = find(r, name, **kwargs)
            except (pyscreeze.ImageNotFoundException, pyautogui.ImageNotFoundException):
                pass
            else:
                print(f"[PopupHandler] {name}")
                f(r)
                return True
        return False

def region_to_box(size, region):
    width, height = size
    left, top, right, bottom = region
    return (
        round(left * width),
        round(top * height),
        round((right - left) * width),
        round((bottom - left) * height)
        )

def wait(name, timeout=10, handler=None, confidence=0.9, region=(0, 0, 1, 1)) -> Match:
    """Wait and return a match on the screen"""
    print(f"[wait] {name}")
    def _locate(im, im_screen):
        box = pyautogui.locate(
            im,
            im_screen,
            confidence=confidence,
            region=region_to_box(pyautogui.size(), region)
            )
        return Match(im_screen, box)
    return _wait(name, timeout=timeout, handler=handler, _locate=_locate)

def _wait(name, timeout, handler, _locate: Callable[[Image.Image, Image.Image], Any]):
    assert _locate
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=timeout)
    err = None
    with Image.open(resources / f"{name}.png") as im:
        while datetime.now() < end_time:
            im_screen = pyautogui.screenshot()
            try:
                return _locate(im, im_screen)
            except (pyscreeze.ImageNotFoundException, pyautogui.ImageNotFoundException) as _err:
                err = _err
                handled = False
                if handler:
                    handled = handler.handle(Match(im_screen, None))
                if not handled:
                    sleep(1)
    raise NotFound(f"Image not found: {name}", origin=err, image_name=name)

def wait_all(name, timeout=10, handler=None, confidence=0.9, key=BOX_KEY, region=(0, 0, 1, 1)) -> list[Match]:
    """Wait and return all matches on the screen"""
    print(f"[wait_all] {name}")
    def _locate_all(im, im_screen):
        l = list(pyautogui.locateAll(
            im,
            im_screen,
            confidence=confidence,
            region=region_to_box(pyautogui.size(), region)
            ))
        l = remove_similar_boxes(l)
        return [Match(im_screen, box) for box in l]
    return _wait(name, timeout=timeout, handler=handler, _locate=_locate_all)

def click(r, x=0.5, y=0.5, **kwargs):
    """Click on the center of the box"""
    target_x = r.box.left + r.box.width * x
    target_y = r.box.top + r.box.height * y
    print(f"[click] ({target_x}, {target_y})")
    pyautogui.click(target_x, target_y, **kwargs)
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

def find(r, name, confidence=0.9, region=(0, 0, 1, 1)):
    """Find an image from a matched screen"""
    with Image.open(resources / f"{name}.png") as im:
        box = pyautogui.locate(im, r.screenshot, confidence=confidence, region=region_to_box(pyautogui.size(), region))
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
