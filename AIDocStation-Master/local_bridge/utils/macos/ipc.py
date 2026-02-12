# -*- coding: utf-8 -*-
"""
@File    : local_bridge/utils/macos/ipc.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from __future__ import annotations

import os
import socket
import sys
import tempfile
import threading
from typing import Callable, Optional

from ..logging import log
from ...core.state import app_state


def _socket_path(app_name: str = "AIDocStation") -> str:
    return os.path.join(tempfile.gettempdir(), f"{app_name}.sock")


def send_command(command: str, *, app_name: str = "AIDocStation") -> bool:
                                                          
    if sys.platform != "darwin":
        return False

    path = _socket_path(app_name)
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(0.5)
            client.connect(path)
            client.sendall((command.strip() + "\n").encode("utf-8"))
        return True
    except Exception as exc:
        log(f"IPC send failed: {exc}")
        return False


def start_server(
    on_command: Callable[[str], None],
    *,
    app_name: str = "AIDocStation",
) -> Optional[socket.socket]:
                                                     
    if sys.platform != "darwin":
        return None

    path = _socket_path(app_name)
    try:
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass

        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(path)
        server.listen(5)
        server.settimeout(0.5)

        def _loop() -> None:
            while True:
                quit_event = getattr(app_state, "quit_event", None)
                if quit_event is not None and quit_event.is_set():
                    break

                try:
                    conn, _ = server.accept()
                except socket.timeout:
                    continue
                except OSError:
                    break

                try:
                    with conn:
                        data = conn.recv(4096)
                        cmd = data.decode("utf-8", errors="ignore").strip()
                        if cmd:
                            on_command(cmd)
                except Exception as exc:
                    log(f"IPC handler error: {exc}")

            try:
                server.close()
            finally:
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except Exception:
                    pass

        threading.Thread(target=_loop, daemon=True).start()
        return server
    except Exception as exc:
        log(f"IPC server start failed: {exc}")
        return None
