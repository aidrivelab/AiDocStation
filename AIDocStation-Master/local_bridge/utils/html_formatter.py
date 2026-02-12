# -*- coding: utf-8 -*-
"""
@File    : local_bridge/utils/html_formatter.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from __future__ import annotations

import re
from typing import Dict, Optional

from bs4 import BeautifulSoup, NavigableString, Tag

_CSS_CLASS_RE = re.compile(r"\.(?P<class>[A-Za-z0-9_-]+)\s*\{(?P<body>[^}]*)\}", re.DOTALL)


def clean_html_content(soup: BeautifulSoup, options: Optional[Dict[str, object]] = None) -> None:
    








       

    options = options or {}


    for svg in soup.find_all("svg"):
        svg.decompose()


    for img in soup.find_all("img", src=True):
        if img["src"].lower().endswith(".svg"):
            img.decompose()
    

    _clean_latex_br_tags(soup)


def convert_css_font_to_semantic(soup: BeautifulSoup) -> None:
    




       
    css_text_parts = []
    for style in soup.find_all("style"):
        css_text_parts.append(style.get_text() or "")
    css_text = "\n".join(css_text_parts)
    if not css_text.strip():
        return

    class_styles: dict[str, tuple[bool, bool]] = {}
    for match in _CSS_CLASS_RE.finditer(css_text):
        class_name = match.group("class")
        body = match.group("body").lower()

        bold = False
        italic = False
        weight_match = re.search(r"font-weight\s*:\s*([^;]+)", body)
        if weight_match:
            value = weight_match.group(1).strip()
            if value in ("bold", "bolder"):
                bold = True
            elif value.isdigit() and int(value) >= 600:
                bold = True

        style_match = re.search(r"font-style\s*:\s*([^;]+)", body)
        if style_match:
            value = style_match.group(1).strip()
            if "italic" in value or "oblique" in value:
                italic = True

        if bold or italic:
            class_styles[class_name] = (bold, italic)

    if not class_styles:
        return

    def _build_wrapper(current_bold: bool, current_italic: bool) -> tuple[Tag, Tag]:
        if current_bold and current_italic:
            strong = soup.new_tag("strong")
            em = soup.new_tag("em")
            strong.append(em)
            return strong, em
        if current_bold:
            strong = soup.new_tag("strong")
            return strong, strong
        em = soup.new_tag("em")
        return em, em

    for tag in soup.find_all(class_=True):
        classes = tag.get("class") or []
        bold = False
        italic = False
        for class_name in classes:
            if class_name in class_styles:
                class_bold, class_italic = class_styles[class_name]
                bold = bold or class_bold
                italic = italic or class_italic

        if not (bold or italic):
            continue

        if tag.name in ("table", "tbody", "thead", "tfoot", "tr"):
            continue

        if tag.name in ("td", "th"):
            if not tag.contents:
                continue
            wrapper, inner = _build_wrapper(bold, italic)
            for child in list(tag.contents):
                inner.append(child.extract())
            tag.append(wrapper)
            continue

        if tag.name in ("strong", "em"):
            if tag.name == "strong" and bold and not italic:
                continue
            if tag.name == "em" and italic and not bold:
                continue

            if tag.name == "strong" and italic:
                wrapper = soup.new_tag("em")
                for child in list(tag.contents):
                    wrapper.append(child.extract())
                tag.append(wrapper)
            elif tag.name == "em" and bold:
                wrapper = soup.new_tag("strong")
                for child in list(tag.contents):
                    wrapper.append(child.extract())
                tag.append(wrapper)
            continue

        wrapper, inner = _build_wrapper(bold, italic)
        for child in list(tag.contents):
            inner.append(child.extract())
        tag.replace_with(wrapper)


def promote_bold_first_row_to_header(soup: BeautifulSoup) -> None:
    




       

    def _meaningful_children(tag: Tag) -> list:
        return [
            child
            for child in tag.contents
            if not (isinstance(child, NavigableString) and not str(child).strip())
        ]

    def _cell_is_bold(cell: Tag) -> bool:
        children = _meaningful_children(cell)
        if len(children) != 1:
            return False
        child = children[0]
        return isinstance(child, Tag) and child.name in ("strong", "b")

    for table in soup.find_all("table"):
        if table.find("th"):
            continue

        rows = table.find_all("tr")
        if len(rows) < 2:
            continue

        header_row = rows[0]
        header_cells = header_row.find_all(["td", "th"], recursive=False)
        if not header_cells:
            continue

        if not all(_cell_is_bold(cell) for cell in header_cells):
            continue

        has_non_bold_cell = False
        for row in rows[1:]:
            for cell in row.find_all(["td", "th"], recursive=False):
                if not _cell_is_bold(cell):
                    has_non_bold_cell = True
                    break
            if has_non_bold_cell:
                break

        if not has_non_bold_cell:
            continue

        for cell in header_cells:
            cell.name = "th"


def convert_strikethrough_to_del(soup) -> None:
    




       

    for element in soup.find_all(text=True):
        if isinstance(element, NavigableString):
            if "~~" not in element:
                continue
            pattern = r'~~([^~]+?)~~'
            if not re.search(pattern, element):
                continue

            new_content = []
            last_end = 0
            for match in re.finditer(pattern, element):
                if match.start() > last_end:
                    new_content.append(element[last_end:match.start()])

                del_tag = soup.new_tag("del")
                del_tag.string = match.group(1)
                new_content.append(del_tag)
                last_end = match.end()

            if last_end < len(element):
                new_content.append(element[last_end:])

            parent = element.parent
            if not parent:
                continue
            index = parent.contents.index(element)
            element.extract()
            for i, item in enumerate(new_content):
                if isinstance(item, str):
                    parent.insert(index + i, NavigableString(item))
                else:
                    parent.insert(index + i, item)


def _clean_latex_br_tags(soup) -> None:
    







         

    katex_elements = soup.find_all(class_=re.compile(r'katex'))
    
    for katex_elem in katex_elements:

        br_tags = katex_elem.find_all('br')
        
        for br in br_tags:

            br.replace_with('')



    for tag in soup.find_all(['p', 'div', 'span', 'li', 'td', 'th']):

        if not tag.find('br', recursive=False) or '$$' not in tag.get_text():
            continue

        in_latex = False

        for child in list(tag.children):
            if isinstance(child, NavigableString):

                if str(child).count('$$') % 2 == 1:
                    in_latex = not in_latex
            elif child.name == 'br':

                if in_latex:
                    child.decompose()
            elif hasattr(child, 'get_text'):


                if child.get_text().count('$$') % 2 == 1:
                    in_latex = not in_latex


def unwrap_all_p_div_inside_li(soup, unwrap_tags=("p", "div")) -> None:
    



       

    wrappers = soup.select(",".join(f"li {t}" for t in unwrap_tags))


    wrappers.sort(key=lambda node: len(list(node.parents)), reverse=True)

    for node in wrappers:

        if isinstance(node, Tag) and node.parent is not None:
            node.unwrap()


    for li in soup.find_all("li"):
        _trim_whitespace_text_nodes(li)


def remove_empty_paragraphs(soup) -> None:
    




       
    for p in soup.find_all("p"):
        text = p.get_text(strip=True).replace("\u00a0", "").strip()

        has_meaningful_media = bool(p.find(["img", "iframe", "video", "audio", "svg"]))
        if (not text) and (not has_meaningful_media):
            p.decompose()


def _trim_whitespace_text_nodes(tag) -> None:
    

       

    while tag.contents and isinstance(tag.contents[0], NavigableString) and not str(tag.contents[0]).strip():
        tag.contents[0].extract()

    while tag.contents and isinstance(tag.contents[-1], NavigableString) and not str(tag.contents[-1]).strip():
        tag.contents[-1].extract()


def postprocess_pandoc_html_macwps(html: str) -> str:
    













       
    soup = BeautifulSoup(html, "html.parser")
    

    unwrap_all_p_div_inside_li(soup)


    _replace_del_with_s(soup)


    _fix_bold_italic_nesting(soup)
    

    _fix_pandoc_code_blocks(soup)
    


    



    _fix_task_list_math_issue(soup)
    
    return str(soup)


def _fix_bold_italic_nesting(soup) -> None:
    










       

    for strong in soup.find_all('strong'):

        children = [c for c in strong.children if c.name or (isinstance(c, NavigableString) and c.strip())]
        if len(children) == 1 and children[0].name == 'em':
            em = children[0]
            text = em.get_text()
            

            span = soup.new_tag('span', style='font-weight: bold; font-style: italic;')
            span.string = text
            

            strong.replace_with(span)
    

    for em in soup.find_all('em'):

        children = [c for c in em.children if c.name or (isinstance(c, NavigableString) and c.strip())]
        if len(children) == 1 and children[0].name == 'strong':
            strong = children[0]
            text = strong.get_text()
            

            span = soup.new_tag('span', style='font-weight: bold; font-style: italic;')
            span.string = text
            

            em.replace_with(span)


def _fix_pandoc_code_blocks(soup) -> None:
    













       

    for div in soup.find_all('div', class_='sourceCode'):

        pre = div.find('pre')
        if pre:
            code = pre.find('code')
            if code:

                code_text = code.get_text()
                

                new_pre = soup.new_tag('pre', style='white-space: pre-wrap;')
                new_code = soup.new_tag('code')
                new_code.string = code_text
                new_pre.append(new_code)
                

                div.replace_with(new_pre)
    

    for p in soup.find_all('p'):

        meaningful_contents = [
            c for c in p.contents 
            if c.name or (isinstance(c, NavigableString) and c.strip())
        ]
        

        code_tags = p.find_all('code', recursive=False)
        if len(code_tags) == 1 and len(meaningful_contents) == 1:
            code = code_tags[0]
            code_text = code.get_text()
            

            if code_text.strip().startswith('{'):


                match = re.match(r'^\{[^}]+\}\s*(.+)$', code_text, re.DOTALL)
                if match:
                    actual_code = match.group(1)
                    



                    actual_code = re.sub(r'    +', '\n    ', actual_code)
                    

                    pre = soup.new_tag('pre', style='white-space: pre-wrap;')
                    new_code = soup.new_tag('code')
                    new_code.string = actual_code
                    pre.append(new_code)
                    

                    p.replace_with(pre)


def _clean_pandoc_attributes(soup) -> None:
    

















       

    allowed_attrs = {
        'a': ['href', 'id'],
        'img': ['src', 'alt'],
        'td': ['colspan', 'rowspan'],
        'th': ['colspan', 'rowspan'],
        'ol': ['type', 'start'],
        'ul': ['type'],

        'h1': ['id'], 'h2': ['id'], 'h3': ['id'], 
        'h4': ['id'], 'h5': ['id'], 'h6': ['id'],
    }
    
    for tag in soup.find_all(True):

        allowed = allowed_attrs.get(tag.name, ['id'])
        

        attrs_to_del = [attr for attr in list(tag.attrs.keys()) if attr not in allowed]
        

        for attr in attrs_to_del:
            del tag.attrs[attr]


def _replace_del_with_s(soup) -> None:
    


       
    for tag in soup.find_all("del"):
        tag.name = "s"


def _clean_pandoc_fenced_divs(soup) -> None:
    







       

    for text_node in soup.find_all(text=True):
        if isinstance(text_node, NavigableString):
            text = str(text_node)

            if re.match(r'^:+\s*\{[^}]*\}', text.strip()):

                text_node.extract()
            elif text.strip().startswith(':::'):

                text_node.extract()


def clean_html_for_wps(html: str) -> str:
    

















       
    soup = BeautifulSoup(html, "html.parser")
    

    _protect_task_list_brackets(soup)
    

    allowed_attrs = {
        'a': ['href', 'id', 'title'],
        'img': ['src', 'alt', 'title'],
        'td': ['colspan', 'rowspan'],
        'th': ['colspan', 'rowspan'],
        'ol': ['type', 'start'],
        'ul': ['type'],

    }
    
    for tag in soup.find_all(True):

        allowed = allowed_attrs.get(tag.name, ['id', 'title'])
        

        attrs_to_del = [attr for attr in list(tag.attrs.keys()) if attr not in allowed]
        

        for attr in attrs_to_del:
            del tag.attrs[attr]
    
    return str(soup)


def _remove_col_tags(soup) -> None:
    


       
    for col in soup.find_all("col"):
        col.decompose()


def protect_brackets(html: str) -> str:
    














       
    soup = BeautifulSoup(html, "html.parser")
    _remove_col_tags(soup)
    _protect_task_list_brackets(soup)
    return str(soup)


def _protect_task_list_brackets(soup) -> None:
    










       

    for text_node in soup.find_all(text=True):
        if isinstance(text_node, NavigableString):
            text = str(text_node)

            if '[x]' in text or '[ ]' in text or '[X]' in text:

                text = text.replace('[x]', '{{TASK_CHECKED}}')
                text = text.replace('[ ]', '{{TASK_UNCHECKED}}')
                text_node.replace_with(text)


def _restore_task_list_brackets(soup) -> None:
    

       

    for checkbox in soup.find_all('input'):

        is_checkbox = checkbox.get('type') == 'checkbox'
        if is_checkbox:

            is_checked = checkbox.has_attr('checked')
            replacement_text = "[x] " if is_checked else "[ ] "
            

            checkbox.replace_with(NavigableString(replacement_text))


def _fix_task_list_math_issue(soup) -> None:
    







       

    _restore_task_list_brackets(soup)
