import time
from ctypes import windll

import win32gui
import win32ui
import win32con
import win32api
import win32process

from PIL import Image
import pyautogui

from .auto import ScreenshotChecker, Screenshot, Offset

class WindowScreenshotChecker(ScreenshotChecker):
    def __init__(self, window, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.window = window

    def get_screenshot(self):
        self.window.update_screenshot()
        return Screenshot(
            self.window.screenshot,
            self.window.top,
            self.window.left,
            self.window.width,
            self.window.height
            )

class Window:
    def __init__(self, title):
        self.hwnd = win32gui.FindWindow(None, title)
        if not self.hwnd:
            raise ValueError(f"Window not found: {title}")
        self.update_box()
        self.hwndDC = win32gui.GetWindowDC(self.hwnd)
        self.mfcDC  = win32ui.CreateDCFromHandle(self.hwndDC)
        self.saveDC = self.mfcDC.CreateCompatibleDC()
        self.saveBitMap = win32ui.CreateBitmap()
        self.saveBitMap.CreateCompatibleBitmap(self.mfcDC, self.width, self.height)
        self.saveDC.SelectObject(self.saveBitMap)
        self.thread_input_attached = False
        self.screenshot = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        win32gui.DeleteObject(self.saveBitMap.GetHandle())
        self.saveDC.DeleteDC()
        self.mfcDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, self.hwndDC)

    def update_screenshot(self):
        result = windll.user32.PrintWindow(self.hwnd, self.saveDC.GetSafeHdc(), 2)
        if result != 1:
            raise ValueError("PrintWindow failed")
        bmpinfo = self.saveBitMap.GetInfo()
        bmpstr = self.saveBitMap.GetBitmapBits(True)
        self.screenshot = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1)

    def move(self, x, y, w=None, h=None):
        if w is None:
            w = self.width
        if h is None:
            h = self.height
        win32gui.MoveWindow(self.hwnd, x, y, w, h, True)
        self.update_box()

    def update_box(self):
        self.left, self.top, self.right, self.bot = win32gui.GetWindowRect(self.hwnd)
        self.width = self.right - self.left
        self.height = self.bot - self.top
        # FIXME: should we re-create bitmap after update?

    def attach_thread_input(self):
        if self.thread_input_attached:
            return
        threadId, _processId = win32process.GetWindowThreadProcessId(self.hwnd)
        win32process.AttachThreadInput(win32api.GetCurrentThreadId(), threadId, True)
        # FIXME: there is no way to detect if AttachThreadInput failed
        self.thread_input_attached = True

    # https://github.com/AutoHotkey/AutoHotkey/blob/v2.0/source/lib/win.cpp#L335
    def click(self, box, offset=Offset("50%")):
        if isinstance(offset, str):
            offset = Offset(offset)
        x, y = offset(box)
        pyautogui.moveTo(x, y)
        self.attach_thread_input()
        # NOTE: this may lift the window to the foreground at the first click
        # Users have to focus and click other windows manually
        win32gui.SetActiveWindow(self.hwnd)
        lparam = win32api.MAKELONG(x, y)
        win32gui.PostMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
        time.sleep(0.020)
        win32gui.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, lparam)
        time.sleep(0.25)

    def wait(self, *args, **kwargs):
        return WindowScreenshotChecker(self, *args, **kwargs).wait()

