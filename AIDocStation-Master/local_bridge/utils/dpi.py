# -*- coding: utf-8 -*-
"""
@File    : local_bridge/utils/dpi.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from .system_detect import is_windows, is_macos
from .logging import log


def set_dpi_awareness():
                        
    if is_windows():
        try:
            from .win32.dpi import set_dpi_awareness as win_set_dpi
            win_set_dpi()
        except ImportError as e:
            log(f"Failed to import Windows DPI utilities: {e}")
    elif is_macos():
        try:
            from .macos.dpi import set_dpi_awareness as mac_set_dpi
            mac_set_dpi()
        except ImportError as e:
            log(f"Failed to import macOS DPI utilities: {e}")
    else:
        log("DPI awareness not supported on this platform")


def get_dpi_scale():
    




       
    if is_windows():
        try:
            from .win32.dpi import get_dpi_scale as win_get_dpi
            return win_get_dpi()
        except ImportError as e:
            log(f"Failed to import Windows DPI utilities: {e}")
            return 1.0
    elif is_macos():
        try:
            from .macos.dpi import get_dpi_scale as mac_get_dpi
            return mac_get_dpi()
        except ImportError as e:
            log(f"Failed to import macOS DPI utilities: {e}")
            return 1.0
    else:
        log("DPI scale detection not supported on this platform")
        return 1.0
