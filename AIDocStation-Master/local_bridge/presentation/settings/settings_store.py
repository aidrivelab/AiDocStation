# -*- coding: utf-8 -*-
"""
@File    : local_bridge/presentation/settings/settings_store.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:42
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from PySide6.QtCore import QObject, Signal
import json
import os
from local_bridge.config.paths import get_config_path
from local_bridge.config.defaults import DEFAULT_CONFIG
from local_bridge.utils.logging import log, log_error

class SettingsStore(QObject):
    

       
    settings_changed = Signal(str, object)

    def __init__(self):
        super().__init__()
        self.config_path = get_config_path()
        self.config = self._load()
        

        if "stats" not in self.config:
            self.config["stats"] = DEFAULT_CONFIG["stats"].copy()
            

        if not self.config.get("last_check_time"):
            from datetime import datetime
            self.config["last_check_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.save()

    def _load(self):
                                                
        if not os.path.exists(self.config_path):
            return DEFAULT_CONFIG.copy()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

                merged = DEFAULT_CONFIG.copy()

                merged.update(data)
                

                if "stats" in data:
                    merged["stats"].update(data["stats"])
                    
                return merged
        except Exception as e:
            log_error(f"Failed to load config: {e}")
            return DEFAULT_CONFIG.copy()

    def save(self):
                              

        if "stats" in self.config:
            self.config["_stats_integrity"] = self._calculate_stats_hash(self.config["stats"])
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            log_error(f"Failed to save config: {e}")

    def _calculate_stats_hash(self, stats: dict) -> str:
                                                               
        import hashlib

        data_str = "".join(f"{k}:{v}" for k, v in sorted(stats.items()) if not k.startswith("_"))

        salt = "aidoc_station_v1"
        return hashlib.md5((data_str + salt).encode()).hexdigest()

    def get(self, key, default=None):
        val = self.config.get(key, default)
        

        if key == "stats" and val:
            stored_hash = self.config.get("_stats_integrity")
            if stored_hash and stored_hash != self._calculate_stats_hash(val):
                log_error("Statistics integrity check failed! Local modifications detected.")

        return val

    def set(self, key, value):
        if self.config.get(key) != value:
            self.config[key] = value
            self.save()
            self.settings_changed.emit(key, value)
            
    def increment_stat(self, stat_key, amount=1):
                                          
        stats = self.config.get("stats", {})
        current = stats.get(stat_key, 0)
        stats[stat_key] = current + amount
        self.config["stats"] = stats
        self.save()
        self.settings_changed.emit("stats", stats)

    def add_listener(self, callback):
                                                       
        self.settings_changed.connect(callback)
