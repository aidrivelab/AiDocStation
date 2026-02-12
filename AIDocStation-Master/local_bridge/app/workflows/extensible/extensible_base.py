# -*- coding: utf-8 -*-
"""
@File    : local_bridge/app/workflows/extensible/extensible_base.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from abc import abstractmethod
from ..base import BaseWorkflow
from ....core.state import app_state


class ExtensibleWorkflow(BaseWorkflow):
    



       
    
    @property
    @abstractmethod
    def workflow_key(self) -> str:
                                   
        ...
    
    @property
    def workflow_config(self) -> dict:
                       
        ext_config = self.config.get("extensible_workflows", {})
        return ext_config.get(self.workflow_key, {})
    
    @property
    def enabled(self) -> bool:
                        
        return self.workflow_config.get("enabled", False)
    
    @property
    def enabled_apps(self) -> list[str]:
                             
        apps = self.workflow_config.get("apps", [])

        return [app["name"] for app in apps if isinstance(app, dict)]
