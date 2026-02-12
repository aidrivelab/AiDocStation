# -*- coding: utf-8 -*-
"""
@File    : local_bridge/utils/win32/detector.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import win32com.client
from .window import (
    get_foreground_process_name,
    get_foreground_process_path,
    get_foreground_window_title,
)
from ..logging import log


def detect_active_app() -> str:
    




       
    process_name = get_foreground_process_name()
    process_path = get_foreground_process_path()
    log(f"前台进程名称: {process_name}")
    
    if "winword" in process_name:
        return "word"
    elif "excel" in process_name:
        return "excel"
    elif process_name == "et.exe":
        return "wps_excel"
    elif "wps" in process_name:

        return detect_wps_type()
    else:

        if process_path:
            return process_path.lower()
        return process_name or ""


def detect_wps_type() -> str:
    





       
    window_title = get_foreground_window_title()
    log(f"WPS 窗口标题: {window_title}")
    


    excel_prog_ids = ["ket.Application", "ET.Application"]
    for prog_id in excel_prog_ids:
        try:
            app = win32com.client.GetActiveObject(prog_id)

            try:
                com_caption = app.ActiveDocument.Name
                log(f"WPS 表格 COM 窗口标题: {com_caption}")

                if _normalize_title(com_caption) in _normalize_title(window_title):
                    log("通过 COM 窗口标题匹配,确认�?WPS 表格")
                    return "wps_excel"
                else:
                    log("COM 窗口标题不匹�?WPS 表格不在前台")
            except Exception as e:
                log(f"无法获取 {prog_id} �?Caption: {e}")

                pass
        except Exception:
            continue
    

    word_prog_ids = ["kwps.Application", "KWPS.Application"]
    for prog_id in word_prog_ids:
        try:
            app = win32com.client.GetActiveObject(prog_id)

            try:

                com_caption = app.ActiveDocument.Name
                log(f"WPS 文字 COM Caption: {com_caption}")



                log(f"成功连接�?{prog_id}")

                break
            except Exception as e:
                log(f"无法获取 {prog_id} �?Caption: {e}")
        except Exception:
            continue
    

    log("COM 检测失�?使用窗口标题判断")
    


    excel_extensions = [
        ".et",
        ".xls",
        ".xlsx",
        ".csv",
    ]
    

    for ext in excel_extensions:
        if ext in window_title.lower():
            log(f"通过窗口标题后缀 '{ext}' 识别�?WPS 表格")
            return "wps_excel"
    

    word_extensions = [
        ".doc",
        ".docx",
        ".wps",
    ]
    

    for ext in word_extensions:
        if ext in window_title.lower():
            log(f"通过窗口标题后缀 '{ext}' 识别�?WPS 文字")
            return "wps"
    


    excel_keywords = [
        "WPS 表格",
        " - WPS Spreadsheets",
        " ET ",
        "工作�?,
    ]
    

    for keyword in excel_keywords:
        if keyword in window_title:
            log(f"通过窗口标题关键�?'{keyword}' 识别�?WPS 表格")
            return "wps_excel"
    

    word_keywords = [
        "文字文稿",
        "WPS 文字",
        " - WPS Writer",
    ]
    

    for keyword in word_keywords:
        if keyword in window_title:
            log(f"通过窗口标题关键�?'{keyword}' 识别�?WPS 文字")
            return "wps"
    

    log("无明确标�?默认识别�?WPS 文字")
    return "wps"


def _normalize_title(title: str) -> str:
    







       
    if not title:
        return ""
    return title.replace(" ", "").replace("\n", "").replace("\r", "").lower()


def _verify_wps_excel_running() -> bool:
    




       
    excel_prog_ids = ["ket.Application", "ET.Application"]
    for prog_id in excel_prog_ids:
        try:
            app = win32com.client.GetActiveObject(prog_id)

            try:
                _ = app.ActiveSheet
                return True
            except Exception:
                continue
        except Exception:
            continue
    return False
