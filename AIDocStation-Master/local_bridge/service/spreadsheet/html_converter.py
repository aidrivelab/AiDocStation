# -*- coding: utf-8 -*-
"""
@File    : local_bridge/service/spreadsheet/html_converter.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from __future__ import annotations

from html import escape
from typing import List, Tuple

from .formatting import CellFormat


def wrap_tag(tag: str, content: str) -> str:
                                     
    return f"<{tag}>{content}</{tag}>"


def cell_to_html(cell_value: str, *, keep_format: bool) -> Tuple[str, bool]:
    










       
    cf = CellFormat(cell_value)
    clean_text = cf.parse()


    if not keep_format:
        return escape(clean_text).replace("\n", "<br />"), False


    if cf.is_code_block:
        inner = escape(clean_text)
        inner = inner.replace("\n", "<br />")
        return wrap_tag("code", inner), True


    parts: List[str] = []
    needs_code_bg = False

    for seg in cf.segments:
        seg_text = escape(seg.text or "").replace("\n", "<br />")
        chunk = seg_text


        if seg.is_code:
            needs_code_bg = True
            chunk = wrap_tag("code", chunk)
        if seg.strikethrough:
            chunk = wrap_tag("s", chunk)
        if seg.italic:
            chunk = wrap_tag("i", chunk)
        if seg.bold:
            chunk = wrap_tag("b", chunk)
        if seg.hyperlink_url:
            url = escape(seg.hyperlink_url, quote=True)
            chunk = f'<a href="{url}">{chunk}</a>'

        parts.append(chunk)

    return "".join(parts) or escape(clean_text), needs_code_bg


def table_to_html(table_data: List[List[str]], *, keep_format: bool) -> str:
    








       
    rows_html: List[str] = []
    start_marker = "<!--StartFragment-->"
    end_marker = "<!--EndFragment-->"

    for r, row in enumerate(table_data):
        cell_tag = "th" if r == 0 else "td"
        cell_html: List[str] = []

        for cell_value in row:
            content_html, needs_code_bg = cell_to_html(
                cell_value, keep_format=keep_format
            )
            

            style_parts = ["padding:2px 6px", "vertical-align:middle"]
            

            if r == 0:
                style_parts.extend(["font-weight:bold", "background-color:#D3D3D3"])
            

            if needs_code_bg:
                style_parts.extend([
                    "background-color:#F0F0F0",
                    "font-family:Menlo,Consolas,monospace"
                ])
            
            style_attr = ";".join(style_parts)
            cell_html.append(
                f"<{cell_tag} style=\"{style_attr}\">{content_html}</{cell_tag}>"
            )

        rows_html.append("<tr>" + "".join(cell_html) + "</tr>")


    return (
        start_marker +
        "<html><head><meta charset=\"utf-8\" />"
        "<style>"
        "table{border-collapse:collapse}"
        "td,th{border:1px solid #D0D0D0}"
        "a{color:#0563C1;text-decoration:underline}"
        "</style>"
        "</head><body>"
        "<table>"
        + "".join(rows_html)
        + "</table>"
        "</body></html>"
        + end_marker
    )


def table_to_tsv(table_data: List[List[str]]) -> str:
    







       
    lines: List[str] = []
    
    for row in table_data:
        out_cells: List[str] = []
        for cell_value in row:
            cf = CellFormat(cell_value)
            text = cf.parse()

            text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", " ")
            out_cells.append(text)
        lines.append("\t".join(out_cells))
    
    return "\n".join(lines)
