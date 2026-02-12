# -*- coding: utf-8 -*-
"""
@File    : local_bridge/app/workflows/word/word_workflow.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from local_bridge.app.workflows.word.word_base import WordBaseWorkflow
from local_bridge.service.document import WordPlacer


class WordWorkflow(WordBaseWorkflow):
                    

    def __init__(self):
        super().__init__()
        self._placer = WordPlacer()

    @property
    def app_name(self) -> str:
        return "Word"

    @property
    def placer(self):
        return self._placer
