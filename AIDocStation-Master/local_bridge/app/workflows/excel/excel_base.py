# -*- coding: utf-8 -*-
"""
@File    : local_bridge/app/workflows/excel/excel_base.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from local_bridge.app.workflows.base import BaseWorkflow
from local_bridge.core.errors import ClipboardError
from local_bridge.i18n import t
from local_bridge.service.spreadsheet import SpreadsheetGenerator
from local_bridge.service.spreadsheet.parser import parse_markdown_table
from local_bridge.utils.clipboard import get_clipboard_text, is_clipboard_empty
from local_bridge.utils.fs import generate_output_path
from local_bridge.utils.clipboard import read_markdown_files_from_clipboard
from local_bridge.utils.markdown_utils import merge_markdown_contents
from local_bridge.core.state import app_state
from local_bridge.api.supabase_client import supabase_client


class ExcelBaseWorkflow(BaseWorkflow, ABC):
                              

    @property
    @abstractmethod
    def app_name(self) -> str: ...

    @property
    @abstractmethod
    def placer(self): ...

    def execute(self) -> None:
        if not self.config.get("enable_excel", True):
            self._log(f"{self.app_name} workflow is disabled in config.")
            self._notify_error(t("tray.status.excel_insert_off"))
            return

        try:
            table_data = self._read_clipboard_table()
            self._log(f"Parsed table with {len(table_data)} rows")

            result = self.placer.place(table_data, self.config)
            

            if result.success and app_state.store:
                app_state.store.increment_stat("excel_paste_count")

                app_state.store.increment_stat("table_paste_count")
                

                if app_state.store:
                    supabase_client.sync_stats(app_state.store.get("stats", {}))

            if result.success:
                if result.method:
                    self._log(f"Insert method: {result.method}")
                self._notify_success(
                    t(
                        "workflow.table.insert_success",
                        rows=len(table_data),
                        app=self.app_name,
                    )
                )
            else:
                self._notify_error(result.error or t("workflow.generic.failure"))

            if result.success and self.config.get("keep_file", False):
                self._save_xlsx(table_data)

        except ClipboardError as e:
            self._log(f"Clipboard error: {e}")
            self._notify_error(t("workflow.table.invalid_with_app", app=self.app_name))
        except Exception as e:
            self._log(f"{self.app_name} workflow failed: {e}")
            import traceback

            traceback.print_exc()
            self._notify_error(t("workflow.generic.failure"))

    def _read_clipboard_table(self) -> list:
        if is_clipboard_empty():
            raise ClipboardError("剪贴板为�?)
        markdown_text = get_clipboard_text()
        found, files_data, _ = read_markdown_files_from_clipboard()
        if found:
            markdown_text = merge_markdown_contents(files_data)
        table_data = parse_markdown_table(markdown_text)

        if not table_data:
            raise ClipboardError("剪贴板中无有�?Markdown 表格")

        return table_data

    def _save_xlsx(self, table_data: list) -> None:
        try:
            xlsx_bytes = SpreadsheetGenerator.generate_xlsx_bytes(
                table_data,
                keep_format=self.config.get(
                    "excel_keep_format", self.config.get("keep_format", True)
                ),
            )

            output_path = generate_output_path(
                keep_file=True,
                save_dir=self.config.get("save_dir", ""),
                table_data=table_data,
            )
            with open(output_path, "wb") as f:
                f.write(xlsx_bytes)
            self._log(f"Saved XLSX to: {output_path}")
        except Exception as e:
            self._log(f"Failed to save XLSX: {e}")
