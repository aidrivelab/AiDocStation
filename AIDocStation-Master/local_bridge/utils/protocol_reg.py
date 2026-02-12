# -*- coding: utf-8 -*-
"""
@File    : local_bridge/utils/protocol_reg.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import winreg
import sys
import os
from local_bridge.utils.logging import log

def _delete_reg_key_recursive(root, path):
                        
    try:
        with winreg.OpenKey(root, path, 0, winreg.KEY_ALL_ACCESS) as key:
            while True:
                try:
                    sub_key_name = winreg.EnumKey(key, 0)
                    _delete_reg_key_recursive(key, sub_key_name)
                except OSError:
                    break
        winreg.DeleteKey(root, path)
    except FileNotFoundError:
        pass
    except Exception as e:
        log(f"[Protocol] Failed to delete key {path}: {e}")

def register_aidoc_protocol():
    return True

def is_protocol_registered() -> bool:
    return True
