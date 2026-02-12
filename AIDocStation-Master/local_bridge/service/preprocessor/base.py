# -*- coding: utf-8 -*-
"""
@File    : local_bridge/service/preprocessor/base.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from abc import ABC, abstractmethod


class BasePreprocessor(ABC):
                       

    @abstractmethod
    def process(self, content: any, config: dict) -> any:
        








           
        pass
