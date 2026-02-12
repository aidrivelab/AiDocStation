# -*- coding: utf-8 -*-
"""
@File    : local_bridge/api/main.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from local_bridge.api.routes.generate import router as generate_router
from local_bridge.api.routes.health import router as health_router
from local_bridge.api.routes.config import router as config_router
from local_bridge.api.routes.log import router as log_router
from local_bridge.api.routes.auth import router as auth_router

app = FastAPI(
    title="AIDOC Station API",
    description="Backend API for AIDOC Station Local Bridge",
    version="1.0.0"
)



origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health_router, tags=["Health"])
app.include_router(config_router, tags=["Config"])
app.include_router(log_router, tags=["Log"])
app.include_router(auth_router, tags=["Auth"])
app.include_router(generate_router, tags=["Generate"])

@app.get("/")
async def root():
    return {"message": "AIDOC Station Local Bridge Service is Running"}
