# -*- coding: utf-8 -*-
"""
@File    : local_bridge/app/workflows/extensible/latex_workflow.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from .extensible_base import ExtensibleWorkflow
from ....core.errors import ClipboardError, PandocError
from ....utils.clipboard import (
    get_clipboard_html,
    get_clipboard_text,
    is_clipboard_empty,
)
from ....utils.html_analyzer import is_plain_html_fragment
from ....i18n import t
from ....service.paste import PlainTextPastePlacer


class LatexWorkflow(ExtensibleWorkflow):
    





       

    def __init__(self):
        super().__init__()
        self.placer = PlainTextPastePlacer()

    @property
    def workflow_key(self) -> str:
        return "latex"
    
    def execute(self) -> None:
                            
        try:

            content_type, content = self._read_clipboard()
            self._log(f"LaTeX workflow: content_type={content_type}")
            

            if content_type == "html":
                content = self.html_preprocessor.process(content, self.config)
                md_text = self.doc_generator.convert_html_to_markdown_text(
                    content, self.config
                )
            else:
                md_text = content
            

            md_text = self.markdown_preprocessor.process(md_text, self.config)
            

            latex_text = self.doc_generator.convert_markdown_to_latex_text(
                md_text, self.config
            )


            result = self.placer.place(
                content=latex_text,
                config=self.config,
            )

            if result.success:
                self._notify_success(t("workflow.latex.paste_success"))
            else:
                self._notify_error(result.error or t("workflow.generic.failure"))

        except ClipboardError as e:
            self._log(f"Clipboard error: {e}")
            self._notify_error(t("workflow.clipboard.read_failed"))
        except PandocError as e:
            self._log(f"Pandoc error: {e}")
            self._notify_error(t("workflow.html.convert_failed_generic"))
        except Exception as e:
            self._log(f"LaTeX workflow failed: {e}")
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
