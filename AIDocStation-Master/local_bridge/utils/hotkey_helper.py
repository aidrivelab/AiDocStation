# -*- coding: utf-8 -*-
"""
@File    : local_bridge/utils/hotkey_helper.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import sys

def is_hotkey_available(hotkey_str: str) -> bool:
    







       
    if sys.platform == 'win32':
        try:
            from local_bridge.utils.win32.hotkey_checker import HotkeyChecker
            return HotkeyChecker.is_hotkey_available(hotkey_str)
        except Exception:
            return True
    else:

        return True


def validate_hotkey_string(hotkey_str: str) -> str | None:
    







       
    if sys.platform == 'win32':
        try:
            from local_bridge.utils.win32.hotkey_checker import HotkeyChecker
            return HotkeyChecker.validate_hotkey_string(hotkey_str)
        except Exception as e:
            return str(e)
    else:

        if not hotkey_str or not hotkey_str.strip():
            return "Hotkey cannot be empty"
        return None
