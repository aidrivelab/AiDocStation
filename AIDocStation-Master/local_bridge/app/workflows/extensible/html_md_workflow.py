# -*- coding: utf-8 -*-
"""
@File    : local_bridge/app/workflows/extensible/html_md_workflow.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import os
import subprocess
import re

from .extensible_base import ExtensibleWorkflow
from ....core.errors import ClipboardError, PandocError
from ....utils.clipboard import (
    get_clipboard_html,
    get_clipboard_text,
    is_clipboard_empty,
)
from ....utils.html_analyzer import is_plain_html_fragment
from ....config.paths import resource_path
from ....i18n import t
from ....service.paste import RichTextPastePlacer

class HtmlWorkflow(ExtensibleWorkflow):
    






       

    def __init__(self):
        super().__init__()
        self.placer = RichTextPastePlacer()

    @property
    def workflow_key(self) -> str:
        return "html"
    
    def execute(self) -> None:
                              
        try:

            content_type, content = self._read_clipboard()
            self._log(f"HTML+MD workflow: content_type={content_type}")
            

            if content_type == "html":
                content = self.html_preprocessor.process(content, self.config)
                md_text = self.doc_generator.convert_html_to_markdown_text(
                    content, self.config
                )
            else:
                md_text = content
            

            md_text = self.markdown_preprocessor.process(md_text, self.config)

            keep_formula = self.workflow_config.get("keep_formula_latex", True)
            html_text = self.doc_generator.convert_markdown_to_html_text(
                md_text, 
                {
                    **self.config,
                    "Keep_original_formula": keep_formula, 
                }
            )

            result = self.placer.place(
                content=md_text,
                config=self.config,
                html=html_text,
            )

            if result.success:
                self._notify_success(t("workflow.html_md.paste_success"))
            else:
                self._notify_error(result.error or t("workflow.generic.failure"))

        except ClipboardError as e:
            self._log(f"Clipboard error: {e}")
            self._notify_error(t("workflow.clipboard.read_failed"))
        except PandocError as e:
            self._log(f"Pandoc error: {e}")
            self._notify_error(t("workflow.html.convert_failed_generic"))
        except Exception as e:
            self._log(f"HTML+MD workflow failed: {e}")
            import traceback
            traceback.print_exc()
            self._notify_error(t("workflow.generic.failure"))
    
    def _read_clipboard(self) -> tuple[str, str]:
                                 

        try:
            html = get_clipboard_html(self.config)
            if not is_plain_html_fragment(html):
                return ("html", html)
        except ClipboardError:
            pass
        

        if not is_clipboard_empty():
            return ("markdown", get_clipboard_text())
        
        raise ClipboardError("剪贴板为空或无有效内�?)
    
    def _strip_html_wrapper(self, html: str) -> str:
                                                          

        body_match = re.search(r"<body[^>]*>(.*?)</body>", html, re.DOTALL | re.IGNORECASE)
        if body_match:
            return body_match.group(1).strip()
        

        html = re.sub(r"<!DOCTYPE[^>]*>", "", html, flags=re.IGNORECASE)
        html = re.sub(r"<html[^>]*>|</html>", "", html, flags=re.IGNORECASE)
        html = re.sub(r"<head[^>]*>.*?</head>", "", html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r"<body[^>]*>|</body>", "", html, flags=re.IGNORECASE)
        
        return html.strip()
