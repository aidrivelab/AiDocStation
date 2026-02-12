# -*- coding: utf-8 -*-
"""
@File    : local_bridge/service/awakener/launcher.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:42
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import os
import subprocess
from typing import Literal

from ...utils.logging import log
from ...utils.system_detect import is_windows, is_macos


AppType = Literal["word", "wps", "excel", "wps_excel"]


class AppLauncher:
                                     
    
    @staticmethod
    def _open_file_with_default_app(file_path: str) -> bool:
        







           
        try:
            if is_windows():

                try:
                    os.startfile(file_path)
                    log(f"Successfully opened file with os.startfile: {file_path}")
                    return True
                except Exception as e:
                    log(f"os.startfile failed, trying cmd start: {e}")
                    subprocess.Popen(
                        ['cmd', '/c', 'start', '', file_path],
                        shell=False,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    log(f"Successfully opened file with cmd start: {file_path}")
                    return True
            elif is_macos():

                subprocess.Popen(['open', file_path])
                log(f"Successfully opened file with open command: {file_path}")
                return True
            else:

                subprocess.Popen(['xdg-open', file_path])
                log(f"Successfully opened file with xdg-open: {file_path}")
                return True
        except Exception as e:
            log(f"Failed to open file with default application: {e}")
            return False
    
    @staticmethod
    def awaken_and_open_document(docx_path: str) -> bool:
        







           
        if not os.path.exists(docx_path):
            log(f"Document file not found: {docx_path}")
            return False
        
        return AppLauncher._open_file_with_default_app(docx_path)
    
    @staticmethod
    def awaken_and_open_spreadsheet(xlsx_path: str) -> bool:
        







           
        if not os.path.exists(xlsx_path):
            log(f"Spreadsheet file not found: {xlsx_path}")
            return False
        
        return AppLauncher._open_file_with_default_app(xlsx_path)
