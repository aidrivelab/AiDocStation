# -*- coding: utf-8 -*-
"""
@File    : local_bridge/api/supabase_client.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import os
import webbrowser
import time

from local_bridge.utils.logging import log
from local_bridge.core.state import app_state

class SupabaseClient:
    def __init__(self):
        self.client = None
    def open_web_login(self): pass
    def set_session(self, *args, **kwargs): return False
    def load_local_session(self): pass
    def get_profile(self): return None
    def logout(self): pass
    def sync_stats(self, *args, **kwargs): return None
    def get_session(self): return None

supabase_client = SupabaseClient()
