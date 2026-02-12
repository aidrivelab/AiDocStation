# -*- coding: utf-8 -*-
"""
@File    : local_bridge/app/workflows/word/word_base.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from local_bridge.app.workflows.base import BaseWorkflow
from local_bridge.core.errors import ClipboardError, PandocError
from local_bridge.i18n import t
from local_bridge.utils.clipboard import (
    get_clipboard_html,
    get_clipboard_text,
    is_clipboard_empty,
    read_markdown_files_from_clipboard,
)
from local_bridge.utils.fs import generate_output_path
from local_bridge.utils.html_analyzer import is_plain_html_fragment
from local_bridge.utils.markdown_utils import merge_markdown_contents
from local_bridge.core.state import app_state
from local_bridge.api.supabase_client import supabase_client


class WordBaseWorkflow(BaseWorkflow, ABC):
                             

    @property
    @abstractmethod
    def app_name(self) -> str: ...

    @property
    @abstractmethod
    def placer(self): ...

    def execute(self) -> None:
        content_type: str | None = None
        from_md_file = False
        md_file_count = 0

        try:
            content_type, content, from_md_file, md_file_count = self._read_clipboard()
            self._log(f"Clipboard content type: {content_type}")

            if content_type == "markdown":

                self._log(f"DEBUG config.remove_horizontal_rules = {self.config.get('remove_horizontal_rules', 'NOT_SET')}")
                self._log(f"DEBUG config.clean_heading_number = {self.config.get('clean_heading_number', 'NOT_SET')}")
                content = self.markdown_preprocessor.process(content, self.config)
            elif content_type == "html":

                content = self.html_preprocessor.process(content, self.config)


            self._notify_info(t("workflow.document.processing"))

            if content_type == "html":
                docx_bytes = self.doc_generator.convert_html_to_docx_bytes(
                    content, self.config
                )
            else:

                if "```mermaid" in content or "```{.mermaid}" in content:
                    self._log("Mermaid code detected, processing as part of document...")
                    
                docx_bytes = self.doc_generator.convert_markdown_to_docx_bytes(
                    content, self.config
                )


            image_scale_str = self.config.get("image_scale_rule", "100%")
            try:
                self.config["image_scale"] = int(image_scale_str.replace("%", ""))
            except:
                self.config["image_scale"] = 100
            
            result = self.placer.place(docx_bytes, self.config)
            

            if result.success and app_state.store:
                app_state.store.increment_stat("word_paste_count")
                

                char_count = len(content)
                app_state.store.increment_stat("word_char_count", char_count)
                

                import re
                md_imgs = len(re.findall(r'!\[.*?\]\(.*?\)', content))
                html_imgs = len(re.findall(r'<img\s+[^>]*src=', content, re.IGNORECASE))

                mermaid_md = len(re.findall(r'```\s*(?:mermaid|\{\s*\.mermaid\s*\})', content, re.IGNORECASE))
                mermaid_html = len(re.findall(r'<(?:pre|div|code)[^>]*class=["\'][^"\']*mermaid', content, re.IGNORECASE))
                mermaid_total = mermaid_md + mermaid_html
                
                img_total = md_imgs + html_imgs + mermaid_total
                self._log(f"[Stats] Detection: md_imgs={md_imgs}, html_imgs={html_imgs}, mermaid={mermaid_total} (md:{mermaid_md}, html:{mermaid_html}), total={img_total}")
                
                if img_total > 0:
                    app_state.store.increment_stat("image_paste_count", img_total)
                

                if "|" in content and "---" in content:

                     table_count = content.count("|---") or 1
                     app_state.store.increment_stat("table_paste_count", table_count)


                if app_state.store:
                    supabase_client.sync_stats(app_state.store.get("stats", {}))

            if result.success:
                if result.method:
                    self._log(f"Insert method: {result.method}")

                if from_md_file:
                    if md_file_count > 1:
                        msg = t(
                            "workflow.md_file.insert_success_multi",
                            count=md_file_count,
                            app=self.app_name,
                        )
                    else:
                        msg = t("workflow.md_file.insert_success", app=self.app_name)
                elif content_type == "html":
                    msg = t("workflow.html.insert_success", app=self.app_name)
                else:
                    msg = t("workflow.word.insert_success", app=self.app_name)

                self._notify_success(msg)
            else:
                self._notify_error(result.error or t("workflow.generic.failure"))

            if result.success and self.config.get("keep_file", False):
                self._save_docx(docx_bytes)

        except ClipboardError as e:
            self._log(f"Clipboard error: {e}")
            self._notify_error(t("workflow.clipboard.read_failed"))
        except PandocError as e:
            self._log(f"Pandoc error: {e}")
            if content_type == "html":
                self._notify_error(t("workflow.html.convert_failed_generic"))
            else:
                self._notify_error(t("workflow.markdown.convert_failed"))
        except Exception as e:
            self._log(f"{self.app_name} workflow failed: {e}")
            import traceback

            traceback.print_exc()
            self._notify_error(t("workflow.generic.failure"))

    def _read_clipboard(self) -> tuple[str, str, bool, int]:
        

           
        try:
            html = get_clipboard_html(self.config)
            self._log(f"HTML analysis: checking if plain fragment...")
            if not is_plain_html_fragment(html):
                self._log("HTML analysis: Rich HTML content detected, using HTML workflow")
                return ("html", html, False, 0)
            else:
                self._log("HTML analysis: Only inline wrappers, treating as plain text.")
        except ClipboardError:
            pass

        found, files_data, total_files = read_markdown_files_from_clipboard()
        self._log(f"Found {len(files_data) if files_data else 0} Markdown files from {total_files} total files")
        self._log(f"Clipboard files check: {found}")
        
        if found:
            merged = merge_markdown_contents(files_data)
            return ("markdown", merged, True, len(files_data))
        
        if not is_clipboard_empty():
            return ("markdown", get_clipboard_text(), False, 0)

        raise ClipboardError("剪贴板为空或无有效内�?)

    def _save_docx(self, docx_bytes: bytes) -> None:
        try:
            output_path = generate_output_path(
                keep_file=True,
                save_dir=self.config.get("save_dir", ""),
                md_text="",
            )
            with open(output_path, "wb") as f:
                f.write(docx_bytes)
            self._log(f"Saved DOCX to: {output_path}")
        except Exception as e:
            self._log(f"Failed to save DOCX: {e}")
