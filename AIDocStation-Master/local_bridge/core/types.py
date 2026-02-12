# -*- coding: utf-8 -*-
"""
@File    : local_bridge/core/types.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from enum import Enum
from typing import Protocol, Any, Dict, Callable, Literal, Optional
from abc import abstractmethod


PlacementMethod = Literal["com", "applescript", "clipboard_bridge"]


class PlacementResult:
                
    
    def __init__(
        self, 
        success: bool, 
        method: Optional[PlacementMethod] = None,
        error: Optional[str] = None, 
        metadata: Optional[dict] = None
    ):
        self.success = success
        self.method = method
        self.error = error
        self.metadata = metadata or {}


class NoAppAction(str, Enum):
                     
    OPEN = "open"
    SAVE = "save"
    CLIPBOARD = "clipboard"
    NONE = "none"


ConfigDict = Dict[str, Any]
InsertTarget = Literal["auto", "word", "wps", "none"]


class Notifier(Protocol):
               
    
    @abstractmethod
    def notify(self, title: str, message: str, ok: bool = True) -> None:
                  
        pass


class Inserter(Protocol):
                 
    
    @abstractmethod
    def insert(self, docx_path: str) -> bool:
                       
        pass


class ConfigLoader(Protocol):
                 
    
    @abstractmethod
    def load(self) -> ConfigDict:
                  
        pass
    
    @abstractmethod
    def save(self, config: ConfigDict) -> None:
                  
        pass


HotkeyCallback = Callable[[], None]
