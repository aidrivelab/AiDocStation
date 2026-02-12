# -*- coding: utf-8 -*-
"""
@File    : local_bridge/config/defaults.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import os
import sys
from typing import Dict, Any
from .paths import resource_path
from ..utils.system_detect import is_macos, is_windows


def find_pandoc() -> str:
    







       

    pandoc_binary = "pandoc.exe" if is_windows() else "pandoc"

    if is_macos():
        base_dir = os.path.dirname(sys.executable)
        candidate = os.path.join(base_dir, "pandoc", "bin", pandoc_binary)
        if os.path.exists(candidate):
            return candidate
    

    exe_dir = os.path.dirname(sys.executable)
    candidate = os.path.join(exe_dir, "pandoc", pandoc_binary)
    if os.path.exists(candidate):
        return candidate


    candidate = resource_path(f"pandoc/{pandoc_binary}")
    if os.path.exists(candidate):
        return candidate


    return "pandoc"


def get_default_save_dir() -> str:
                                    
    if is_windows():
        try:
            import ctypes
            from ctypes import wintypes

            buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
            ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, buf)
            base_dir = buf.value
        except:

            base_dir = os.path.expandvars(r"%USERPROFILE%\Documents")
        return os.path.join(base_dir, "AIDocStation")
    else:

        base_dir = os.path.expanduser("~/Documents")
        return os.path.join(base_dir, "AIDocStation")


DEFAULT_CONFIG: Dict[str, Any] = {
    "hotkey": "<ctrl>+<alt>+q",
    "hotkey_show_hide": "<ctrl>+<alt>+e",
    "pandoc_path": find_pandoc(),
    "reference_docx": None,
    "word_reference_mode": "built-in",
    "save_dir": get_default_save_dir(),
    "keep_file": False,
    "notify": True,

    "enable_double_click_paste": False,
    "double_click_paste_key": "ctrl_l",

    "enable_paste_hotkey": True,
    "enable_show_hide_hotkey": True,
    "enable_excel": True,
    "excel_keep_format": True,
    "no_app_action": "open",



    "style_mapping_method": "post_processing",



    "list_handle_method": "keep",


    "html_formatting": {
        "strikethrough_to_del": True,
    },

    "Keep_original_formula": False,
    "language": "auto",
    "enable_latex_replacements": True,
    "fix_single_dollar_block": True,
    "pandoc_filters": [],
    


    "auto_start": True,
    "start_minimized": True,
    "is_first_run": True,
    

    "aidoc_port": 4286,
    "aidoc_api_enabled": False,
    

    "body_style": "正文",
    "table_style": "",
    "table_line_spacing": True,
    "soft_break_to_hard": True,
    "cursor_position": "end",
    "remove_horizontal_rules": True,
    "table_border_default": True,
    

    "clean_heading_number": True,
    "disable_first_para_indent": True,
    
    "table_text_style": "正文",
    "table_line_height_rule": "1.0",
    "image_style": "正文",
    "image_scale_rule": "95%",
    

    "last_check_time": "",
    "enable_auto_sync": True,
    "last_sync_time": "从未同步",
    "has_update": False,
    "remote_update_info": {},
    "last_update_check": "",
    "stats": {
        "word_paste_count": 0,
        "word_char_count": 0,
        "table_paste_count": 0,
        "image_paste_count": 0,
        "excel_paste_count": 0,
    }
}
