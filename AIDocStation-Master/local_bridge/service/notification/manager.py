# -*- coding: utf-8 -*-
"""
@File    : local_bridge/service/notification/manager.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""


                                                                               

import os
import sys
import threading
import queue
import time
import warnings
from typing import Optional, Callable

from local_bridge.utils.system_detect import is_windows, is_macos

from ...core.constants import NOTIFICATION_TIMEOUT
from ...config.paths import get_app_icon_path, get_app_white_png_path, get_app_icon_ico_path
from ...utils.logging import log
from ...core.state import app_state


warnings.filterwarnings("ignore", category=UserWarning, module="win10toast")


try:
    from plyer import notification as _plyer_notification
    _PLYER_OK = True
    log("plyer module loaded successfully")
except Exception as e:
    _PLYER_OK = False
    log(f"plyer module load failed: {e}")


try:
    from win11toast import toast as _win11_toast
    _WIN11_OK = is_windows()
except Exception:
    _WIN11_OK = False


_WIN10_OK = False
_win10_toaster = None
if is_windows():
    try:
        from win10toast import ToastNotifier as _ToastNotifier
        _win10_toaster = _ToastNotifier()
        _WIN10_OK = True
    except Exception:
        _win10_toaster = None
        _WIN10_OK = False


_NATIVE_MACOS_OK = False
_native_notifier = None
if is_macos():
    try:
        from .native_macos import NativeMacOSNotifier
        if NativeMacOSNotifier.is_available():
            _native_notifier = NativeMacOSNotifier
            _NATIVE_MACOS_OK = True
            log("Native macOS notifier loaded successfully")
        else:
            log("Native macOS notifier not available (Foundation framework missing)")
    except Exception as e:
        log(f"Native macOS notifier load failed: {e}")


_PYNC_OK = False
_pync_notify = None
if is_macos():
    try:
        from pync import Notifier as _PyncNotifier
        _pync_notify = _PyncNotifier
        _PYNC_OK = True
        log("pync module loaded successfully")
    except Exception as e:
        _PYNC_OK = False
        _pync_notify = None
        log(f"pync module load failed: {e}")



def _icon_or_none(path: Optional[str]) -> Optional[str]:
    return path if path and os.path.exists(path) else None


def _secs_to_win11_duration(secs: int | float) -> str:

    try:
        return "short" if float(secs) <= 5 else "long"
    except Exception:
        return "short"


class NotificationManager:
                                        

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, app_name: str = "AIDocStation", max_queue: int = 30):

        if hasattr(self, "_initialized"):
            return
        
        self.app_name = app_name
        if is_windows():
            self.icon_path = get_app_icon_ico_path()
        else:
            self.icon_path = get_app_white_png_path()
        self._q: "queue.Queue[tuple[str,str,bool,Optional[Callable]]]" = queue.Queue(maxsize=max_queue)
        self._stop = threading.Event()
        self._worker = threading.Thread(target=self._worker_loop, name="NotifyWorker", daemon=True)
        self._worker.start()
        self._initialized = True


    def notify(self, title: str, message: str, ok: bool = True, on_click: Optional[Callable] = None, **kwargs) -> None:
        

           
        log(f"Notify enqueue: {title} - {message} ({'OK' if ok else 'ERR'})")

        if app_state.config.get("notify", True) is False:
            return


        try:
            self._q.put((title, message, ok, on_click), block=False)
        except queue.Full:
            try:
                _ = self._q.get_nowait()  
            except Exception:
                pass
            try:
                self._q.put_nowait((title, message, ok, on_click))
            except Exception:
                pass  

    def is_available(self) -> bool:
        if sys.platform == "win32" and (_WIN11_OK or _WIN10_OK):
            return True
        return _PLYER_OK


    def shutdown(self, drain_timeout: float = 1.0) -> None:
                                   
        self._stop.set()
        t0 = time.time()
        while not self._q.empty() and (time.time() - t0) < drain_timeout:
            time.sleep(0.02)


    def _worker_loop(self):
        while not self._stop.is_set():
            if app_state.config.get("notify", True) is False:

                while not self._q.empty():
                    try:
                        self._q.get_nowait()
                    except Exception:
                        pass
                    finally:
                        self._q.task_done()
                time.sleep(0.25)
                continue
            try:
                title, message, ok, on_click = self._q.get(timeout=0.25)
            except queue.Empty:
                continue

            try:
                self._send_one(title, message, on_click=on_click)
            except Exception as e:
                log(f"Notification send error: {e}")
            finally:

                time.sleep(0.01)
                self._q.task_done()


    def _send_one(self, title: str, message: str, **kwargs) -> None:

        if _WIN11_OK:
            try:

                _ = _win11_toast(
                    title,
                    message,
                    app_id="AIDoc Station",
                    icon=_icon_or_none(self.icon_path),
                    duration=_secs_to_win11_duration(NOTIFICATION_TIMEOUT),
                    on_click=on_click
                )
                return
            except Exception as e:
                log(f"win11toast error, fallback to win10: {e}")


        if _WIN10_OK and _win10_toaster is not None:
            try:
                _win10_toaster.show_toast(
                    title,
                    message,
                    icon_path=_icon_or_none(self.icon_path),
                    duration=int(NOTIFICATION_TIMEOUT) if NOTIFICATION_TIMEOUT else 5,
                    threaded=True,
                )
                return
            except Exception as e:
                log(f"win10toast error, fallback to pync: {e}")


        if is_macos() and _PYNC_OK and _pync_notify is not None:
            try:
                _pync_notify.notify(
                    message=message,
                    title=title,
                    group="cn.aidrivelab.station",
                    sender="cn.aidrivelab.station",
                    appIcon=_icon_or_none(self.icon_path),
                    timeout=NOTIFICATION_TIMEOUT,
                )
                return
            except Exception as e:
                log(f"pync notify error: {e}")


        if _NATIVE_MACOS_OK and _native_notifier:
            try:
                success = _native_notifier.notify(
                    title=title,
                    message=message,
                    app_icon=_icon_or_none(self.icon_path),
                    timeout=NOTIFICATION_TIMEOUT,
                    group="cn.aidrivelab.station"
                )
                if success:
                    return
            except Exception as e:
                log(f"Native macOS notification error, fallback: {e}")


        if _PLYER_OK:
            try:
                _plyer_notification.notify(
                    title=title,
                    message=message,
                    timeout=NOTIFICATION_TIMEOUT,
                    app_icon=self.icon_path if os.path.exists(self.icon_path) else None,
                )
            except Exception as e:
                log(f"plyer notify error: {e}")

if __name__ == "__main__":

    nm = NotificationManager()
    nm.notify("测试通知", "这是一条测试通知内容�?, ok=True)
    time.sleep(3)
    nm.notify("错误通知", "这是一条错误通知内容�?, ok=False)
    time.sleep(5)
