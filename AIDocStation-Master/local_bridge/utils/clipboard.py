# -*- coding: utf-8 -*-
"""
@File    : local_bridge/utils/clipboard.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import sys
from ..core.errors import ClipboardError



if sys.platform == "darwin":
    from .macos.clipboard import (
        get_clipboard_text,
        set_clipboard_text,
        is_clipboard_empty,
        is_clipboard_html,
        get_clipboard_html,
        set_clipboard_rich_text,
        copy_files_to_clipboard,
        is_clipboard_files,
        get_clipboard_files,
        get_markdown_files_from_clipboard,
        read_markdown_files_from_clipboard,
        preserve_clipboard,
    )
    from .macos.keystroke import simulate_paste

    from .clipboard_file_utils import read_file_with_encoding
elif sys.platform == "win32":
    from .win32.clipboard import (
        get_clipboard_text,
        set_clipboard_text,
        is_clipboard_empty,
        is_clipboard_html,
        get_clipboard_html,
        set_clipboard_rich_text,
        copy_files_to_clipboard,
        is_clipboard_files,
        get_clipboard_files,
        get_markdown_files_from_clipboard,
        read_markdown_files_from_clipboard,
        preserve_clipboard,
    )
    from .win32.keystroke import simulate_paste

    from .clipboard_file_utils import read_file_with_encoding
else:

    import pyperclip

    def get_clipboard_text() -> str:
        







           
        try:
            text = pyperclip.paste()
            if text is None:
                return ""
            return text
        except Exception as e:
            raise ClipboardError(f"Failed to read clipboard: {e}")

    def is_clipboard_empty() -> bool:
        




           
        try:
            text = get_clipboard_text()
            return not text or not text.strip()
        except ClipboardError:
            return True

    def is_clipboard_html() -> bool:
        







           
        return False

    def get_clipboard_html(config: dict | None = None) -> str:
        







           
        raise ClipboardError(f"HTML clipboard operations not supported on {sys.platform}")

    def set_clipboard_rich_text(
        *,
        html: str | None = None,
        rtf_bytes: bytes | None = None,
        docx_bytes: bytes | None = None,
        text: str | None = None,
    ) -> None:
        raise ClipboardError(
            f"Rich-text clipboard operations not supported on {sys.platform}"
        )

    def simulate_paste(*, timeout_s: float = 5.0) -> None:
        raise ClipboardError(f"Paste keystroke not supported on {sys.platform}")



__all__ = [
    "get_clipboard_text",
    "set_clipboard_text",
    "is_clipboard_empty",
    "is_clipboard_html",
    "get_clipboard_html",
    "ClipboardError",
]


if sys.platform in ("win32", "darwin"):
    __all__.extend([
        "set_clipboard_rich_text",
        "simulate_paste",
        "copy_files_to_clipboard",
        "is_clipboard_files",
        "get_clipboard_files",
        "get_markdown_files_from_clipboard",
        "read_markdown_files_from_clipboard",
        "read_file_with_encoding",
        "preserve_clipboard",
    ])
