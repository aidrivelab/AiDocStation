# -*- coding: utf-8 -*-
"""
@File    : local_bridge/utils/macos/dpi.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from AppKit import NSScreen
from ..logging import log


def set_dpi_awareness():
    


       

    log("macOS handles DPI automatically (Retina support)")


def get_dpi_scale():
    




       
    try:

        main_screen = NSScreen.mainScreen()
        if main_screen:

            scale = main_screen.backingScaleFactor()
            return float(scale)
        return 1.0
    except Exception as e:
        log(f"Failed to get DPI scale: {e}")
        return 1.0
