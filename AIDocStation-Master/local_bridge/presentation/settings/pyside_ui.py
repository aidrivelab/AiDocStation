# -*- coding: utf-8 -*-
"""
@File    : local_bridge/presentation/settings/pyside_ui.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:42
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import sys
import os
import shutil
import webbrowser
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QLabel, QStackedWidget, QScrollArea, QPushButton, QComboBox, QFrame,
    QFileDialog, QMessageBox, QLineEdit, QSizePolicy
)

from PySide6.QtCore import Qt, QSize, QRect, QVariantAnimation, QTimer
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QIcon, QPixmap, QIntValidator



current_file_path = os.path.abspath(__file__)
presentation_dir = os.path.dirname(os.path.dirname(current_file_path))
project_root = os.path.dirname(os.path.dirname(presentation_dir))

if project_root not in sys.path:
    sys.path.insert(0, project_root)
if presentation_dir not in sys.path:
    sys.path.insert(0, presentation_dir)

from local_bridge.presentation.components.qt_widgets import (
    ModernSwitch, SidebarTile, SettingRow, SectionCard, SCROLLBAR_STYLE,
    ModernComboBox, PathSelector, HotkeyEdit,
    COLOR_BG, COLOR_DIVIDER, COLOR_PRIMARY
)
from local_bridge.utils.hotkey_helper import is_hotkey_available
from local_bridge.i18n import t, set_language
from local_bridge.config.paths import get_log_path, get_app_icon_path, resource_path
from local_bridge.utils.logging import log
from local_bridge.api.supabase_client import supabase_client
from local_bridge.config.defaults import get_default_save_dir, find_pandoc
from local_bridge.utils.protocol_reg import is_protocol_registered, register_aidoc_protocol

try:
    from local_bridge.presentation.settings.settings_store import SettingsStore
except ImportError:
    from settings_store import SettingsStore

from local_bridge.service.update_service import UpdateService
from PySide6.QtWidgets import QProgressBar, QTextEdit


SECONDARY_BTN_STYLE = """
    QPushButton {
        background-color: #E9E9E9;
        color: #333333;
        border-radius: 6px;
        font-weight: normal;
        border: 1px solid #D0D0D0;
    }
    QPushButton:hover {
        background-color: #DADADA;
        border-color: #C0C0C0;
    }
    QPushButton:pressed {
        background-color: #CCCCCC;
    }
"""

class BasePage(QWidget):
                                            
    def __init__(self, title_key: str, store: SettingsStore, parent=None):
        super().__init__(parent)
        self.store = store
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(SCROLLBAR_STYLE + "background-color: #F3F3F3;")
        
        self.container = QWidget()
        self.container.setStyleSheet("background-color: #F3F3F3;")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(20, 40, 25, 40)
        self.container_layout.setSpacing(15)
        self.container_layout.setAlignment(Qt.AlignTop)


        title_text = t(title_key)
        self.title_label = QLabel(title_text)
        self.title_label.setStyleSheet("font-family: 'Microsoft YaHei'; font-size: 26px; font-weight: bold; color: #000000; margin-bottom: 5px;")
        self.container_layout.addWidget(self.title_label)
        
        scroll.setWidget(self.container)
        layout.addWidget(scroll)

    def add_section(self, title_key, widgets):
        return self.add_section_direct_title(t(title_key), widgets)

    def add_section_direct_title(self, title_text, widgets):

        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        section = SectionCard()

        header = QLabel(title_text.upper())
        header.setStyleSheet("font-family: 'Microsoft YaHei'; font-size: 12px; font-weight: bold; color: #666666; margin-left: 5px; margin-bottom: 5px; border: none; background: transparent;")
        
        container_layout.addWidget(header)
        
        for i, widget in enumerate(widgets):
            section.add_row(widget, show_divider=(i < len(widgets) - 1))
        
        section.finish_layout()
        container_layout.addWidget(section)
        

        self.container_layout.addWidget(container)
        return container

class GeneralPage(BasePage):
    def __init__(self, store):
        super().__init__("settings.page.title.general", store)
        
        

        def create_sw(key, default):
            sw = ModernSwitch()
            sw.setChecked(store.get(key, default))
            sw.clicked.connect(lambda: store.set(key, sw.isChecked()))
            return sw
            

        combo_lang = ModernComboBox()

        combo_lang.addItem(t("settings.general.language.auto"), "auto")
        combo_lang.addItem("简体中�?, "zh")
        combo_lang.addItem("English", "en")
        

        current_val = store.get("language", "auto")
        if current_val == "auto": combo_lang.setCurrentIndex(0)
        elif current_val == "zh": combo_lang.setCurrentIndex(1)
        elif current_val == "en": combo_lang.setCurrentIndex(2)
        
        def on_lang_changed(idx):
            lang_map = {0: "auto", 1: "zh", 2: "en"}
            new_lang = lang_map.get(idx, "auto")
            

            store.set("language", new_lang)
            

            set_language(new_lang)
            


            window = self.window()
            if hasattr(window, "retranslateUi"):
                window.retranslateUi()
                



        combo_lang.currentIndexChanged.connect(on_lang_changed)



        icon_active_dir = resource_path(os.path.join("assets", "images", "icon_Active"))
        icon_inactive_dir = resource_path(os.path.join("assets", "images", "icon_Inactive"))
        
        ICON_REF_DISABLED_ACT = os.path.join(icon_active_dir, "icon_refile.png")
        ICON_REF_DISABLED_INA = os.path.join(icon_inactive_dir, "icon_refile.png")
        ICON_REF_BUILTIN_ACT = os.path.join(icon_active_dir, "icon_Template.png")
        ICON_REF_BUILTIN_INA = os.path.join(icon_inactive_dir, "icon_Template.png")
        ICON_BROWSE_ACT = os.path.join(icon_active_dir, "icon_liulan.png")
        ICON_BROWSE_INA = os.path.join(icon_inactive_dir, "icon_liulan.png")
        ICON_RESET_ACT = os.path.join(icon_active_dir, "icon_sync-fill.png")
        ICON_RESET_INA = os.path.join(icon_inactive_dir, "icon_sync-fill.png") 
        ICON_OPEN_ACT = os.path.join(icon_active_dir, "icon_Syspath.png")
        ICON_CLEAN_ACT = os.path.join(icon_active_dir, "icon_clener.png")
        ICON_CLEAN_INA = os.path.join(icon_inactive_dir, "icon_clener.png")


        ICON_SYNC = ICON_RESET_ACT
        ICON_BROWSE = ICON_BROWSE_ACT
        ICON_REFILE = ICON_REF_DISABLED_ACT
        ICON_RESET = ICON_SYNC


        def create_triple_control(ps_widget, btn_data):
            container = QWidget()
            container.setStyleSheet("background-color: #FFFFFF; border: none;")
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(12)
            
            btn_group = QWidget()
            btn_group.setStyleSheet("background-color: #FFFFFF; border: none;")
            btn_group_layout = QHBoxLayout(btn_group)
            btn_group_layout.setContentsMargins(0, 0, 0, 0)
            btn_group_layout.setSpacing(5)
            
            buttons_meta = []

            def refresh_toggles(mk, tm):
                for b, act, ina, tips, is_t, m_key, t_mode in buttons_meta:
                    if m_key == mk:
                        if is_t:
                            b.setIcon(QIcon(act if t_mode == tm else ina))
                        

                        if isinstance(tips, (list, tuple)):
                            b.setToolTip(tips[1] if t_mode == tm else tips[0])

            for act, ina, tips, cb, is_toggle, m_key, t_mode in btn_data:
                btn = QPushButton()
                btn.setFixedSize(25, 25)
                btn.setCursor(Qt.PointingHandCursor)
                btn.setStyleSheet("QPushButton { border: none; background: transparent; padding: 0; } QPushButton:hover { background: #EAEAEA; border-radius: 4px; }")
                
                if is_toggle:
                    curr = store.get(m_key)
                    btn.setIcon(QIcon(act if curr == t_mode else ina))
                else:
                    btn.setIcon(QIcon(act))
                
                btn.setIconSize(QSize(20, 20))
                
                if isinstance(tips, (list, tuple)):
                    curr = store.get(m_key) if is_toggle else None
                    btn.setToolTip(tips[1] if curr == t_mode else tips[0])
                else:
                    btn.setToolTip(tips)
                
                if is_toggle:
                    def make_click(mk=m_key, tm=t_mode, callback=cb):
                        def on_click():
                            store.set(mk, tm)
                            refresh_toggles(mk, tm)
                            if callback: callback(tm)
                        return on_click
                    btn.clicked.connect(make_click())
                else:
                    if cb: btn.clicked.connect(cb)
                
                btn_group_layout.addWidget(btn)
                buttons_meta.append((btn, act, ina, tips, is_toggle, m_key, t_mode))

            container_layout.addWidget(ps_widget)
            container_layout.addWidget(btn_group)


            def on_global_settings_changed(key, val):

                for b, act, ina, tips, is_t, m_key, t_mode in buttons_meta:
                    if m_key == key:
                        refresh_toggles(key, val)
                        break
            
            store.settings_changed.connect(on_global_settings_changed)
            
            return container


        def browse_save_dir():
            d = QFileDialog.getExistingDirectory(self, t("settings.dialog.select_save_dir"), store.get("save_dir", ""))
            if d:
                store.set("save_dir", d)
                ps_save.line_edit.setText(d)
        
        def reset_save_dir():
             default = get_default_save_dir()
             store.set("save_dir", default)
             ps_save.line_edit.setText(default)
        
        def clean_save_dir():
            path = store.get("save_dir", get_default_save_dir())
            if not os.path.exists(path):
                return
            
            deleted_any = False
            total_count = 0
            try:
                if os.path.isdir(path):
                    for f in os.listdir(path):
                        if f.lower().endswith(('.docx', '.xlsx')):
                            try:
                                os.remove(os.path.join(path, f))
                                deleted_any = True
                                total_count += 1
                            except: pass
            except: pass
            
            if deleted_any:
                lbl_save_hint.setText(f"已清理目录下�?{total_count} �?Word/Excel 文件�?)
            else:
                lbl_save_hint.setText("未发现需要清理的 Word �?Excel 文件�?)
                

            QTimer.singleShot(3000, lambda: lbl_save_hint.setText(" "))


        curr_saved_path = str(store.get("save_dir", ""))
        real_default = get_default_save_dir()

        if curr_saved_path and "Users" in curr_saved_path and "Documents" in curr_saved_path:
             if curr_saved_path.lower() != real_default.lower() and "AIDOC" not in curr_saved_path:

                 store.set("save_dir", real_default)
                 curr_saved_path = real_default

        ps_save = PathSelector(
            current_path=curr_saved_path if curr_saved_path else real_default,
            input_width=210,
            show_browse=False
        )
        ps_save.line_edit.editingFinished.connect(lambda: store.set("save_dir", ps_save.line_edit.text()))
        

        lbl_save_hint = QLabel(" ")
        lbl_save_hint.setStyleSheet("color: #335DFF; font-size: 11px; margin-top: -2px; border: none; background: transparent;")

        save_btn_data = [
            (ICON_BROWSE_ACT, ICON_BROWSE_INA, t("settings.general.browse"), browse_save_dir, False, None, None),
            (ICON_CLEAN_ACT, ICON_CLEAN_INA, "删除保存目录文件", clean_save_dir, False, None, None),
            (ICON_RESET_ACT, ICON_RESET_ACT, t("settings.general.restore_default"), reset_save_dir, False, None, None)
        ]
        
        save_controls_vbox = QVBoxLayout()
        save_controls_vbox.setContentsMargins(0, 0, 0, 0)
        save_controls_vbox.setSpacing(2)
        
        save_inner_controls = create_triple_control(ps_save, save_btn_data)
        save_controls_vbox.addWidget(save_inner_controls)
        save_controls_vbox.addWidget(lbl_save_hint)
        
        save_controls = QWidget()
        save_controls.setStyleSheet("background-color: transparent; border: none;")
        save_controls.setLayout(save_controls_vbox)


        def browse_pandoc():
            f, _ = QFileDialog.getOpenFileName(self, t("settings.dialog.select_pandoc"), "", "Executables (*.exe);;All Files (*.*)")
            if f:
                store.set("pandoc_path", f)
                ps_pandoc.line_edit.setText(f)

        def reset_pandoc():
            store.set("pandoc_path", "Auto-detected")
            ps_pandoc.line_edit.setText(find_pandoc())

        val_pandoc = str(store.get("pandoc_path", "Auto-detected"))
        display_pandoc = val_pandoc if val_pandoc != "Auto-detected" else find_pandoc()

        ps_pandoc = PathSelector(
            current_path=display_pandoc,
            placeholder=t("settings.conversion.pandoc_placeholder"),
            input_width=210,
            show_browse=False
        )
        

        lbl_pandoc_ver = QLabel()
        lbl_pandoc_ver.setStyleSheet("color: #666666; font-size: 11px; margin-top: -2px;")
        
        def refresh_pandoc_version(path):
            if not path or not os.path.exists(path):
                lbl_pandoc_ver.setText(" ")
                return
            try:
                import subprocess

                startupinfo = None
                creationflags = 0
                if os.name == "nt":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    creationflags = subprocess.CREATE_NO_WINDOW
                
                res = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=2,
                                     startupinfo=startupinfo, creationflags=creationflags)
                first_line = res.stdout.split('\n')[0]
                lbl_pandoc_ver.setText(first_line)
                lbl_pandoc_ver.setStyleSheet("color: #666666; font-size: 11px; margin-top: -2px; border: none; background: transparent;")
            except:
                lbl_pandoc_ver.setText("Error: Pandoc invalid")
                lbl_pandoc_ver.setStyleSheet("color: #335DFF; font-size: 11px; margin-top: -2px; border: none; background: transparent;")
                QTimer.singleShot(2000, lambda: lbl_pandoc_ver.setText(" "))

        refresh_pandoc_version(display_pandoc)
        
        def update_pandoc_store():
            text = ps_pandoc.line_edit.text().strip()
            if not text:
                store.set("pandoc_path", "Auto-detected")
                ps_pandoc.line_edit.setText(find_pandoc())
            else:
                store.set("pandoc_path", text)
        ps_pandoc.line_edit.editingFinished.connect(update_pandoc_store)

        def reset_pandoc():
            default = find_pandoc()
            store.set("pandoc_path", default)
            ps_pandoc.line_edit.setText(default)
            refresh_pandoc_version(default)

        def check_system_pandoc():
            found = shutil.which("pandoc")
            if found:
                store.set("pandoc_path", found)
                ps_pandoc.line_edit.setText(found)
                refresh_pandoc_version(found)
            else:
                lbl_pandoc_ver.setText("系统环境变量未设置pandoc路径")
                lbl_pandoc_ver.setStyleSheet("color: #335DFF; font-size: 11px; margin-top: -2px; border: none; background: transparent;")

                QTimer.singleShot(2000, lambda: lbl_pandoc_ver.setText(" "))

        pandoc_btn_data = [
            (ICON_BROWSE_ACT, ICON_BROWSE_INA, t("settings.general.browse"), browse_pandoc, False, None, None),
            (ICON_OPEN_ACT, ICON_OPEN_ACT, "设置为系统路�?, check_system_pandoc, False, None, None),
            (ICON_RESET_ACT, ICON_RESET_ACT, t("settings.general.restore_default"), reset_pandoc, False, None, None)
        ]
        
        pandoc_controls_vbox = QVBoxLayout()
        pandoc_controls_vbox.setContentsMargins(0, 0, 0, 0)
        pandoc_controls_vbox.setSpacing(2)
        
        pandoc_inner_controls = create_triple_control(ps_pandoc, pandoc_btn_data)
        pandoc_controls_vbox.addWidget(pandoc_inner_controls)
        pandoc_controls_vbox.addWidget(lbl_pandoc_ver)
        
        pandoc_controls = QWidget()
        pandoc_controls.setStyleSheet("background-color: transparent; border: none;")
        pandoc_controls.setLayout(pandoc_controls_vbox)
        

        def on_pandoc_changed(new_p):
            refresh_pandoc_version(new_p if new_p != "Auto-detected" else find_pandoc())
        
        ps_pandoc.pathChanged.connect(on_pandoc_changed)



        REF_MODE_DISABLED = "disabled"
        REF_MODE_BUILTIN = "built-in"
        REF_MODE_CUSTOM = "custom"


        icon_active_dir = resource_path(os.path.join("assets", "images", "icon_Active"))
        icon_inactive_dir = resource_path(os.path.join("assets", "images", "icon_Inactive"))
        
        ICON_REF_DISABLED_ACT = os.path.join(icon_active_dir, "icon_refile.png")
        ICON_REF_DISABLED_INA = os.path.join(icon_inactive_dir, "icon_refile.png")
        ICON_REF_BUILTIN_ACT = os.path.join(icon_active_dir, "icon_Template.png")
        ICON_REF_BUILTIN_INA = os.path.join(icon_inactive_dir, "icon_Template.png")
        ICON_REF_CUSTOM_ACT = os.path.join(icon_active_dir, "icon_TempUser.png")
        ICON_REF_CUSTOM_INA = os.path.join(icon_inactive_dir, "icon_TempUser.png")


        def browse_ref():
            f, _ = QFileDialog.getOpenFileName(self, t("settings.dialog.select_ref_docx"), "", "Word Documents (*.docx);;All Files (*.*)")
            if f:
                store.set("reference_docx", f)
                ps_ref.line_edit.setText(f)
                return True
            return False
        
        ps_ref = PathSelector(
            current_path=str(store.get("reference_docx") or ""),
            placeholder=t("settings.general.default"),
            input_width=210,
            show_browse=False
        )
        ps_ref.line_edit.editingFinished.connect(lambda: store.set("reference_docx", ps_ref.line_edit.text()))
        

        def ps_set_alpha(self_ps, alpha):
            if alpha >= 1.0:
                self_ps.setGraphicsEffect(None)
            else:
                from PySide6.QtWidgets import QGraphicsOpacityEffect
                eff = QGraphicsOpacityEffect(self_ps)
                eff.setOpacity(alpha)
                self_ps.setGraphicsEffect(eff)
        
        import types
        ps_ref.setAlpha = types.MethodType(ps_set_alpha, ps_ref)

        def update_ref_mode_ui(mode):
            ps_ref.setEnabled(mode == "custom")
            ps_ref.setAlpha(1.0 if mode == "custom" else 0.5)
            

            if mode == REF_MODE_DISABLED:
                ps_ref.line_edit.setPlaceholderText(t("settings.reference.disabled"))
                ps_ref.line_edit.setText("") 
            elif mode == REF_MODE_BUILTIN:
                ps_ref.line_edit.setPlaceholderText(t("settings.reference.builtin"))
                ps_ref.line_edit.setText("")
            else:
                ps_ref.line_edit.setText(str(store.get("reference_docx", "")) if store.get("reference_docx") else "")
                ps_ref.line_edit.setPlaceholderText(t("settings.reference.custom_placeholder"))
            

            hint_opacity.setOpacity(1.0 if mode == REF_MODE_BUILTIN else 0.0)
            hint_container.setEnabled(mode == REF_MODE_BUILTIN)





        ref_btn_data = [
            (ICON_REF_CUSTOM_ACT, ICON_REF_CUSTOM_INA, t("settings.reference.tooltip.custom"), browse_ref, True, "word_reference_mode", "custom"),
            (ICON_REF_BUILTIN_ACT, ICON_REF_BUILTIN_INA, t("settings.reference.tooltip.builtin"), None, True, "word_reference_mode", "built-in"),
            (ICON_REF_DISABLED_ACT, ICON_REF_DISABLED_INA, (t("settings.reference.tooltip.disabled_click"), t("settings.reference.tooltip.disabled_active")), None, True, "word_reference_mode", "disabled"),
        ]
        
        def on_ref_mode_change(mode):
            update_ref_mode_ui(mode)
        
        ref_btn_data_with_cb = []
        for d in ref_btn_data:
            orig_cb = d[3]
            act_mode = d[6]
            def combined_cb(m, old_cb=orig_cb, m_fixed=act_mode):

                if m_fixed == "custom" and old_cb:
                    success = old_cb()
                    current_path = store.get("reference_docx")

                    if not success and not current_path:
                        log("[UI] Custom ref selection cancelled with no existing path. Reverting to built-in.")
                        store.set("word_reference_mode", "built-in")
                        on_ref_mode_change("built-in")
                        return
                
                on_ref_mode_change(m)
                if old_cb and m_fixed != "custom": old_cb()
            ref_btn_data_with_cb.append((*d[:3], combined_cb, *d[4:]))
        

        hint_container = QWidget()
        hint_container.setStyleSheet("background-color: transparent; border: none;")
        from PySide6.QtWidgets import QGraphicsOpacityEffect
        hint_opacity = QGraphicsOpacityEffect(hint_container)
        hint_container.setGraphicsEffect(hint_opacity)
        hint_layout = QHBoxLayout(hint_container)
        hint_layout.setContentsMargins(0, 0, 0, 0)
        hint_layout.setSpacing(5)
        
        lbl_info_icon = QLabel("!")
        lbl_info_icon.setFixedSize(14, 14)
        lbl_info_icon.setAlignment(Qt.AlignCenter)
        lbl_info_icon.setStyleSheet("background-color: #335DFF; color: white; border-radius: 7px; font-weight: bold; font-size: 9px; line-height: 14px;")
        
        btn_edit_builtin = QPushButton(t("settings.reference.edit_builtin"))
        btn_edit_builtin.setStyleSheet("QPushButton { color: #335DFF; border: none; background: transparent; text-decoration: underline; text-align: left; font-size: 12px; } QPushButton:hover { color: #254EDB; }")
        btn_edit_builtin.setCursor(Qt.PointingHandCursor)
        
        def open_builtin_ref():
            builtin_path = resource_path(os.path.join("pandoc", "Reference-document.docx"))
            if os.path.exists(builtin_path):
                os.startfile(builtin_path)
            else:
                QMessageBox.warning(self, "Warning", f"Built-in template not found: {builtin_path}")
        
        btn_edit_builtin.clicked.connect(open_builtin_ref)
        hint_layout.addWidget(lbl_info_icon)
        hint_layout.addWidget(btn_edit_builtin)
        hint_layout.addStretch()

        ref_controls_vbox = QVBoxLayout()
        ref_controls_vbox.setContentsMargins(0, 0, 0, 0)
        ref_controls_vbox.setSpacing(4)
        
        ref_inner_controls = create_triple_control(ps_ref, ref_btn_data_with_cb)
        ref_controls_vbox.addWidget(ref_inner_controls)
        ref_controls_vbox.addWidget(hint_container)
        
        ref_controls = QWidget()
        ref_controls.setStyleSheet("background-color: transparent; border: none;")
        ref_controls.setLayout(ref_controls_vbox)
        

        initial_ref_mode = store.get("word_reference_mode", REF_MODE_DISABLED)
        update_ref_mode_ui(initial_ref_mode)
        
        
        

        

        combo_no_app = ModernComboBox()
        from local_bridge.i18n import get_no_app_action_map
        action_map = get_no_app_action_map()
        

        ordered_keys = ["open", "save", "clipboard", "none"]
        for k in ordered_keys:
            combo_no_app.addItem(action_map.get(k, k), k)
            
        curr_action = store.get("no_app_action", "open")
        idx = ordered_keys.index(curr_action) if curr_action in ordered_keys else 0
        combo_no_app.setCurrentIndex(idx)
        combo_no_app.currentIndexChanged.connect(lambda i: store.set("no_app_action", ordered_keys[i]))


        def check_global_conflict(hk, edit_widget, current_key):
                                   

            other_keys = {
                "hotkey": t("settings.general.hotkey_paste"),
                "hotkey_show_hide": t("settings.general.hotkey_show_hide")
            }
            for k, name in other_keys.items():
                if k != current_key:
                    if store.get(k) == hk:
                        edit_widget.set_conflict(True, t("settings.hotkey.conflict", hotkey=hk, name=name))
                        return True
            

            if not is_hotkey_available(hk):

                from local_bridge.service.hotkey.manager import HotkeyManager
                if HotkeyManager().is_bound(hk):
                    edit_widget.set_conflict(False)
                    return False

                edit_widget.set_conflict(True, t("settings.hotkey.system_conflict", hotkey=hk))
                return True
                
            edit_widget.set_conflict(False)
            return False

        def on_hotkey_changed(hk, key_name, edit_widget):
            store.set(key_name, hk)
            check_global_conflict(hk, edit_widget, key_name)

        hk_paste = HotkeyEdit(
            current_hotkey=store.get("hotkey", "<ctrl>+<alt>+q"),
            default_val="<ctrl>+<alt>+q",
            width=None,

        )
        hk_paste.hotkeyChanged.connect(lambda hk: on_hotkey_changed(hk, "hotkey", hk_paste))

        hk_show_hide = HotkeyEdit(
            current_hotkey=store.get("hotkey_show_hide", "<ctrl>+<alt>+e"),
            default_val="<ctrl>+<alt>+e",
            width=None,

        )
        hk_show_hide.hotkeyChanged.connect(lambda hk: on_hotkey_changed(hk, "hotkey_show_hide", hk_show_hide))
        

        check_global_conflict(store.get("hotkey"), hk_paste, "hotkey")
        check_global_conflict(store.get("hotkey_show_hide"), hk_show_hide, "hotkey_show_hide")






        row_lang = SettingRow(t("settings.general.language"), t("settings.desc.general.language"), combo_lang, icon="Language")
        row_save = SettingRow(t("settings.general.save_dir"), t("settings.desc.general.save_dir"), save_controls, icon="Folder", sub_width=175)
        row_pandoc = SettingRow(t("settings.conversion.pandoc_path"), t("settings.desc.conversion.pandoc_path"), pandoc_controls, icon="Convert", sub_width=175)
        row_ref = SettingRow(t("settings.conversion.reference_docx"), t("settings.desc.conversion.reference_docx"), ref_controls, icon="Format", sub_width=175)
        row_no_app = SettingRow(t("settings.general.no_app_action"), t("settings.desc.general.no_app_action"), combo_no_app, icon="Action")
        row_hk_paste = SettingRow(t("settings.general.hotkey_paste"), t("settings.desc.general.hotkey_paste"), hk_paste, icon="Keyboard")
        row_hk_show_hide = SettingRow(t("settings.general.hotkey_show_hide"), t("settings.desc.general.hotkey_show_hide"), hk_show_hide, icon="Visibility")


        self.add_section("settings.section.general.appearance", [
            row_lang
        ])
        

        self.add_section("settings.section.general.environment", [
            row_save,
            row_pandoc,
            row_ref
        ])
        

        

        def create_hk_row(edit_widget, switch_widget):
            c = QWidget()

            c.setAttribute(Qt.WA_TranslucentBackground)
            c.setStyleSheet("background: transparent;")
            l = QHBoxLayout(c)
            l.setContentsMargins(0, 0, 0, 0)
            l.setSpacing(10)
            l.addWidget(edit_widget)
            l.addWidget(switch_widget)
            return c


        def on_dc_key_change(new_key):
             store.set("double_click_paste_key", new_key)
             if store.get("enable_double_click_paste", False):
                 try:
                     from local_bridge.core.state import app_state
                     app_state.hotkey_manager.start_double_click_listener()
                 except: pass

        edit_dc_paste = HotkeyEdit(
            current_hotkey=store.get("double_click_paste_key", "ctrl_l"),
            default_val="ctrl_l",
            single_key_mode=True,
            width=130,

        )
        edit_dc_paste.hotkeyChanged.connect(on_dc_key_change)



        switch_dc = ModernSwitch()
        switch_dc.setChecked(store.get("enable_double_click_paste", False))
        
        def on_dc_toggle(checked):
            store.set("enable_double_click_paste", checked)
            try:
                from local_bridge.core.state import app_state
                if checked:
                     app_state.hotkey_manager.start_double_click_listener()
                else:
                     app_state.hotkey_manager.stop_double_click_listener()
            except: pass
            
        switch_dc.clicked.connect(lambda: on_dc_toggle(switch_dc.isChecked()))
        
        container_dc = create_hk_row(edit_dc_paste, switch_dc)


        def on_paste_hk_change(new_key):
            store.set("hotkey", new_key)



            pass

        edit_paste = HotkeyEdit(
            current_hotkey=store.get("hotkey", "<ctrl>+<alt>+q"),
            default_val="<ctrl>+<alt>+q",
            width=130,

        )
        edit_paste.hotkeyChanged.connect(on_paste_hk_change)
        
        switch_paste = ModernSwitch()
        switch_paste.setChecked(store.get("enable_paste_hotkey", True))
        switch_paste.clicked.connect(lambda: store.set("enable_paste_hotkey", switch_paste.isChecked()))
        
        container_paste = create_hk_row(edit_paste, switch_paste)
        
        row_hk_paste = SettingRow(t("settings.general.hotkey_paste"), t("settings.desc.general.hotkey_paste"), container_paste, icon="Keyboard")


        def on_sh_hk_change(new_key):
            store.set("hotkey_show_hide", new_key)

        edit_sh = HotkeyEdit(
            current_hotkey=store.get("hotkey_show_hide", "<ctrl>+<alt>+e"),
            default_val="<ctrl>+<alt>+e",
            width=130,

        )
        edit_sh.hotkeyChanged.connect(on_sh_hk_change)
        
        switch_sh = ModernSwitch()
        switch_sh.setChecked(store.get("enable_show_hide_hotkey", True))
        switch_sh.clicked.connect(lambda: store.set("enable_show_hide_hotkey", switch_sh.isChecked()))
        
        container_sh = create_hk_row(edit_sh, switch_sh)
        
        row_hk_show_hide = SettingRow(t("settings.general.hotkey_show_hide"), t("settings.desc.general.hotkey_show_hide"), container_sh, icon="Window")


        self.add_section("settings.section.general.behavior", [
            SettingRow(t("settings.general.double_click_paste"), t("settings.desc.general.double_click_paste"), container_dc, icon="Keyboard"), 
            row_hk_paste,
            row_hk_show_hide,
            row_no_app
        ])




        self.add_section("settings.section.general.startup", [
            SettingRow(t("settings.general.auto_start"), t("settings.desc.general.auto_start"), create_sw("auto_start", False), icon="Start"),
            SettingRow(t("settings.general.start_minimized"), t("settings.desc.general.start_minimized"), create_sw("start_minimized", True), icon="Hidden"),
            SettingRow(t("settings.general.notify"), t("settings.desc.general.notify"), create_sw("notify", True), icon="Notify"),
        ])

class FormattingPage(BasePage):
    def __init__(self, store):
        super().__init__("settings.page.title.formatting", store)
        
        
        def create_sw(key, default):
            sw = ModernSwitch()
            sw.setChecked(store.get(key, default))
            sw.clicked.connect(lambda: store.set(key, sw.isChecked()))
            return sw
            
        def toggle_html_opt(sub_key, default):

            sw = ModernSwitch()
            hf = store.get("html_formatting", {})
            sw.setChecked(hf.get(sub_key, default))
            
            def on_click():
                curr = store.get("html_formatting", {})
                curr[sub_key] = sw.isChecked()
                store.set("html_formatting", curr)
                
            sw.clicked.connect(on_click)
            return sw


        self.add_section("settings.section.formatting.html", [
            SettingRow(t("settings.conversion.strikethrough"), t("settings.desc.conversion.strikethrough"), toggle_html_opt("strikethrough_to_del", True), icon="HTML")
        ])


        self.add_section("settings.section.formatting.cleaning", [
            SettingRow(t("settings.conversion.clean_heading_number"), t("settings.desc.conversion.clean_heading_number"), create_sw("clean_heading_number", False), icon="Clean"),
            SettingRow(t("settings.conversion.disable_first_para_indent"), t("settings.desc.conversion.disable_first_para_indent"), create_sw("disable_first_para_indent", True), icon="Format")
        ])


        combo_cursor = ModernComboBox()
        combo_cursor.addItems([t("settings.conversion.cursor_end"), t("settings.conversion.cursor_newline"), t("settings.conversion.cursor_keep")])
        cursor_map = {"end": 0, "newline": 1, "keep": 2}
        inv_cursor_map = {0: "end", 1: "newline", 2: "keep"}
        curr_cursor = store.get("cursor_position", "end")
        combo_cursor.setCurrentIndex(cursor_map.get(curr_cursor, 0))
        combo_cursor.currentIndexChanged.connect(lambda idx: store.set("cursor_position", inv_cursor_map.get(idx, "end")))

        self.add_section("settings.section.formatting.post_process", [
            SettingRow(t("settings.conversion.soft_break_to_hard"), t("settings.desc.conversion.soft_break_to_hard"), create_sw("soft_break_to_hard", True), icon="Process"),
            SettingRow(t("settings.conversion.remove_horizontal_rules"), t("settings.desc.conversion.remove_horizontal_rules"), create_sw("remove_horizontal_rules", True), icon="Clean"),
            SettingRow(t("settings.conversion.cursor_position"), t("settings.desc.conversion.cursor_position"), combo_cursor, icon="End"),
        ])
        

        self.add_section("settings.section.formatting.excel", [
            SettingRow(t("settings.advanced.excel_enable"), t("settings.desc.advanced.excel_enable"), create_sw("enable_excel", True), icon="Excel"),
            SettingRow(t("settings.advanced.excel_format"), t("settings.desc.advanced.excel_format"), create_sw("excel_keep_format", True), icon="Format"),
        ])

class StylesPage(BasePage):
    def __init__(self, store):
        super().__init__("settings.page.title.styles", store)
        
        
        def create_sw(key, default):
            sw = ModernSwitch()
            sw.setChecked(store.get(key, default))
            sw.clicked.connect(lambda: store.set(key, sw.isChecked()))
            return sw


        def create_combo(key, options, default):
            cb = ModernComboBox()

            for lbl, val in options:
                cb.addItem(lbl, val)
                
            curr = store.get(key, default)

            idx = 0
            for i, (_, val) in enumerate(options):
                if val == curr:
                    idx = i
                    break
            cb.setCurrentIndex(idx)
            
            def on_index_changed(index, k=key, opts=options):
                val = opts[index][1]
                log(f"[UI] Setting config '{k}' to '{val}'")
                store.set(k, val)

            cb.currentIndexChanged.connect(on_index_changed)
            return cb

        style_opts = [
            (t("settings.conversion.body_style_normal"), "正文"),
            (t("settings.conversion.body_style_body_text"), "正文文本"),
            (t("settings.conversion.body_style_indent"), "正文缩进"),
            (t("settings.conversion.body_style_text_indent"), "正文文本缩进"),
            (t("settings.conversion.body_style_text_first_indent"), "正文文本首行缩进"),

        ]
        
        image_styles = [
            (t("settings.style.style_body"), "正文"),
            (t("settings.style.style_caption"), "题注"),
        ]
        
        scales = [("50%", "50%"), ("75%", "75%"), ("95%", "95%"), ("100%", "100%")]
        lines = [("1.0", "1.0"), ("1.15", "1.15"), ("1.5", "1.5"), ("2.0", "2.0")]

        mapping_opts = [
            (t("settings.style.mapping_post_processing"), "post_processing"),
            (t("settings.style.mapping_reference"), "reference_doc"),
        ]
        
        list_opts = [
            (t("settings.style.list_clear"), "clear"),
            (t("settings.style.list_keep"), "keep"),
        ]

        self.add_section("settings.section.styles.body", [
            SettingRow(t("settings.conversion.body_style"), t("settings.desc.conversion.body_style"), create_combo("body_style", style_opts, "正文"), icon="Style"),
            SettingRow(t("settings.style.list_handle_method"), t("settings.desc.style.list_handle_method"), create_combo("list_handle_method", list_opts, "keep"), icon="List"),
            SettingRow(t("settings.style.mapping_method"), t("settings.desc.style.mapping_method"), create_combo("style_mapping_method", mapping_opts, "post_processing"), icon="Process")
        ])
        
        self.add_section("settings.section.styles.table", [
            SettingRow(t("settings.style.table_text_style"), t("settings.desc.style.table_text_style"), create_combo("table_text_style", image_styles, "正文"), icon="Table"),
            SettingRow(t("settings.style.table_line_spacing"), t("settings.desc.style.table_line_spacing"), create_combo("table_line_height_rule", lines, "1.0"), icon="Line"),
        ])
        
        self.add_section("settings.section.styles.image", [
            SettingRow(t("settings.style.image_style"), t("settings.desc.style.image_style"), create_combo("image_style", image_styles, "正文"), icon="Image"),
            SettingRow(t("settings.style.image_scale"), t("settings.desc.style.image_scale"), create_combo("image_scale_rule", scales, "95%"), icon="Width"),
        ])

class ExperimentalPage(BasePage):
    def __init__(self, store):
        super().__init__("settings.page.title.experimental", store)
        
        
        def create_sw(key, default):
            sw = ModernSwitch()
            sw.setChecked(store.get(key, default))
            sw.clicked.connect(lambda: store.set(key, sw.isChecked()))
            return sw
            
        self.add_section("settings.section.experimental.formula", [
            SettingRow(t("settings.conversion.keep_formula"), t("settings.desc.experimental.keep_formula"), create_sw("Keep_original_formula", False), icon="Math"),
            SettingRow(t("settings.conversion.enable_latex_replacements"), t("settings.desc.experimental.enable_latex_replacements"), create_sw("enable_latex_replacements", True), icon="Latex"),
            SettingRow(t("settings.conversion.fix_single_dollar_block"), t("settings.desc.experimental.fix_single_dollar_block"), create_sw("fix_single_dollar_block", True), icon="Block"),
        ])
        
        self.add_section("settings.section.experimental.filters", [
             SettingRow(t("settings.conversion.pandoc_filters"), t("settings.desc.experimental.pandoc_filters"), None, icon="Filter") 
        ])

class AboutPage(BasePage):
    def __init__(self, store):
        super().__init__("settings.page.title.about", store)
        self.update_service = UpdateService(store)
        self._is_install_mode = False
        

        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self._refresh_ui_state)
        self.poll_timer.start(1000)
        self.btn_update = QPushButton(t("settings.row.about.update"))
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(12)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #E9E9E9;
                border-radius: 6px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: #335DFF;
                border-radius: 6px;
            }
        """)
        self.progress_bar.hide()
        
        self.changelog_area = QTextEdit()
        self.changelog_area.setReadOnly(True)
        self.changelog_area.setFrameShape(QFrame.NoFrame)
        self.changelog_area.setMaximumHeight(200)
        self.changelog_area.setStyleSheet("""
            QTextEdit {
                background-color: #F8F9FF;
                border-radius: 8px;
                padding: 12px;
                font-family: 'Microsoft YaHei';
                font-size: 13px;
                color: #444444;
                border: 1px solid #E0E0FF;
            }
        """)
        self.changelog_area.hide()
        
        self.btn_download = QPushButton(t("settings.action.download_now") if "settings.action.download_now" in t("all") else "立即下载并安�?)
        self.btn_download.setFixedHeight(36)
        self.btn_download.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{ background-color: #254EDB; }}
            QPushButton:disabled {{ background-color: #CCCCCC; }}
        """)
        self.btn_download.hide()


        self.btn_update.setFixedSize(100, 32)
        self.btn_update.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: white;
                border: none;
                border-radius: 6px;
                font-family: 'Microsoft YaHei';
                font-size: 13px;
            }}
            QPushButton:hover {{ background-color: #254EDB; }}
            QPushButton:disabled {{ background-color: #CCCCCC; }}
        """)
        self.btn_update.clicked.connect(self.check_update)

        last_check_raw = store.get("last_update_check", "")
        last_check_display = last_check_raw if last_check_raw else t("settings.general.none")
        
        from local_bridge.version import __version__
        self.row_version = SettingRow(
            f"AIDOC Station V{__version__}", 
            t("settings.desc.about.update", time=last_check_display), 
            self.btn_update,
            icon="Version"
        )
        

        self.main_section = SectionCard()
        m_layout = self.main_section.layout
        m_layout.setContentsMargins(0, 0, 0, 0)
        

        m_layout.addWidget(self.row_version)
        

        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Plain)
        line1.setStyleSheet(f"background-color: {COLOR_DIVIDER}; max-height: 1px; border: none;")
        m_layout.addWidget(line1)
        

        self.progress_bar.hide()
        m_layout.addWidget(self.progress_bar)
        

        self.row_auto = SettingRow(t("settings.row.about.auto_update"), t("settings.desc.about.auto_update"), self._create_sw("auto_update", True), icon="Update")
        self.row_notify = SettingRow(t("settings.row.about.notify_update"), t("settings.desc.about.notify_update"), self._create_sw("notify_update", True), icon="Notify")
        
        m_layout.addWidget(self.row_auto)
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Plain)
        line2.setStyleSheet(f"background-color: {COLOR_DIVIDER}; max-height: 1px; border: none;")
        m_layout.addWidget(line2)
        m_layout.addWidget(self.row_notify)
        
        self.container_layout.addWidget(self.main_section)


        self.btn_download = None 
        

        if store.get("has_update", False):
            self._refresh_ui_state()


        log_path = get_log_path()
        try:
            log_size_bytes = os.path.getsize(log_path) if os.path.exists(log_path) else 0
            log_size = f"{log_size_bytes / 1024:.1f} KB"
        except:
            log_size = "0 KB"
            
        display_path = log_path.replace("\\", "\\\u200B").replace("/", "/\u200B")
        
        btn_view_log = QPushButton(t("settings.action.view_logs"))
        from local_bridge.utils.logging import open_log_file, clear_log_file
        btn_view_log.setFixedSize(100, 32)
        btn_view_log.setStyleSheet(SECONDARY_BTN_STYLE)
        btn_view_log.clicked.connect(open_log_file)
        
        self.btn_clean_log = QPushButton(t("settings.action.clean_logs"))
        self.btn_clean_log.setFixedSize(100, 32)
        self.btn_clean_log.setStyleSheet(SECONDARY_BTN_STYLE)
        
        log_btn_container = QWidget()
        log_btn_container.setStyleSheet("background: transparent;")
        lb_layout = QHBoxLayout(log_btn_container)
        lb_layout.setContentsMargins(0, 0, 0, 0)
        lb_layout.setSpacing(10)
        lb_layout.addWidget(btn_view_log)
        lb_layout.addWidget(self.btn_clean_log)
        
        self.log_row = SettingRow(
            t("settings.row.about.logs"), 
            t("settings.desc.about.logs", path=display_path, size=log_size), 
            log_btn_container, 
            icon="Logs"
        )
        self.btn_clean_log.clicked.connect(lambda: self.clean_logs(log_path, display_path))
        
        self.add_section("settings.section.about.devtools", [
             self.log_row
        ])


        btn_web = QPushButton(t("settings.action.website"))
        btn_web.setFixedSize(100, 32)
        btn_web.setStyleSheet(SECONDARY_BTN_STYLE)
        btn_web.clicked.connect(lambda: webbrowser.open("https://www.pcfox.cn"))
        
        btn_github = QPushButton(t("settings.action.github"))
        btn_github.setFixedSize(100, 32)
        btn_github.setStyleSheet(SECONDARY_BTN_STYLE)
        btn_github.clicked.connect(lambda: webbrowser.open("https://github.com/aidrivelab/AiDocStation"))
        
        link_container = QWidget()
        link_container.setStyleSheet("background: transparent;")
        link_layout = QHBoxLayout(link_container)
        link_layout.setContentsMargins(0, 0, 0, 0)
        link_layout.setSpacing(10)
        link_layout.addWidget(btn_web)
        link_layout.addWidget(btn_github)

        qr_container = QWidget()
        qr_container.setStyleSheet("background: transparent;")
        qr_layout = QHBoxLayout(qr_container)
        qr_layout.setContentsMargins(10, 10, 10, 10)
        qr_layout.setSpacing(30)

        def create_qr_widget(file_name, label_text):
            w = QWidget()
            v = QVBoxLayout(w)
            v.setContentsMargins(0, 0, 0, 0)
            v.setSpacing(6)
            img_lbl = QLabel()
            path = resource_path(os.path.join("assets", "images", file_name))
            if os.path.exists(path):
                pix = QPixmap(path)
                dpr = self.devicePixelRatio()
                pix = pix.scaled(QSize(100, 100) * dpr, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                pix.setDevicePixelRatio(dpr)
                img_lbl.setPixmap(pix)
            else:
                img_lbl.setText("Missing")
            img_lbl.setFixedSize(100, 100)
            img_lbl.setStyleSheet("border: 1px solid #EEEEEE; border-radius: 4px; background: white;")
            img_lbl.setAlignment(Qt.AlignCenter)
            v.addWidget(img_lbl, 0, Qt.AlignCenter)
            if label_text:
                txt_lbl = QLabel(label_text)
                txt_lbl.setStyleSheet("color: #666666; font-size: 11px;")
                txt_lbl.setAlignment(Qt.AlignCenter)
                v.addWidget(txt_lbl, 0, Qt.AlignCenter)
            return w

        qr_layout.addWidget(create_qr_widget("AIDriveQR.jpg", t("settings.label.about.qr_wechat")))
        qr_layout.addWidget(create_qr_widget("AIDriveVQR.jpg", t("settings.label.about.qr_support")))
        qr_layout.addStretch()
        
        self.add_section("settings.section.about.official", [
            SettingRow(t("settings.row.about.website"), "", link_container, icon="Web"),
            SettingRow(t("settings.row.about.community"), "", qr_container, icon="QR")
        ])

    def clean_logs(self, log_path, display_path):
        from local_bridge.utils.logging import clear_log_file
        try:
            current_bytes = os.path.getsize(log_path) if os.path.exists(log_path) else 0
            current_kb = current_bytes / 1024.0
        except:
            current_kb = 0
            
        self.clean_anim = QVariantAnimation(self)
        self.clean_anim.setDuration(1000)
        self.clean_anim.setStartValue(current_kb)
        self.clean_anim.setEndValue(0.0)
        
        def on_value_changed(val):
            display_kb = f"{val:.1f} KB"
            self.log_row.set_subtitle(t("settings.desc.about.logs", path=display_path, size=display_kb))
        
        self.clean_anim.valueChanged.connect(on_value_changed)
        
        def on_finished():
            clear_log_file()
            self.log_row.set_subtitle(t("settings.desc.about.logs", path=display_path, size="0.0 KB"))
            self.btn_clean_log.setEnabled(True)
            
        self.clean_anim.finished.connect(on_finished)
        self.btn_clean_log.setEnabled(False)
        self.clean_anim.start()

    def _create_sw(self, key, default):
        sw = ModernSwitch()
        sw.setChecked(self.store.get(key, default))
        sw.clicked.connect(lambda: self.store.set(key, sw.isChecked()))
        return sw

    def check_update(self):
        self.row_version.set_subtitle(t("settings.desc.about.updating"))
        self.btn_update.setEnabled(False)
        def run_check():
            try:
                success = self.update_service.check_update(manual=True)
                QTimer.singleShot(0, lambda: self._on_check_finished(success))
            except Exception as e:
                from local_bridge.utils.logging import log_error
                log_error(f"UI run_check error: {e}")
                QTimer.singleShot(0, lambda: self._on_check_finished(False))
        import threading
        threading.Thread(target=run_check, daemon=True).start()

    def _on_check_finished(self, success: bool):
        self.btn_update.setEnabled(True)
        self.btn_update.setText(t("settings.row.about.update"))
        

        self._refresh_ui_state()

    def _refresh_ui_state(self):
                                                              

        if self.update_service.is_checking:

            self.btn_update.setEnabled(False)
            return


        if self.update_service.is_downloading:
            self.btn_update.setEnabled(False)
            self.btn_update.setText(t("settings.row.about.is_downloading"))
            self.progress_bar.show()
            self.progress_bar.setValue(self.update_service.download_progress)
            self.row_version.set_subtitle(t("settings.desc.about.downloading", progress=self.update_service.download_progress))
            self._is_install_mode = False
            return


        if self.update_service.is_update_downloaded():
            self.btn_update.setEnabled(True)
            self.btn_update.setText(t("settings.row.about.install"))
            self.progress_bar.hide()
            self.row_version.set_subtitle(t("settings.desc.about.ready"))
            

            if not self._is_install_mode:
                self._is_install_mode = True
                try: self.btn_update.clicked.disconnect()
                except: pass
                self.btn_update.clicked.connect(self.install_update)
            return


        if self.update_service.update_available:
            version = self.update_service.update_info.get("version", "unknown").lstrip('v')
            self.btn_update.setEnabled(True)
            self.btn_update.setText(t("settings.row.about.download"))
            self.progress_bar.hide()
            self.row_version.set_subtitle(t("settings.desc.about.detected", version=f"v{version}"))
            

            if self._is_install_mode or self.btn_update.text() == t("settings.row.about.update"):
                self._is_install_mode = False
                try: self.btn_update.clicked.disconnect()
                except: pass
                self.btn_update.clicked.connect(self.start_download)
            return


        self.btn_update.setEnabled(True)
        self.btn_update.setText(t("settings.row.about.update"))
        self.progress_bar.hide()
        
        last_check = self.store.get("last_update_check", t("settings.general.none"))
        self.row_version.set_subtitle(t("settings.desc.about.update", time=last_check))
        

        try: self.btn_update.clicked.disconnect()
        except: pass
        self.btn_update.clicked.connect(self.check_update)
        self._is_install_mode = False

    def start_download(self):
                                        
        log("AboutPage: Starting download manually.")
        self.btn_update.setEnabled(False)
        self.btn_update.setText(t("settings.row.about.is_downloading"))
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        

        import threading
        threading.Thread(target=self.update_service.download_update, daemon=True).start()

    def install_update(self):
                                      
        path = self.update_service.get_local_download_path()
        if path and os.path.exists(path):
            log(f"AboutPage: Launching installer: {path}")
            os.startfile(path)


        else:
            log_error(f"AboutPage: Installer not found at {path}")
            self.update_service.last_download_path = None
            self._refresh_ui_state()

    def update_log_info(self):
        pass


class AccountPage(BasePage):
    def __init__(self, store):
        super().__init__("settings.page.title.account", store)
        
        self.stat_labels = {}
        self._repair_feedback = None
        self._sync_feedback = False
        

        self._login_countdown = 0
        self._login_waiting_failed = False
        self._login_timer = QTimer()
        self._login_timer.timeout.connect(self._on_login_tick)
        
        self.init_ui()
        

        self.store.settings_changed.connect(self._on_settings_changed)
        
        self.update_profile_ui()

    def _on_settings_changed(self, key, value):
        if key == "last_sync_time":
            self.update_profile_ui()
        elif key == "stats":
            self.update_stats_ui()

    def init_ui(self):

        stats_header_text = t("settings.row.about.stats") 
        stats_header = QLabel(stats_header_text)
        stats_header.setStyleSheet("font-family: 'Microsoft YaHei'; font-size: 12px; font-weight: bold; color: #666666; margin-left: 5px; margin-bottom: 5px; border: none; background: transparent;")
        
        stats_desc_text = t("settings.desc.about.stats")
        stats_desc = QLabel(stats_desc_text)
        stats_desc.setStyleSheet("color: #999999; font-size: 11px; margin-left: 5px; margin-bottom: 10px;")

        stats_container = QWidget()
        stats_layout = QVBoxLayout(stats_container)
        stats_layout.setContentsMargins(15, 10, 15, 10)
        stats_layout.setSpacing(10)
        
        def create_stat_item(icon_name, stat_key):
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(8)
            try:
                icon_path = resource_path(os.path.join("assets", "images", "icon_Active", icon_name))
                if os.path.exists(icon_path):
                    lbl_icon = QLabel()
                    pix = QPixmap(icon_path)
                    dpr = self.devicePixelRatio()
                    pix = pix.scaled(QSize(24, 24) * dpr, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    pix.setDevicePixelRatio(dpr)
                    lbl_icon.setPixmap(pix)
                    lbl_icon.setFixedSize(24, 24)
                    item_layout.addWidget(lbl_icon)
                else:
                    lbl_fallback = QLabel("�?)
                    lbl_fallback.setStyleSheet("color: #CCCCCC;")
                    item_layout.addWidget(lbl_fallback)
            except Exception: pass
            lbl_text = QLabel()
            lbl_text.setStyleSheet("color: #333333; font-size: 13px;")
            self.stat_labels[stat_key] = lbl_text
            item_layout.addWidget(lbl_text)
            item_layout.addStretch()
            return item_widget

        row1 = QWidget(); r1l = QHBoxLayout(row1); r1l.setContentsMargins(0,0,0,0); r1l.setSpacing(15)
        r1l.addWidget(create_stat_item("icon-word.png", "word_paste_count"))
        r1l.addWidget(create_stat_item("icon-wenben.png", "word_char_count"))
        r1l.addWidget(create_stat_item("icon-biaoge.png", "excel_paste_count"))
        
        row2 = QWidget(); r2l = QHBoxLayout(row2); r2l.setContentsMargins(0,0,0,0); r2l.setSpacing(15)
        r2l.addWidget(create_stat_item("icon-tupian.png", "image_paste_count"))
        r2l.addWidget(create_stat_item("icon-table.png", "table_paste_count"))
        r2l.addStretch()
        
        stats_layout.addWidget(row1)
        stats_layout.addWidget(row2)
        
        self.container_layout.addWidget(stats_header)
        self.container_layout.addWidget(stats_desc)
        self.container_layout.addWidget(stats_container)
        self.update_stats_ui()


        profile = supabase_client.get_profile()
        

        def handle_login():
            supabase_client.open_web_login()
            self.start_login_countdown()

        def handle_logout():
            supabase_client.logout()
            self.stop_login_countdown()
            self.update_profile_ui()

        self.btn_login = QPushButton(t("settings.account.login"))
        self.btn_login.clicked.connect(handle_login)
        self.btn_login.setFixedSize(120, 32)
        self.btn_login.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY}; 
                color: white; 
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #254EDB; }}
            QPushButton:disabled {{ background-color: #CCCCCC; color: #FFFFFF; }}
        """)
        
        self.btn_logout = QPushButton(t("settings.account.logout") if hasattr(self, "btn_logout") or True else "Logout")
        self.btn_logout.clicked.connect(handle_logout)
        self.btn_logout.setFixedSize(100, 32)
        self.btn_logout.setStyleSheet(SECONDARY_BTN_STYLE)
        self.btn_logout.hide()

        self.login_row = SettingRow(t("settings.account.login"), t("settings.account.login_desc"), self.btn_login, icon="Account", sub_width=400)

        self.login_row.sub_label.setOpenExternalLinks(False)
        self.login_row.sub_label.linkActivated.connect(self._handle_subtitle_link)
        
        self.add_section("settings.account.profile", [
            self.login_row
        ])
        

        self.switch_sync = ModernSwitch()
        self.switch_sync.setChecked(self.store.get("enable_auto_sync", True))
        self.switch_sync.clicked.connect(lambda: self.store.set("enable_auto_sync", self.switch_sync.isChecked()))

        sync_title = t("settings.account.sync_title")
        

        self.btn_sync_now = QPushButton(t("settings.account.sync_now"))
        self.btn_sync_now.setFixedSize(80, 26)
        self.btn_sync_now.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #335DFF;
                border: 1px solid #335DFF;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #F0F4FF; }
            QPushButton:pressed { background-color: #E0E8FF; }
        """)
        self.btn_sync_now.clicked.connect(self.manual_sync)
        
        sync_control_container = QWidget()
        sync_control_container.setStyleSheet("background: transparent;")
        scc_layout = QHBoxLayout(sync_control_container)
        scc_layout.setContentsMargins(0, 0, 0, 0)
        scc_layout.setSpacing(10)
        scc_layout.addWidget(self.btn_sync_now)
        scc_layout.addWidget(self.switch_sync)

        self.sync_row = SettingRow(
            sync_title,
            "",
            sync_control_container, 
            icon="Update",
            sub_width=350 
        )
        self.sync_section = self.add_section(sync_title, [
            self.sync_row
        ])
        

        QTimer.singleShot(100, self.update_profile_ui)

    def _handle_subtitle_link(self, link):
                               
        if link == "fix":
            self.repair_web_link()
        elif link == "login":

            supabase_client.open_web_login()
            self.start_login_countdown()

    def start_login_countdown(self):
                                   
        self._login_countdown = 30
        self._login_waiting_failed = False
        self._login_timer.start(1000)
        self.update_profile_ui()

    def stop_login_countdown(self, failed=False):
                          
        self._login_timer.stop()
        self._login_countdown = 0

        self._login_waiting_failed = False
        self.update_profile_ui()

    def _on_login_tick(self):
                      
        if self._login_countdown > 0:
            self._login_countdown -= 1
            if self._login_countdown == 0:
                self.stop_login_countdown(failed=True)
            else:
                self.update_profile_ui()
        else:
            self.stop_login_countdown()

    def repair_web_link(self):
                                                                                             
        if True:
            log("[Protocol] Repair success. Requesting UI feedback...")
            self._repair_feedback = "success"
        else:
            log("[Protocol] Repair failed.")
            self._repair_feedback = "failed"
        

        self.update_profile_ui()
        

        QTimer.singleShot(5000, self._clear_repair_feedback)

    def _clear_repair_feedback(self):
        self._repair_feedback = None
        self.update_profile_ui()

    def manual_sync(self):
                                    
        stats = self.store.get("stats", {})
        supabase_client.sync_stats(stats)
        

        self._sync_feedback = True
        self.update_profile_ui()
        

        QTimer.singleShot(3000, self._clear_sync_feedback)

    def _clear_sync_feedback(self):
        self._sync_feedback = False
        self.update_profile_ui()

    def update_profile_ui(self):
                                                                                        
        profile = supabase_client.get_profile()
        

        is_link_ok = True
        if sys.platform == "win32":
            is_link_ok = is_protocol_registered()

        if profile:

            self.login_row.set_title(t("settings.account.logged_in_as"))
            self.login_row.set_subtitle(f"{profile['email']}")
            self.btn_login.hide()
            

            if self.btn_logout.parent() is None or self.btn_logout.parent() != self.login_row:
                 self.login_row.content_layout.addWidget(self.btn_logout)
            
            self.btn_logout.show()
            self.sync_section.show()
            

            desc_text = t("settings.account.sync_desc")
            last_sync = self.store.get("last_sync_time")
            
            sync_status_label = t("settings.account.sync_status")
            if not last_sync or last_sync == t("settings.account.sync_never"):
                status_text = t("settings.account.sync_waiting")
                status_html = f"<span style='color: #E6A23C; font-weight: bold;'>{sync_status_label}: {status_text}</span>"
            else:
                status_text = t("settings.account.sync_done")
                last_time_label = t("settings.account.sync_last_time")

                status_html = f"<span style='color: #335DFF; font-weight: bold;'>{sync_status_label}: {status_text}</span> ({last_time_label}: {last_sync})"
                
            full_subtitle = f"<div style='line-height: 140%;'>{desc_text}<br/>{status_html}</div>"
            

            if getattr(self, "_sync_feedback", False):
                success_msg = t("settings.account.sync_success")
                full_subtitle = f"<div style='line-height: 140%;'>{desc_text}<br/><span style='color: #335DFF; font-weight: bold;'>�?{success_msg}</span></div>"

            self.sync_row.set_subtitle(full_subtitle)
        else:

            self.login_row.set_title(t("settings.account.login"))
            

            if self._login_countdown > 0:

                self.login_row.set_subtitle(t("settings.account.login_waiting_desc"))
                self.btn_login.setText(t("settings.account.login_waiting_btn", seconds=self._login_countdown))
                self.btn_login.setEnabled(False)
            else:

                self.btn_login.setText(t("settings.account.login"))
                self.btn_login.setEnabled(True)


                if getattr(self, "_repair_feedback", None) == "success":
                    success_text = t("settings.account.fix_success")

                    self.login_row.set_subtitle(f"<span style='color: #335DFF; font-weight: bold;'>�?{success_text}</span>")
                elif getattr(self, "_repair_feedback", None) == "failed":
                    failed_text = t("settings.account.fix_failed")
                    self.login_row.set_subtitle(f"<span style='color: #F56C6C; font-weight: bold;'>�?{failed_text}</span>")
                else:

                    if not is_link_ok:

                        broken_text = t("settings.account.protocol_broken_desc")
                        self.login_row.set_subtitle(broken_text)
                    else:

                        self.login_row.set_subtitle(t("settings.account.login_desc"))

            self.btn_login.show()
            self.btn_logout.hide()
            self.sync_section.hide()

    def _format_large_number(self, value):
                                                                          
        from local_bridge.i18n import get_language
        lang = get_language()
        is_zh = (lang == "zh")
        
        try:
            num = float(value)
            if is_zh:
                if num < 10000:
                    return str(int(num))
                elif num < 100000000:
                    v = num / 10000
                    unit = t("settings.stats.unit_wan")
                    return f"{v:.1f}{unit}".replace(f".0{unit}", unit)
                else:
                    v = num / 100000000
                    unit = t("settings.stats.unit_yi")
                    return f"{v:.2f}{unit}".rstrip('0').rstrip('.') + unit
            else:

                if num < 1000:
                    return str(int(num))
                elif num < 1000000:
                    v = num / 1000
                    return f"{v:.1f}k".replace(".0k", "k")
                else:
                    v = num / 1000000
                    return f"{v:.2f}M".rstrip('0').rstrip('.') + "M"
        except:
            return str(value)

    def update_stats_ui(self):
                                                                            
        stats = self.store.get("stats", {})
        if not isinstance(stats, dict): stats = {}
        mapping = {
            "word_paste_count": (t("settings.stats.word_paste"), "settings.stats.format_times"),
            "word_char_count": (t("settings.stats.char_count"), "settings.stats.format_chars"),
            "image_paste_count": (t("settings.stats.image_paste"), "settings.stats.format_times"),
            "word_char_count": (t("settings.stats.char_count"), "settings.stats.format_chars"),
            "image_paste_count": (t("settings.stats.image_paste"), "settings.stats.format_times"),
            "table_paste_count": (t("settings.stats.table_paste"), "settings.stats.format_times"),
            "excel_paste_count": (t("settings.stats.excel_paste"), "settings.stats.format_times")
        }
        

        for key, (prefix, fmt_key) in mapping.items():
            if key in self.stat_labels:
                count = stats.get(key, 0)
                formatted = self._format_large_number(count)

                if "count" in key and "char" not in key:
                    self.stat_labels[key].setText(f"{prefix}: {t(fmt_key, value=formatted)}")
                else:

                    unit_char = t("settings.stats.unit_word")
                    self.stat_labels[key].setText(f"{prefix}: {formatted} {unit_char}")

class SettingsDialog(QMainWindow):
    def __init__(self, store=None):
        super().__init__()
        self.setWindowTitle("AIDoc Station")
        self.resize(930, 600)
        self.store = store or SettingsStore()
        

        def sync_about_dot(key, val):
            if key == "has_update":
                btn_about = self.nav_buttons[4]
                btn_about.set_show_dot(val)
        
        self.store.add_listener(sync_about_dot)
        

        self.setStyleSheet("""
            QToolTip {
                color: #000000;
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
            }
        """)
        

        icon_path = get_app_icon_path()
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        

        center = QWidget()
        self.setCentralWidget(center)
        self.main_layout = QHBoxLayout(center)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
    

        

        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet("background-color: #FFFFFF; border: none;")
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(24, 20, 10, 20)
        self.sidebar_layout.setSpacing(5)
        

        logo_label = QLabel()

        logo_brand_path = resource_path(os.path.join("assets", "images", "aidrivelogo.png"))
        logo_path = get_app_icon_path() 
        
        if os.path.exists(logo_brand_path):
             logo_label.setPixmap(QPixmap(logo_brand_path).scaled(180, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        elif os.path.exists(logo_path):

             pixmap = QPixmap(logo_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
             logo_label.setPixmap(pixmap)
             
        logo_box = QHBoxLayout()
        logo_box.addWidget(logo_label)
        if not os.path.exists(logo_brand_path):
             logo_text = QLabel("AIDoc Station")
             logo_text.setStyleSheet("font-weight: bold; font-size: 20px; color: #335DFF; font-family: 'Microsoft YaHei';")
             logo_box.addWidget(logo_text)
             
        logo_box.addStretch()
        
        self.sidebar_layout.addLayout(logo_box)
        self.sidebar_layout.addSpacing(20)
        

        icon_base = resource_path(os.path.join("assets", "images", "icon_Active"))
        
        self.nav_buttons = []

        lite_items = [
            (os.path.join(icon_base, "icon_general.png"), "settings.nav.general"),
            (os.path.join(icon_base, "icon_formatting.png"), "settings.nav.formatting"),
            (os.path.join(icon_base, "icon_styles.png"), "settings.nav.styles"),
            (os.path.join(icon_base, "icon_experimental.png"), "settings.nav.experimental"),
        ]
        for i, (icon, title_key) in enumerate(lite_items):
            btn = SidebarTile(icon, t(title_key), selected=(i==0))
            btn.clicked.connect(lambda checked=False, idx=i: self.switch_page(idx))
            self.sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)
            
        self.sidebar_layout.addStretch()
        
        self.footer_label = QLabel(f'<a href="https://www.pcfox.cn" style="color: #AAAAAA; text-decoration: none;">{t("settings.footer.powered_by")}</a>')
        self.footer_label.setOpenExternalLinks(True)
        self.footer_label.setCursor(Qt.PointingHandCursor)
        self.footer_label.setStyleSheet("font-size: 10px; margin-bottom: 10px;")
        self.footer_label.setContentsMargins(0, 0, 36, 0)
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.sidebar_layout.addWidget(self.footer_label)
        
        self.main_layout.addWidget(self.sidebar)
        

        self.content_stack = QStackedWidget()
        self._init_pages()
        
        self.main_layout.addWidget(self.content_stack)

    def _init_pages(self):
                                                 

        for i in range(self.content_stack.count() - 1, -1, -1):
            widget = self.content_stack.widget(i)
            self.content_stack.removeWidget(widget)
            widget.deleteLater()
            
        self.content_stack.addWidget(GeneralPage(self.store))
        self.content_stack.addWidget(FormattingPage(self.store))
        self.content_stack.addWidget(StylesPage(self.store))
        self.content_stack.addWidget(ExperimentalPage(self.store))


    def retranslateUi(self):
                                       

        self.setWindowTitle("AIDoc Station")
        

        for i, btn in enumerate(self.nav_buttons):
            if i < len(self.nav_items_data):
                 _, key = self.nav_items_data[i]
                 btn.setText(t(key))
                 

        self.footer_label.setText(f'<a href="https://www.pcfox.cn" style="color: #AAAAAA; text-decoration: none;">{t("settings.footer.powered_by")}</a>')
                 

        current_idx = self.content_stack.currentIndex()
        self._init_pages()
        self.content_stack.setCurrentIndex(current_idx)


    def switch_page(self, index):
        self.content_stack.setCurrentIndex(index)
        

        for i, btn in enumerate(self.nav_buttons):
            btn.set_selected(i == index)
            

        if index == 4:
             w = self.content_stack.widget(4)
             if hasattr(w, "update_log_info"): w.update_log_info()
        if index == 5:
             w = self.content_stack.widget(5)
             if hasattr(w, "update_profile_ui"): w.update_profile_ui()
             if hasattr(w, "update_stats_ui"): w.update_stats_ui()

    def refresh_auth_status(self):
                                                                                          



        account_page = self.content_stack.widget(5)
        

        if hasattr(account_page, "stop_login_countdown"):
            account_page.stop_login_countdown()

        if hasattr(account_page, "update_profile_ui"):
            account_page.update_profile_ui()
        

        self.switch_page(5)

    def switch_page_by_name(self, name):
                                                                  
        mapping = {
            "general": 0,
            "formatting": 1,
            "styles": 2,
            "experimental": 3,
            "about": 4,
            "account": 5
        }
        if name in mapping:
            self.switch_page(mapping[name])

    def closeEvent(self, event):
        

           
        if self.store.get("start_minimized", True):
             event.ignore()
             self.hide()
        else:

             event.ignore()
             self.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    store = SettingsStore()
    w = SettingsDialog(store)
    w.show()
    sys.exit(app.exec())
