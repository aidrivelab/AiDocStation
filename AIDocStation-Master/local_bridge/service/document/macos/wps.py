# -*- coding: utf-8 -*-
"""
@File    : local_bridge/service/document/macos/wps.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:42
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from __future__ import annotations

import sys

from ..base import BaseDocumentPlacer
from ....core.types import PlacementResult
from ....utils.logging import log
from ....i18n import t
from ....utils.clipboard import set_clipboard_rich_text, simulate_paste
from ....utils.macos.clipboard import preserve_clipboard


class WPSPlacer(BaseDocumentPlacer):
                         

    def place(self, docx_bytes: bytes, config: dict, **kwargs) -> PlacementResult:
        






           
        if sys.platform != "darwin":
            return PlacementResult(
                success=False,
                method=None,
                error=t("placer.macos_wps.not_supported"),
            )

        try:

            plain_text = kwargs.get("_plain_text")
            html_text = kwargs.get("_html_text")

            with preserve_clipboard():
                set_clipboard_rich_text(
                    html=html_text, rtf_bytes=None, text=plain_text, docx_bytes=None
                )
                simulate_paste()

            return PlacementResult(success=True, method="clipboard_rtf_html")
        except Exception as e:
            log(f"macOS WPS RTF/HTML 粘贴失败: {e}")
            return PlacementResult(
                success=False,
                method="clipboard_rtf_html",
                error=str(e),
            )
