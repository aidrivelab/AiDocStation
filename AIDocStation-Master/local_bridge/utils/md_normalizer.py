# -*- coding: utf-8 -*-
"""
@File    : local_bridge/utils/md_normalizer.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import re


def normalize_markdown(md_text: str) -> str:
    













       

    text = md_text.replace('\r\n', '\n').replace('\r', '\n')
    lines = text.split('\n')
    
    result = []
    in_code_block = False
    in_table = False
    prev_line_type = 'start'
    
    for i, line in enumerate(lines):
        current_type = _get_line_type(line, in_code_block, in_table)
        

        if line.startswith('```'):
            in_code_block = not in_code_block
        

        if current_type == 'table':
            in_table = True
        elif in_table and current_type not in ('table', 'empty'):
            in_table = False
        

        need_blank_before = _should_add_blank_line(prev_line_type, current_type)
        
        if need_blank_before and result and result[-1].strip():
            result.append('')
        
        result.append(line)
        

        need_blank_after = _should_add_blank_after(current_type, i, lines)
        
        if need_blank_after and i + 1 < len(lines) and lines[i + 1].strip():
            result.append('')
        

        prev_line_type = current_type if line.strip() else 'empty'
    
    text = '\n'.join(result)
    

    text = re.sub(r'\n{3,}', '\n\n', text)
    

    if '\r\n' in md_text:
        text = text.replace('\n', '\r\n')
    
    return text


def _get_line_type(line: str, in_code_block: bool, in_table: bool) -> str:
                
    stripped = line.strip()
    
    if not stripped:
        return 'empty'
    
    if in_code_block:
        return 'code'
    

    if line.startswith('```'):
        return 'code'
    

    if re.match(r'^#{1,6}\s+', line):
        return 'heading'
    

    if line.startswith('|') and line.endswith('|'):
        return 'table'
    

    if re.match(r'^[-*_]{3,}$', stripped):
        return 'hr'
    

    if re.match(r'^[-*+]\s', line):
        return 'list'
    

    if re.match(r'^\d+\.\s', line):
        return 'list'
    

    if line.startswith('>'):
        return 'quote'
    
    return 'text'


def _should_add_blank_line(prev_type: str, current_type: str) -> bool:
                        

    if prev_type in ('start', 'empty'):
        return False
    

    if current_type == 'empty':
        return False
    

    if current_type == 'heading':
        return prev_type not in ('heading',)
    

    if current_type == 'code' and prev_type != 'code':
        return True
    

    if current_type == 'table' and prev_type not in ('table',):
        return True
    

    if current_type == 'list' and prev_type not in ('list',):
        return True
    

    if current_type == 'quote' and prev_type not in ('quote',):
        return True
    

    if current_type == 'hr':
        return True
    
    return False


def _should_add_blank_after(current_type: str, index: int, lines: list) -> bool:
                      

    if index >= len(lines) - 1:
        return False
    
    next_line = lines[index + 1].strip()
    

    if not next_line:
        return False
    

    if current_type == 'heading':
        return True
    

    if current_type == 'code' and lines[index].startswith('```'):

        in_code = False
        for i in range(index):
            if lines[i].startswith('```'):
                in_code = not in_code
        if not in_code:
            return True
    

    if current_type == 'hr':
        return True
    
    return False
