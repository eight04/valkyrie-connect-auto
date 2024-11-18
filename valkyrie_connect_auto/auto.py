import importlib.resources
import time
import functools

import pyautogui
import pyscreeze
from PIL.Image import Image, open as open_image
from pyscreeze import Box

resources = importlib.resources.files("valkyrie_connect_auto.resources")

AllImageNotFoundException = (pyautogui.ImageNotFoundException, pyscreeze.ImageNotFoundException)

class Offset:
    def __init__(self, text):
        self.tokens = []
        for token in text.split():
            if token.endswith("%"):
                self.tokens.append((float(token[:-1]), "%"))
            else:
                self.tokens.append((int(token), "px"))
        if len(self.tokens) < 2:
            self.tokens.append(self.tokens[0])

    def __call__(self, box: Box):
        return (
            box.left + apply_unit(box.width, self.tokens[0]),
            box.top + apply_unit(box.height, self.tokens[1]))

class Match:
    def __init__(self, screenshot=None, top=None, left=None, width=None, height=None):
        self.screenshot = screenshot
        self.top = top
        self.left = left
        self.width = width
        self.height = height

    def __lt__(self, other):
        if self.left < other.left:
            return True
        if self.left > other.left:
            return False
        return self.top < other.top

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

    def handle(self, screenshot):
        for (name, f, kwargs) in self.handlers:
            try:
                match = find(screenshot, name, **kwargs)
            except AllImageNotFoundException:
                pass
            else:
                print(f"[PopupHandler] {name}")
                f(match)
                return True
        return False

class Screenshot:
    def __init__(self, image, top, left, width, height):
        self.image = image
        self.top = top
        self.left = left
        self.width = width
        self.height = height

    def find(self, *args, **kwargs):
        return find(self, *args, **kwargs)

    def find_all(self, *args, **kwargs):
        return find_all(self, *args, **kwargs)

def apply_unit(base, token):
    value, unit = token
    if unit == "%":
        return round(base * value / 100)
    return value

@functools.lru_cache
def padding_to_region(padding, width, height):
    if not padding:
        return None

    tokens = []
    for token in padding.split():
        if token.endswith("%"):
            tokens.append((float(token[:-1]), "%"))
        else:
            tokens.append((int(token), "px"))

    if len(tokens) == 3:
        tokens.append(tokens[1])
    elif len(tokens) < 4:
        for i in range(4 - len(tokens)):
            tokens.append(tokens[i])

    return (
        apply_unit(width, tokens[3]),
        apply_unit(height, tokens[0]),
        width - apply_unit(width, tokens[1]),
        height - apply_unit(height, tokens[2]),
        )

class ScreenshotChecker:
    def __init__(self, needle_image: str, timeout=10, handler=None, confidence=0.9, padding=None, interval=1):
        self.needle_image = needle_image
        self.timeout = timeout
        self.handler = handler
        self.confidence = confidence
        self.interval = interval
        self.padding = padding

    def get_screenshot(self):
        image = pyautogui.screenshot()
        # FIMXE: what if there are multiple monitors?
        return Screenshot(image, 0, 0, image.width, image.height)

    def wait(self):
        return self._wait(self.locate)

    def wait_all(self):
        return self._wait(self.locate_all)

    def _wait(self, _locate):
        print(f"[wait] {self.needle_image}")
        start = time.time()
        with open_image(resources / f"{self.needle_image}.png") as needle:
            while True:
                screenshot = self.get_screenshot()
                try:
                    return _locate(screenshot, needle)
                except AllImageNotFoundException as e:
                    if time.time() - start > self.timeout:
                        raise NotFound(f"Failed to find {self.needle_image}", self.needle_image, e) from e
                    if self.handler:
                        if self.handler.handle(screenshot):
                            start = time.time()
                    time.sleep(self.interval)

    def locate(self, screenshot, image):
        return screenshot.find(image, confidence=self.confidence, padding=self.padding)

    def locate_all(self, screenshot, image):
        return screenshot.find_all(image, confidence=self.confidence, padding=self.padding)


def wait(*args, **kwargs) -> Match:
    """Wait and return a match on the screen"""
    return ScreenshotChecker(*args, **kwargs).wait()

def wait_all(*args, **kwargs) -> list[Match]:
    """Wait and return all matches on the screen"""
    return ScreenshotChecker(*args, **kwargs).wait_all()

def click(box, offset=Offset("50%")):
    """Click on the center of the box"""
    if isinstance(offset, str):
        offset = Offset(offset)
    target_x, target_y = offset(box)
    while True:
        try:
            print(f"[click] ({target_x}, {target_y})")
            pyautogui.click(target_x, target_y)
        except pyautogui.FailSafeException:
            print("[click] Failsafe")
            time.sleep(0.25)
            continue
        break
    time.sleep(0.25)

def box_to_bound(box: Box, offset, size) -> tuple:
    return (box.left + offset[0], box.top + offset[1], box.left + offset[0] + size[0], box.top + offset[1] + size[1])

def get_text(match, region: Box | None = None) -> str:
    """Get text from the match"""
    import pytesseract
    if not region:
        region = Box(match.left, match.top, match.width, match.height)
    cropped_image = match.screenshot.image.crop(box=(
        match.left + region.left - match.screenshot.left,
        match.top + region.top - match.screenshot.top,
        match.left + region.left + region.width - match.screenshot.left,
        match.top + region.top + region.height - match.screenshot.top
        ))
    # cropped_image.save("cropped.png")
    try:
        text = pytesseract.image_to_string(cropped_image, config="--psm 7")
    except pytesseract.pytesseract.TesseractNotFoundError:
        print("[get_text] Tesseract not available")
        return ""
    print(f"[get_text] {text}")
    return text

def find(screenshot, image: Image | str, confidence=0.9, padding=None):
    """Find an image from a matched screen"""
    if not isinstance(image, Image):
        with open_image(resources / f"{image}.png") as im:
            return find(screenshot, im, confidence, padding)
    box = pyautogui.locate(
        image,
        screenshot.image,
        confidence=confidence,
        region=padding_to_region(padding, screenshot.width, screenshot.height)
        )
    assert box
    return Match(
        screenshot,
        top=screenshot.top + box.top,
        left=screenshot.left + box.left,
        width=box.width,
        height=box.height
        )

def find_all(screenshot, image: Image | str, confidence=0.9, padding=None):
    """Find all images from a matched screen"""
    if not isinstance(image, Image):
        with open_image(resources / f"{image}.png") as im:
            return find_all(screenshot, im, confidence, padding)
    boxes = pyautogui.locateAll(
        image,
        screenshot.image,
        confidence=confidence,
        region=padding_to_region(padding, screenshot.width, screenshot.height)
        )
    boxes = list(boxes)
    boxes = remove_similar_boxes(boxes)
    return [Match(
        screenshot,
        top=screenshot.top + box.top,
        left=screenshot.left + box.left,
        width=box.width,
        height=box.height
        ) for box in boxes]

def remove_similar_boxes(boxes: list[Box]):
    if not boxes:
        return boxes
    result = [boxes[0]]
    # FIXME: this is O(n^2)
    for box in boxes[1:]:
        if any(has_similar_pos(box, r) for r in result):
            continue
        result.append(box)
    return result

def has_similar_pos(a, b):
    return abs(a.left - b.left) < 10 and abs(a.top - b.top) < 10

