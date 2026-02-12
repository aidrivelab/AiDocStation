# -*- coding: utf-8 -*-
"""
@File    : local_bridge/config/loader.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import json
import os
import copy
from .defaults import DEFAULT_CONFIG
from .paths import get_config_path
from ..core.types import ConfigDict
from ..core.errors import ConfigError
from ..utils.logging import log


class ConfigLoader:
               

    def __init__(self):
        self.config_path = get_config_path()

    def load(self) -> ConfigDict:
                            

        config = copy.deepcopy(DEFAULT_CONFIG)
        user_config_raw = {}
        config_needs_save = False


        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    user_config_raw = json.load(f)
            except Exception as e:
                log(f"Load config error: {e}, utilizing default config.")
                config_needs_save = True

        else:

            config_needs_save = True



        if self._update_recursive(config, user_config_raw):
            config_needs_save = True



        if config_needs_save:
            log("Configuration updated/initialized, saving to disk...")
            self.save(config)




        if "save_dir" in config:
            config["save_dir"] = os.path.expandvars(config["save_dir"])

        return config

    def _update_recursive(self, target: dict, source: dict) -> bool:
        


           
        has_changes = False


        if "auto_open_on_no_app" in source and "no_app_action" not in source:
            old_value = source["auto_open_on_no_app"]

            target["no_app_action"] = "open" if old_value else "none"
            has_changes = True
            log(f"Migrated auto_open_on_no_app={old_value} to no_app_action='{target['no_app_action']}'")

        for key, value in source.items():
            if key in target:
                if isinstance(value, dict) and isinstance(target[key], dict):

                    if self._update_recursive(target[key], value):
                        has_changes = True
                else:


                    target[key] = value
            else:


                target[key] = value




        for key in target.keys():
            if key not in source:
                has_changes = True

        return has_changes

    def check_workflow_conflicts(self, config: ConfigDict) -> dict:
        



           
        ext_config = config.get("extensible_workflows", {})
        app_workflows = {}
        

        for workflow_key in ["html", "md", "latex", "file"]:
            workflow_config = ext_config.get(workflow_key, {})
            apps = workflow_config.get("apps", [])
            
            for app in apps:

                if isinstance(app, dict):
                    app_name = app.get("name", "")
                else:
                    app_name = str(app)
                
                if app_name:
                    if app_name not in app_workflows:
                        app_workflows[app_name] = []
                    app_workflows[app_name].append(workflow_key)
        

        conflicts = {app: workflows 
                    for app, workflows in app_workflows.items() 
                    if len(workflows) > 1}
        
        return conflicts

    def save(self, config: ConfigDict) -> None:
                    
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log(f"Save config error: {e}")
            raise ConfigError(f"Failed to save config: {e}")
