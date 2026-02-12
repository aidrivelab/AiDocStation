# -*- coding: utf-8 -*-
"""
@File    : local_bridge/utils/latex.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import re


def convert_latex_delimiters(text: str, fix_single_dollar_block: bool = True) -> str:
    






       

    protected_content = []
    
    def mask_code(match):
        placeholder = f"____PROTECTED_CODE_{len(protected_content)}____"
        protected_content.append(match.group(0))
        return placeholder



    text = re.sub(r'```[\s\S]*?```|~~~[\s\S]*?~~~', mask_code, text)

    text = re.sub(r'(`+)([\s\S]*?)\1', mask_code, text)


    text = _convert_standard_latex_delimiters(text)
    
    if fix_single_dollar_block:

        text = _fix_math_formatting(text)

        text = _fix_single_dollar_blocks(text)
    

    def restore_code(match):
        idx = int(match.group(1))
        return protected_content[idx] if idx < len(protected_content) else match.group(0)

    text = re.sub(r'____PROTECTED_CODE_(\d+)____', restore_code, text)
        
    return text


def _convert_standard_latex_delimiters(text: str) -> str:
    





       

    text = re.sub(r'\\\[([\s\S]*?)\\\]', lambda m: f"\n$$\n{m.group(1).strip()}\n$$\n", text)
    

    text = re.sub(r'\\\(([^ \n][^\n]*?)\\\)', lambda m: f"${m.group(1).strip()}$", text)
    
    return text


def _fix_math_formatting(text: str) -> str:
    


       










    



    
    pattern_block = r'\$\$((?:(?!\n\s*\n)[\s\S])*?)\$\$'
    
    def fix_block(match):
        content = match.group(1).strip()
        return f"$$\n{content}\n$$"

    text = re.sub(pattern_block, fix_block, text)



    def fix_inline_spaces(match):
        content = match.group(1).strip()
        if not content: return match.group(0)
        return f"${content}$"









    pattern_inline = r'(?<!\$) \$(?!\s) ([^\n$]+?) (?<!\s)\$ (?!\$)'
    return re.sub(pattern_inline, fix_inline_spaces, text, flags=re.VERBOSE)


def _fix_single_dollar_blocks(text: str) -> str:
    

       
    lines = text.split('\n')
    new_lines = []
    

    re_single_line_math = re.compile(r'^\s*\$([^\$]+)\$\s*$')

    re_double_dollar = re.compile(r'^\s*\$\$\s*$')

    for line in lines:
        stripped = line.strip()
        if not stripped:
            new_lines.append(line)
            continue
            

        if stripped.startswith('$'):
            if re_double_dollar.match(stripped):
                new_lines.append("$$")
                continue
            
            match = re_single_line_math.match(line)
            if match:
                content = match.group(1).strip()
                new_lines.append(f"$$\n{content}\n$$")
                continue
            

            new_lines.append(stripped)
        else:
            new_lines.append(line)
            
    return '\n'.join(new_lines)
