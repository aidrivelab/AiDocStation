# -*- coding: utf-8 -*-
"""
@File    : local_bridge/service/update_service.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:42
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import os
import requests
import threading
import tempfile
import platform
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from local_bridge.version import __version__
from local_bridge.utils.logging import log, log_error
from local_bridge.presentation.settings.settings_store import SettingsStore
from local_bridge.service.notification.manager import NotificationManager
from local_bridge.i18n import t

class UpdateService:
    

       
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(UpdateService, cls).__new__(cls)
        return cls._instance

    def __init__(self, store: Optional[SettingsStore] = None):
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.store = store
        self.current_version = __version__
        self.update_available = False
        self.is_checking = False
        self.update_info: Dict[str, Any] = {}
        self.notification_manager = NotificationManager()
        self._dl_lock = threading.Lock()
        self.on_notification_click: Optional[Callable] = None
        

        self.is_downloading = False
        self.download_progress = 0
        self.last_download_path = None
        
        self._initialized = True

    def check_update(self, manual: bool = False) -> bool:
        return False

    def _is_newer(self, remote: str, local: str) -> bool:
        try:
            from packaging import version
            r = version.parse(remote.lstrip('v'))
            l = version.parse(local.lstrip('v'))
            return r > l
        except Exception as e:
            log_error(f"Version comparison error: {e}")
            return False

    def is_update_downloaded(self) -> bool:
                                                             
        if self.last_download_path and os.path.exists(self.last_download_path):
            return True

        if self.store:
            stored_path = self.store.get("downloaded_update_path")
            if stored_path and os.path.exists(stored_path):

                if self.update_info:
                    target_version = self.update_info.get("version", "").lstrip('v')
                    if target_version in stored_path:
                        self.last_download_path = stored_path
                        return True
        return False

    def get_local_download_path(self) -> Optional[str]:
        return self.last_download_path

    def _get_platform_suffix(self) -> str:
                                                        
        sys_name = platform.system().lower()
        if sys_name == "darwin":
            return "mac"
        return "win"

    def _get_file_extension(self, url: str) -> str:
                                                                                
        try:

            clean_url = url.split('?')[0]
            ext = os.path.splitext(clean_url)[1].lower()
            if ext in ['.exe', '.dmg', '.pkg', '.zip', '.msi']:
                return ext
        except:
            pass

        if platform.system().lower() == "darwin":
            return ".pkg"
        return ".exe"

    def download_update(self):
        pass
