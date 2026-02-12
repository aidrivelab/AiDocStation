# -*- coding: utf-8 -*-
"""
@File    : local_bridge/service/document/win32/wps.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:42
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from ..base import BaseDocumentPlacer
import os
from ....utils.win32.memfile import EphemeralFile
from ....core.errors import InsertError
from ....core.types import PlacementResult
from ....utils.logging import log
from ....i18n import t


from .wps_inserter import WPSInserter


class WPSPlacer(BaseDocumentPlacer):
                           
    
    def __init__(self):
        self.com_inserter = WPSInserter()
    
    def place(self, docx_bytes: bytes, config: dict) -> PlacementResult:
                             
        try:
            from ....config.paths import resource_path
            

            mode = config.get("word_reference_mode", "disabled")
            if mode == "disabled":
                template_path = None
            elif mode == "custom":
                template_path = config.get("reference_docx")
                if not template_path or not os.path.exists(template_path):
                    template_path = None
            else:
                template_path = resource_path("pandoc/Reference-document.docx")

            with EphemeralFile(suffix=".docx") as eph:
                eph.write_bytes(docx_bytes)

                success = self.com_inserter.insert(
                    eph.path,
                    template_path=template_path,
                    sync_mode=mode,
                    move_cursor_to_end=config.get("move_cursor_to_end", True),
                    table_text_style=config.get("table_text_style", "正文"),
                    body_style=config.get("body_style", "正文"),
                    image_style=config.get("image_style", "正文"),
                    image_scale=config.get("image_scale", 100),
                    list_handle_method=config.get("list_handle_method", "clear"),
                    table_line_height_rule=config.get("table_line_height_rule", "1.0")
                )
            
            if success:
                return PlacementResult(success=True, method="com")
            else:
                raise InsertError("COM 插入返回 False")
        
        except Exception as e:
            log(f"WPS COM 插入失败: {e}")
            return PlacementResult(
                success=False,
                method="com",
                error=t("placer.win32_wps.insert_failed", error=str(e))
            )
