# -*- coding: utf-8 -*-
"""
@File    : local_bridge/app/workflows/excel/excel_workflow.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from local_bridge.app.workflows.excel.excel_base import ExcelBaseWorkflow
from local_bridge.service.spreadsheet import ExcelPlacer


class ExcelWorkflow(ExcelBaseWorkflow):
                     

    def __init__(self):
        super().__init__()
        self._placer = ExcelPlacer()

    @property
    def app_name(self) -> str:
        return "Excel"

    @property
    def placer(self):
        return self._placer
