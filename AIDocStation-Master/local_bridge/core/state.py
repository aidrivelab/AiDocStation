# -*- coding: utf-8 -*-
"""
@File    : local_bridge/core/state.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import threading


@dataclass
class AppState:
                
    enabled: bool = True
    running: bool = False
    ui_block_hotkeys: bool = False
    last_fire: float = 0.0
    last_ok: bool = True
    hotkey_str: str = "<ctrl>+<shift>+b"
    config: Dict[str, Any] = field(default_factory=dict)
    store: Optional[Any] = None


    root: Optional[Any] = None
    listener: Optional[Any] = None
    icon: Optional[Any] = None


    instance_checker: Optional[Any] = None


    ui_queue: Optional[Any] = None


    quit_event: Optional[Any] = None


    _lock: threading.Lock = field(default_factory=threading.Lock)
    
    def with_lock(self, func):
                      
        with self._lock:
            return func()
    
    def set_running(self, running: bool):
                        
        with self._lock:
            self.running = running
    
    def is_running(self) -> bool:
                        
        with self._lock:
            return self.running



app_state = AppState()
