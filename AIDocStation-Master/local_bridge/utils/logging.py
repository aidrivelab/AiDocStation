# -*- coding: utf-8 -*-
"""
@File    : local_bridge/utils/logging.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from ..config.paths import get_log_path

LOG_MAX_BYTES = 3 * 1024 * 1024
LOG_BACKUP_COUNT = 3

_logger: logging.Logger | None = None


def _get_logger() -> logging.Logger:
                                                      
    global _logger
    if _logger is not None:
        return _logger

    _logger = logging.getLogger("local_bridge")
    

    import sys
    is_frozen = getattr(sys, 'frozen', False)
    log_level = logging.INFO if is_frozen else logging.DEBUG
    _logger.setLevel(log_level)


    if _logger.handlers:
        return _logger

    try:
        log_path = get_log_path()

        os.makedirs(os.path.dirname(log_path), exist_ok=True)


        handler = RotatingFileHandler(
            log_path,
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
        handler.setLevel(logging.DEBUG)


        formatter = logging.Formatter(
            "[%(asctime)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        _logger.addHandler(handler)


        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)
        _logger.addHandler(stream_handler)


        if not is_frozen:
            try:

                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(os.path.dirname(current_dir))
                debug_log_dir = os.path.join(project_root, "log")
                os.makedirs(debug_log_dir, exist_ok=True)
                
                debug_log_path = os.path.join(debug_log_dir, "aidoc_debug.log")
                debug_handler = RotatingFileHandler(
                    debug_log_path,
                    maxBytes=LOG_MAX_BYTES,
                    backupCount=1,
                    encoding="utf-8",
                )
                debug_handler.setLevel(logging.DEBUG)
                debug_handler.setFormatter(formatter)
                _logger.addHandler(debug_handler)
            except Exception as e:

                print(f"Failed to setup debug log clone: {e}")
    except Exception:

        _logger.addHandler(logging.NullHandler())

    return _logger


def log(message: str) -> None:
                 
    try:
        _get_logger().info(message)
    except Exception:

        pass


def log_error(message: str) -> None:
                   
    try:
        _get_logger().error(message)
    except Exception:

        pass


def open_log_file() -> None:
                          
    try:
        import platform
        import subprocess
        log_path = get_log_path()
        

        if not os.path.exists(log_path):
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            open(log_path, 'a').close()
        

        if platform.system() == "Windows":
            os.startfile(log_path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", log_path])
        else:
            subprocess.run(["xdg-open", log_path])
    except Exception as e:
        log_error(f"打开日志文件失败: {str(e)}")


def clear_log_file() -> None:
                  
    try:
        log_path = get_log_path()
        if os.path.exists(log_path):
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write("")
            log("日志文件已清�?)
    except Exception as e:
        log_error(f"清空日志文件失败: {str(e)}")
