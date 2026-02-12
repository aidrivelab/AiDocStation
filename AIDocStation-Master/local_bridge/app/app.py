# -*- coding: utf-8 -*-
"""
@File    : local_bridge/app/app.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from local_bridge.presentation.settings.pyside_ui import SettingsDialog
from local_bridge.presentation.tray.qt_tray import QtTrayManager
from local_bridge.presentation.settings.settings_store import SettingsStore
from local_bridge.config.paths import get_app_icon_path
from local_bridge.core.state import app_state
from local_bridge.utils.logging import log
from local_bridge.app.server_thread import ServerThread
from local_bridge.service.hotkey.manager import HotkeyManager
from local_bridge.api.supabase_client import supabase_client

from local_bridge.app.instance_controller import SingleInstanceController

from PySide6.QtCore import QSharedMemory, QTimer

def run_app():
                                               
    print("DEBUG: run_app() starting...")
    log("Starting AIDOC Station...")
    app = QApplication(sys.argv)
    

    msg = sys.argv[1] if len(sys.argv) > 1 else ""
    instance_controller = SingleInstanceController()
    
    if instance_controller.is_already_running(msg):
        log("Another instance is already running. Message sent. Exiting.")
        print("DEBUG: Another instance detected, exiting.")
        sys.exit(0)
    
    if not instance_controller.start_server():
        log("Failed to start instance controller server. Exiting.")
        sys.exit(1)
        

    app._instance_controller = instance_controller
    

    if sys.platform == "win32":



        if not getattr(sys, 'frozen', False):
            print("DEBUG: Dev mode detected, registering protocol...")
            pass
        else:
            log("[Protocol] Production mode: Skipping runtime registration (Managed by Installer).")
    

    icon_path = get_app_icon_path()
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))




    from PySide6.QtGui import QPalette, QColor
    from PySide6.QtWidgets import QToolTip
    
    palette = QToolTip.palette()
    palette.setColor(QPalette.ToolTipBase, QColor("#FFFFFF"))
    palette.setColor(QPalette.ToolTipText, QColor("#000000"))
    QToolTip.setPalette(palette)
    
    app.setStyleSheet("""
        QToolTip {
            color: #000000;
            background-color: #FFFFFF;
            border: 1px solid #CCCCCC;
            padding: 4px;
            border-radius: 4px;
            font-family: 'Microsoft YaHei'; 
        }
    """)
    


    store = SettingsStore()
    

    from local_bridge.i18n import set_language
    set_language(store.get("language", "auto"))
    

    def on_config_changed(key, value):
        if key == "language":
            set_language(value)
            log(f"Language synced to i18n: {value}")
            
    store.add_listener(on_config_changed)
    
    app_state.store = store
    app_state.config = store.config
    log(f"Config loaded via SettingsStore: {len(app_state.config)} keys")


    pass
    

    

    window = SettingsDialog(store=store)
    

    tray = QtTrayManager(store, parent_window=window)
    

    app_state.hotkey_manager = HotkeyManager()
    hotkey_manager = app_state.hotkey_manager
    



    from PySide6.QtCore import QObject, Signal
    
    class HotkeyCaller(QObject):
        paste_signal = Signal()
        toggle_signal = Signal()
    
    hotkey_caller = HotkeyCaller()
    

    def do_toggle():
        log(f"[Toggle] isVisible={window.isVisible()}, isMinimized={window.isMinimized()}")
        if window.isVisible() and not window.isMinimized():
            window.hide()
            log("[Toggle] Window hidden.")
        else:
            window.show()
            window.raise_()
            window.activateWindow()
            log("[Toggle] Window shown and activated.")
    

    hotkey_caller.paste_signal.connect(tray.trigger_paste)
    hotkey_caller.toggle_signal.connect(do_toggle)
    

    if store.get("enable_paste_hotkey", True):
        paste_hotkey = store.get("hotkey", "<ctrl>+<alt>+q")
        if paste_hotkey:
            try:
                hotkey_manager.bind(paste_hotkey, hotkey_caller.paste_signal.emit)
                log(f"Paste hotkey bound: {paste_hotkey}")
            except Exception as e:
                log(f"Failed to bind paste hotkey: {e}")
    else:
        log("Paste hotkey disabled by config.")

    if store.get("enable_show_hide_hotkey", True):
        show_hide_hotkey = store.get("hotkey_show_hide", "<ctrl>+<alt>+e")
        if show_hide_hotkey:
            try:
                hotkey_manager.bind(show_hide_hotkey, hotkey_caller.toggle_signal.emit)
                log(f"Show/Hide hotkey bound: {show_hide_hotkey}")
            except Exception as e:
                log(f"Failed to bind show/hide hotkey: {e}")
    else:
        log("Show/Hide hotkey disabled by config.")
    

    app._tray = tray
    app._hotkey_manager = hotkey_manager
    app._hotkey_caller = hotkey_caller
    
    

    if store.get("enable_double_click_paste", False):
        try:
            hotkey_manager.start_double_click_listener(callback=hotkey_caller.paste_signal.emit)
            log("Double-Click listener started on startup.")
        except Exception as e:
            log(f"Failed to start Double-Click listener: {e}")


    def on_deep_link(url: str):
        if url.startswith("aidoc://auth"):
            log("[DeepLink] Received auth link (Token hidden)")

            from PySide6.QtCore import QUrl, QUrlQuery
            parsed_url = QUrl(url)
            query = QUrlQuery(parsed_url.query())
            access_token = query.queryItemValue("access_token")
            refresh_token = query.queryItemValue("refresh_token")
            
            if access_token:

                log(f"[DeepLink] Extracted token. Length: {len(access_token)}, Head: {access_token[:20]}..., Tail: {access_token[-20:]}")
                log("[DeepLink] Syncing with Supabase...")
                success = supabase_client.set_session(access_token, refresh_token)
                log(f"[DeepLink] set_session result: {success}")
                
                if success:

                    log("[DeepLink] Refreshing UI...")
                    window.show()
                    window.raise_()
                    window.activateWindow()

                    window.refresh_auth_status()
                    

                    trigger_auto_sync()
                else:
                    log("[DeepLink] Failed to set session. Supabase client might be uninitialized.")

    instance_controller.message_received.connect(on_deep_link)


    def trigger_auto_sync():
        if store.get("enable_auto_sync", True):
            log("[AutoSync] Triggering 15-minute scheduled sync...")
            stats = store.get("stats", {})
            supabase_client.sync_stats(stats)
    
    sync_timer = QTimer(app)
    sync_timer.timeout.connect(trigger_auto_sync)

    sync_timer.start(15 * 60 * 1000)
    app._sync_timer = sync_timer


    if store.get("supabase_session"):
        QTimer.singleShot(5000, trigger_auto_sync)


    if msg:
        log(f"[Startup] Initial Deep Link detected: {msg}")
        QTimer.singleShot(1000, lambda: on_deep_link(msg))




    is_first_run = store.get("is_first_run", True)
    start_minimized = store.get("start_minimized", True)
    
    if is_first_run:
        log("[Startup] First run detected. Forcing main window show.")
        window.show()

        store.set("is_first_run", False)
    elif not start_minimized:
        log("[Startup] Showing main window per user settings.")
        window.show()
    else:
        log("[Startup] Application started minimized to tray.")
    
    sys.exit(app.exec())
