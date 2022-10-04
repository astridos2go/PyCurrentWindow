# Modified from https://github.com/Danesprite/windows-fun/blob/master/window%20change%20listener.py under the Unlicense License

"""
Script using the Windows API to register for window focus changes and print the
executable name of newly focused windows.
"""

import ctypes
import ctypes.wintypes

from psutil import Process

class ObservableWindowChange(object):
    def __init__(self):
        self.__observers = []

    def register_observer(self, observer):
        self.__observers.append(observer)

    def notify_observers(self, executable_name, *_):
        if executable_name == '':
            return ''
        for observer in self.__observers:
            observer.notify(executable_name)

    def start_event_listener(self):
        # Create a WindowChangeEventListener object with this instance of
        # ObservableWindowChange as a parameter (self)
        listener = WindowChangeEventListener(self)
        listener.listen_forever()


class IWindowChangeObserver(object):
    """
    Base class for observing window changes
    """

    def __init__(self, observable):
        observable.register_observer(self)

    def notify(self, _):
        raise NotImplementedError


class WindowChangeEventListener(object):
    """
    WindowChangeEventListener
    """

    def __init__(self, observable):
        self.observable = observable

    def listen_forever(self):
        # Look here for DWORD event constants:
        # http://stackoverflow.com/questions/15927262/convert-dword-event-constant-from-wineventproc-to-name-in-c-sharp
        # Don't worry, they work for python too.
        WINEVENT_OUTOFCONTEXT = 0x0000
        EVENT_SYSTEM_FOREGROUND = 0x0003
        WINEVENT_SKIPOWNPROCESS = 0x0002

        user32 = ctypes.windll.user32
        ole32 = ctypes.windll.ole32

        ole32.CoInitialize(0)

        WinEventProcType = ctypes.WINFUNCTYPE(
            None,
            ctypes.wintypes.HANDLE,
            ctypes.wintypes.DWORD,
            ctypes.wintypes.HWND,
            ctypes.wintypes.LONG,
            ctypes.wintypes.LONG,
            ctypes.wintypes.DWORD,
            ctypes.wintypes.DWORD
        )

        def callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
            PID = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(PID))
            Executable = Process(int(PID.value)).name()
            # Notify observers
            self.observable.notify_observers(Executable)

        WinEventProc = WinEventProcType(callback)

        user32.SetWinEventHook.restype = ctypes.wintypes.HANDLE
        hook = user32.SetWinEventHook(
            EVENT_SYSTEM_FOREGROUND,
            EVENT_SYSTEM_FOREGROUND,
            0,
            WinEventProc,
            0,
            0,
            WINEVENT_OUTOFCONTEXT | WINEVENT_SKIPOWNPROCESS
        )
        if hook == 0:
            print('SetWinEventHook failed')
            exit(1)

        msg = ctypes.wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
            user32.TranslateMessageW(msg)
            user32.DispatchMessageW(msg)

        # Stopped receiving events, so clear up the winevent hook and uninitialise.
        print('Stopped receiving new window change events. Exiting...')
        user32.UnhookWinEvent(hook)
        ole32.CoUninitialize()


class SerialWindowObserver(IWindowChangeObserver):
    def __init__(self, observable, serial, verbose):
        super().__init__(observable)
        self.serial = serial
        self.verbose = verbose

    def notify(self, executable_name):
        self.serial.write(str.encode(executable_name))
        if self.verbose:
            print(f"[INFO]: {executable_name}")
