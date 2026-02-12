# -*- coding: utf-8 -*-
"""
@File    : local_bridge/core/errors.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

class AIDocStationError(Exception):
                  
    pass


class ConfigError(AIDocStationError):
                
    pass


class PandocError(AIDocStationError):
                     
    pass


class InsertError(AIDocStationError):
                
    pass


class ClipboardError(AIDocStationError):
                 
    pass
