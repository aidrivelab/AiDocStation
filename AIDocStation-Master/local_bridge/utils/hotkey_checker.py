# -*- coding: utf-8 -*-
"""
@File    : local_bridge/utils/hotkey_checker.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from typing import Optional, Set
from .system_detect import is_windows, is_macos
from .logging import log


class HotkeyChecker:
                  
    
    _checker = None
    
    @classmethod
    def _get_checker(cls):
                          
        if cls._checker is None:
            if is_windows():
                try:
                    from .win32.hotkey_checker import HotkeyChecker as WinChecker
                    cls._checker = WinChecker
                    log("Using Windows hotkey checker")
                except ImportError as e:
                    log(f"Failed to import Windows hotkey checker: {e}")
                    cls._checker = None
            elif is_macos():
                try:
                    from .macos.hotkey_checker import HotkeyChecker as MacChecker
                    cls._checker = MacChecker
                    log("Using macOS hotkey checker")
                except ImportError as e:
                    log(f"Failed to import macOS hotkey checker: {e}")
                    cls._checker = None
            else:
                log("Unsupported platform for hotkey checking")
                cls._checker = None
        
        return cls._checker
    
    @classmethod
    def validate_hotkey_keys(
        cls,
        keys: Set[str],
        *,
        hotkey_repr: str = "",
        detailed: bool = False,
    ) -> Optional[str]:
        


           
        checker = cls._get_checker()
        if checker is None:
            return None
        
        return checker.validate_hotkey_keys(
            keys,
            hotkey_repr=hotkey_repr,
            detailed=detailed,
        )
    
    @classmethod
    def validate_hotkey_string(cls, hotkey_str: str, *, detailed: bool = False) -> Optional[str]:
        

           
        checker = cls._get_checker()
        if checker is None:
            return None
        
        return checker.validate_hotkey_string(hotkey_str, detailed=detailed)
    
    @classmethod
    def is_hotkey_available(cls, hotkey_str: str) -> bool:
        







           
        checker = cls._get_checker()
        if checker is None:
            return True
        
        return checker.is_hotkey_available(hotkey_str)
