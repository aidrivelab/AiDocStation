# -*- coding: utf-8 -*-
"""
@File    : local_bridge/utils/win32/com.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import pythoncom
from functools import wraps


def ensure_com(func):
    



       
    @wraps(func)
    def wrapper(*args, **kwargs):
        pythoncom.CoInitialize()
        try:
            return func(*args, **kwargs)
        finally:
            try:
                pythoncom.CoUninitialize()
            except Exception:

                pass
    return wrapper
