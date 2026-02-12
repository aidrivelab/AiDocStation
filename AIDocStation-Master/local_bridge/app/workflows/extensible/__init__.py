# -*- coding: utf-8 -*-
"""
@File    : local_bridge/app/workflows/extensible/__init__.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from .extensible_base import ExtensibleWorkflow
from .html_md_workflow import HtmlWorkflow
from .md_workflow import MdWorkflow
from .latex_workflow import LatexWorkflow
from .file_workflow import FileWorkflow

__all__ = [
    "ExtensibleWorkflow",
    "HtmlWorkflow",
    "MdWorkflow",
    "LatexWorkflow",
    "FileWorkflow",
]
