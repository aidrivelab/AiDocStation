# -*- coding: utf-8 -*-
"""
@File    : local_bridge/api/routes/health.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from fastapi import APIRouter
from local_bridge.config.defaults import find_pandoc
import os
import subprocess

router = APIRouter()

@router.get("/health")
@router.get("/status")
async def health_check():
    


       
    pandoc_path = find_pandoc()
    pandoc_ok = False
    pandoc_version = "Not found"
    
    try:
        if pandoc_path:

            p_path = pandoc_path.replace("/", "\\") if os.name == "nt" else pandoc_path
            result = subprocess.run([p_path, "--version"], capture_output=True, text=True, check=False)
            if result.returncode == 0:
                pandoc_ok = True
                pandoc_version = result.stdout.splitlines()[0] if result.stdout else "Unknown version"
    except Exception:
        pass

    return {
        "status": "healthy",
        "app_name": "AIDOC",
        "service": "AIDOC Station Local Bridge",
        "version": "1.0.0",
        "pandoc": {
            "ok": pandoc_ok,
            "available": pandoc_ok,
            "path": pandoc_path,
            "version": pandoc_version
        }
    }
