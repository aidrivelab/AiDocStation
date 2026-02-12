# -*- coding: utf-8 -*-
"""
@File    : local_bridge/service/paste/file.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import time
from typing import Optional

from ...core.types import PlacementResult
from ...utils.clipboard import copy_files_to_clipboard, simulate_paste, preserve_clipboard
from ...utils.logging import log
from .base import BasePastePlacer


class FilePastePlacer(BasePastePlacer):
    


       

    def place(
        self,
        content: str,
        config: dict,
        file_paths: Optional[list[str]] = None,
        **kwargs
    ) -> PlacementResult:
        









           
        paths = list(file_paths or [])
        if not paths and content:
            paths = [content]

        if not paths:
            return PlacementResult(
                success=False,
                method="clipboard_file",
                error="no_file_paths",
            )

        try:
            paste_delay_s = config.get("paste_delay_s", 0.3)
            with preserve_clipboard():
                copy_files_to_clipboard(paths)
                time.sleep(paste_delay_s)
                simulate_paste()

            return PlacementResult(
                success=True,
                method="clipboard_file",
                metadata={"count": len(paths)},
            )
        except Exception as e:
            log(f"文件粘贴失败: {e}")
            return PlacementResult(
                success=False,
                method="clipboard_file",
                error=str(e),
            )
