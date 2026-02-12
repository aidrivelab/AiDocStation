# -*- coding: utf-8 -*-
"""
@File    : local_bridge/utils/macos/reopen.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from __future__ import annotations

import sys
from typing import Callable, Optional

from Foundation import NSObject
import objc

from ..logging import log
from ...core.state import app_state


def install_reopen_handler(on_reopen: Callable[[], None]) -> bool:
    




       
    if sys.platform != "darwin":
        return False

    try:
        from Foundation import NSAppleEventManager
    except Exception as exc:
        log(f"Failed to import AppleEvent APIs: {exc}")
        return False

    def _fourcc(code: str) -> int:


        raw = code.encode("ascii", errors="strict")
        if len(raw) != 4:
            raise ValueError("fourcc must be exactly 4 ASCII chars")
        return int.from_bytes(raw, byteorder="big", signed=False)

    kCoreEventClass = _fourcc("aevt")
    kAEReopenApplication = _fourcc("rapp")

    class _ReopenHandler(NSObject):
        def initWithCallback_(self, callback):
            self = objc.super(_ReopenHandler, self).init()
            if self is None:
                return None
            self._callback = callback
            return self

        def handleReopen_withReplyEvent_(self, event, replyEvent):
            try:
                if callable(getattr(self, "_callback", None)):
                    self._callback()
            except Exception as exc:
                log(f"Reopen handler error: {exc}")

    try:
        manager = NSAppleEventManager.sharedAppleEventManager()
        handler: Optional[NSObject] = _ReopenHandler.alloc().initWithCallback_(on_reopen)
        if handler is None:
            return False


        app_state.macos_reopen_handler = handler
        manager.setEventHandler_andSelector_forEventClass_andEventID_(
            handler,
            "handleReopen:withReplyEvent:",
            kCoreEventClass,
            kAEReopenApplication,
        )
        return True
    except Exception as exc:
        log(f"Failed to install reopen handler: {exc}")
        return False
