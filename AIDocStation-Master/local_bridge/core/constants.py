# -*- coding: utf-8 -*-
"""
@File    : local_bridge/core/constants.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from local_bridge.version import __version__ as APP_VERSION


FIRE_DEBOUNCE_SEC = 0.5


WORD_INSERT_RETRY_COUNT = 3
WORD_INSERT_RETRY_DELAY = 0.3


NOTIFICATION_TIMEOUT = 3


CLEANUP_DELAY = 1.0


DEFAULT_DELETE_RETRY = 3
DEFAULT_DELETE_WAIT  = 0.05


CLIPBOARD_HTML_WAIT_MS = 500
CLIPBOARD_POLL_INTERVAL_MS = 20
