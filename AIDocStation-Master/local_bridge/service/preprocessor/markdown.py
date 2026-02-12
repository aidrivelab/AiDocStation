# -*- coding: utf-8 -*-
"""
@File    : local_bridge/service/preprocessor/markdown.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import re
from .base import BasePreprocessor
from ...utils.md_normalizer import normalize_markdown
from ...utils.latex import convert_latex_delimiters
from ...utils.logging import log


class MarkdownPreprocessor(BasePreprocessor):
                              

    def process(self, markdown: str, config: dict) -> str:
        















           
        log("Preprocessing Markdown content")


        if config.get("normalize_markdown", True):
            markdown = normalize_markdown(markdown)


        if config.get("latex_support", True):
            fix_single_dollar_block = config.get("fix_single_dollar_block", True)
            markdown = convert_latex_delimiters(markdown, fix_single_dollar_block)


        remove_hr_enabled = config.get("remove_horizontal_rules", False)
        log(f"remove_horizontal_rules config: {remove_hr_enabled}")
        if remove_hr_enabled:
            markdown, hr_count = self._remove_horizontal_rules(markdown)
            log(f"Horizontal rules processing: found and removed {hr_count} rule(s)")
        else:
            log("Horizontal rules processing: DISABLED by config")


        clean_heading_enabled = config.get("clean_heading_number", False)
        log(f"clean_heading_number config: {clean_heading_enabled}")
        if clean_heading_enabled:
            markdown, cleaned_count = self._clean_heading_numbers(markdown)
            log(f"Heading number cleaning: cleaned {cleaned_count} heading(s)")


        if config.get("enable_mermaid_rendering", True):
            markdown, mermaid_count = self._render_mermaid_blocks(markdown)
            if mermaid_count > 0:
                log(f"Mermaid rendering: converted {mermaid_count} diagram(s) to image(s)")

        return markdown

    def _render_mermaid_blocks(self, markdown: str) -> tuple[str, int]:
        














           


        pattern = r'```mermaid\s*\n(.*?)\n```'
        

        count = len(re.findall(pattern, markdown, re.DOTALL))
        
        if count == 0:
            return markdown, 0
            
        def replace_with_class(match):
            code = match.group(1)

            return f"```{{.mermaid}}\n{code}\n```"


        result = re.sub(pattern, replace_with_class, markdown, flags=re.DOTALL)
        
        return result, count

    def _remove_horizontal_rules(self, markdown: str) -> tuple[str, int]:
        r"""
        删除 Markdown 中的水平分割�?
        
        按照 AIDOC Copilot 的实现方式：
        使用正则表达�?/^(\s*[-*_]{3,}\s*)$/gm 匹配分割�?
        
        支持的分割线格式:
        - --- (3个及以上连字�?
        - *** (3个及以上星号)
        - ___ (3个及以上下划�?
        - 前后可有空格
        - HTML hr 标签
        
        Returns:
            tuple[str, int]: (处理后的 Markdown, 删除的分割线数量)
        """


        md_hr_pattern = r'^\s*[-*_]{3,}\s*$'
        html_hr_pattern = r'^\s*<hr\s*/?>\s*$'
        

        combined_pattern = f'({md_hr_pattern})|({html_hr_pattern})'
        

        removed_count = 0
        
        def count_and_remove(match):
            nonlocal removed_count
            removed_count += 1
            log(f"DEBUG: Removing HR: '{match.group().strip()}'")
            return ''
        

        result = re.sub(combined_pattern, count_and_remove, markdown, flags=re.MULTILINE | re.IGNORECASE)
        

        result = re.sub(r'\n{3,}', '\n\n', result)
        
        return result, removed_count

    def _clean_heading_numbers(self, markdown: str) -> tuple[str, int]:
        










           
        lines = markdown.split('\n')
        cleaned_lines = []
        cleaned_count = 0
        

        heading_pattern = r'^(#{1,6})\s+'
        

        number_patterns = [
            r'^\d+[\.\、\.\s]+',
            r'^[一二三四五六七八九十]+[\、\.\s]+',
            r'^第[一二三四五六七八九十\d]+[章节部分篇]\s*',
            r'^\([一二三四五六七八九十\d]+\)\s*',
            r'^（[一二三四五六七八九十\d]+）\s*',
            r'^\[[一二三四五六七八九十\d]+\]\s*',
        ]
        
        for line in lines:
            heading_match = re.match(heading_pattern, line)
            if heading_match:

                prefix = heading_match.group(0)
                content = line[len(prefix):]
                
                original_content = content

                for pattern in number_patterns:
                    new_content = re.sub(pattern, '', content, count=1)
                    if new_content != content:
                        content = new_content.strip()
                        break
                
                if content != original_content:
                    cleaned_count += 1
                    new_line = prefix + content
                    log(f"Cleaned heading: '{line.strip()}' -> '{new_line.strip()}'")
                    cleaned_lines.append(new_line)
                else:
                    cleaned_lines.append(line)
            else:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines), cleaned_count
