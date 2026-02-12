# -*- coding: utf-8 -*-
"""
@File    : local_bridge/service/hotkey/debounce.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import time
import threading
from typing import Callable

from ...core.constants import FIRE_DEBOUNCE_SEC
from ...core.state import app_state
from ...utils.logging import log


class DebounceManager:
                   
    
    def __init__(self):
        pass
    
    def trigger_async(self, callback: Callable[[], None]) -> None:
        




           
        now = time.time()
        

        if now - app_state.last_fire < FIRE_DEBOUNCE_SEC:
            return
        
        app_state.last_fire = now
        

        if app_state.is_running():
            return
        

        def worker():
            app_state.set_running(True)
            try:
                callback()
            except Exception as e:
                log(f"Callback execution failed: {e}")
            finally:
                app_state.set_running(False)
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
