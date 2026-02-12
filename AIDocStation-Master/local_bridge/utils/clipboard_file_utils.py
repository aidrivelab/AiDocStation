# -*- coding: utf-8 -*-
"""
@File    : local_bridge/utils/clipboard_file_utils.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import os
from ..utils.logging import log
from ..core.errors import ClipboardError


def read_file_with_encoding(file_path: str) -> str:
    












       
    encodings = ["utf-8", "gbk", "gb2312", "utf-8-sig"]
    
    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                content = f.read()
                log(f"Successfully read file '{file_path}' with encoding: {encoding}")
                return content
        except UnicodeDecodeError:
            log(f"Failed to decode '{file_path}' with encoding: {encoding}")
            continue
        except Exception as e:
            log(f"Error reading file '{file_path}' with encoding {encoding}: {e}")
            continue
    

    raise ClipboardError(
        f"Failed to read file '{file_path}' with any supported encoding: {encodings}"
    )


def filter_markdown_files(file_paths: list[str]) -> list[str]:
    









       
    md_extensions = (".md", ".markdown")
    md_files = [
        f for f in file_paths
        if os.path.isfile(f) and f.lower().endswith(md_extensions)
    ]
    

    md_files.sort(key=lambda x: os.path.basename(x).lower())
    
    log(f"Found {len(md_files)} Markdown files from {len(file_paths)} total files")
    return md_files


def read_markdown_files(file_paths: list[str]) -> tuple[bool, list[tuple[str, str]], list[tuple[str, str]]]:
    












       
    if not file_paths:
        return False, [], []
    
    files_data: list[tuple[str, str]] = []
    errors: list[tuple[str, str]] = []
    
    for file_path in file_paths:
        filename = os.path.basename(file_path)
        try:
            content = read_file_with_encoding(file_path)
            files_data.append((filename, content))
            log(f"Successfully read MD file: {filename}")
        except Exception as e:

            error_msg = str(e)
            log(f"Failed to read MD file '{filename}': {error_msg}")
            errors.append((filename, error_msg))
    

    return len(files_data) > 0, files_data, errors
