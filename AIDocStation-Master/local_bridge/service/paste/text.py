# -*- coding: utf-8 -*-
"""
@File    : local_bridge/service/paste/text.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import time
from typing import Optional
from ...core.types import PlacementResult
from ...utils.clipboard import set_clipboard_text, simulate_paste, preserve_clipboard
from ...utils.logging import log
from .base import BasePastePlacer

class PlainTextPastePlacer(BasePastePlacer):
    


       

    def place(
        self,
        content: str,
        config: dict,
        **kwargs
    ) -> PlacementResult:
        








           
        try:
            paste_delay_s = config.get("paste_delay_s", 0.3)
            with preserve_clipboard():
                set_clipboard_text(content)
                time.sleep(paste_delay_s)
                simulate_paste()

            return PlacementResult(
                success=True,
                method="clipboard_plain_text",
            )
        except Exception as e:
            log(f"纯文本粘贴失�? {e}")
            return PlacementResult(
                success=False,
                method="clipboard_plain_text",
                error=str(e),
            )
