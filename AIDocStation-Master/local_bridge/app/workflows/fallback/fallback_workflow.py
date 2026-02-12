# -*- coding: utf-8 -*-
"""
@File    : local_bridge/app/workflows/fallback/fallback_workflow.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from ..base import BaseWorkflow
from .output_executor import OutputExecutor
from local_bridge.utils.clipboard import (
    get_clipboard_text, get_clipboard_html, is_clipboard_empty,
    read_markdown_files_from_clipboard
)
from local_bridge.utils.html_analyzer import is_plain_html_fragment
from local_bridge.utils.markdown_utils import merge_markdown_contents
from local_bridge.service.spreadsheet.parser import parse_markdown_table
from local_bridge.utils.fs import generate_output_path
from local_bridge.core.errors import ClipboardError, PandocError
from local_bridge.i18n import t


class FallbackWorkflow(BaseWorkflow):
                                    
    
    def __init__(self):
        super().__init__()
        self.output_executor = OutputExecutor(self.notification_manager)
    
    def execute(self) -> None:
        






           
        content_type: str | None = None
        try:


            no_app_action = self.config.get("no_app_action", "notify")
            self._log(f"No app detected, executing action: {no_app_action}")
            
            if no_app_action == "notify":
                self._notify_info(t("workflow.fallback.no_app_detected"))
                return
            elif no_app_action == "none":
                 return
            

            content_type = self._detect_content_type()
            


            self._notify_info(t("workflow.document.processing"))
            
            if content_type == "table":
                self._handle_table(no_app_action)
            else:
                self._handle_document(no_app_action, content_type)
        
        except ClipboardError as e:
            self._log(f"Clipboard error: {e}")
            msg = str(e)
            if "为空" in msg:
                self._notify_error(t("workflow.clipboard.empty"))
            else:
                self._notify_error(t("workflow.clipboard.read_failed"))
        except PandocError as e:
            self._log(f"Pandoc error: {e}")
            if content_type == "html":
                self._notify_error(t("workflow.html.convert_failed_generic"))
            else:
                self._notify_error(t("workflow.markdown.convert_failed"))
        except Exception as e:
            self._log(f"Fallback workflow failed: {e}")
            import traceback
            traceback.print_exc()
            self._notify_error(t("workflow.generic.failure"))
    
    def _detect_content_type(self) -> str:
        




           
        if is_clipboard_empty():
            raise ClipboardError("剪贴板为�?)
        

        markdown_text = get_clipboard_text()
        found, files_data, _ = read_markdown_files_from_clipboard()
        if found:
            markdown_text = merge_markdown_contents(files_data)
        table_data = parse_markdown_table(markdown_text)
        if table_data:
            return "table"
        

        try:
            html = get_clipboard_html(self.config)
            if not is_plain_html_fragment(html):
                return "html"
        except ClipboardError:
            pass
        

        return "markdown"
    
    def _handle_table(self, action: str):
                    
        markdown_text = get_clipboard_text()
        found, files_data, _ = read_markdown_files_from_clipboard()
        if found:
            markdown_text = merge_markdown_contents(files_data)
        table_data = parse_markdown_table(markdown_text)
        

        output_path = generate_output_path(
            keep_file=True,
            save_dir=self.config.get("save_dir", ""),
            table_data=table_data,
        )
        

        keep_format = self.config.get("excel_keep_format", self.config.get("keep_format", True))
        success = self.output_executor.execute_xlsx(
            action=action,
            table_data=table_data,
            output_path=output_path,
            keep_format=keep_format
        )
        
        if not success:
            self._log(f"XLSX output failed with action: {action}")
    
    def _handle_document(self, action: str, content_type: str):
                                     

        if content_type == "html":
            html = get_clipboard_html(self.config)
            html = self.html_preprocessor.process(html, self.config)
            docx_bytes = self.doc_generator.convert_html_to_docx_bytes(
                html, self.config
            )
            from_html = True
            md_text = ""
        else:

            content = get_clipboard_text()
            found, files_data, _ = read_markdown_files_from_clipboard()
            if found:
                content = merge_markdown_contents(files_data)

            content = self.markdown_preprocessor.process(content, self.config)
            docx_bytes = self.doc_generator.convert_markdown_to_docx_bytes(
                content, self.config
            )
            from_html = False
            md_text = content
        

        output_path = generate_output_path(
            keep_file=True,
            save_dir=self.config.get("save_dir", ""),
            md_text=md_text,
            html_text=html if from_html else "",
        )
        

        success = self.output_executor.execute_docx(
            action=action,
            docx_bytes=docx_bytes,
            output_path=output_path,
            from_md_file=False,
            from_html=from_html,
            config=self.config
        )
        
        if not success:
            self._log(f"DOCX output failed with action: {action}")
    
    def _read_markdown_content(self) -> str:
        




           

        if not is_clipboard_empty():
            return get_clipboard_text()
        

        found, files_data, _ = read_markdown_files_from_clipboard()
        if found:
            return merge_markdown_contents(files_data)
        
        raise ClipboardError("剪贴板为空或无有效内�?)
