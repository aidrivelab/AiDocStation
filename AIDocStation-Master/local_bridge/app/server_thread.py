# -*- coding: utf-8 -*-
"""
@File    : local_bridge/app/server_thread.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import uvicorn
from PySide6.QtCore import QThread, Signal
from local_bridge.api.main import app
from local_bridge.utils.logging import log

class ServerThread(QThread):
    def __init__(self, host="127.0.0.1", port=4286):
        super().__init__()
        self.host = host
        self.port = port
        self.server = None

    def run(self):
        log(f"Starting API Server on {self.host}:{self.port}...")
        try:
            config = uvicorn.Config(app=app, host=self.host, port=self.port, log_level="info", log_config=None)
            self.server = uvicorn.Server(config)
            self.server.run()
        except Exception as e:
            log(f"Server crashed: {e}")

    def stop(self):
        if self.server:
            self.server.should_exit = True
            self.wait()
