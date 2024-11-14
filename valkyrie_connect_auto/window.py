import win32gui
import win32ui
from ctypes import windll
from PIL import Image

class Window:
    def __init__(self, title):
        self.hwnd = win32gui.FindWindow(None, title)
        if not self.hwnd:
            raise ValueError(f"Window not found: {title}")
        self.update_rect()
        self.hwndDC = win32gui.GetWindowDC(self.hwnd)
        self.mfcDC  = win32ui.CreateDCFromHandle(self.hwndDC)
        self.saveDC = self.mfcDC.CreateCompatibleDC()
        self.saveBitMap = win32ui.CreateBitmap()
        self.saveBitMap.CreateCompatibleBitmap(self.mfcDC, self.w, self.h)
        self.saveDC.SelectObject(self.saveBitMap)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        win32gui.DeleteObject(self.saveBitMap.GetHandle())
        self.saveDC.DeleteDC()
        self.mfcDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, self.hwndDC)

    def screenshot(self):
        result = windll.user32.PrintWindow(self.hwnd, self.saveDC.GetSafeHdc(), 2)
        if result != 1:
            raise ValueError("PrintWindow failed")
        bmpinfo = self.saveBitMap.GetInfo()
        bmpstr = self.saveBitMap.GetBitmapBits(True)
        return Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1)

    def move(self, x, y, w=None, h=None):
        if w is None:
            w = self.w
        if h is None:
            h = self.h
        result = win32gui.MoveWindow(self.hwnd, x, y, w, h, True)
        if not result:
            raise ValueError("MoveWindow failed")
        self.update_rect()

    def update_rect(self):
        self.left, self.top, self.right, self.bot = win32gui.GetWindowRect(self.hwnd)
        self.w = self.right - self.left
        self.h = self.bot - self.top

