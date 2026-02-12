# -*- coding: utf-8 -*-
"""
@File    : local_bridge/utils/detector.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from __future__ import annotations
import sys
from typing import Literal

AppType = Literal["word", "wps", "excel", "wps_excel", ""]


if sys.platform == "darwin":
    from .macos.detector import (
        detect_active_app as _detect_active_app,
        detect_wps_type as _detect_wps_type,
        get_frontmost_window_title as _get_frontmost_window_title,
    )
elif sys.platform == "win32":
    from .win32.detector import (
        detect_active_app as _detect_active_app,
        detect_wps_type as _detect_wps_type,
    )
    from .win32.window import (
        get_foreground_window_title as _get_frontmost_window_title,
    )
else:

    def _detect_active_app() -> str:
        return ""
    
    def _detect_wps_type() -> str:
        return ""
    
    def _get_frontmost_window_title() -> str:
        return ""


def detect_active_app() -> AppType:
    















       
    return _detect_active_app()


def detect_wps_type() -> AppType:
    














       
    return _detect_wps_type()


def is_office_app(app_type: str) -> bool:
    







       
    return app_type in ("word", "excel", "wps", "wps_excel")


def is_word_like(app_type: str) -> bool:
    







       
    return app_type in ("word", "wps")


def is_excel_like(app_type: str) -> bool:
    







       
    return app_type in ("excel", "wps_excel")


def get_app_display_name(app_type: str) -> str:
    







       
    display_names = {
        "word": "Microsoft Word",
        "excel": "Microsoft Excel",
        "wps": "WPS 文字",
        "wps_excel": "WPS 表格",
        "": "未知应用",
    }
    return display_names.get(app_type, app_type)


def get_frontmost_window_title() -> str:
    






       
    return _get_frontmost_window_title()


__all__ = [
    "AppType",
    "detect_active_app",
    "detect_wps_type",
    "is_office_app",
    "is_word_like",
    "is_excel_like",
    "get_app_display_name",
    "get_frontmost_window_title",
]
