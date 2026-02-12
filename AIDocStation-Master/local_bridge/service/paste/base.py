# -*- coding: utf-8 -*-
"""
@File    : local_bridge/service/paste/base.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from abc import ABC, abstractmethod
from ...core.types import PlacementResult


class BasePastePlacer(ABC):
    



       

    @abstractmethod
    def place(self, content: str, config: dict, **kwargs) -> PlacementResult:
        









           
        pass
