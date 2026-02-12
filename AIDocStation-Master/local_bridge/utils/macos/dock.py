# -*- coding: utf-8 -*-
"""
@File    : local_bridge/utils/macos/dock.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from __future__ import annotations

import sys
from typing import Optional

from ...core.state import app_state
from ..logging import log


def _get_refcount() -> int:
    return int(getattr(app_state, "macos_ui_refcount", 0) or 0)


def _set_refcount(value: int) -> None:
    setattr(app_state, "macos_ui_refcount", max(0, int(value)))


def _ns_app():
    try:
        from AppKit import NSApplication

        return NSApplication.sharedApplication()
    except Exception:
        return None


def set_dock_visible(visible: bool) -> None:
    





       
    if sys.platform != "darwin":
        return

    app = _ns_app()
    if app is None:
        return

    try:
        from AppKit import (
            NSApplicationActivationPolicyAccessory,
            NSApplicationActivationPolicyRegular,
        )

        policy = (
            NSApplicationActivationPolicyRegular
            if visible
            else NSApplicationActivationPolicyAccessory
        )
        app.setActivationPolicy_(policy)
    except Exception as exc:
        log(f"Failed to set Dock visibility: {exc}")


def activate_app() -> None:
                                                
    if sys.platform != "darwin":
        return

    app = _ns_app()
    if app is None:
        return

    try:
        app.activateIgnoringOtherApps_(True)
    except Exception as exc:
        log(f"Failed to activate app: {exc}")


def begin_ui_session() -> None:
    



       
    if sys.platform != "darwin":
        return

    refcount = _get_refcount() + 1
    _set_refcount(refcount)

    if refcount == 1:
        set_dock_visible(True)
        activate_app()


def end_ui_session() -> None:
    



       
    if sys.platform != "darwin":
        return

    refcount = _get_refcount() - 1
    _set_refcount(refcount)

    if refcount <= 0:
        set_dock_visible(False)
