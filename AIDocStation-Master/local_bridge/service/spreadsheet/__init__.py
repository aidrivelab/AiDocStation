# -*- coding: utf-8 -*-
"""
@File    : local_bridge/service/spreadsheet/__init__.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import sys


from .base import BaseSpreadsheetPlacer
from .generator import SpreadsheetGenerator


from ...core.types import PlacementResult


if sys.platform == "darwin":
    from .macos.excel import ExcelPlacer
    from .macos.wps_excel import WPSExcelPlacer
elif sys.platform == "win32":
    from .win32.excel import ExcelPlacer
    from .win32.wps_excel import WPSExcelPlacer
else:

    class ExcelPlacer(BaseSpreadsheetPlacer):
        def place(self, *args, **kwargs):
            raise NotImplementedError(f"不支持的平台: {sys.platform}")
    
    class WPSExcelPlacer(BaseSpreadsheetPlacer):
        def place(self, *args, **kwargs):
            raise NotImplementedError(f"不支持的平台: {sys.platform}")

__all__ = [
    "BaseSpreadsheetPlacer",
    "PlacementResult",
    "ExcelPlacer",
    "WPSExcelPlacer",
    "SpreadsheetGenerator",
]
