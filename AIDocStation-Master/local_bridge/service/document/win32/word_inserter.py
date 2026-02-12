# -*- coding: utf-8 -*-
"""
@File    : local_bridge/service/document/win32/word_inserter.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:42
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import os
import time
import win32com.client
from win32com.client import gencache
from win32com.client import dynamic

from ....utils.win32.com import ensure_com
from ....utils.logging import log
from ....constants.word_styles import get_english_style_name
from ....core.constants import WORD_INSERT_RETRY_COUNT, WORD_INSERT_RETRY_DELAY
from ....core.errors import InsertError
import win32clipboard as wc
import shutil
import tempfile
import hashlib



FORCE_LOCAL_STYLE_SYNC = True


class BaseWordInserter:
                                          
    
    def __init__(self, prog_id, app_name: str):
        





           

        self.prog_ids = [prog_id] if isinstance(prog_id, str) else prog_id
        self.prog_id = self.prog_ids[0]
        self.app_name = app_name

    @ensure_com
    def insert(self, docx_path: str, template_path: str = None, sync_mode: str = "built-in",
               move_cursor_to_end: bool = True, table_text_style: str = "正文", 
               body_style: str = "正文", image_style: str = "正文", image_scale: int = 100, 
               list_handle_method: str = "keep", table_line_height_rule: str = "1.0") -> bool:
        

           
        try:
            app = self._get_application()

            self._ensure_app_ready(app, add_if_empty=True)
            return self._perform_insertion(app, docx_path, template_path=template_path, sync_mode=sync_mode,
                                          move_cursor_to_end=move_cursor_to_end, 
                                          table_text_style=table_text_style, body_style=body_style, 
                                          image_style=image_style, image_scale=image_scale, 
                                          list_handle_method=list_handle_method, 
                                          table_line_height_rule=table_line_height_rule)
        except Exception as e:
            log(f"{self.app_name} insertion failed: {e}")
            raise InsertError(f"{self.app_name} 插入失败: {e}")

    @ensure_com
    def insert_into_new_from_template(self, docx_path: str, template_path: str, table_text_style: str = "正文", 
                                     body_style: str = "正文", image_style: str = "正文", image_scale: int = 100, 
                                     list_handle_method: str = "keep", table_line_height_rule: str = "1.0") -> bool:
        








           
        try:
            app = self._get_application()

            self._ensure_app_ready(app, add_if_empty=False)
            

            original_screen_updating = app.ScreenUpdating
            app.ScreenUpdating = False
            
            try:

                if template_path and os.path.exists(template_path):
                    log(f"[{self.app_name}] Creating new document from template: {template_path}")
                    doc = app.Documents.Add(Template=template_path)
                else:
                    log(f"[{self.app_name}] Template not found, creating blank document")
                    doc = app.Documents.Add()
                

                selection = app.Selection
                selection.InsertFile(docx_path)
                
                log(f"[{self.app_name}] Successfully injected content into template-based document.")
                

                full_range = doc.Content
                self._apply_table_autofit(full_range, table_text_style, table_line_height_rule)
                self._apply_paragraph_styles(full_range, body_style, list_handle_method)
                self._apply_image_styles(doc, image_style, image_scale, 0)
                

                doc.Activate()
                app.Visible = True
                return True
            finally:
                app.ScreenUpdating = original_screen_updating
                
        except Exception as e:
            log(f"[{self.app_name}] Failed in insert_into_new_from_template: {e}")
            return False

    def _get_template_fingerprint(self, template_path: str) -> str:
                                   
        if not template_path or not os.path.exists(template_path):
            return ""
        try:
            mtime = os.path.getmtime(template_path)

            seed = f"{template_path}_{mtime}"
            return hashlib.md5(seed.encode('utf-8')).hexdigest()
        except:
            return ""

    def _get_document_fingerprint(self, doc) -> str:
                                              
        try:
            return str(doc.Variables("AIDoc-Template-Fingerprint").Value)
        except:
            return ""

    def _set_document_fingerprint(self, doc, fingerprint: str) -> None:
                                              
        if not fingerprint:
            return
        try:

            doc.Variables("AIDoc-Template-Fingerprint").Value = fingerprint
        except:
            try:

                doc.Variables.Add("AIDoc-Template-Fingerprint", fingerprint)
            except Exception as e:
                log(f"[Word] Failed to set document fingerprint: {e}")

    def _should_sync_branding(self, doc, template_path: str, sync_mode: str) -> bool:
        





           
        if sync_mode == "disabled":
            log("[Word] Sync Mode: Disabled. Skipping branding sync.")
            return False
            
        if not template_path or not os.path.exists(template_path):
            log("[Word] Template not found. Skipping branding sync.")
            return False


        tpl_fp = self._get_template_fingerprint(template_path)
        doc_fp = self._get_document_fingerprint(doc)
        
        if tpl_fp and tpl_fp == doc_fp:
            log(f"[Word] Document fingerprint matches template ({tpl_fp}). Skipping redundant sync.")
            return False
            
        log(f"[Word] Fingerprint mismatch (Doc:{doc_fp} != Tpl:{tpl_fp}). Triggering branding sync.")
        return True


    def _sample_host_styles(self, doc, style_names: list):
        


           
        try:

            if not hasattr(self, "_current_style_samples") or self._current_style_samples is None:
                self._current_style_samples = {}
            


                try:
                    s_obj = doc.Styles(s_name)

                    cu_indent = 0
                    try: cu_indent = getattr(s_obj.ParagraphFormat, "CharacterUnitFirstLineIndent", 0)
                    except: pass
                    
                    self._current_style_samples[s_name] = {
                        "FontName": s_obj.Font.Name,
                        "FontNameFarEast": s_obj.Font.NameFarEast,
                        "FontSize": s_obj.Font.Size,
                        "Bold": s_obj.Font.Bold,
                        "Alignment": s_obj.ParagraphFormat.Alignment,
                        "LineSpacingRule": s_obj.ParagraphFormat.LineSpacingRule,
                        "LineSpacing": s_obj.ParagraphFormat.LineSpacing,
                        "FirstLineIndent": s_obj.ParagraphFormat.FirstLineIndent,
                        "CharacterUnitFirstLineIndent": cu_indent
                    }
                    log(f"[{self.app_name}] Sampled HOST style '{s_name}': Font={s_obj.Font.Name}, Size={s_obj.Font.Size}, Indent={s_obj.ParagraphFormat.FirstLineIndent}pt, CU_Indent={cu_indent}ch")
                except:

                    pass
        except Exception as e:
            log(f"[{self.app_name}] Critical: _sample_host_styles failed: {e}")

    def _sync_document_branding(self, target_doc, template_path: str, tpl_doc_handle=None) -> bool:
        


           
        try:



            
            if not template_path or not os.path.exists(template_path):
                return False
                
            try:
                app = target_doc.Parent

                style_samples = {}
                

                tpl_doc = app.Documents.Open(template_path, Visible=False, ReadOnly=True)
                try:
                    if tpl_doc.Windows.Count > 0:
                        tpl_doc.Windows(1).Visible = False

                    log("[Word] Starting branding sync & style sampling...")




                    sample_list = ["正文缩进", "正文文本缩进", "题注", "页眉", "Normal Indent", "Caption", "Header"]
                    for s_name in sample_list:
                        try:
                            s_obj = tpl_doc.Styles(s_name)
                            style_samples[s_name] = {
                                "Size": s_obj.Font.Size,
                                "Bold": s_obj.Font.Bold,
                                "Name": s_obj.Font.Name,
                                "NameFarEast": s_obj.Font.NameFarEast,
                                "Alignment": s_obj.ParagraphFormat.Alignment,
                                "LineSpacing": s_obj.ParagraphFormat.LineSpacing,
                                "LineSpacingRule": s_obj.ParagraphFormat.LineSpacingRule,
                                "FirstLineIndent": s_obj.ParagraphFormat.FirstLineIndent
                            }
                        except: pass
                    

                    self._current_style_samples = style_samples




                    if FORCE_LOCAL_STYLE_SYNC:
                        try:


                            is_compat = False
                            try:
                                if hasattr(target_doc, 'CompatibilityMode') and target_doc.CompatibilityMode < 15:
                                    is_compat = True
                            except: pass
                            
                            if is_compat:
                                log("[Word] Compatibility mode detected, skipping CopyStylesFromTemplate to avoid COM crash.")


                                for s_name, samples in style_samples.items():
                                    try:
                                        target_s = target_doc.Styles(s_name)


                                        if "Name" in samples:
                                            target_s.Font.Name = samples["Name"]
                                        if "NameFarEast" in samples:
                                            target_s.Font.NameFarEast = samples["NameFarEast"]
                                            log(f"[Word] [V5.8] Injected dual fonts ({samples.get('Name')}/{samples.get('NameFarEast')}) into style '{s_name}'")
                                        


                                        if "Size" in samples:
                                            target_s.Font.Size = samples["Size"]
                                        if "Bold" in samples:
                                            target_s.Font.Bold = samples["Bold"]
                                        if "LineSpacing" in samples:
                                            try: target_s.ParagraphFormat.LineSpacing = samples["LineSpacing"]
                                            except: pass
                                        if "LineSpacingRule" in samples:
                                            try: target_s.ParagraphFormat.LineSpacingRule = samples["LineSpacingRule"]
                                            except: pass
                                        if "FirstLineIndent" in samples:
                                            try: target_s.ParagraphFormat.FirstLineIndent = samples["FirstLineIndent"]
                                            except: pass

                                        
                                        

                                        if s_name in ["页眉", "Header"]:
                                            try:

                                                target_s.Borders(-3).LineStyle = 1
                                                target_s.Borders(-3).LineWidth = 4
                                                log("[Word] [V5.7] Restored header bottom border style.")
                                            except: pass
                                    except: pass
                            else:
                                log(f"[Word] Syncing style definitions from template: {os.path.basename(template_path)}")
                                target_doc.CopyStylesFromTemplate(template_path)
                        except Exception as e:
                            log(f"[Word] Warning: Failed to copy styles from template: {e}")
                    

                    if not self._is_object_alive(target_doc):
                        log("[Word] Target document disconnected after style sync. Aborting branding.")
                        return False
                    
                    tpl_sec_count = tpl_doc.Sections.Count
                    
                    for i in range(1, target_doc.Sections.Count + 1):
                        target_sec = target_doc.Sections.Item(i)

                        tpl_sec = tpl_doc.Sections.Item(min(i, tpl_sec_count))
                        

                        ts = target_sec.PageSetup
                        ps = tpl_sec.PageSetup
                        try:
                            ts.TopMargin = ps.TopMargin
                            ts.BottomMargin = ps.BottomMargin
                            ts.LeftMargin = ps.LeftMargin
                            ts.RightMargin = ps.RightMargin
                            ts.HeaderDistance = ps.HeaderDistance
                            ts.FooterDistance = ps.FooterDistance
                            
                            ts.DifferentFirstPageHeaderFooter = ps.DifferentFirstPageHeaderFooter
                            ts.OddAndEvenPagesHeaderFooter = ps.OddAndEvenPagesHeaderFooter
                        except: pass


                        for hf_type in [1, 2, 3]:
                            try:

                                target_sec.Headers.Item(hf_type).LinkToPrevious = False
                                target_sec.Footers.Item(hf_type).LinkToPrevious = False
                                

                                tpl_h_range = tpl_sec.Headers.Item(hf_type).Range
                                target_h_range = target_sec.Headers.Item(hf_type).Range
                                

                                has_content = tpl_h_range.Text.strip() or tpl_h_range.InlineShapes.Count > 0 or tpl_h_range.ShapeRange.Count > 0
                                
                                if has_content:
                                     target_h_range.Delete() 
                                     target_h_range.FormattedText = tpl_h_range.FormattedText
                                     


                                     try:
                                         usable_width = ps.PageWidth - ps.LeftMargin - ps.RightMargin
                                         for h_shape in target_h_range.InlineShapes:
                                             if h_shape.Width > usable_width:
                                                 ratio = usable_width / h_shape.Width
                                                 h_shape.Width = usable_width
                                                 h_shape.Height = h_shape.Height * ratio
                                                 log(f"[Word] Scaled header image to fit page width: {usable_width}")
                                     except: pass




                                     for _ in range(5):
                                         h_obj = target_sec.Headers.Item(hf_type)
                                         if h_obj.Range.Paragraphs.Count <= 1: break
                                         last_p = h_obj.Range.Paragraphs.Last
                                         p_text = last_p.Range.Text.strip('\r\n\t \xa0\x0c')

                                         if not p_text and last_p.Range.InlineShapes.Count == 0:
                                             try: last_p.Range.Delete()
                                             except: break
                                         else:
                                             break
                                

                                tpl_f_range = tpl_sec.Footers.Item(hf_type).Range
                                target_f_range = target_sec.Footers.Item(hf_type).Range
                                has_f_content = tpl_f_range.Text.strip() or tpl_f_range.InlineShapes.Count > 0 or tpl_f_range.ShapeRange.Count > 0
                                
                                if has_f_content:
                                    target_f_range.Delete() 
                                    target_f_range.FormattedText = tpl_f_range.FormattedText
                                    for _ in range(5):
                                        f_obj = target_sec.Footers.Item(hf_type)
                                        if f_obj.Range.Paragraphs.Count <= 1: break
                                        last_p = f_obj.Range.Paragraphs.Last
                                        p_text = last_p.Range.Text.strip('\r\n\t \xa0\x0c')
                                        if not p_text and last_p.Range.InlineShapes.Count == 0:
                                            try: last_p.Range.Delete()
                                            except: break
                                        else:
                                            break
                            except: pass
                    
                    log(f"[Word] Successfully fully replaced branding from: {os.path.basename(template_path)}")
                    

                    new_fp = self._get_template_fingerprint(template_path)
                    self._set_document_fingerprint(target_doc, new_fp)
                    
                    return True
                finally:
                    tpl_doc.Close(0)
            except Exception as e:
                log(f"[Word] Hard branding sync failed: {e}")
                return False
        except Exception as e:
            log(f"[{self.app_name}] _sync_document_branding_v4 failed at top level: {e}")
            return False

    def _perform_insertion(self, app, docx_path: str, template_path: str = None, sync_mode: str = "built-in",
                           move_cursor_to_end: bool = True, table_text_style: str = "正文", 
                           body_style: str = "正文", image_style: str = "正文", image_scale: int = 100, 
                           list_handle_method: str = "keep", table_line_height_rule: str = "1.0") -> bool:
        


















           

        selection = self._get_selection(app)
        if selection is None:
            raise InsertError(f"无法访问 {self.app_name} 选择区域")
        

        target_doc_name = None
        try:
            target_doc_name = app.ActiveDocument.Name
        except: pass


        for attempt in range(WORD_INSERT_RETRY_COUNT):

            original_visible = True
            original_screen_updating = True
            original_display_alerts = 0
            is_doc_empty = False
            
            try:

                try:
                    original_visible = app.Visible
                    original_screen_updating = app.ScreenUpdating
                    original_display_alerts = app.DisplayAlerts

                    is_doc_empty = self._is_doc_empty(app.ActiveDocument)
                except: pass


                if not self._is_object_alive(app):
                    log(f"[{self.app_name}] Application object dead, attempting to reconnect...")
                    app = self._get_application()
                    selection = self._get_selection(app)


                doc = app.ActiveDocument
                try:
                    if target_doc_name and (not self._is_object_alive(doc) or doc.Name != target_doc_name):
                        log(f"[{self.app_name}] Document focus hijacked/lost. Recalling {target_doc_name}...")
                        found = False
                        for d in app.Documents:
                            if d.Name == target_doc_name:
                                doc = d
                                doc.Activate()
                                found = True
                                break
                        if not found:
                            log(f"[{self.app_name}] Warning: Could not find original target {target_doc_name}.")
                except: pass

                if not self._is_object_alive(doc):
                     doc = app.ActiveDocument
                

                is_doc_empty = self._is_doc_empty(doc)


                try:
                    app.ScreenUpdating = False
                    app.DisplayAlerts = 0
                except: pass
                    
                try:

                    doc = app.ActiveDocument
                    
                    if is_doc_empty:


                        log(f"[{self.app_name}] Empty document detected. In-place branding sync Mode: {sync_mode}")
                        

                        if sync_mode != "disabled" and template_path and os.path.exists(template_path):
                            self._sync_document_branding(doc, template_path)
                        else:

                            self._sample_host_styles(doc, [body_style, table_text_style, image_style])
                        



                        self._insert_with_formatted_text(doc.Range(0, 0), docx_path)
                        

                        log("Applying style normalization on current (was empty) document.")
                        full_range = doc.Content
                        self._apply_paragraph_styles(full_range, body_style, list_handle_method)
                        self._apply_table_autofit(full_range, table_text_style, table_line_height_rule)
                        self._apply_image_styles(doc, image_style, image_scale, 0)
                        

                        self._apply_style_compensation(full_range)
                    else:

                        log("[Word] Merging content into existing document at selection.")
                        
                        if self._should_sync_branding(doc, template_path, sync_mode):
                            self._sync_document_branding(doc, template_path)
                        else:

                            log("[Word] Skipping branding sync. Sampling host styles instead.")
                            self._sample_host_styles(doc, [body_style, table_text_style, image_style])
                            
                        insert_start = selection.Range.Start
                        shapes_before = doc.InlineShapes.Count
                        


                        target_range = selection.Range
                        if move_cursor_to_end:
                            target_range.Collapse(0)
                        
                        self._insert_with_formatted_text(target_range, docx_path)
                        
                        log(f"Successfully inserted into {self.app_name}: {docx_path}")
                        
                        doc_new_end = doc.Content.End
                        inserted_range = doc.Range(insert_start, doc_new_end)
                        self._apply_paragraph_styles(inserted_range, body_style, list_handle_method)
                        

                        pass
                        
                        self._apply_table_autofit(inserted_range, table_text_style, table_line_height_rule)
                        self._apply_image_styles(doc, image_style, image_scale, shapes_before)
                        

                        self._apply_style_compensation(inserted_range)
                        
                        if move_cursor_to_end:
                            try:


                                end_pos = doc.Content.End
                                cursor_range = doc.Range(end_pos - 1, end_pos - 1)
                                cursor_range.Select()
                                log(f"[{self.app_name}] [V5.6 STABLE] Cursor moved to doc end: {end_pos - 1}")
                            except Exception as e:
                                log(f"[{self.app_name}] [V5.6] Absolute End Cursor failed: {e}")


                    return True
                
                finally:

                    try:
                        app.ScreenUpdating = True
                        app.DisplayAlerts = original_display_alerts
                        

                        doc = app.ActiveDocument
                        try:
                            v_type = doc.ActiveWindow.View.Type
                            doc.ActiveWindow.View.Type = 3

                            if v_type == 3:
                                doc.ActiveWindow.SmallScroll(Down=0)
                        except: pass
                        




                        if self.app_name == "Word":
                            try:
                                app.Visible = True
                                app.Activate()
                                if doc:
                                    doc.Activate()
                            except: pass
                        elif not original_visible:
                             app.Visible = True 
                             try: app.Activate()
                             except: pass
                        log(f"[{self.app_name}] Restored visibility and cleared rendering artifacts.")
                    except: pass
                    
            except Exception as e:
                if attempt < WORD_INSERT_RETRY_COUNT - 1:
                    log(f"{self.app_name} insert attempt {attempt + 1} failed, retrying: {e}")
                    time.sleep(WORD_INSERT_RETRY_DELAY)
                else:
                    raise InsertError(f"插入失败（已重试 {WORD_INSERT_RETRY_COUNT} 次）: {e}")
        
        return False

    def _insert_with_formatted_text(self, target_range, source_docx: str) -> bool:
        




           
        if not source_docx or not os.path.exists(source_docx):
            return False
            
        is_wps = "wps" in self.app_name.lower()
        
        try:
            app = target_range.Application
            doc = target_range.Document
            tables_before = doc.Tables.Count
            

            target_range.Collapse(1)
            


            if is_wps:
                try:
                    log(f"[WPS] Executing Clipboard Clone for {os.path.basename(source_docx)}...")

                    src_doc = app.Documents.Open(source_docx, Visible=False, ReadOnly=True, Format=12)
                    try:
                        if src_doc.Windows.Count > 0:
                            src_doc.Windows(1).Visible = False
                        

                        src_doc.Range().Copy()
                        target_range.Paste()
                        

                        if doc.Tables.Count > tables_before:
                            log("[WPS] Table structure successfully cloned via Clipboard.")
                        else:
                            log("[WPS] Warning: No tables added after Clipboard Paste.")
                        return True
                    finally:
                        src_doc.Close(False)
                except Exception as e:
                    log(f"[WPS] Clipboard Clone failed: {e}. Falling back to FormattedText...")

            else:



                try:
                    log(f"[{self.app_name}] Executing native InsertFile...")
                    target_range.InsertFile(source_docx)
                    return True
                except Exception as e:
                    log(f"[{self.app_name}] InsertFile failed: {e}. Falling back to FormattedText clone...")


            src_doc = app.Documents.Open(source_docx, Visible=False, ReadOnly=True, Format=12)
            try:
                if src_doc.Windows.Count > 0:
                    src_doc.Windows(1).Visible = False
                    
                log(f"[{self.app_name}] Executing FormattedText Clone...")
                target_range.FormattedText = src_doc.Range().FormattedText
                return True
            finally:
                src_doc.Close(False)
                
        except Exception as e:
            log(f"[{self.app_name}] Insertion flow failed: {e}. Final fallback to InsertFile...")
            try:
                target_range.InsertFile(source_docx)
                return True
            except:
                return False
    
    def _apply_style_compensation(self, range_obj) -> None:
        


           
        try:

            samples = getattr(self, "_current_style_samples", {})
            

            default_size_map = {
                "正文缩进": 12.0, "题注": 12.0, "Normal Indent": 12.0, "Caption": 12.0,
                "正文文本缩进": 12.0, "Body Text Indent": 12.0
            }
            

            for para in range_obj.Paragraphs:
                try:
                    style_name = para.Style.NameLocal
                    

                    if style_name in samples:
                        s_info = samples[style_name]
                        para.Range.Font.Size = s_info["Size"]
                        para.Range.Font.Bold = s_info["Bold"]
                        


                        if "Name" in s_info:
                            para.Range.Font.Name = s_info["Name"]
                        if "NameFarEast" in s_info:
                            para.Range.Font.NameFarEast = s_info["NameFarEast"]
                        if "Alignment" in s_info:
                            try: para.Range.ParagraphFormat.Alignment = s_info["Alignment"]
                            except: pass

                        if "LineSpacing" in s_info:
                            try: para.Range.ParagraphFormat.LineSpacing = s_info["LineSpacing"]
                            except: pass
                        if "LineSpacingRule" in s_info:
                            try: para.Range.ParagraphFormat.LineSpacingRule = s_info["LineSpacingRule"]
                            except: pass

                        


                        if "FirstLineIndent" in s_info:
                            try: para.ParagraphFormat.FirstLineIndent = s_info["FirstLineIndent"]
                            except: pass
                        if "CharacterUnitFirstLineIndent" in s_info:
                            try: para.ParagraphFormat.CharacterUnitFirstLineIndent = s_info["CharacterUnitFirstLineIndent"]
                            except: pass
                    

                    elif style_name in default_size_map:
                        para.Range.Font.Size = default_size_map[style_name]

                        if "缩进" in style_name:
                            para.Range.Font.Bold = True
                except: pass
        except Exception as e:
            log(f"[{self.app_name}] Style compensation failed: {e}")

    def _apply_table_autofit(self, range_obj, table_text_style: str = "正文", table_line_height_rule: str = "1.0") -> None:
        






           
        try:

            tables = getattr(range_obj, "Tables", None)
            count = 0
            if tables:
                count = tables.Count
                
            if count == 0:


                log("No tables found in specific range, checking ActiveDocument tables")
                try:
                    all_tables = range_obj.Document.Tables
                    if all_tables.Count > 0:


                        last_table = all_tables.Item(all_tables.Count)
                        self._fix_single_table(last_table, table_text_style, table_line_height_rule)
                    return
                except:
                    pass

            log(f"Applying AutoFitWindow and style '{table_text_style}' to {count} table(s) in insertion range")
            for i in range(1, count + 1):
                try:
                    table = tables.Item(i)
                    self._fix_single_table(table, table_text_style, table_line_height_rule)
                except Exception as table_err:
                    log(f"Failed to apply AutoFit to table {i}: {table_err}")
        except Exception as e:
            log(f"Failed to traverse tables for AutoFit: {e}")

    def _fix_single_table(self, table, table_text_style: str = "正文", table_line_height_rule: str = "1.0") -> None:
        


           
        try:

            app_name_lower = self.app_name.lower()
            is_wps = "wps" in app_name_lower
            log(f"[{self.app_name}] Table Fix Strategy: is_wps={is_wps} (raw='{self.app_name}')")


            try:
                table.AutoFitBehavior(1)
                table.PreferredWidthType = 2
                table.PreferredWidth = 100
            except: pass
            

            en_table_style = get_english_style_name(table_text_style)
            line_spacing_map = {"1.0": 0, "1.5": 1, "2.0": 2}
            spacing_rule = line_spacing_map.get(table_line_height_rule, 0)

            try:

                try: table.Range.Style = en_table_style
                except:
                    try: table.Range.Style = table_text_style
                    except: pass
                

                try:
                    bg_color = 16777215
                    if is_wps:
                        bg_color = -16777216
                    table.Range.Cells.Shading.BackgroundPatternColor = bg_color
                    table.Range.Cells.Shading.Texture = 0
                except: pass


                pf = table.Range.ParagraphFormat
                try:
                    pf.Reset()
                    pf.LineSpacingRule = spacing_rule
                except: pass
            except Exception as e:
                log(f"[{self.app_name}] Table style application fallback: {e}")



            try:

                try:
                    bds = table.Borders
                    bds.OutsideLineStyle = 1
                    bds.InsideLineStyle = 1
                    bds.OutsideLineWidth = 8
                    bds.InsideLineWidth = 8
                    bds.OutsideColor = 0
                    bds.InsideColor = 0
                except: pass
                


                if is_wps:
                    try:
                        log(f"[WPS] Executing cell-level border reinforcement (via Rows)...")

                        rows = table.Rows
                        if rows:
                            for row in rows:
                                try:
                                    cells = row.Cells
                                    if cells:
                                        for cell in cells:
                                            try:
                                                cbds = cell.Borders
                                                cbds.Enable = True

                                                for b_idx in [-1, -2, -3, -4]: 
                                                    try:
                                                        bi = cbds.Item(b_idx)
                                                        bi.LineStyle = 1
                                                        bi.LineWidth = 6
                                                        bi.Color = 0
                                                    except: pass
                                            except: pass
                                except: pass
                    except Exception as e:
                        log(f"[WPS] Cell-level reinforcement encountered error: {e}")
                

                try: table.Borders.Enable = True
                except: pass
                
                log(f"[{self.app_name}] Table borders FORCED ACTIVATED.")
            except Exception as border_err:
                log(f"[{self.app_name}] Failed to force activate borders: {border_err}")

            log(f"[{self.app_name}] Force applied AutoFitWindow and style optimization to table")
        except Exception as e:
            log(f"Error in _fix_single_table: {e}")



    def _apply_paragraph_styles(self, range_obj, body_style: str = "正文", list_handle_method: str = "clear") -> None:
        





           
        try:



            


            search_range = range_obj.Duplicate
            find = search_range.Find
            find.ClearFormatting()
            find.Replacement.ClearFormatting()
            find.Forward = True
            find.Wrap = 0
            

            stale_styles = [
                "First Paragraph", "Compact", "Body Text", "Normal", 
                "正文", "正文文本", "Body Text Indent", "Body Text First Indent",
                "正文缩进", "正文文本缩进", "正文首行缩进", "紧凑", 
                "Compact 1", "紧凑 1", "List Paragraph", "列表段落"
            ]
            


            conflict_style_name = body_style + "1"
            try:
                range_obj.Application.ActiveDocument.Styles(conflict_style_name)
                stale_styles.append(conflict_style_name)
                log(f"[{self.app_name}] Detected conflict style '{conflict_style_name}', adding to cleanup list")
            except:
                pass

            log(f"[{self.app_name}] Executing global style normalization -> '{body_style}' (Method: {list_handle_method})")




            if list_handle_method == "clear":
                try:
                    range_obj.ParagraphFormat.Reset()

                    try: range_obj.Font.Reset()
                    except: pass
                    
                    log(f"[{self.app_name}] Reset ParagraphFormat & Font for the entire block to style defaults.")
                except Exception as e:
                    log(f"[{self.app_name}] Failed to reset ParagraphFormat/Font: {e}")
            else:
                log(f"[{self.app_name}] Skipping global ParagraphFormat.Reset() to preserve list numbering.")


            en_body_style = get_english_style_name(body_style)

            for stale_style in stale_styles:

                if stale_style == body_style or stale_style == en_body_style:
                    if stale_style != conflict_style_name:
                        continue
                    
                try:


                    search_range = range_obj.Duplicate
                    find = search_range.Find
                    find.ClearFormatting()
                    find.Replacement.ClearFormatting()
                    

                    find.Style = stale_style

                    try:
                        find.Replacement.Style = en_body_style
                    except:
                        find.Replacement.Style = body_style
                        

                    find.Execute(Replace=2)
                except Exception:

                    pass
                    


            para_count = range_obj.Paragraphs.Count
            

            check_limit = min(para_count, 1000)
            
            if check_limit > 0:

                import re
                re_header = re.compile(r'标题|Heading', re.I)

                re_stale_body = re.compile(r'first paragraph|compact|紧凑|正文文本缩进|list paragraph|列表段落', re.I)
                
                samples = getattr(self, "_current_style_samples", {})
                

                if check_limit > 0:
                    time.sleep(0.1)

                for p_idx, p in enumerate(range_obj.Paragraphs, 1):
                    try:

                        p_range = p.Range
                        s_name = ""
                        try: s_name = str(p.Style)
                        except: pass
                        
                        if re_header.search(s_name):
                            continue





                        try:
                            if p_range.Information(12):
                                continue
                        except: pass


                        is_stale = bool(re_stale_body.search(s_name))
                        
                        if is_stale:
                            if s_name != body_style and s_name != en_body_style:
                                try:
                                    p.Style = en_body_style
                                except:
                                    try:
                                        p.Style = body_style
                                    except: pass
                            

                            try:
                                if not p_range.Information(12):
                                    p.ParagraphFormat.Reset()
                                    p.Range.Font.Reset() 
                            except:
                                p.ParagraphFormat.Reset()
                                try: p.Range.Font.Reset()
                                except: pass



                        pass

                    except:
                        pass
                        
                    if list_handle_method == "keep":



                        try:
                            if not p.Range.ListFormat.ListType: 
                                p.Range.Font.Reset()
                        except: pass
                

                    if p_idx == 1:
                        try:
                            dbg_style = p.Style.NameLocal
                            log(f"[{self.app_name}] [Debug] First paragraph style: '{dbg_style}' (BodyStyle: '{body_style}')")
                        except: pass
                        
        except Exception as e:
            log(f"[{self.app_name}] Global style check failed: {e}")

    def _apply_image_styles(self, doc, image_style: str = "正文", image_scale: int = 100, shapes_before: int = 0) -> None:
        







           
        try:
            all_shapes = doc.InlineShapes
            total_count = all_shapes.Count
            new_count = total_count - shapes_before
            
            if new_count <= 0:
                log(f"[{self.app_name}] No new images detected (before: {shapes_before}, after: {total_count})")
                return
            
            log(f"[{self.app_name}] Processing {new_count} new image(s) for style '{image_style}'")
            
            processed_count = 0

            for i in range(shapes_before + 1, total_count + 1):
                try:
                    shape = all_shapes.Item(i)
                    

                    para = shape.Range.Paragraphs.Item(1)
                    if para:
                        en_image_style = get_english_style_name(image_style)
                        try:
                            para.Style = en_image_style
                            processed_count += 1
                        except:
                            try:
                                para.Style = image_style
                                processed_count += 1
                            except Exception as style_err:
                                log(f"[{self.app_name}] Failed to apply style to image {i}: {style_err}")
                        
                except Exception as shape_err:
                    log(f"[{self.app_name}] Failed to process image {i}: {shape_err}")
            
            if processed_count > 0:
                log(f"[{self.app_name}] Applied style '{image_style}' to {processed_count} image paragraph(s)")
        except Exception as e:
            log(f"Failed to traverse images for styles: {e}")


    
    def _is_object_alive(self, obj) -> bool:
        

           
        if obj is None:
            return False
        try:

            _ = obj.Application
            return True
        except:
            return False

    def _get_selection(self, app):
        







           
        return getattr(app, "Selection", None)
    
    def _ensure_app_ready(self, app, add_if_empty: bool = True, **kwargs) -> None:
                          
        try:

            app.Visible = True
        except Exception:
            pass
        

        if add_if_empty:
            documents = getattr(app, "Documents", None)
            if documents is None or documents.Count == 0:
                documents.Add()
        

        try:

            app.ActiveWindow.View.SeekView = 0
        except Exception:
            pass

    def _is_doc_empty(self, doc) -> bool:
        

           
        try:

            try:

                full_name = doc.FullName
                if "\\" in full_name or "/" in full_name:
                    log(f"[{self.app_name}] Document is already saved at {full_name}, treating as NON-empty.")
                    return False
                

                default_names = ["Document", "文档", "新文�?, "文字文稿", "演示文稿", "工作�?]
                if not any(dn in doc.Name for dn in default_names):
                    log(f"[{self.app_name}] Document has custom name '{doc.Name}', treating as NON-empty.")
                    return False
            except: pass


            text = doc.Content.Text
            if len(text) > 1:

                if text.strip() and text.strip() != "\x0c":
                    log(f"[{self.app_name}] Document contains text (len={len(text)}), treating as NON-empty.")
                    return False


            if doc.Sections.Count > 1:
                log(f"[{self.app_name}] Document has multiple sections, treating as NON-empty.")
                return False
            
            if doc.Tables.Count > 0:
                log(f"[{self.app_name}] Document contains tables, treating as NON-empty.")
                return False
                
            if doc.InlineShapes.Count > 0:
                log(f"[{self.app_name}] Document contains images/shapes, treating as NON-empty.")
                return False

            log(f"[{self.app_name}] Document confirmed as strictly empty and replaceable.")
            return True
        except Exception as e:
            log(f"[{self.app_name}] Error in _is_doc_empty: {e}")
            return False

    def _refresh_app(self) -> object:
        




           
        return self._get_application()


class WordInserter(BaseWordInserter):
                              
    
    def __init__(self):
        super().__init__(prog_id="Word.Application", app_name="Word")
    
    def _get_application(self):
                                            

        for prog_id in self.prog_ids:
            try:

                app = win32com.client.GetActiveObject(prog_id)
                log(f"Successfully connected to Word via {prog_id}")
                return app
            except Exception as e:
                log(f"Cannot get Word application via {prog_id}: {e}")
            
            try:
                app = dynamic.Dispatch(prog_id)
                
                log(f"Successfully created Word instance via {prog_id} (Dynamic)")
                return app
            except Exception as e:
                log(f"Cannot get Word application via {prog_id}: {e}")
            
            try:

                app = gencache.EnsureDispatch(prog_id)
                log(f"Successfully ensured Word instance via {prog_id} (Gencache)")
                return app
            except Exception as e:
                log(f"Cannot get Word application via {prog_id} (Gencache): {e}")
        
        raise InsertError("无法连接�?Word。请确保 Word 已安装并正常运行�?)
    








    def _build_cf_html(self, html: str) -> bytes:
                                          
        start_marker = "<!--StartFragment-->"
        end_marker = "<!--EndFragment-->"

        if start_marker in html and end_marker in html:
            html_doc = html
        else:
            html_doc = (
                "<html><head><meta charset=\"utf-8\"></head><body>"
                f"{start_marker}{html}{end_marker}"
                "</body></html>"
            )

        html_bytes = html_doc.encode("utf-8")

        header_template = (
            "Version:1.0\r\n"
            "StartHTML:{:010d}\r\n"
            "EndHTML:{:010d}\r\n"
            "StartFragment:{:010d}\r\n"
            "EndFragment:{:010d}\r\n"
        )


        header_placeholder = header_template.format(0, 0, 0, 0).encode("ascii")
        start_html = len(header_placeholder)
        end_html = start_html + len(html_bytes)

        start_marker_b = start_marker.encode("ascii")
        end_marker_b = end_marker.encode("ascii")
        sf_index = html_bytes.find(start_marker_b)
        ef_index = html_bytes.find(end_marker_b)
        
        if sf_index == -1 or ef_index == -1 or ef_index < sf_index:
            start_fragment = start_html
            end_fragment = end_html
        else:
            start_fragment = start_html + sf_index + len(start_marker_b)
            end_fragment = start_html + ef_index

        header = header_template.format(start_html, end_html, start_fragment, end_fragment).encode("ascii")
        return header + html_bytes

    def _set_clipboard_html(self, html: str) -> bool:
                                          
        try:
            fmt_html = wc.RegisterClipboardFormat("HTML Format")
            wc.OpenClipboard(0)
            try:
                wc.EmptyClipboard()
                wc.SetClipboardData(fmt_html, self._build_cf_html(html))
                return True
            finally:
                wc.CloseClipboard()
        except Exception as e:
            log(f"[{self.app_name}] Failed to write HTML to clipboard: {e}")
            return False
