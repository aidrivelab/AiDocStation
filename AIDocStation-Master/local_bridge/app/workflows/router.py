# -*- coding: utf-8 -*-
"""
@File    : local_bridge/app/workflows/router.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import re
from ...core.state import app_state
from ...utils.detector import detect_active_app, get_frontmost_window_title
from ...utils.logging import log
from ...service.notification.manager import NotificationManager
from ...i18n import t

from .word import WordWorkflow, WPSWorkflow
from .excel import ExcelWorkflow, WPSExcelWorkflow
from .fallback import FallbackWorkflow
from .extensible import HtmlWorkflow, MdWorkflow, LatexWorkflow, FileWorkflow


class WorkflowRouter:
                    
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance
    
    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        

        self.core_workflows = {
            "word": WordWorkflow(),
            "wps": WPSWorkflow(),
            "excel": ExcelWorkflow(),
            "wps_excel": WPSExcelWorkflow(),
            "": FallbackWorkflow(),
        }
        

        self.extensible_registry = {
            "html": HtmlWorkflow(),
            "md": MdWorkflow(),
            "latex": LatexWorkflow(),
            "file": FileWorkflow(),
        }
        
        self.notification_manager = NotificationManager()
        self._initialized = True
        log("WorkflowRouter initialized")
    
    def _build_dynamic_routes(self, window_title: str = "") -> dict:
        



           
        routes = dict(self.core_workflows)
        
        ext_config = app_state.config.get("extensible_workflows", {})
        for key, workflow in self.extensible_registry.items():
            cfg = ext_config.get(key, {})
            if cfg.get("enabled", False):

                for app in cfg.get("apps", []):
                    app_name = app.get("name") if isinstance(app, dict) else app
                    app_id = app.get("id", "") if isinstance(app, dict) else ""
                    if isinstance(app_id, str):
                        app_id = app_id.lower()
                    window_patterns = app.get("window_patterns", []) if isinstance(app, dict) else []
                    
                    app_key = app_id

                    if not app_key:
                        continue
                    

                    if window_patterns and window_title:
                        if self._match_window_patterns(window_title, window_patterns):
                            routes[app_key] = workflow
                            log(f"Registered extensible route (window matched): {app_key} -> {key}")

                    elif not window_patterns:

                        if app_key not in routes:
                            routes[app_key] = workflow
                            log(f"Registered extensible route: {app_key} -> {key}")
        
        return routes
    
    def _match_window_patterns(self, window_title: str, patterns: list) -> bool:
        







           
        for pattern in patterns:
            if not pattern:
                continue
            try:
                if re.search(pattern, window_title, re.IGNORECASE):
                    log(f"Window title '{window_title}' matched pattern '{pattern}'")
                    return True
            except re.error as e:
                log(f"Invalid regex pattern '{pattern}': {e}")
        return False
    
    def route(self) -> None:
                               
        try:

            target_app = detect_active_app()
            log(f"Detected target app: {target_app}")
            

            window_title = get_frontmost_window_title()
            log(f"Window title: {window_title}")
            

            routes = self._build_dynamic_routes(window_title)
            workflow = routes.get(target_app, routes[""])
            workflow.execute()
        
        except Exception as e:
            log(f"Router failed: {e}")
            import traceback
            traceback.print_exc()
            self.notification_manager.notify("AIDocStation", t("workflow.generic.failure"), ok=False)



router = WorkflowRouter()


def execute_paste_workflow():
                

    import time
    time.sleep(0.2)
    router.route()
