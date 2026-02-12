# -*- coding: utf-8 -*-
"""
@File    : local_bridge/app/workflows/extensible/md_workflow.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from .extensible_base import ExtensibleWorkflow
from ....core.errors import ClipboardError
from ....utils.clipboard import (
    get_clipboard_html,
    get_clipboard_text,
    is_clipboard_empty,
)
from ....utils.html_analyzer import is_plain_html_fragment
from ....i18n import t
from ....service.paste import PlainTextPastePlacer


class MdWorkflow(ExtensibleWorkflow):
    





       

    def __init__(self):
        super().__init__()
        self.placer = PlainTextPastePlacer()

    @property
    def workflow_key(self) -> str:
        return "md"
    
    def execute(self) -> None:
                               
        try:

            content_type, content = self._read_clipboard()
            self._log(f"MD workflow: content_type={content_type}")
            effective_config = self._build_md_config()
            

            if content_type == "html":
                content = self.html_preprocessor.process(content, effective_config)
                md_text = self.doc_generator.convert_html_to_markdown_text(
                    content, effective_config
                )
            else:
                md_text = content
            

            md_text = self.markdown_preprocessor.process(md_text, effective_config)


            result = self.placer.place(
                content=md_text,
                config=effective_config,
            )

            if result.success:
                self._notify_success(t("workflow.md.paste_success"))
            else:
                self._notify_error(result.error or t("workflow.generic.failure"))

        except ClipboardError as e:
            self._log(f"Clipboard error: {e}")
            self._notify_error(t("workflow.clipboard.read_failed"))
        except Exception as e:
            self._log(f"MD workflow failed: {e}")
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

    def _build_md_config(self) -> dict:
                                                                                         
        config = dict(self.config)
        html_formatting = dict(config.get("html_formatting", {}) or {})

        md_ext = (config.get("extensible_workflows") or {}).get("md", {})
        md_html_formatting = md_ext.get("html_formatting")
        if isinstance(md_html_formatting, dict):
            html_formatting.update(md_html_formatting)

        config["html_formatting"] = html_formatting
        return config
