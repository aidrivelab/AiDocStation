# -*- coding: utf-8 -*-
"""
@File    : local_bridge/utils/fs.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import os
import pathlib
import subprocess
import tempfile
import re
from datetime import datetime
from typing import Optional, List
from bs4 import BeautifulSoup
from .system_detect import is_windows, is_macos


def ensure_dir(path: str) -> None:
                        
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)


def open_dir(path: str) -> None:
                     
    path = os.path.abspath(path)
    if os.path.isdir(path):
        if is_windows():
            os.startfile(path)
        elif is_macos():
            subprocess.Popen(['open', path])
        else:
            subprocess.Popen(['xdg-open', path])


def open_file(path: str) -> None:
                    
    path = os.path.abspath(path)
    if os.path.isfile(path):
        if is_windows():
            os.startfile(path)
        elif is_macos():
            subprocess.Popen(['open', path])
        else:
            subprocess.Popen(['xdg-open', path])


def extract_title_from_markdown(md_text: str, max_chars: int = 30) -> Optional[str]:
    









       
    lines = md_text.strip().split('\n')
    

    for heading_level in range(1, 7):
        heading_marker = '#' * heading_level
        for line in lines:
            line = line.strip()

            match = re.match(rf'^{re.escape(heading_marker)}\s+(.+?)$', line)
            if match:
                title = match.group(1).strip()

                cleaned = sanitize_filename(title, max_length=max_chars)
                if cleaned:
                    return cleaned
    

    for line in lines:
        line = line.strip()

        if not line or line.startswith('|') or line.startswith('-') or \
           line.startswith('*') or line.startswith('`') or line.startswith('>'):
            continue
        

        text = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)
        text = re.sub(r'`(.+?)`', r'\1', text)
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
        
        text = text.strip()
        if text:

            cleaned = sanitize_filename(text, max_length=max_chars)
            if cleaned:
                return cleaned
    
    return None


def extract_title_from_html(html_text: str, max_chars: int = 30) -> Optional[str]:
                           
    if not html_text:
        return None

    soup = None
    try:
        soup = BeautifulSoup(html_text, "lxml")
    except Exception:
        try:
            soup = BeautifulSoup(html_text, "html.parser")
        except Exception:
            return None

    if soup.title and soup.title.string:
        candidate = sanitize_filename(soup.title.string.strip(), max_length=max_chars)
        if candidate:
            return candidate

    for heading_level in range(1, 7):
        for tag in soup.find_all(f"h{heading_level}"):
            text = tag.get_text(strip=True)
            if text:
                candidate = sanitize_filename(text, max_length=max_chars)
                if candidate:
                    return candidate

    for text in soup.stripped_strings:
        candidate = sanitize_filename(text, max_length=max_chars)
        if candidate:
            return candidate

    return None


def extract_table_name_from_data(table_data: List[List[str]], max_chars: int = 30) -> Optional[str]:
    









       
    if not table_data or len(table_data) == 0:
        return None
    

    first_row = table_data[0]
    if first_row:

        cells = first_row[:min(6, len(first_row))]

        cells = [cell.strip() for cell in cells if cell.strip()]
        if cells:
            table_name = "_".join(cells)
            table_name = sanitize_filename(table_name, max_length=max_chars)
            return table_name if table_name else None
    
    return None


def sanitize_filename(filename: str, max_length: int = 100) -> str:
    








       

    invalid_chars = r'[<>:"/\\|?*]'
    cleaned = re.sub(invalid_chars, '_', filename)
    

    cleaned = re.sub(r'_+', '_', cleaned)
    

    cleaned = cleaned.strip('_')
    

    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length].rstrip('_')
    
    return cleaned or "document"


def generate_unique_path(base_path: str) -> str:
    







       
    if not os.path.exists(base_path):
        return base_path
    

    dir_path = os.path.dirname(base_path)
    filename = os.path.basename(base_path)
    name, ext = os.path.splitext(filename)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_filename = f"{name}_{timestamp}{ext}"
    
    return os.path.join(dir_path, new_filename)


def generate_output_path(keep_file: bool, save_dir: str, md_text: str = "",
                         table_data: Optional[List[List[str]]] = None,
                         html_text: str = "") -> str:
    











       
    filename = None
    file_ext = "xlsx" if table_data is not None else "docx"
    

    if table_data is not None:
        table_name = extract_table_name_from_data(table_data)
        if table_name:
            filename = f"{table_name}.{file_ext}"
    

    if filename is None and html_text:
        html_title = extract_title_from_html(html_text)
        if html_title:
            filename = f"{html_title}.{file_ext}"


    if filename is None and md_text:
        title = extract_title_from_markdown(md_text)
        if title:
            filename = f"{title}.{file_ext}"
    

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"md_paste_{timestamp}.{file_ext}"
    
    if keep_file:
        ensure_dir(save_dir)
        base_path = os.path.join(save_dir, filename)
        return generate_unique_path(base_path)
    else:
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        return generate_unique_path(temp_path)
