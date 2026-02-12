# -*- coding: utf-8 -*-
"""
@File    : main.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import os
import sys
import ctypes
import asyncio


if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


try:
    myappid = 'AIDoc Station'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass


if getattr(sys, 'frozen', False):

    basedir = sys._MEIPASS
else:

    basedir = os.path.dirname(os.path.abspath(__file__))

if basedir not in sys.path:
    sys.path.insert(0, basedir)

from local_bridge.app.app import run_app

if __name__ == "__main__":
    print("DEBUG: Entering main()...")

    run_app()
