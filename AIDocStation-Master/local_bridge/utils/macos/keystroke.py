# -*- coding: utf-8 -*-
"""
@File    : local_bridge/utils/macos/keystroke.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from __future__ import annotations

import subprocess

from ...core.errors import ClipboardError


def simulate_paste(*, timeout_s: float = 5.0) -> None:
    



       
    script = 'tell application "System Events" to keystroke "v" using command down'
    try:
        subprocess.run(
            ["osascript", "-e", script],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_s,
        )
    except subprocess.CalledProcessError as e:
        msg = (e.stderr or "").strip() or (e.stdout or "").strip() or str(e)
        raise ClipboardError(f"Failed to simulate Cmd+V: {msg}") from e
    except subprocess.TimeoutExpired as e:
        raise ClipboardError("Failed to simulate Cmd+V: timeout") from e
