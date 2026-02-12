# -*- coding: utf-8 -*-
"""
@File    : local_bridge/utils/macos/detector.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from __future__ import annotations
import subprocess

from AppKit import NSWorkspace, NSRunningApplication
from Quartz import (
    CGWindowListCopyWindowInfo,
    kCGWindowListOptionOnScreenOnly,
    kCGWindowListExcludeDesktopElements,
)

from ..logging import log


def detect_active_app() -> str:
    




       

    app = _get_frontmost_app_via_osascript()
    if app:
        name = (app.get("name") or "").lower()
        bundle_id = app.get("bundle_id") or ""
        if not bundle_id or name in ("electron",):
            ns_app = _get_frontmost_app()
            if ns_app and (ns_app.get("bundle_id") or ""):
                app = ns_app
    
    if not app:
        return ""

    name = (app.get("name") or "").lower()
    original_name = app.get("name") or ""
    bundle_id = app.get("bundle_id") or ""
    bundle_id_norm = bundle_id.lower() if bundle_id else ""
    pid = app.get("pid")

    log(f"前台应用: name={original_name}, bundle_id={bundle_id}, pid={pid}")


    if name in ("word", "microsoft word"):
        return "word"
    if name in ("excel", "microsoft excel"):
        return "excel"
    if "wps" in name or "kingsoft" in name:
        return detect_wps_type()


    if bundle_id_norm:
        return bundle_id_norm
    return original_name


def detect_wps_type() -> str:
    





       
    window_title = get_frontmost_window_title()
    log(f"WPS 窗口标题: {window_title}")


    if not window_title:
        log("无法获取窗口标题,默认识别�?WPS 文字")
        return "wps"

    title_l = window_title.lower()


    excel_extensions = [".et", ".xls", ".xlsx", ".csv"]
    for ext in excel_extensions:
        if ext in title_l:
            log(f"通过窗口标题后缀 '{ext}' 识别�?WPS 表格")
            return "wps_excel"

    word_extensions = [".doc", ".docx", ".wps"]
    for ext in word_extensions:
        if ext in title_l:
            log(f"通过窗口标题后缀 '{ext}' 识别�?WPS 文字")
            return "wps"


    excel_keywords = [
        "wps spreadsheets",
        "表格",
        "工作�?,
        "spreadsheet",
        "sheet",
    ]
    for kw in excel_keywords:
        if kw.lower() in title_l:
            log(f"通过窗口标题关键�?'{kw}' 识别�?WPS 表格")
            return "wps_excel"

    word_keywords = [
        "wps writer",
        "文字",
        "文档",
        "writer",
        "document",
    ]
    for kw in word_keywords:
        if kw.lower() in title_l:
            log(f"通过窗口标题关键�?'{kw}' 识别�?WPS 文字")
            return "wps"

    log("无明确标�?默认识别�?WPS 文字")
    return "wps"


def _get_frontmost_app() -> dict | None:
                                 
    try:
        ws = NSWorkspace.sharedWorkspace()
        app = ws.frontmostApplication()
        if not app:
            return None
        return {
            "name": str(app.localizedName() or ""),
            "bundle_id": str(app.bundleIdentifier() or ""),
            "pid": int(app.processIdentifier()),
        }
    except Exception as e:
        log(f"获取前台应用失败(NSWorkspace): {e}")
        return None


def _get_frontmost_app_via_osascript() -> dict | None:
    


       
    try:
        pid_cmd = [
            "osascript",
            "-e",
            'tell application "System Events" to get unix id of first application process whose frontmost is true'
        ]
        pid_str = subprocess.check_output(
            pid_cmd,
            text=True,
            encoding="utf-8",
            errors="replace",
        ).strip()
        bundle_id = ""
        bundle_cmd = [
            "osascript",
            "-e",
            'tell application "System Events" to get bundle identifier of first application process whose frontmost is true'
        ]
        try:
            bundle_id = subprocess.check_output(
                bundle_cmd,
                text=True,
                encoding="utf-8",
                errors="replace",
            ).strip()
        except Exception:
            bundle_id = ""
        if pid_str:
            pid = int(pid_str)
            app = NSRunningApplication.runningApplicationWithProcessIdentifier_(pid)
            if app:
                app_name = str(app.localizedName() or "")
                app_bundle_id = str(app.bundleIdentifier() or "") or bundle_id
                return {
                    "name": app_name,
                    "bundle_id": app_bundle_id,
                    "pid": pid,
                }
        if bundle_id:
            apps = NSRunningApplication.runningApplicationsWithBundleIdentifier_(bundle_id) or []
            if apps:
                app = apps[0]
                return {
                    "name": str(app.localizedName() or ""),
                    "bundle_id": str(app.bundleIdentifier() or ""),
                    "pid": int(app.processIdentifier()),
                }

        name_cmd = [
            "osascript",
            "-e",
            'tell application "System Events" to get name of first application process whose frontmost is true'
        ]
        name = subprocess.check_output(
            name_cmd,
            text=True,
            encoding="utf-8",
            errors="replace",
        ).strip()
        if not name:
            return None
        return {"name": name, "bundle_id": bundle_id, "pid": None}
    except Exception as e:
        log(f"获取前台应用失败(osascript): {e}")
        return None


def get_frontmost_window_title() -> str:
    


       
    try:

        cmd = [
            "osascript",
            "-e",
            'tell application "System Events" to get unix id of first application process whose frontmost is true'
        ]
        pid_str = subprocess.check_output(
            cmd,
            text=True,
            encoding="utf-8",
            errors="replace",
        ).strip()
        if not pid_str:
            return ""
        
        frontmost_pid = int(pid_str)
        

        options = kCGWindowListOptionOnScreenOnly | kCGWindowListExcludeDesktopElements
        win_list = CGWindowListCopyWindowInfo(options, 0) or []


        candidates = []
        for w in win_list:
            try:
                owner_pid = int(w.get("kCGWindowOwnerPID", -1))
                layer = int(w.get("kCGWindowLayer", 999))
                title = w.get("kCGWindowName", "") or ""

                if layer != 0:
                    continue
                if owner_pid != frontmost_pid:
                    continue

                if title.strip():
                    candidates.append(title)
            except Exception:
                continue

        if candidates:
            return str(candidates[0])

        return ""
    except Exception as e:
        log(f"获取前台窗口标题失败: {e}")
        return ""


if __name__ == "__main__":
    import time
    from pynput import keyboard

    log("macOS 前台应用检测测�?- �?Cmd+Shift+D 触发检测，�?Ctrl+C 退�?)
    
    def on_activate():
                       

        time.sleep(0.1)
        
        print(f"\n{'='*60}")
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 开始检�?)
        

        result = detect_active_app()
        
        print(f"检测结�? {result}")
        print(f"{'='*60}\n")
    

    hotkey = keyboard.GlobalHotKeys({
        '<cmd>+<shift>+d': on_activate
    })
    
    try:
        hotkey.start()
        print("�?热键监听已启�?)
        print("�?请切换到要检测的应用窗口")
        print("�?�?Cmd+Shift+D 触发检�?)
        print("�?�?Ctrl+C 退出\n")
        hotkey.join()
    except KeyboardInterrupt:
        log("检测测试已手动终止")
        print("\n退出检�?)
