# -*- coding: utf-8 -*-
"""
@File    : local_bridge/app/wiring.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from local_bridge.core.state import app_state
from local_bridge.config.loader import ConfigLoader
from local_bridge.service.notification.manager import NotificationManager
from local_bridge.app.workflows import execute_paste_workflow
from local_bridge.presentation.tray.menu import TrayMenuManager
from local_bridge.presentation.tray.run import TrayRunner
from local_bridge.presentation.hotkey.run import HotkeyRunner


class Container:
                
    
    def __init__(self):

        self.config_loader = ConfigLoader()
        self.notification_manager = NotificationManager()
        

        self.workflow_router = execute_paste_workflow
        

        self.tray_menu_manager = TrayMenuManager(
            self.config_loader,
            self.notification_manager
        )
        self.tray_runner = TrayRunner(self.tray_menu_manager)
        self.hotkey_runner = HotkeyRunner(
            self.workflow_router,
            self.notification_manager,
            self.config_loader
        )
        

        self.tray_menu_manager.set_restart_hotkey_callback(
            self.hotkey_runner.restart
        )
        

        self.tray_menu_manager.set_pause_hotkey_callback(
            self.hotkey_runner.get_hotkey_manager().pause
        )
        

        def on_hotkey_resumed():
                            
            if app_state.enabled:
                self.hotkey_runner.debounce_manager.trigger_async(
                    self.workflow_router
                )
        
        def resume_hotkey():
                        
            self.hotkey_runner.get_hotkey_manager().resume(on_hotkey_resumed)
        
        self.tray_menu_manager.set_resume_hotkey_callback(resume_hotkey)
    
    def get_workflow_router(self):
                       
        return self.workflow_router
    
    def get_hotkey_runner(self) -> HotkeyRunner:
        return self.hotkey_runner
    
    def get_tray_runner(self) -> TrayRunner:
        return self.tray_runner
    
    def get_notification_manager(self) -> NotificationManager:
        return self.notification_manager
