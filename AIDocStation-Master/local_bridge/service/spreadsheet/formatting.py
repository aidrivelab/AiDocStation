# -*- coding: utf-8 -*-
"""
@File    : local_bridge/service/spreadsheet/formatting.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import re
from typing import List, Optional


class TextSegment:
                     
    def __init__(self, text: str, bold: bool = False, italic: bool = False,
                 strikethrough: bool = False, is_code: bool = False,
                 hyperlink_url: Optional[str] = None):
        self.text = text
        self.bold = bold
        self.italic = italic
        self.strikethrough = strikethrough
        self.is_code = is_code
        self.hyperlink_url = hyperlink_url


class CellFormat:
                 
    def __init__(self, text: str):
        self.text = text
        self.is_code_block = False
        self.has_newline = False
        self.segments = []
        self.clean_text = text
    
    def parse(self) -> str:
                                          
        text = self.text
        

        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        if '\n' in text:
            self.has_newline = True
        

        if '<pre>' in text.lower() or '<code>' in text.lower():
            self.is_code_block = True

            text = re.sub(r'<pre>(.*?)</pre>',
                          lambda m: re.sub(r'<br\s*/?>', '\n', m.group(1), flags=re.IGNORECASE),
                          text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<code>(.*?)</code>',
                          lambda m: re.sub(r'<br\s*/?>', '\n', m.group(1), flags=re.IGNORECASE),
                          text, flags=re.DOTALL | re.IGNORECASE)
            self.clean_text = text.strip()
            self.segments = [TextSegment(self.clean_text, is_code=True)]
            return self.clean_text
        

        self.segments = self._parse_segments(text)
        self.clean_text = ''.join(seg.text for seg in self.segments)
        return self.clean_text
    
    def _parse_segments(self, text: str, bold: bool = False, italic: bool = False,
                        strikethrough: bool = False) -> List[TextSegment]:
        







           
        segments = []
        i = 0
        current_text = []
        
        def flush_current():
                               
            if current_text:
                text_str = ''.join(current_text)
                if text_str:
                    segments.append(TextSegment(text_str, bold, italic, strikethrough))
                current_text.clear()
        
        while i < len(text):

            if text[i] == '\\' and i + 1 < len(text):
                current_text.append(text[i + 1])
                i += 2
                continue
            

            if text[i] == '`':
                end = text.find('`', i + 1)
                if end != -1:
                    flush_current()

                    code_text = text[i + 1:end]
                    segments.append(TextSegment(code_text, is_code=True))
                    i = end + 1
                    continue
            

            if text[i:i + 2] == '~~' and not strikethrough:
                end = text.find('~~', i + 2)
                if end != -1:
                    flush_current()
                    inner = text[i + 2:end]

                    segments.extend(self._parse_segments(inner, bold, italic, True))
                    i = end + 2
                    continue
            

            if text[i:i + 3] == '***' and not bold and not italic:
                end = text.find('***', i + 3)
                if end != -1:
                    flush_current()
                    inner = text[i + 3:end]

                    segments.extend(self._parse_segments(inner, True, True, strikethrough))
                    i = end + 3
                    continue
            

            if text[i:i + 2] == '**' and not bold:

                end = i + 2
                while end < len(text) - 1:
                    if text[end:end + 2] == '**':
                        flush_current()
                        inner = text[i + 2:end]

                        segments.extend(self._parse_segments(inner, True, italic, strikethrough))
                        i = end + 2
                        break
                    end += 1
                else:

                    current_text.append(text[i])
                    i += 1
                continue
            

            if text[i:i + 3] == '___' and not bold and not italic:
                end = text.find('___', i + 3)
                if end != -1:
                    flush_current()
                    inner = text[i + 3:end]

                    segments.extend(self._parse_segments(inner, True, True, strikethrough))
                    i = end + 3
                    continue
            
            if text[i:i + 2] == '__' and not bold:

                end = i + 2
                while end < len(text) - 1:
                    if text[end:end + 2] == '__':
                        flush_current()
                        inner = text[i + 2:end]
                        segments.extend(self._parse_segments(inner, True, italic, strikethrough))
                        i = end + 2
                        break
                    end += 1
                else:

                    current_text.append(text[i])
                    i += 1
                continue
            

            if text[i] == '*' and (i + 1 >= len(text) or text[i + 1] != '*'):
                end = i + 1

                while end < len(text):
                    if text[end] == '*' and (end + 1 >= len(text) or text[end + 1] != '*'):
                        flush_current()
                        inner = text[i + 1:end]

                        segments.extend(self._parse_segments(inner, bold, True, strikethrough))
                        i = end + 1
                        break
                    end += 1
                else:

                    current_text.append(text[i])
                    i += 1
                continue
            
            if text[i] == '_' and (i + 1 >= len(text) or text[i + 1] != '_'):
                end = i + 1
                while end < len(text):
                    if text[end] == '_' and (end + 1 >= len(text) or text[end + 1] != '_'):
                        flush_current()
                        inner = text[i + 1:end]
                        segments.extend(self._parse_segments(inner, bold, True, strikethrough))
                        i = end + 1
                        break
                    end += 1
                else:

                    current_text.append(text[i])
                    i += 1
                continue
            

            if text[i] == '[':
                close_bracket = text.find(']', i + 1)
                if close_bracket != -1 and close_bracket + 1 < len(text) and text[close_bracket + 1] == '(':
                    close_paren = text.find(')', close_bracket + 2)
                    if close_paren != -1:
                        flush_current()

                        link_text = text[i + 1:close_bracket]
                        link_url = text[close_bracket + 2:close_paren]

                        link_segments = self._parse_segments(link_text, bold, italic, strikethrough)

                        for seg in link_segments:
                            seg.hyperlink_url = link_url
                        segments.extend(link_segments)
                        i = close_paren + 1
                        continue
            

            current_text.append(text[i])
            i += 1
        
        flush_current()
        return segments
