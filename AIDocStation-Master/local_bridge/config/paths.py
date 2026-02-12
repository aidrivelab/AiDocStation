# -*- coding: utf-8 -*-
"""
@File    : local_bridge/config/paths.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import os
import sys

def get_app_data_dir() -> str:
                                                                            
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.path.expanduser("~/.config")
    
    path = os.path.join(base, "AIDOC")
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def get_log_path() -> str:
                                       
    return os.path.join(get_app_data_dir(), "aidoc.log")

def get_config_path() -> str:
                                               
    return os.path.join(get_app_data_dir(), "config.json")

def resource_path(relative_path: str) -> str:
                                                                           
    try:

        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        base_path = os.path.join(base_path, "local_bridge")

    return os.path.join(base_path, relative_path)

def get_app_icon_path() -> str:
                                                     

    return resource_path(os.path.join("assets", "icons", "icon.png"))


def get_app_white_png_path() -> str:
                                                                                        

    white_path = resource_path(os.path.join("assets", "icons", "icon_white.png"))
    if os.path.exists(white_path):
        return white_path
    return get_app_icon_path()


def get_app_icon_ico_path() -> str:
                                                                                     
    return resource_path(os.path.join("assets", "icons", "logo.ico"))
