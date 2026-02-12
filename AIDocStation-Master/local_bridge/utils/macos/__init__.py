# -*- coding: utf-8 -*-
"""
@File    : local_bridge/utils/macos/__init__.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

try:
    from .hotkey_checker import HotkeyChecker
    from .dpi import set_dpi_awareness, get_dpi_scale
    __all__ = ['HotkeyChecker', 'set_dpi_awareness', 'get_dpi_scale']
except ImportError:

    __all__ = []
