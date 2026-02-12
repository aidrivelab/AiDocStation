# -*- coding: utf-8 -*-
"""
@File    : local_bridge/api/routes/config.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from local_bridge.core.state import app_state
from local_bridge.config.loader import ConfigLoader
from local_bridge.utils.logging import log

router = APIRouter()

class UpdateConfigRequest(BaseModel):
    config: Dict[str, Any]

@router.get("/config")
async def get_config():
                                                
    return {
        "status": "success",
        "config": app_state.config
    }

@router.post("/config")
async def update_config(request: UpdateConfigRequest):
                                                    
    try:
        new_config = request.config
        

        app_state.config.update(new_config)
        

        loader = ConfigLoader()
        loader.save(app_state.config)
        
        log(f"Config updated via API: {new_config.keys()}")
        



        
        return {
            "status": "success",
            "message": "Configuration updated and saved successfully"
        }
    except Exception as e:
        log(f"Error updating config via API: {e}")
        raise HTTPException(status_code=500, detail=str(e))
