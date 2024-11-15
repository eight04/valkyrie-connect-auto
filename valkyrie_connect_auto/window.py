import time

import win32gui
import win32ui
import win32con
import win32api
import win32process

from ctypes import windll
from PIL import Image
import pyautogui

from .auto import Match

class Window(Match):
    def __init__(self, title):
        super().__init__(None, None)
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
        self.thread_input_attached = False
        # self.ahk_win = ahk.win_get(title=f"AHK_ID {self.hwnd}")

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
        # FIXME: MoveWindow always returns None?
        # if not result:
        #     raise ValueError("MoveWindow failed")
        self.update_rect()

    def update_rect(self):
        self.left, self.top, self.right, self.bot = win32gui.GetWindowRect(self.hwnd)
        self.w = self.right - self.left
        self.h = self.bot - self.top

    def attach_thread_input(self):
        if self.thread_input_attached:
            return
        threadId, processId = win32process.GetWindowThreadProcessId(self.hwnd)
        result = win32process.AttachThreadInput(win32api.GetCurrentThreadId(), threadId, True)
        # FIXME: there is no way to detect if AttachThreadInput failed
        self.thread_input_attached = True

    # https://github.com/AutoHotkey/AutoHotkey/blob/v2.0/source/lib/win.cpp#L335
    def click(self, x, y):
        pyautogui.moveTo(self.left + x, self.top + y)
        self.attach_thread_input()
        # NOTE: this may lift the window to the foreground at the first click
        # Users have to focus and click other windows manually
        win32gui.SetActiveWindow(self.hwnd)
        lparam = win32api.MAKELONG(x, y)
        win32gui.PostMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
        time.sleep(0.020)
        win32gui.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, lparam)

