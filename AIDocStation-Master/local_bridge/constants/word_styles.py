# -*- coding: utf-8 -*-
"""
@File    : local_bridge/constants/word_styles.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""




STYLE_CN_TO_EN = {

    "正文": "Normal",
    "正文文本": "Body Text",
    "正文文本 2": "Body Text 2",
    "正文文本 3": "Body Text 3",
    "正文文本缩进": "Body Text Indent",
    "正文文本缩进 2": "Body Text Indent 2",
    "正文文本缩进 3": "Body Text Indent 3",
    "正文文本首行缩进": "Body Text First Indent",
    "正文首行缩进": "Body Text First Indent",
    "正文缩进": "Normal Indent",
    "正文文本缩进 1": "Body Text Indent",
    "正文缩进 1": "Normal Indent",
    

    "题注": "Caption",
    "标题": "Title",
    "副标�?: "Subtitle",
    

    "引文": "Quote",
    "强烈引用": "Intense Quote",
    

    "标题1": "Heading 1",
    "标题2": "Heading 2",
    "标题3": "Heading 3",
    "标题4": "Heading 4",
    "标题5": "Heading 5",
    "标题6": "Heading 6",
    "标题7": "Heading 7",
    "标题8": "Heading 8",
    "标题9": "Heading 9",
    

    "列表": "List",
    "列表2": "List 2",
    "列表3": "List 3",
    "列表项目符号": "List Bullet",
    "列表编号": "List Number",
    "列表段落": "List Paragraph",
    

    "页眉": "Header",
    "页脚": "Footer",
}


def get_english_style_name(style_name: str) -> str:
    







       
    return STYLE_CN_TO_EN.get(style_name, style_name)


def apply_style_safe(paragraph, style_name: str) -> bool:
    








       
    if not style_name:
        return False
    

    english_name = get_english_style_name(style_name)
    

    try:
        paragraph.style = english_name
        return True
    except KeyError:
        pass
    

    if english_name != style_name:
        try:
            paragraph.style = style_name
            return True
        except KeyError:
            pass
    
    return False
