# -*- coding: utf-8 -*-
"""
@File    : local_bridge/app/workflows/base.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from abc import ABC, abstractmethod
from ...core.state import app_state
from ...service.notification.manager import NotificationManager
from ...service.document import DocumentGenerator
from ...service.spreadsheet import SpreadsheetGenerator
from ...service.preprocessor import HtmlPreprocessor, MarkdownPreprocessor
from ...utils.logging import log


class BaseWorkflow(ABC):
               
    
    def __init__(self):

        self.notification_manager = NotificationManager()
        

        self._doc_generator = None
        self._sheet_generator = None
        

        self._markdown_preprocessor = MarkdownPreprocessor()
        self._html_preprocessor = HtmlPreprocessor()
    
    @property
    def config(self):
                      
        return app_state.config
    
    @property
    def doc_generator(self):
                                   
        if self._doc_generator is None:
            self._doc_generator = DocumentGenerator()
        return self._doc_generator
    
    @property
    def sheet_generator(self):
                                      
        if self._sheet_generator is None:
            self._sheet_generator = SpreadsheetGenerator()
        return self._sheet_generator
    
    @property
    def markdown_preprocessor(self):
                                         
        return self._markdown_preprocessor
    
    @property
    def html_preprocessor(self):
                                     
        return self._html_preprocessor
    
    @abstractmethod
    def execute(self) -> None:
                         
        pass
    

    def _notify_success(self, msg: str):
                  
        self.notification_manager.notify("AIDocStation", msg, ok=True)
    
    def _notify_error(self, msg: str):
                  
        self.notification_manager.notify("AIDocStation", msg, ok=False)
    
    def _notify_info(self, msg: str):
                         
        self.notification_manager.notify("AIDocStation", msg, ok=True)
    
    def _log(self, msg: str):
                  
        log(msg)
