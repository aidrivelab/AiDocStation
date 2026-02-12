# -*- coding: utf-8 -*-
"""
@File    : local_bridge/service/spreadsheet/parser.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import re
from typing import List, Optional


def _split_table_cells(line: str) -> List[str]:
    







       
    cells = []
    current_cell = []
    i = 0
    
    while i < len(line):
        if i > 0 and line[i] == '|' and line[i - 1] == '\\':

            current_cell[-1] = '|'
            i += 1
        elif line[i] == '|':

            cells.append(''.join(current_cell).strip())
            current_cell = []
            i += 1
        else:
            current_cell.append(line[i])
            i += 1
    

    if current_cell or cells:
        cells.append(''.join(current_cell).strip())
    
    return cells


def parse_markdown_table(md_text: str) -> Optional[List[List[str]]]:
    







       
    lines = md_text.strip().split('\n')
    if len(lines) < 2:
        return None
    
    table_data = []
    separator_found = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        

        if not line:
            continue
            

        if not (line.startswith('|') or line.endswith('|') or '|' in line):

            if separator_found:
                break

            return None
        

        if re.match(r'^\s*\|?\s*[-:]+\s*(\|\s*[-:]+\s*)+\|?\s*$', line):
            separator_found = True
            continue
        

        cells = _split_table_cells(line)
        

        if cells and cells[0] == '':
            cells = cells[1:]
        if cells and cells[-1] == '':
            cells = cells[:-1]
        
        if cells:
            table_data.append(cells)
    

    if not separator_found or not table_data:
        return None
    
    return table_data
