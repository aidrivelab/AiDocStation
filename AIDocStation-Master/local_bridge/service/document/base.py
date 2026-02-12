# -*- coding: utf-8 -*-
"""
@File    : local_bridge/service/document/base.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:42
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from abc import ABC, abstractmethod
from ...core.types import PlacementResult


class BaseDocumentPlacer(ABC):
                   
    
    @abstractmethod
    def place(self, docx_bytes: bytes, config: dict, **kwargs) -> PlacementResult:
        












           
        pass
