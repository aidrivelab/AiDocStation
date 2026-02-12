# -*- coding: utf-8 -*-
"""
@File    : local_bridge/utils/html_analyzer.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from __future__ import annotations

from typing import Iterable, Set

try:
    from bs4 import BeautifulSoup, FeatureNotFound
except Exception:
    BeautifulSoup = None
    FeatureNotFound = None

from .logging import log
from .clipboard import get_clipboard_text
from .markdown_utils import is_markdown


SEMANTIC_TAGS: Set[str] = {
    "p",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "ul",
    "ol",
    "li",
    "dl",
    "dt",
    "dd",
    "table",
    "thead",
    "tbody",
    "tfoot",
    "tr",
    "th",
    "td",
    "col",
    "colgroup",
    "pre",
    "code",
    "blockquote",
    "figure",
    "figcaption",
    "math",
    "section",
    "article",
    "header",
    "footer",
    "aside",
    "nav",
    "hr",
}


INLINE_WRAPPER_TAGS: Set[str] = {
    "span",
    "font",
    "strong",
    "em",
    "b",
    "i",
    "u",
    "sub",
    "sup",
    "s",
    "del",
    "mark",
    "a",
}


MARKDOWN_HINTS: Iterable[str] = (
    "\n#",
    "\n##",
    "\n- ",
    "\n* ",
    "\n1.",
    "```",
    "**",
    "__",
    "~~",
    "> ",
    "$$",
    "\\(",
    "\\)",
    "|",
    "\n---",
    "\n***",
    "`",
)


def _count_semantic_tags(html_soup) -> int:
                               
    body = html_soup.body or html_soup
    count = 0
    for tag in body.find_all(True):
        name = tag.name.lower()
        if name in SEMANTIC_TAGS:
            count += 1
    return count


def _only_contains_inline_wrappers(html_soup) -> bool:
                                            
    body = html_soup.body or html_soup
    for tag in body.find_all(True):
        name = tag.name.lower()
        if name in ("html", "head", "body", "meta", "style"):
            continue
        if name not in INLINE_WRAPPER_TAGS:
            return False
    return True


def _markdown_hint_score(text: str) -> int:
                               
    score = 0
    for hint in MARKDOWN_HINTS:
        if hint in text:
            score += 1
    return score


def _has_yuanbao_formula_tags(soup) -> bool:
                            
    

    yuanbao_classes = ["ybc-markdown-katex", "ybc-pre-component", "ybc-p", "ybc-ul-component", "ybc-ol-component"]
    
    for class_name in yuanbao_classes:

        elements = soup.find_all(class_=class_name)
        if elements:
            return True
    
    return False



def is_plain_html_fragment(html: str) -> bool:
    









       
    if not html or not html.strip():
        return True

    if BeautifulSoup is None:

        lowered = html.lower()
        return not any(tag in lowered for tag in ("<p", "<h1", "<ul", "<table", "<pre", "<code", "<blockquote"))

    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception as exc:
        if FeatureNotFound is not None and isinstance(exc, FeatureNotFound):
            soup = BeautifulSoup(html, "html.parser")
        else:
            soup = BeautifulSoup(html, "html.parser")

    if "ybc" in html:
        if _has_yuanbao_formula_tags(soup):
            try:
                clipboard_text = get_clipboard_text()
                if clipboard_text and is_markdown(clipboard_text):
                    log("检测到元宝公式标签且剪切板文本包含LaTeX公式，使用文本流�?)
                    return True
            except Exception as e:
                log(f"检测元宝公式时获取剪切板文本失�? {e}")

    semantic_count = _count_semantic_tags(soup)

    if semantic_count > 0:
        return False

    if _only_contains_inline_wrappers(soup):
        return True

    body = soup.body or soup
    text = body.get_text(separator="\n").strip()
    if not text:
        return True

    hint_score = _markdown_hint_score(text)

    return hint_score >= 2
