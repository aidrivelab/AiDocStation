# -*- coding: utf-8 -*-
"""
@File    : local_bridge/utils/win32/memfile.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""


import os, tempfile, time
import win32file, win32con

from local_bridge.core.constants import DEFAULT_DELETE_RETRY, DEFAULT_DELETE_WAIT


class EphemeralFile:
    


       
    def __init__(self, suffix=".docx", dir_=None):
        self.dir = dir_ or tempfile.gettempdir()
        os.makedirs(self.dir, exist_ok=True)
        fd, path = tempfile.mkstemp(suffix=suffix, dir=self.dir)
        os.close(fd)
        self.path = path
        self.handle = None

    def write_bytes(self, data: bytes):
        if isinstance(data, str):
            data = data.encode("utf-8")

        self.handle = win32file.CreateFile(
            self.path,
            win32con.GENERIC_WRITE | win32con.GENERIC_READ,
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
            None,
            win32con.CREATE_ALWAYS,
            win32con.FILE_ATTRIBUTE_TEMPORARY,
            None
        )
        win32file.WriteFile(self.handle, data)


        win32file.CloseHandle(self.handle)
        self.handle = None

    def cleanup(self):
        try:
            if self.handle:
                win32file.CloseHandle(self.handle)
                self.handle = None
        except Exception:
            pass

        for _ in range(DEFAULT_DELETE_RETRY):
            try:
                if os.path.exists(self.path):
                    os.remove(self.path)
                break
            except Exception:
                time.sleep(DEFAULT_DELETE_WAIT)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.cleanup()
