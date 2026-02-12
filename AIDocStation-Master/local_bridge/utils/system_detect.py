# -*- coding: utf-8 -*-
"""
@File    : local_bridge/utils/system_detect.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import platform


def get_os_name() -> str:
    sys_name = platform.system().lower()
    if sys_name == "darwin":
        return "macos"
    if sys_name == "windows":
        return "windows"
    if sys_name == "linux":
        return "linux"
    return "unknown"


def is_macos() -> bool:
    return get_os_name() == "macos"


def is_windows() -> bool:
    return get_os_name() == "windows"


def is_linux() -> bool:
    return get_os_name() == "linux"
