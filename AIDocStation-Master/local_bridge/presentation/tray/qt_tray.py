# -*- coding: utf-8 -*-
"""
@File    : local_bridge/presentation/tray/qt_tray.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:42
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import sys
import os
import subprocess
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Slot
from local_bridge.presentation.settings.settings_store import SettingsStore
from local_bridge.i18n import t, get_no_app_action_map
from local_bridge.config.paths import get_app_icon_path, get_log_path
from local_bridge.utils.logging import log, open_log_file
from local_bridge.version import __version__
from local_bridge.service.update_service import UpdateService
from PySide6.QtCore import Slot, QTimer

class QtTrayManager(QSystemTrayIcon):
    def __init__(self, store: SettingsStore, parent_window=None):
        super().__init__()
        self.store = store
        self.parent_window = parent_window
        self.update_service = UpdateService(store)
        self.update_service.on_notification_click = self._handle_notification_click
        

        icon_path = get_app_icon_path()
        if os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
            
        self.setToolTip("AIDOC Station")
        

        self.activated.connect(self.on_activated)
        

        self._build_menu()
        self.show()
        

        

        self.store.add_listener(self._on_settings_changed)

    def _on_settings_changed(self, key, value):

        keys = ["language", "enable_hotkey", "notify", "move_cursor_to_end", 
                "no_app_action", "html_formatting", "keep_file", "hotkey", "has_update"]
        if key in keys:
            if key == "language":
                from local_bridge.i18n import set_language
                set_language(value)
            self._build_menu()
            
    def _build_menu(self):
        menu = QMenu()
        

        hotkey = self.store.get("hotkey", "Ctrl+Shift+B")
        action_hotkey_info = menu.addAction(t("tray.menu.hotkey_display", hotkey=hotkey))
        action_hotkey_info.setEnabled(False)
        
        menu.addSeparator()
        



        action_enable = menu.addAction(t("tray.menu.enable_hotkey"))
        action_enable.setCheckable(True)

        is_enabled = self.store.get("enable_hotkey", True) 
        action_enable.setChecked(is_enabled)
        action_enable.triggered.connect(lambda c: self._toggle_setting("enable_hotkey", c, "tray.status.hotkey_enabled", "tray.status.hotkey_paused"))
        

        action_notify = menu.addAction(t("tray.menu.show_notifications"))
        action_notify.setCheckable(True)
        action_notify.setChecked(self.store.get("notify", True))
        action_notify.triggered.connect(lambda c: self.store.set("notify", c))
        

        if sys.platform == "win32":
            action_move = menu.addAction(t("tray.menu.move_cursor"))
            action_move.setCheckable(True)
            action_move.setChecked(self.store.get("move_cursor_to_end", True))
            action_move.triggered.connect(lambda c: self._toggle_setting("move_cursor_to_end", c, "tray.status.move_cursor_on", "tray.status.move_cursor_off"))
            

        
        menu.addSeparator()
        

        

        

        menu.addAction(t("tray.menu.open_log")).triggered.connect(self._open_log)
        
        menu.addSeparator()
        

        action_settings = menu.addAction(t("tray.menu.settings"))
        action_settings.triggered.connect(self.show_settings)
        
        menu.addSeparator()
        

        

        action_about = menu.addAction(t("tray.menu.about"))
        action_about.triggered.connect(self._open_about)
        if self.store.get("has_update", False):

            from PySide6.QtGui import QPixmap, QPainter, QColor
            from PySide6.QtCore import Qt
            dot_pixmap = QPixmap(10, 10)
            dot_pixmap.fill(Qt.transparent)
            painter = QPainter(dot_pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QColor("#FF4D4F"))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(2, 2, 6, 6)
            painter.end()
            action_about.setIcon(QIcon(dot_pixmap))
        

        menu.addAction(t("tray.menu.quit")).triggered.connect(self.quit_app)
        
        self.setContextMenu(menu)
        
    def _build_no_app_action_menu(self, parent_menu):
        submenu = parent_menu.addMenu(t("tray.menu.no_app_action"))
        current = self.store.get("no_app_action", "open")
        
        actions = [
            ("open", "action.open"),
            ("save", "action.save"),
            ("clipboard", "action.clipboard"),
            ("none", "action.none")
        ]
        
        group = []
        for key, label_key in actions:
            act = submenu.addAction(t(label_key))
            act.setCheckable(True)
            act.setChecked(current == key)
            act.triggered.connect(lambda c, k=key: self.store.set("no_app_action", k))

    def _build_html_formatting_menu(self, parent_menu):
        submenu = parent_menu.addMenu(t("tray.menu.html_formatting"))
        

        html_opts = self.store.get("html_formatting", {})
        if not isinstance(html_opts, dict): html_opts = {}
        curr_strike = html_opts.get("strikethrough_to_del", True)
        
        act = submenu.addAction(t("tray.menu.strikethrough_to_del"))
        act.setCheckable(True)
        act.setChecked(curr_strike)
        
        def toggle_strike(checked):
            opts = self.store.get("html_formatting", {})
            if not isinstance(opts, dict): opts = {}
            opts["strikethrough_to_del"] = checked
            self.store.set("html_formatting", opts)

            status = t("tray.status.html_strike_on") if checked else t("tray.status.html_strike_off")
            self.showMessage("AIDOC Station", status)
            
        act.triggered.connect(toggle_strike)

    def _toggle_setting(self, key, value, msg_on_key, msg_off_key):
        self.store.set(key, value)
        msg = t(msg_on_key) if value else t(msg_off_key)
        if self.store.get("notify", True):
            self.showMessage("AIDOC Station", msg)

    @Slot()
    def trigger_paste(self):
        log("Tray received trigger_paste signal")
        try:
            from local_bridge.app.workflows import execute_paste_workflow







            import threading
            threading.Thread(target=execute_paste_workflow, daemon=True).start()
            
        except Exception as e:
            msg = f"Failed to execute paste workflow: {e}"
            log(msg)
            if self.store.get("notify", True):
                self.showMessage("AIDOC Station", msg)

    def on_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_settings()

    def show_settings(self, tab=None):
        if self.parent_window:
            self.parent_window.show()
            self.parent_window.activateWindow()
            self.parent_window.raise_()
            if tab and hasattr(self.parent_window, "switch_page_by_name"):
                 self.parent_window.switch_page_by_name(tab)

    def _open_save_dir(self):
        root = self.store.get("save_dir", "")
        path = os.path.expandvars(root)
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except: pass
        if os.path.exists(path):
            os.startfile(path) if sys.platform == "win32" else os.system(f"open '{path}'")

    def _open_log(self):
        open_log_file()
            
    def _trigger_auto_check(self): pass
    def _check_update(self): pass

    def _open_about(self):
        self.show_settings(tab="about")

    def _handle_notification_click(self):
                                                            
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, lambda: self.show_settings(tab="about"))

    def quit_app(self):
        QApplication.instance().quit()
