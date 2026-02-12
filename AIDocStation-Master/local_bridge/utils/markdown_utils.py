# -*- coding: utf-8 -*-
"""
@File    : local_bridge/utils/markdown_utils.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import re


def merge_markdown_contents(files_data: list[tuple[str, str]]) -> str:
    











       
    if len(files_data) == 1:

        return files_data[0][1]
    

    merged_parts = []
    for filename, content in files_data:
        merged_parts.append(f"<!-- Source: {filename} -->")
        merged_parts.append(content.strip())
        merged_parts.append("")
    
    return "\n".join(merged_parts)

def has_backtick_fenced_code_block(text: str) -> bool:
    

       
    if not text:
        return False

    pattern = re.compile(
        r'^\s{0,3}(`{3,})[^\n]*\n'
        r'[\s\S]*?\n'
        r'^\s{0,3}\1\s*$',
        re.MULTILINE
    )
    return bool(pattern.search(text))


def has_latex_math(text: str) -> bool:
    




       
    if not text:
        return False


    if re.search(r'\$\$[\s\S]*?\$\$', text):
        return True


    if re.search(r'\\\[[\s\S]*?\\\]', text):
        return True


    if re.search(r'\\\([^\n]*?\\\)', text):
        return True


    if re.search(r'(?<!\$)\$(?!\$)[^\n$]+(?<!\$)\$(?!\$)', text):
        return True

    return False

def is_markdown(text: str) -> bool:
    if not text or not isinstance(text, str):
        return False

    if has_backtick_fenced_code_block(text):
        return True

    if has_latex_math(text):
        return True

    md_patterns = [
        r'^\s{0,3}#{1,6}\s+',
        r'\[.+?\]\(.+?\)',
        r'^\s*[-*+]\s+',
        r'^\s*\d+\.\s+',
        r'^>\s+',
        r'`[^`]+`',
        r'!\[.*?\]\(.+?\)',
        r'(\*\*|__).+?(\*\*|__)',
        r'(\*|_).+?(\*|_)',
    ]

    for p in md_patterns:
        if re.search(p, text, re.MULTILINE):
            return True
    return False
