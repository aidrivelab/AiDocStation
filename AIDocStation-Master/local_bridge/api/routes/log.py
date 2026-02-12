# -*- coding: utf-8 -*-
"""
@File    : local_bridge/api/routes/log.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from fastapi import APIRouter, HTTPException, Query
from local_bridge.config.paths import get_log_path
import os

router = APIRouter()

@router.get("/log/status")
async def get_log_status():
    


       
    log_file = get_log_path()
    size = 0
    if os.path.exists(log_file):
        size = os.path.getsize(log_file)
    
    return {
        "currentSize": size,
        "maxSize": 10 * 1024 * 1024,
        "maxBackups": 5,
        "logFile": log_file
    }

@router.get("/log")
@router.get("/logs")
async def get_logs(lines: int = Query(100, ge=1)):
    

       
    log_file = get_log_path()
    if not os.path.exists(log_file):
        return {"status": "success", "logs": "No log file found yet."}

    try:
        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
            all_lines = f.readlines()
            last_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            return {
                "status": "success",
                "logs": "".join(last_lines)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading logs: {str(e)}")

@router.delete("/log")
async def clear_logs():
    


       
    log_file = get_log_path()
    try:
        if os.path.exists(log_file):
            with open(log_file, "w", encoding="utf-8") as f:
                f.truncate(0)
        return {"status": "success", "message": "Logs cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing logs: {str(e)}")
