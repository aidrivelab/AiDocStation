# -*- coding: utf-8 -*-
"""
@File    : local_bridge/service/document/win32/wps_inserter.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import os
import time
import win32com.client
from win32com.client import dynamic

from .word_inserter import BaseWordInserter
from ....utils.logging import log
from ....utils.win32 import cleanup_background_wps_processes
from ....core.constants import WORD_INSERT_RETRY_COUNT, WORD_INSERT_RETRY_DELAY


class WPSInserter(BaseWordInserter):
                   
    
    def __init__(self):

        super().__init__(
            prog_id=["kwps.Application", "KWPS.Application"],
            app_name="WPS 文字"
        )

    def insert(self, docx_path: str, template_path: str = None, sync_mode: str = "built-in",
               move_cursor_to_end: bool = True, table_text_style: str = "正文", 
               body_style: str = "正文", image_style: str = "正文", image_scale: int = 100, 
               list_handle_method: str = "keep", table_line_height_rule: str = "1.0") -> bool:
        

           
        try:

            return super().insert(
                docx_path=docx_path, 
                template_path=template_path, 
                sync_mode=sync_mode,
                move_cursor_to_end=move_cursor_to_end, 
                table_text_style=table_text_style, 
                body_style=body_style, 
                image_style=image_style, 
                image_scale=image_scale, 
                list_handle_method=list_handle_method,
                table_line_height_rule=table_line_height_rule
            )
        except Exception as e:

            log(f"WPS 首次插入失败: {e}，尝试清理后�?WPS 进程重试...")
            cleaned_count = cleanup_background_wps_processes()
            
            if cleaned_count > 0:
                log(f"已清�?{cleaned_count} 个后�?WPS 进程，重试插�?..")

                return super().insert(
                    docx_path=docx_path, 
                    template_path=template_path, 
                    sync_mode=sync_mode,
                    move_cursor_to_end=move_cursor_to_end, 
                    table_text_style=table_text_style, 
                    body_style=body_style, 
                    image_style=image_style, 
                    image_scale=image_scale, 
                    list_handle_method=list_handle_method,
                    table_line_height_rule=table_line_height_rule
                )
            else:
                log("没有找到需要清理的后台进程")
                raise


    def _get_application(self):
                                           
        for prog_id in self.prog_ids:
            try:

                app = win32com.client.GetActiveObject(prog_id)
                log(f"Successfully connected to WPS via {prog_id}")
                return app
            except Exception as e:
                log(f"Cannot get running WPS application via {prog_id}: {e}")
            
            try: 
                app = dynamic.Dispatch(prog_id)
                
                log(f"Successfully created WPS via {prog_id} (Dynamic)")
                self._ensure_app_ready(app)
                return app
            except Exception as e:
                log(f"Cannot get WPS application via {prog_id}: {e}")
            
            try:

                app = win32com.client.Dispatch(prog_id)
                log(f"Successfully created WPS instance via {prog_id}")
                return app
            except Exception as e:
                log(f"Cannot get WPS application via {prog_id}: {e}")
                continue
        
        raise Exception(f"未找到运行中�?{self.app_name}，请先打开")
    
    def _get_selection(self, app):
        










           
        import pywintypes
        

        try:
            selection = app.Selection
            if selection is not None:
                log("获取 WPS Selection 成功（通过 app.Selection�?)
                return selection
        except (AttributeError, pywintypes.com_error) as e:
            log(f"无法�?app 获取 Selection: {e}")
        

        try:
            selection = app.ActiveDocument.ActiveWindow.Selection
            if selection is not None:
                log("获取 WPS Selection 成功（通过 ActiveDocument.ActiveWindow.Selection�?)
                return selection
        except (AttributeError, pywintypes.com_error) as e:
            log(f"无法�?ActiveDocument.ActiveWindow 获取 Selection: {e}")
        

        try:
            selection = app.ActiveWindow.Selection
            if selection is not None:
                log("获取 WPS Selection 成功（通过 ActiveWindow.Selection�?)
                return selection
        except (AttributeError, pywintypes.com_error) as e:
            log(f"无法�?ActiveWindow 获取 Selection: {e}")
        

        try:
            documents = app.Documents
            if documents and documents.Count > 0:
                selection = documents(1).ActiveWindow.Selection
                if selection is not None:
                    log("获取 WPS Selection 成功（通过 Documents(1).ActiveWindow.Selection�?)
                    return selection
        except (AttributeError, pywintypes.com_error) as e:
            log(f"无法�?Documents(1).ActiveWindow 获取 Selection: {e}")
        

        log("所有获�?Selection 的方法都失败")
        raise Exception("无法获取 WPS Selection，可能存在后台进程干�?)

    def _insert_with_formatted_text(self, target_range, source_docx: str) -> bool:
        





           
        if not source_docx or not os.path.exists(source_docx):
            return False

        app = target_range.Application
        doc = target_range.Document
        tables_before = doc.Tables.Count
        

        orig_updating = True
        orig_alerts = 0
        try:
            orig_updating = app.ScreenUpdating
            orig_alerts = app.DisplayAlerts
        except: pass

        try:

            app.ScreenUpdating = True
            app.DisplayAlerts = 0 
            

            target_range.Collapse(1)


            has_table = False
            try:

                check_doc = app.Documents.Open(source_docx, Visible=False, ReadOnly=True)
                if check_doc.Tables.Count > 0:
                    has_table = True
                    log(f"[WPS] Detected {check_doc.Tables.Count} table(s) in source. Enforcing HTML Clipboard strategy.")
                check_doc.Close(False)
            except Exception as e:
                log(f"[WPS] Pre-flight table check led to error (ignoring): {e}")

            insertion_done = False



            if not has_table:
                log(f"[WPS] No tables detected. Attempting native InsertFile for {os.path.basename(source_docx)}...")
                try:

                    app.Selection.InsertFile(source_docx)
                    insertion_done = True
                except Exception as e:
                    log(f"[WPS] selection.InsertFile failed, trying range.InsertFile: {e}")
                    try:
                        target_range.InsertFile(source_docx)
                        insertion_done = True
                    except: pass
                

                time.sleep(0.1)
                if insertion_done:
                    log(f"[WPS] Native InsertFile successful (Text Mode).")
                    return True
            

            trigger_reason = "Contains Tables" if has_table else "InsertFile Failed"
            log(f"[WPS] Strategy: HTML Clipboard Fallback (Reason: {trigger_reason})...")
            
            html_content = None
            try:
                from ....utils.path_utils import get_pypandoc_path
                from ....service.generator import DocumentGenerator

                gen = DocumentGenerator()
                html_content = gen.convert_docx_to_html_text(source_docx)
            except Exception as e:
                log(f"[WPS] HTML Conversion failed: {e}")
            
            if html_content:
                if self._set_clipboard_html(html_content):
                    log("[WPS] HTML payload injected. Executing Native Paste...")
                    target_range.Collapse(1)
                    app.Selection.Paste()
                    

                    log(f"[WPS] HTML Paste executed.")
                    return True
            

            log("[WPS] Final effort: FormattedText assignment...")
            src_doc = None
            try:

                src_doc = app.Documents.Open(source_docx, Visible=False, ReadOnly=True)
                target_range.FormattedText = src_doc.Range().FormattedText
                return True
            except Exception as e:
                log(f"[WPS] FormattedText fallback failed: {e}")
                return False
            finally:
                if src_doc:
                    try: src_doc.Close(False)
                    except: pass

        except Exception as e:
            log(f"[WPS] Global insertion flow failed: {e}")
            return False
            
        finally:

            try:
                app.ScreenUpdating = orig_updating
                app.DisplayAlerts = orig_alerts
            except: pass

    def _set_clipboard_html(self, html_content: str) -> bool:
        

           
        try:
            import win32clipboard
            


            header_template = (
                "Version:0.9\r\n"
                "StartHTML:{0:08d}\r\n"
                "EndHTML:{1:08d}\r\n"
                "StartFragment:{2:08d}\r\n"
                "EndFragment:{3:08d}\r\n"
            )
            
            html_start = "<html><body>"
            html_end = "</body></html>"
            frag_start = "<!--StartFragment-->"
            frag_end = "<!--EndFragment-->"
            


            





            dummy_header = header_template.format(0, 0, 0, 0)
            header_len = len(dummy_header.encode('utf-8'))
            

            full_body = html_start + frag_start + html_content + frag_end + html_end
            body_bytes = full_body.encode('utf-8')
            





            
            start_html = header_len
            end_html = header_len + len(body_bytes)
            
            start_fragment = start_html + len((html_start + frag_start).encode('utf-8'))
            end_fragment = start_fragment + len(html_content.encode('utf-8'))
            

            final_header = header_template.format(start_html, end_html, start_fragment, end_fragment)
            final_data = final_header.encode('utf-8') + body_bytes
            

            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            

            CF_HTML = win32clipboard.RegisterClipboardFormat("HTML Format")
            
            win32clipboard.SetClipboardData(CF_HTML, final_data)
            win32clipboard.CloseClipboard()
            return True
        except Exception as e:
            log(f"[WPS] Clipboard Error: {e}")
            try: win32clipboard.CloseClipboard()
            except: pass
            return False

    def _apply_paragraph_styles(self, range_obj, body_style: str = "正文", list_handle_method: str = "clear") -> None:
        






           
        try:
            from ....constants.word_styles import get_english_style_name
            import re
            

            re_stale_body = re.compile(r'first paragraph|compact|紧凑|正文文本缩进|list paragraph|列表段落|body text|normal', re.I)
            re_header = re.compile(r'标题|Heading', re.I)
            
            en_body_style = get_english_style_name(body_style)
            
            log(f"[WPS] Executing SAFE style normalization -> '{body_style}' (Global Reset DISABLED)")
            


            para_count = range_obj.Paragraphs.Count
            check_limit = min(para_count, 1500)
            
            for i in range(1, check_limit + 1):
                try:
                    p = range_obj.Paragraphs.Item(i)
                    p_range = p.Range
                    


                    try:
                        if p_range.Information(12):
                            continue
                    except: pass
                    

                    s_name = ""
                    try: s_name = str(p.Style)
                    except: pass
                    

                    if re_header.search(s_name):
                        continue
                        


                    if re_stale_body.search(s_name) or s_name == "Normal":
                        if s_name != body_style and s_name != en_body_style:
                            try:


                                p.Style = body_style
                                

                                if list_handle_method == "clear":
                                    p.ParagraphFormat.Reset()
                                    try: p.Range.Font.Reset()
                                    except: pass
                                    
                            except Exception as style_err:

                                try: p.Style = en_body_style
                                except: pass
                                log(f"[WPS] Paragraph correction warning: {style_err}")



                        if i == 1 and not p_range.Information(12):
                            if any(kw in (body_style + s_name) for kw in ["缩进", "Indent", "正文文本", "Body Text"]):
                                try:
                                    samples = getattr(self, "_current_style_samples", {})

                                    val_pts = 24
                                    val_ch = 2
                                    if body_style in samples:
                                        val_pts = samples[body_style].get("FirstLineIndent", 0)
                                        val_ch = samples[body_style].get("CharacterUnitFirstLineIndent", 0)
                                    

                                    try: p.ParagraphFormat.FirstLineIndent = val_pts
                                    except: pass
                                    try: p.ParagraphFormat.CharacterUnitFirstLineIndent = val_ch
                                    except: pass
                                    log(f"[WPS] Forced first paragraph indent via Host Sample: {val_pts}pt / {val_ch}ch")
                                except: pass

                except Exception as p_err:

                    pass
            
            log(f"[WPS] Safe style normalization completed for {check_limit} paragraphs.")
            
        except Exception as e:
            log(f"[WPS] _apply_paragraph_styles failed: {e}")


    def _fix_single_table(self, table, table_text_style: str = "正文", table_line_height_rule: str = "1.0") -> None:
        









           
        try:
            log(f"[WPS] Executing Minimalist Table Fix (AutoFit Only)...")
            

            try:
                table.AutoFitBehavior(1)
                table.PreferredWidthType = 2
                table.PreferredWidth = 100
            except Exception as e:
                log(f"[WPS] AutoFit failed: {e}")
                




            try:

                for row in table.Rows:
                    for cell in row.Cells:
                        for p in cell.Range.Paragraphs:
                            try:



                                p.Style = table_text_style
                            except: pass
            except: 

                try:
                    for p in table.Range.Paragraphs:
                        try: p.Style = table_text_style
                        except: pass
                except: pass


            log("[WPS] Applied safe paragraph-level styling to table cells.")
                
        except Exception as e:
            log(f"[WPS] _fix_single_table failed: {e}")
