# -*- coding: utf-8 -*-
"""
@File    : local_bridge/service/spreadsheet/base.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import sys
from abc import ABC, abstractmethod
import time
from typing import List
from ...core.types import PlacementResult
from ...utils.logging import log
from ...i18n import t
from ...utils.clipboard import set_clipboard_rich_text, simulate_paste, preserve_clipboard
from .html_converter import table_to_html, table_to_tsv


class BaseSpreadsheetPlacer(ABC):
                   
    
    @abstractmethod
    def place(self, table_data: List[List[str]], config: dict) -> PlacementResult:
        












           
        pass


class ClipboardHTMLSpreadsheetPlacer(BaseSpreadsheetPlacer):
    



       
    app_name: str = None
    
    def place(self, table_data: List[List[str]], config: dict) -> PlacementResult:
        try:
            keep_format = config.get("excel_keep_format", config.get("keep_format", True))
            paste_delay_s = config.get("paste_delay_s", 0.3)
            

            html_text = table_to_html(table_data, keep_format=keep_format)
            tsv_text = table_to_tsv(table_data)


            with preserve_clipboard():
                set_clipboard_rich_text(html=html_text, text=tsv_text)
                time.sleep(paste_delay_s)
                simulate_paste()

            return PlacementResult(
                success=True,
                method="clipboard_html_table" if keep_format else "clipboard_tsv",
            )
        except Exception as e:
            log(f"{self.app_name} HTML 粘贴失败: {e}")
            return PlacementResult(
                success=False,
                method="clipboard_html_table",
                error=t(f"{self.i18n_prefix}.insert_failed", error=str(e)),
            )
