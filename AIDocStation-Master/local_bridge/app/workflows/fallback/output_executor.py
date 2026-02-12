# -*- coding: utf-8 -*-
"""
@File    : local_bridge/app/workflows/fallback/output_executor.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import os
from typing import List, Tuple, Optional

from local_bridge.utils.clipboard import copy_files_to_clipboard
from local_bridge.utils.logging import log
from local_bridge.service.awakener import AppLauncher
from local_bridge.service.spreadsheet.generator import SpreadsheetGenerator
from local_bridge.utils.system_detect import is_windows
from local_bridge.service.document.win32.word_inserter import WordInserter
from local_bridge.utils.fs import generate_unique_path
from local_bridge.i18n import t


class OutputExecutor:
    




       
    
    def __init__(self, notification_manager):
        




           
        self.notification_manager = notification_manager
    
    def execute_docx(
        self,
        action: str,
        docx_bytes: bytes,
        output_path: str,
        *,
        from_md_file: bool = False,
        from_html: bool = False,
        config: dict = None
    ) -> bool:
        











           
        try:

            with open(output_path, "wb") as f:
                f.write(docx_bytes)
            log(f"Generated DOCX: {output_path}")
            

            if action == "open":
                return self._docx_open(output_path, from_md_file, from_html, config=config)
            elif action == "save":
                return self._docx_save(output_path, from_md_file)
            elif action == "clipboard":
                return self._docx_clipboard(output_path, from_md_file)
            else:
                log(f"Unknown DOCX action: {action}")
                return False
                
        except Exception as e:
            log(f"DOCX output failed: {e}")

            if action == "clipboard":

                self.notification_manager.notify(
                    "AIDocStation", t("workflow.action.clipboard_failed"), ok=False
                )
            elif action == "save":

                self.notification_manager.notify(
                    "AIDocStation", t("workflow.document.save_failed"), ok=False
                )
            elif from_html:

                self.notification_manager.notify(
                    "AIDocStation", t("workflow.html.generate_failed"), ok=False
                )
            else:

                self.notification_manager.notify(
                    "AIDocStation", t("workflow.document.generate_failed"), ok=False
                )
            return False
    
    def execute_docx_batch(
        self,
        action: str,
        items: List[Tuple[bytes, str, str]],
        *,
        from_md_file: bool = False,
        from_html: bool = False,
        config: dict = None,
        pre_failures: Optional[List[Tuple[str, str]]] = None,
    ) -> dict:
        











           
        if not items:
            return {"success_paths": [], "failures": list(pre_failures or [])}


        seen_paths: set[str] = set()
        normalized_items: List[Tuple[bytes, str, str]] = []
        for docx_bytes, output_path, source_filename in items:
            unique_path = output_path

            if unique_path in seen_paths:
                base_dir = os.path.dirname(unique_path)
                stem, ext = os.path.splitext(os.path.basename(unique_path))
                idx = 1
                candidate = unique_path
                while candidate in seen_paths or os.path.exists(candidate):
                    candidate = os.path.join(base_dir, f"{stem}_batch{idx}{ext}")
                    idx += 1
                unique_path = candidate
            else:
                unique_path = generate_unique_path(unique_path)
                while unique_path in seen_paths or os.path.exists(unique_path):
                    unique_path = generate_unique_path(unique_path)

            seen_paths.add(unique_path)
            normalized_items.append((docx_bytes, unique_path, source_filename))

        success_paths: List[str] = []
        failures: List[Tuple[str, str]] = list(pre_failures or [])

        for docx_bytes, output_path, source_filename in normalized_items:
            try:
                with open(output_path, "wb") as f:
                    f.write(docx_bytes)
                log(f"Generated DOCX (batch): {output_path}")

                if action == "open":
                    ok = self._docx_open(
                        output_path, from_md_file, from_html, config=config, notify_success=False
                    )
                elif action == "save":
                    ok = self._docx_save(output_path, from_md_file, notify_success=False)
                elif action == "clipboard":
                    ok = True
                else:
                    log(f"Unknown DOCX action in batch: {action}")
                    ok = False

                if ok:
                    success_paths.append(output_path)
                else:
                    failures.append((source_filename, f"action_failed:{action}"))
            except Exception as e:
                log(f"DOCX batch item failed ({source_filename}): {e}")

                if action == "clipboard":
                    self.notification_manager.notify(
                        "AIDocStation", t("workflow.action.clipboard_failed"), ok=False
                    )
                elif action == "save":
                    self.notification_manager.notify(
                        "AIDocStation", t("workflow.document.save_failed"), ok=False
                    )
                elif from_html:
                    self.notification_manager.notify(
                        "AIDocStation", t("workflow.html.generate_failed"), ok=False
                    )
                else:
                    self.notification_manager.notify(
                        "AIDocStation", t("workflow.document.generate_failed"), ok=False
                    )
                failures.append((source_filename, str(e)))


        if action == "clipboard" and success_paths:
            try:
                copy_files_to_clipboard(success_paths)
            except Exception as e:
                log(f"DOCX batch clipboard failed: {e}")
                self.notification_manager.notify(
                    "AIDocStation", t("workflow.action.clipboard_failed"), ok=False
                )
                failures.append(("_batch_clipboard", str(e)))
                return {"success_paths": success_paths, "failures": failures}


        total_attempted = len(items) + len(pre_failures or [])
        if total_attempted > 1 and success_paths:
            action_name = (
                t(f"action.{action}")
                if action in ("open", "save", "clipboard", "none")
                else action
            )
            msg = t("workflow.md_file.batch_success", count=len(success_paths))
            msg += "\n" + t("workflow.md_file.batch_action_line", action=action_name)

            failed_items = [
                name
                for name, _ in failures
                if name and not name.startswith("_batch_")
            ]
            if failed_items:
                msg += "\n" + t(
                    "workflow.md_file.batch_failure_line",
                    failed_count=len(failed_items),
                    failed_files=", ".join(failed_items),
                )

            self.notification_manager.notify("AIDocStation", msg, ok=True)

        return {"success_paths": success_paths, "failures": failures}

    def execute_xlsx(
        self,
        action: str,
        table_data: List[List[str]],
        output_path: str,
        keep_format: bool = True
    ) -> bool:
        










           
        try:
            if action == "open":
                return self._xlsx_open(table_data, output_path, keep_format)
            elif action == "save":
                return self._xlsx_save(table_data, output_path, keep_format)
            elif action == "clipboard":
                return self._xlsx_clipboard(table_data, output_path, keep_format)
            else:
                log(f"Unknown XLSX action: {action}")
                return False
                
        except Exception as e:
            log(f"XLSX output failed: {e}")
            if action == "clipboard":
                self.notification_manager.notify(
                    "AIDocStation", t("workflow.action.clipboard_failed"), ok=False
                )
            else:
                self.notification_manager.notify(
                    "AIDocStation", t("workflow.table.export_failed"), ok=False
                )
            return False
    

    
    def _docx_open(
        self,
        output_path: str,
        from_md_file: bool,
        from_html: bool,
        *,
        config: dict = None,
        notify_success: bool = True,
    ) -> bool:
                        

        if is_windows() and config:
            try:

                current_dir = os.path.dirname(os.path.abspath(__file__))

                bridge_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
                template_path = os.path.join(bridge_root, "local_bridge", "pandoc", "Reference-document.docx")
                

                body_style = config.get("body_style", "正文")
                table_text_style = config.get("table_text_style", "正文")
                image_style = config.get("image_style", "正文")
                image_scale = config.get("image_scale", 100)
                table_line_height_rule = config.get("table_line_height_rule", "1.0")
                
                log(f"[Output] Attempting Single-Step Render (Professional Mode)...")
                inserter = WordInserter()


                success = inserter.open_and_beautify(
                    docx_path=output_path,
                    body_style=body_style,
                    table_text_style=table_text_style,
                    image_style=image_style,
                    image_scale=image_scale,
                    table_line_height_rule=table_line_height_rule
                )
                
                if success:
                    log(f"[Output] Option 2 succeeded via WordInserter.")
                    if notify_success:
                        self._notify_generated(output_path, from_html, from_md_file)
                    return True
                else:
                    log(f"[Output] Option 2 failed, falling back to default open.")
            except Exception as e:
                log(f"[Output] Option 2 error: {e}, falling back.")


        if AppLauncher.awaken_and_open_document(output_path):
            if notify_success:
                self._notify_generated(output_path, from_html, from_md_file)
            return True
        else:
            self.notification_manager.notify(
                "AIDocStation",
                t("workflow.document.open_failed", path=output_path),
                ok=False
            )
            return False
            
    def _notify_generated(self, output_path: str, from_html: bool, from_md_file: bool):
                          
        if from_html:
            msg = t("workflow.html.generated_and_opened", path=output_path)
        elif from_md_file:
            msg = t("workflow.md_file.generated_and_opened", path=output_path)
        else:
            msg = t("workflow.document.generated_and_opened", path=output_path)
        self.notification_manager.notify("AIDocStation", msg, ok=True)
    
    def _docx_save(
        self,
        output_path: str,
        from_md_file: bool,
        *,
        notify_success: bool = True,
    ) -> bool:
                                   
        if notify_success:
            if from_md_file:
                msg = t("workflow.md_file.saved", path=output_path)
            else:
                msg = t("workflow.action.saved", path=output_path)
            self.notification_manager.notify("AIDocStation", msg, ok=True)
        return True
    
    def _docx_clipboard(self, output_path: str, from_md_file: bool) -> bool:
                            
        copy_files_to_clipboard([output_path])
        if from_md_file:
            msg = t("workflow.md_file.clipboard_copied")
        else:
            msg = t("workflow.action.clipboard_copied")
        self.notification_manager.notify("AIDocStation", msg, ok=True)
        return True
    

    
    def _xlsx_open(self, table_data: List[List[str]], output_path: str, keep_format: bool) -> bool:
                           
        try:
            xlsx_bytes = SpreadsheetGenerator.generate_xlsx_bytes(table_data, keep_format)
            if not xlsx_bytes:
                raise Exception("Generated XLSX bytes are empty")
            with open(output_path, "wb") as f:
                f.write(xlsx_bytes)
            log(f"Successfully generated spreadsheet: {output_path}")
            if AppLauncher.awaken_and_open_spreadsheet(output_path):
                self.notification_manager.notify(
                    "AIDocStation",
                    t("workflow.table.export_success", rows=len(table_data), path=output_path),
                    ok=True
                )
                return True
            else:
                self.notification_manager.notify(
                    "AIDocStation",
                    t("workflow.table.export_open_failed", path=output_path),
                    ok=False
                )
                return False
        except Exception as e:
            log(f"Failed to generate spreadsheet: {e}")
            self.notification_manager.notify(
                "AIDocStation",
                t("workflow.table.export_failed"),
                ok=False
            )
            return False
    
    def _xlsx_save(self, table_data: List[List[str]], output_path: str, keep_format: bool) -> bool:
                             
        try:
            xlsx_bytes = SpreadsheetGenerator.generate_xlsx_bytes(table_data, keep_format)
            if not xlsx_bytes:
                raise Exception("Generated XLSX bytes are empty")
            with open(output_path, "wb") as f:
                f.write(xlsx_bytes)
            log(f"Successfully generated spreadsheet: {output_path}")
            self.notification_manager.notify(
                "AIDocStation",
                t("workflow.action.saved", path=output_path),
                ok=True
            )
            return True
        except Exception as e:
            log(f"Failed to generate spreadsheet: {e}")
            self.notification_manager.notify(
                "AIDocStation",
                t("workflow.table.export_failed"),
                ok=False
            )
            return False
    
    def _xlsx_clipboard(self, table_data: List[List[str]], output_path: str, keep_format: bool) -> bool:
                               
        try:
            xlsx_bytes = SpreadsheetGenerator.generate_xlsx_bytes(table_data, keep_format)
            if not xlsx_bytes:
                raise Exception("Generated XLSX bytes are empty")
            with open(output_path, "wb") as f:
                f.write(xlsx_bytes)
            log(f"Successfully generated spreadsheet: {output_path}")
            copy_files_to_clipboard([output_path])
            self.notification_manager.notify(
                "AIDocStation",
                t("workflow.action.clipboard_copied"),
                ok=True
            )
            return True
        except Exception as e:
            log(f"Failed to generate spreadsheet: {e}")
            self.notification_manager.notify(
                "AIDocStation",
                t("workflow.table.export_failed"),
                ok=False
            )
            return False
