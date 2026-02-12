# -*- coding: utf-8 -*-
"""
@File    : local_bridge/utils/win32/clipboard.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import os
import re
import sys
import time
import contextlib
import pyperclip
import ctypes
from ctypes import wintypes
import win32clipboard as wc
from ...core.errors import ClipboardError
from ...core.state import app_state
from ..clipboard_file_utils import read_file_with_encoding, filter_markdown_files, read_markdown_files
from ...utils.logging import log
from ...core.constants import CLIPBOARD_HTML_WAIT_MS, CLIPBOARD_POLL_INTERVAL_MS


def _snapshot_clipboard() -> dict[int, bytes]:
    



       
    snapshot: dict[int, bytes] = {}
    try:
        wc.OpenClipboard(None)
        try:

            fmt = 0
            while True:
                fmt = wc.EnumClipboardFormats(fmt)
                if fmt == 0:
                    break
                try:
                    data = wc.GetClipboardData(fmt)
                    if data is not None:

                        if isinstance(data, bytes):
                            snapshot[fmt] = data
                        elif isinstance(data, str):
                            snapshot[fmt] = data.encode('utf-16le')
                        elif isinstance(data, (list, tuple)):

                            snapshot[fmt] = "\0".join(data).encode('utf-16le') + b'\0\0'
                        else:

                            try:
                                snapshot[fmt] = bytes(data)
                            except Exception:
                                pass
                except Exception as e:
                    log(f"Failed to snapshot clipboard format {fmt}: {e}")
                    continue
        finally:
            wc.CloseClipboard()
    except Exception as e:
        log(f"Failed to snapshot clipboard: {e}")
    
    return snapshot


def _restore_clipboard(snapshot: dict[int, bytes]) -> None:
    

       
    try:
        wc.OpenClipboard(None)
        try:
            wc.EmptyClipboard()
            
            for fmt, data in snapshot.items():
                try:

                    if fmt == wc.CF_UNICODETEXT:

                        text = data.decode('utf-16le', errors='ignore').rstrip('\0')
                        wc.SetClipboardData(fmt, text)
                    elif fmt == wc.CF_TEXT:

                        text = data.decode('cp1252', errors='ignore').rstrip('\0')
                        wc.SetClipboardData(fmt, text)
                    elif fmt == wc.CF_HDROP:

                        files_str = data.decode('utf-16le', errors='ignore').rstrip('\0')
                        files = [f for f in files_str.split('\0') if f]
                        if files:
                            hdrop_data = _build_hdrop_data(files)
                            wc.SetClipboardData(fmt, hdrop_data)
                    else:

                        wc.SetClipboardData(fmt, data)
                except Exception as e:
                    log(f"Failed to restore clipboard format {fmt}: {e}")
                    continue
        finally:
            wc.CloseClipboard()
    except Exception as e:
        log(f"Failed to restore clipboard: {e}")


@contextlib.contextmanager
def preserve_clipboard(*, restore_delay_s: float = 0.25):
    



       
    snapshot: dict[int, bytes] | None = None
    try:
        snapshot = _snapshot_clipboard()
        yield
    finally:
        if restore_delay_s > 0:
            time.sleep(restore_delay_s)
        if snapshot is not None:
            try:
                _restore_clipboard(snapshot)
            except Exception as exc:
                log(f"Failed to restore clipboard: {exc}")


def _build_cf_html(html: str) -> bytes:
    




       
    start_marker = "<!--StartFragment-->"
    end_marker = "<!--EndFragment-->"

    if start_marker in html and end_marker in html:
        html_doc = html
    else:
        html_doc = (
            "<html><head><meta charset=\"utf-8\"></head><body>"
            f"{start_marker}{html}{end_marker}"
            "</body></html>"
        )

    html_bytes = html_doc.encode("utf-8")

    header_template = (
        "Version:1.0\r\n"
        "StartHTML:{:010d}\r\n"
        "EndHTML:{:010d}\r\n"
        "StartFragment:{:010d}\r\n"
        "EndFragment:{:010d}\r\n"
    )


    header_placeholder = header_template.format(0, 0, 0, 0).encode("ascii")
    start_html = len(header_placeholder)
    end_html = start_html + len(html_bytes)

    start_marker_b = start_marker.encode("ascii")
    end_marker_b = end_marker.encode("ascii")
    sf_index = html_bytes.find(start_marker_b)
    ef_index = html_bytes.find(end_marker_b)
    if sf_index == -1 or ef_index == -1 or ef_index < sf_index:
        start_fragment = start_html
        end_fragment = end_html
    else:
        start_fragment = start_html + sf_index + len(start_marker_b)
        end_fragment = start_html + ef_index

    header = header_template.format(start_html, end_html, start_fragment, end_fragment).encode(
        "ascii"
    )
    return header + html_bytes


def set_clipboard_rich_text(
    *,
    html: str | None = None,
    rtf_bytes: bytes | None = None,
    docx_bytes: bytes | None = None,
    text: str | None = None,
) -> None:
    





       
    try:
        fmt_html = wc.RegisterClipboardFormat("HTML Format")
        fmt_rtf = wc.RegisterClipboardFormat("Rich Text Format")

        wc.OpenClipboard(None)
        try:
            wc.EmptyClipboard()

            if html is not None:
                wc.SetClipboardData(fmt_html, _build_cf_html(html))
                log(f"set HTML type=HTML Format len={len(html.encode('utf-8'))}")

            if rtf_bytes is not None:
                wc.SetClipboardData(fmt_rtf, rtf_bytes)
                log(f"set RTF type=Rich Text Format len={len(rtf_bytes)}")

            if text is not None:
                wc.SetClipboardData(wc.CF_UNICODETEXT, text)
                log(f"set PLAIN type=CF_UNICODETEXT len={len(text)}")

            if docx_bytes is not None:
                log(f"docx_bytes provided (len={len(docx_bytes)}), ignored on Windows clipboard")
        finally:
            wc.CloseClipboard()
    except Exception as e:
        raise ClipboardError(f"Failed to write rich text to clipboard: {e}") from e


def _try_read_cf_html(wait_ms: int, interval_ms: int) -> bytes | str | None:
    








       
    try:
        fmt = wc.RegisterClipboardFormat("HTML Format")
    except Exception:
        return None

    deadline = time.monotonic() + (wait_ms / 1000.0)
    interval_s = max(1, interval_ms) / 1000.0

    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            wc.OpenClipboard(None)
        except Exception as exc:
            last_error = exc
            time.sleep(interval_s)
            continue

        try:
            try:
                available: bool | None = bool(wc.IsClipboardFormatAvailable(fmt))
            except Exception as exc:
                last_error = exc
                available = None

            if available is False:
                return None

            if available:
                try:
                    data = wc.GetClipboardData(fmt)
                    if data is None:
                        last_error = ValueError("CF_HTML data is None")
                    else:
                        return data
                except Exception as exc:
                    last_error = exc
        finally:
            try:
                wc.CloseClipboard()
            except Exception:
                pass

        time.sleep(interval_s)

    if last_error is not None:
        log(f"CF_HTML read timed out after {wait_ms}ms: {last_error}")
    return None


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
        if is_clipboard_files():
            return False
        text = get_clipboard_text()
        return not text or not text.strip()
    except ClipboardError:
        return True


def is_clipboard_html() -> bool:
    




       
    data = _try_read_cf_html(CLIPBOARD_HTML_WAIT_MS, CLIPBOARD_POLL_INTERVAL_MS)
    return data is not None and data != "" and data != b""


def get_clipboard_html(config: dict | None = None) -> str:
    










       
    config = config or getattr(app_state, "config", {})

    data = _try_read_cf_html(CLIPBOARD_HTML_WAIT_MS, CLIPBOARD_POLL_INTERVAL_MS)
    if data is None or data == "" or data == b"":
        raise ClipboardError("No HTML format data in clipboard")

    try:

        if isinstance(data, bytes):
            fragment = _extract_html_fragment_bytes(data)
        else:
            fragment = _extract_html_fragment(data)


        return fragment
    except Exception as e:
        raise ClipboardError(f"Failed to read HTML from clipboard: {e}") from e


def _extract_html_fragment_bytes(cf_html_bytes: bytes) -> str:
    





       
    meta: dict[str, str] = {}
    for raw_line in cf_html_bytes.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith(b"<!--"):
            break
        if b":" in raw_line:
            k, v = raw_line.split(b":", 1)
            key = k.decode("ascii", errors="ignore").strip()
            val = v.decode("ascii", errors="ignore").strip()
            if key:
                meta[key] = val


    start_html = meta.get("StartHTML", "")
    end_html = meta.get("EndHTML", "")
    if start_html.isdigit() and end_html.isdigit():
        try:
            start = int(start_html)
            end = int(end_html)
            if 0 <= start <= end <= len(cf_html_bytes):
                return cf_html_bytes[start:end].decode("utf-8", errors="ignore")
        except Exception:
            pass


    sf = meta.get("StartFragment", "")
    ef = meta.get("EndFragment", "")
    if sf.isdigit() and ef.isdigit():
        try:
            start_fragment = int(sf)
            end_fragment = int(ef)
            if 0 <= start_fragment <= end_fragment <= len(cf_html_bytes):
                return cf_html_bytes[start_fragment:end_fragment].decode("utf-8", errors="ignore")
        except Exception:
            pass


    m = re.search(
        rb"<!--StartFragment-->(.*)<!--EndFragment-->",
        cf_html_bytes,
        flags=re.S,
    )
    if m:
        return m.group(1).decode("utf-8", errors="ignore")


    return cf_html_bytes.decode("utf-8", errors="ignore")


def _extract_html_fragment(cf_html: str) -> str:
    







       

    meta = {}
    for line in cf_html.splitlines():
        if line.strip().startswith("<!--"):
            break
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    

    start_html = meta.get("StartHTML")
    end_html = meta.get("EndHTML")
    if start_html and end_html and start_html.isdigit() and end_html.isdigit():
        try:
            start = int(start_html)
            end = int(end_html)
            return cf_html[start:end]
        except Exception:
            pass
    

    sf = meta.get("StartFragment")
    ef = meta.get("EndFragment")
    if sf and ef and sf.isdigit() and ef.isdigit():
        try:
            start_fragment = int(sf)
            end_fragment = int(ef)
            return cf_html[start_fragment:end_fragment]
        except Exception:
            pass
    

    m = re.search(r"<!--StartFragment-->(.*)<!--EndFragment-->", cf_html, flags=re.S)
    if m:
        return m.group(1)
    

    return cf_html


def copy_files_to_clipboard(file_paths: list) -> None:
    







       
    try:

        absolute_paths = [os.path.abspath(path) for path in file_paths if os.path.exists(path)]
        
        if not absolute_paths:
            raise ClipboardError("No valid files to copy to clipboard")
        

        _copy_files_simple(absolute_paths)
        
    except Exception as e:
        raise ClipboardError(f"Failed to copy files to clipboard: {e}")


def _build_hdrop_data(file_paths: list) -> bytes:
                           

    class DROPFILES(ctypes.Structure):
        _fields_ = [
            ("pFiles", wintypes.DWORD),
            ("pt", wintypes.POINT),
            ("fNC", wintypes.BOOL),
            ("fWide", wintypes.BOOL),
        ]



    files_text = "\0".join(file_paths) + "\0\0"
    files_data = files_text.encode("utf-16le")
    

    struct_size = ctypes.sizeof(DROPFILES)
    

    total_size = struct_size + len(files_data)
    buf = ctypes.create_string_buffer(total_size)
    

    dropfiles = DROPFILES.from_buffer(buf)
    dropfiles.pFiles = struct_size
    dropfiles.pt = wintypes.POINT(0, 0)
    dropfiles.fNC = False
    dropfiles.fWide = True
    


    ctypes.memmove(ctypes.byref(buf, struct_size), files_data, len(files_data))
    
    return buf.raw


def _copy_files_simple(file_paths: list) -> None:
                            
    try:

        wc.OpenClipboard(None)
        try:

            wc.EmptyClipboard()
            

            data = _build_hdrop_data(file_paths)
            

            wc.SetClipboardData(wc.CF_HDROP, data)
            
            log(f"Successfully copied {len(file_paths)} files to clipboard using CF_HDROP")
            
        finally:
            wc.CloseClipboard()
            
    except Exception as e1:
        log(f"CF_HDROP method failed: {e1}")

        try:
            _copy_files_as_text(file_paths)
        except Exception as e2:

            raise ClipboardError(
                f"All clipboard methods failed. CF_HDROP: {e1}; Text fallback: {e2}"
            ) from e1


def _copy_files_as_text(file_paths: list) -> None:
                        
    try:
        wc.OpenClipboard(None)
        try:
            wc.EmptyClipboard()
            

            text_data = "\r\n".join(file_paths)
            wc.SetClipboardData(wc.CF_UNICODETEXT, text_data)
            
            log("Copied file paths as text to clipboard as fallback")
            
        finally:
            wc.CloseClipboard()
            
    except Exception as e:
        log(f"Text fallback method failed: {e}")

        text_data = "\r\n".join(file_paths)
        pyperclip.copy(text_data)
        log("Used pyperclip as final fallback")






def is_clipboard_files() -> bool:
    




       
    try:

        for attempt in range(3):
            try:
                wc.OpenClipboard(None)
                try:
                    result = bool(wc.IsClipboardFormatAvailable(wc.CF_HDROP))
                    log(f"Clipboard files check: {result}")
                    return result
                finally:
                    wc.CloseClipboard()
            except Exception as e:
                log(f"Clipboard files check attempt {attempt + 1} failed: {e}")
                time.sleep(0.03)
        return False
    except Exception as e:
        log(f"Failed to check clipboard files: {e}")
        return False


def get_clipboard_files() -> list[str]:
    






       
    file_paths = []
    try:
        for attempt in range(3):
            try:
                wc.OpenClipboard(None)
                try:
                    if wc.IsClipboardFormatAvailable(wc.CF_HDROP):
                        data = wc.GetClipboardData(wc.CF_HDROP)

                        if data:
                            file_paths = list(data)
                            log(f"Got {len(file_paths)} files from clipboard")
                        break
                finally:
                    wc.CloseClipboard()
            except Exception as e:
                log(f"Get clipboard files attempt {attempt + 1} failed: {e}")
                time.sleep(0.03)
    except Exception as e:
        log(f"Failed to get clipboard files: {e}")
    
    return file_paths






def get_markdown_files_from_clipboard() -> list[str]:
    






       
    all_files = get_clipboard_files()
    return filter_markdown_files(all_files)


def read_markdown_files_from_clipboard() -> tuple[bool, list[tuple[str, str]], list[tuple[str, str]]]:
    










       
    md_files = get_markdown_files_from_clipboard()
    return read_markdown_files(md_files)
