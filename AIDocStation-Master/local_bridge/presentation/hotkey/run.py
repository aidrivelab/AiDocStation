# -*- coding: utf-8 -*-
"""
@File    : local_bridge/presentation/hotkey/run.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:42
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from ...service.hotkey.manager import HotkeyManager
from ...service.hotkey.debounce import DebounceManager
from ...config.defaults import DEFAULT_CONFIG
from ...core.state import app_state
from ...utils.logging import log
from ...utils.hotkey_checker import HotkeyChecker
from ...i18n import t


class HotkeyRunner:
               
    
    def __init__(self, controller_callback, notification_manager=None, config_loader=None):
        self.hotkey_manager = HotkeyManager()
        self.debounce_manager = DebounceManager()
        self.controller_callback = controller_callback
        self.notification_manager = notification_manager
        self.config_loader = config_loader
    
    def get_hotkey_manager(self) -> HotkeyManager:
                              
        return self.hotkey_manager
    
    def start(self) -> None:
                    
        hotkey = app_state.hotkey_str
        

        error = HotkeyChecker.validate_hotkey_string(hotkey)
        if error:
            log(f"Invalid hotkey '{hotkey}': {error}. Resetting to default.")
            

            default_hotkey = DEFAULT_CONFIG["hotkey"]
            app_state.hotkey_str = default_hotkey
            app_state.config["hotkey"] = default_hotkey
            hotkey = default_hotkey
            

            if self.config_loader:
                try:
                    self.config_loader.save(app_state.config)
                except Exception as e:
                    log(f"Failed to save corrected config: {e}")
            

            if self.notification_manager:
                self.notification_manager.notify(
                    f"AIDOC Station - {t('hotkey.runner.title_invalid_config')}",
                    t("hotkey.runner.invalid_config", error=error, default=DEFAULT_CONFIG["hotkey"]),
                    ok=False
                )
        
        def on_hotkey():
            if app_state.enabled and not getattr(app_state, "ui_block_hotkeys", False):
                self.debounce_manager.trigger_async(self.controller_callback)
        
        try:
            self.hotkey_manager.bind(hotkey, on_hotkey)
        except Exception as e:

            log(f"Failed to bind hotkey '{hotkey}': {e}")
            

            if hotkey != DEFAULT_CONFIG["hotkey"]:
                try:
                    default_hotkey = DEFAULT_CONFIG["hotkey"]
                    app_state.hotkey_str = default_hotkey
                    app_state.config["hotkey"] = default_hotkey
                    self.hotkey_manager.bind(default_hotkey, on_hotkey)
                    
                    if self.config_loader:
                        self.config_loader.save(app_state.config)
                    
                    if self.notification_manager:
                        self.notification_manager.notify(
                            f"AIDOC Station - {t('hotkey.runner.title_binding_failed')}",
                            t("hotkey.runner.binding_failed", default=DEFAULT_CONFIG["hotkey"]),
                            ok=False
                        )
                except Exception as fallback_error:
                    log(f"Failed to bind default hotkey: {fallback_error}")
                    if self.notification_manager:
                        self.notification_manager.notify(
                            f"AIDocStation - {t('hotkey.runner.title_serious_error')}",
                            t("hotkey.runner.serious_error"),
                            ok=False
                        )
    
    def stop(self) -> None:
                    
        self.hotkey_manager.unbind()
    
    def restart(self) -> None:
                    
        self.stop()
        self.start()
