# -*- coding: utf-8 -*-
"""
@File    : local_bridge/service/document/__init__.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:42
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import sys


from .base import BaseDocumentPlacer
from .generator import DocumentGenerator


from ...core.types import PlacementResult, PlacementMethod


if sys.platform == "darwin":
    from .macos.word import WordPlacer
    from .macos.wps import WPSPlacer
elif sys.platform == "win32":
    from .win32.word import WordPlacer
    from .win32.wps import WPSPlacer
else:

    class WordPlacer(BaseDocumentPlacer):
        def place(self, *args, **kwargs):
            raise NotImplementedError(f"不支持的平台: {sys.platform}")
    
    class WPSPlacer(BaseDocumentPlacer):
        def place(self, *args, **kwargs):
            raise NotImplementedError(f"不支持的平台: {sys.platform}")

__all__ = [
    "BaseDocumentPlacer",
    "PlacementResult",
    "PlacementMethod",
    "WordPlacer",
    "WPSPlacer",
    "DocumentGenerator",
]
