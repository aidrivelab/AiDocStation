# -*- coding: utf-8 -*-
"""
@File    : local_bridge/service/preprocessor/html.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from bs4 import BeautifulSoup
from .base import BasePreprocessor
from ...utils.html_formatter import (
    clean_html_content,
    convert_css_font_to_semantic,
    convert_strikethrough_to_del,
    promote_bold_first_row_to_header,
)
from ...utils.logging import log


class HtmlPreprocessor(BasePreprocessor):
                          

    def process(self, html: str, config: dict) -> str:
        















           
        log("Preprocessing HTML content")


        soup = BeautifulSoup(html, "html.parser")
        clean_html_content(soup, config)


        if config.get("remove_horizontal_rules", False):
            hr_tags = soup.find_all("hr")
            hr_count = len(hr_tags)
            for hr in hr_tags:
                hr.decompose()
            if hr_count > 0:
                log(f"Removed {hr_count} <hr> tag(s) from HTML")
            else:
                log("No <hr> tags found in HTML")

        html_formatting = config.get("html_formatting") or config.get("Html_formatting") or {}
        if not isinstance(html_formatting, dict):
            html_formatting = {}
        if html_formatting.get("strikethrough_to_del", True):
            convert_strikethrough_to_del(soup)
        if html_formatting.get("css_font_to_semantic", True):
            convert_css_font_to_semantic(soup)
        if html_formatting.get("bold_first_row_to_header", False):
            promote_bold_first_row_to_header(soup)




        html_output = str(soup)
        

        if "<!DOCTYPE" not in html_output.upper():
            html_output = f"<!DOCTYPE html>\n<meta charset='utf-8'>\n{html_output}"
        
        return html_output
