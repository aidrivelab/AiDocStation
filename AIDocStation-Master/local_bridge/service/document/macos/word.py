# -*- coding: utf-8 -*-
"""
@File    : local_bridge/service/document/macos/word.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:42
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import subprocess
import os
from ..base import BaseDocumentPlacer
from ....core.types import PlacementResult
from ....utils.logging import log
from ....i18n import t
from ....config.paths import get_user_data_dir


class WordPlacer(BaseDocumentPlacer):
                          
    
    def __init__(self):
                             
        super().__init__()

        temp_dir = os.path.join(get_user_data_dir(), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        self._fixed_temp_path = os.path.join(temp_dir, "local_bridge_word_insert.docx")
        log(f"Word 临时文件路径: {self._fixed_temp_path}")
    
    def place(self, docx_bytes: bytes, config: dict) -> PlacementResult:
                                     
        try:

            with open(self._fixed_temp_path, 'wb') as f:
                f.write(docx_bytes)
            

            move_cursor_to_end = config.get("move_cursor_to_end", True)
            success = self._applescript_insert(self._fixed_temp_path, move_cursor_to_end)
            
            if success:
                return PlacementResult(success=True, method="applescript")
            else:
                raise Exception(t("placer.macos_word.applescript_failed"))
        
        except Exception as e:
            log(f"Word AppleScript 插入失败: {e}")
            return PlacementResult(
                success=False,
                method="applescript",
                error=t("placer.macos_word.insert_failed", error=str(e))
            )
    
    def _applescript_insert(self, docx_path: str, move_cursor_to_end: bool = True) -> bool:
        

           


        posix_path = os.path.abspath(docx_path)

        script = f'''
        tell application "Microsoft Word"
            activate
            if (count of documents) is 0 then
                make new document
            end if
            
            -- 如果当前有选区，先删除再插入（否则 insert file 会“插入”而不是“替换”）
            try
                set selRange to text object of selection
                if (start of selRange) is not (end of selRange) then
                    delete selRange
                end if
            on error
                try
                    delete selection
                end try
            end try

            -- 在当前光标位置插入文件（插入�?selection 通常会选中新内容）
            set targetRange to text object of selection
            insert file at targetRange file name "{posix_path}"
        end tell
        '''
        
        try:
            subprocess.run(
                ["osascript", "-e", script],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30
            )
            log(f"AppleScript 插入成功: {docx_path} ")
            return True
        except subprocess.CalledProcessError as e:

            error_msg = e.stderr.strip()
            log(f"AppleScript 执行失败: {error_msg}")
            

            if "file not found" in error_msg.lower():
                raise Exception(f"Word 找不到文�? {posix_path}")
            
            raise Exception(f"AppleScript 错误: {error_msg}")
        except subprocess.TimeoutExpired:
            log("AppleScript 执行超时")
            raise Exception(t("placer.macos_word.timeout"))
