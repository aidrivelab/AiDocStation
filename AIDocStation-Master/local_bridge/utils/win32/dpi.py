# -*- coding: utf-8 -*-
"""
@File    : local_bridge/utils/win32/dpi.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import ctypes
import platform
from ..logging import log

def set_dpi_awareness():
    



       
    try:



        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        log("DPI awareness set to PROCESS_SYSTEM_DPI_AWARE via shcore")
    except (AttributeError, OSError):
        try:

            ctypes.windll.user32.SetProcessDPIAware()
            log("DPI awareness set via user32.SetProcessDPIAware")
        except (AttributeError, OSError) as e:
            log(f"Failed to set DPI awareness: {e}")

def get_dpi_scale():
    




       
    try:

        hdc = ctypes.windll.user32.GetDC(0)
        dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)
        ctypes.windll.user32.ReleaseDC(0, hdc)
        return dpi / 96.0
    except Exception as e:
        log(f"Failed to get DPI scale: {e}")
        return 1.0
