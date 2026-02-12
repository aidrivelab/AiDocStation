# -*- coding: utf-8 -*-
"""
@File    : local_bridge/utils/macos/clipboard.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from __future__ import annotations

import contextlib
import time

import pyperclip
from AppKit import (
    NSPasteboard,
    NSPasteboardTypeHTML,
    NSPasteboardTypeRTF,
    NSPasteboardItem,
    NSPasteboardTypeString,
    NSFilenamesPboardType,
    NSURL,
)
from Foundation import NSData
from ...core.errors import ClipboardError
from ...core.state import app_state
from ..clipboard_file_utils import read_file_with_encoding, filter_markdown_files, read_markdown_files
from ..logging import log

DOCX_UTIS = [
    "org.openxmlformats-officedocument.wordprocessingml.document",
    "org.openxmlformats.wordprocessingml.document",
    "com.microsoft.word.docx",
]

RTF_UTI = "public.rtf"
HTML_UTI = "public.html"
PLAIN_UTI = "public.utf8-plain-text"


def _nsdata_to_bytes(data: NSData | None) -> bytes | None:
    if data is None:
        return None
    try:
        return bytes(data)
    except Exception:
        try:
            return data.bytes()
        except Exception:
            return None


def _snapshot_pasteboard() -> list[dict[str, bytes]]:
    





       
    pasteboard = NSPasteboard.generalPasteboard()
    items = pasteboard.pasteboardItems() or []

    snapshot: list[dict[str, bytes]] = []
    for item in items:
        types = item.types() or []
        item_data: dict[str, bytes] = {}
        for t in types:
            try:
                t_str = str(t)
                data = _nsdata_to_bytes(item.dataForType_(t))
                if data is not None:
                    item_data[t_str] = data
                    continue

                s = item.stringForType_(t)
                if s is not None:
                    item_data[t_str] = str(s).encode("utf-8")
            except Exception:
                continue
        snapshot.append(item_data)

    return snapshot


def _restore_pasteboard(snapshot: list[dict[str, bytes]]) -> None:
    pasteboard = NSPasteboard.generalPasteboard()
    pasteboard.clearContents()

    items: list[NSPasteboardItem] = []
    for item_data in snapshot:
        item = NSPasteboardItem.alloc().init()
        for t_str, raw in item_data.items():
            try:
                data = NSData.dataWithBytes_length_(raw, len(raw))
                item.setData_forType_(data, t_str)
            except Exception:
                continue
        items.append(item)

    if items:
        pasteboard.writeObjects_(items)


@contextlib.contextmanager
def preserve_clipboard(*, restore_delay_s: float = 0.25):
    



       
    snapshot: list[dict[str, bytes]] | None = None
    try:
        snapshot = _snapshot_pasteboard()
        yield
    finally:
        if restore_delay_s > 0:
            time.sleep(restore_delay_s)
        if snapshot is not None:
            try:
                _restore_pasteboard(snapshot)
            except Exception as exc:
                log(f"Failed to restore clipboard: {exc}")


def get_clipboard_text() -> str:
    







       
    try:
        text = pyperclip.paste()
        if text is None:
            return ""
        return text
    except Exception as e:
        raise ClipboardError(f"Failed to read clipboard: {e}")


def set_clipboard_text(text: str) -> None:
    







       
    try:
        pyperclip.copy(text)
    except Exception as e:
        raise ClipboardError(f"Failed to set clipboard text: {e}")


def is_clipboard_empty() -> bool:
    




       
    try:
        text = get_clipboard_text()
        return not text or not text.strip()
    except ClipboardError:
        return True


def is_clipboard_html() -> bool:
    




       
    try:
        pasteboard = NSPasteboard.generalPasteboard()

        types = pasteboard.types()
        if types is None:
            return False
        

        return NSPasteboardTypeHTML in types
    except Exception:
        return False


def get_clipboard_html(config: dict | None = None) -> str:
    







       
    try:
        config = config or getattr(app_state, "config", {})

        pasteboard = NSPasteboard.generalPasteboard()


        html_data = pasteboard.stringForType_(NSPasteboardTypeHTML)

        if html_data is None:
            raise ClipboardError("No HTML format data in clipboard")


        html_content = str(html_data)


        return html_content

    except Exception as e:
        raise ClipboardError(f"Failed to read HTML from clipboard: {e}")


def set_clipboard_rich_text(
    *,
    html: str | None = None,
    rtf_bytes: bytes | None = None,
    docx_bytes: bytes | None = None,
    text: str | None = None,
) -> None:
    




       
    try:
        pasteboard = NSPasteboard.generalPasteboard()
        pasteboard.clearContents()

        item = NSPasteboardItem.alloc().init()


        if docx_bytes is not None:
            docx_data = NSData.dataWithBytes_length_(docx_bytes, len(docx_bytes))
            for uti in DOCX_UTIS:
                item.setData_forType_(docx_data, uti)
                log(f"set DOCX type={uti} len={len(docx_bytes)}")


        if rtf_bytes is not None:
            rtf_data = NSData.dataWithBytes_length_(rtf_bytes, len(rtf_bytes))
            item.setData_forType_(rtf_data, NSPasteboardTypeRTF)
            log(f"set RTF type={NSPasteboardTypeRTF} len={len(rtf_bytes)}")
            

        if html is not None:
            html_data = NSData.dataWithBytes_length_(html.encode("utf-8"), len(html.encode("utf-8")))
            item.setData_forType_(html_data, NSPasteboardTypeHTML)
            item.setString_forType_(html, HTML_UTI)
            log(f"set HTML type={NSPasteboardTypeHTML},{HTML_UTI} len={len(html.encode('utf-8'))}")


        if text is not None:
            item.setString_forType_(text, PLAIN_UTI)
            item.setString_forType_(text, NSPasteboardTypeString)
            log(f"set PLAIN type={PLAIN_UTI},NSPasteboardTypeString len={len(text.encode('utf-8'))}")
        
        wrote = pasteboard.writeObjects_([item])
        if not wrote:
            raise ClipboardError("Failed to write rich text to clipboard")
    except Exception as e:
        raise ClipboardError(f"Failed to write rich text to clipboard: {e}")






def copy_files_to_clipboard(file_paths: list) -> None:
    







       
    try:
        import os

        absolute_paths = [os.path.abspath(path) for path in file_paths if os.path.exists(path)]
        
        if not absolute_paths:
            raise ClipboardError("No valid files to copy to clipboard")
        
        pasteboard = NSPasteboard.generalPasteboard()
        pasteboard.clearContents()
        

        success = pasteboard.setPropertyList_forType_(absolute_paths, NSFilenamesPboardType)
        
        if not success:
            raise ClipboardError("Failed to set file paths to clipboard")
        
        log(f"Successfully copied {len(absolute_paths)} files to clipboard")
        
    except Exception as e:
        raise ClipboardError(f"Failed to copy files to clipboard: {e}")


def is_clipboard_files() -> bool:
    




       
    try:
        pasteboard = NSPasteboard.generalPasteboard()
        types = pasteboard.types()
        if types is None:
            return False
        

        result = NSFilenamesPboardType in types
        log(f"Clipboard files check: {result}")
        return result
    except Exception as e:
        log(f"Failed to check clipboard files: {e}")
        return False


def get_clipboard_files() -> list[str]:
    




       
    file_paths = []
    try:
        pasteboard = NSPasteboard.generalPasteboard()
        

        files = pasteboard.propertyListForType_(NSFilenamesPboardType)
        
        if files:
            file_paths = list(files)
            log(f"Got {len(file_paths)} files from clipboard")
        
    except Exception as e:
        log(f"Failed to get clipboard files: {e}")
    
    return file_paths


def get_markdown_files_from_clipboard() -> list[str]:
    






       
    all_files = get_clipboard_files()
    return filter_markdown_files(all_files)


def read_markdown_files_from_clipboard() -> tuple[bool, list[tuple[str, str]], list[tuple[str, str]]]:
    










       
    md_files = get_markdown_files_from_clipboard()
    return read_markdown_files(md_files)
