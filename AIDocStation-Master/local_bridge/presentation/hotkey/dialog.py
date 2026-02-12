# -*- coding: utf-8 -*-
"""
@File    : local_bridge/presentation/hotkey/dialog.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:42
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable

import os

from ...config.paths import get_app_icon_path
from ...utils.logging import log
from ...utils.hotkey_checker import HotkeyChecker
from ...utils.dpi import get_dpi_scale
from ...utils.system_detect import is_windows, is_macos
from ...service.hotkey.recorder import HotkeyRecorder
from ...i18n import t
from ...core.state import app_state


class HotkeyDialog:
                 
    
    def __init__(self, current_hotkey: str, on_save: Callable[[str], None], on_close: Optional[Callable[[], None]] = None):
        






           
        self.current_hotkey = current_hotkey
        self.on_save = on_save
        self.on_close_callback = on_close
        self.new_hotkey: Optional[str] = None
        self._close_callback_called = False
        self._tk_recording = False
        self._tk_pressed_keys: set[str] = set()
        self._tk_released_keys: set[str] = set()
        self._tk_all_pressed_keys: set[str] = set()
        self._tk_press_binding: Optional[str] = None
        self._tk_release_binding: Optional[str] = None
        
        if app_state.root:
            self.root = tk.Toplevel(app_state.root)
        else:
            self.root = tk.Tk()
            
        self.root.title(t("hotkey.dialog.title"))
        

        if is_windows():
            try:
                icon_path = get_app_icon_path()
                if os.path.exists(icon_path):
                    self.root.iconbitmap(icon_path)
            except Exception as e:
                log(f"Failed to set hotkey dialog icon: {e}")
        

        scale = get_dpi_scale()
        

        if not is_windows():

            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            

            width = max(400, min(500, int(screen_width * 0.35)))
            height = max(250, min(350, int(screen_height * 0.3)))
        else:

            width = int(450 * scale)
            height = int(300 * scale)
        
        self.root.geometry(f"{width}x{height}")
        

        if not is_windows():
            self.root.resizable(True, True)

            self.root.minsize(400, 250)
        else:
            self.root.resizable(False, False)
        

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        

        self._center_window()
        

        self._create_widgets()
        


        self.recorder = None if is_macos() else HotkeyRecorder()

    def _call_on_close_callback(self):
                                   
        if self._close_callback_called:
            return
        self._close_callback_called = True
        if self.on_close_callback:
            try:
                self.on_close_callback()
            except Exception as e:
                log(f"Error in close callback: {e}")

    def _schedule_on_close_callback(self):
                                          
        if self._close_callback_called:
            return
        try:
            if app_state.root and app_state.root.winfo_exists():
                app_state.root.after(0, self._call_on_close_callback)
            else:
                self._call_on_close_callback()
        except Exception as e:
            log(f"Error scheduling close callback: {e}")
            self._call_on_close_callback()

    @staticmethod
    def _tk_key_to_name(event: tk.Event) -> Optional[str]:
        keysym = getattr(event, "keysym", "") or ""
        lower = keysym.lower()


        if lower in {"control_l", "control_r", "control"}:
            return "ctrl"
        if lower in {"shift_l", "shift_r", "shift"}:
            return "shift"
        if lower in {"alt_l", "alt_r", "option_l", "option_r", "option"}:
            return "alt"
        if lower in {"command", "command_l", "command_r", "meta_l", "meta_r", "super_l", "super_r"}:
            return "cmd"


        if lower in {"return", "enter"}:
            return "enter"
        if lower in {"escape"}:
            return "esc"
        if lower in {"space"}:
            return "space"
        if lower in {"tab"}:
            return "tab"
        if lower in {"backspace"}:
            return "backspace"
        if lower in {"delete"}:
            return "delete"


        if len(lower) == 1:
            return lower
        return lower or None

    def _tk_on_key_press(self, event: tk.Event):
        if not self._tk_recording:
            return

        key_name = self._tk_key_to_name(event)
        if not key_name:
            return
        if key_name in self._tk_pressed_keys:
            return

        self._tk_pressed_keys.add(key_name)
        self._tk_all_pressed_keys.add(key_name)
        self._notify_tk_update()

    def _tk_on_key_release(self, event: tk.Event):
        if not self._tk_recording:
            return

        key_name = self._tk_key_to_name(event)
        if not key_name:
            return

        self._tk_released_keys.add(key_name)
        self._tk_pressed_keys.discard(key_name)
        self._notify_tk_update()

        if self._tk_all_pressed_keys and self._tk_all_pressed_keys == self._tk_released_keys:
            self._finish_tk_recording()

    def _notify_tk_update(self):
        if not self._tk_all_pressed_keys:
            return

        modifier_order = ["ctrl", "shift", "alt", "cmd"]
        modifiers = [m for m in modifier_order if m in self._tk_all_pressed_keys]
        keys = sorted(k for k in self._tk_all_pressed_keys if k not in modifier_order)
        all_keys = modifiers + keys
        display_text = " + ".join(k.title() for k in all_keys)
        self.root.after(0, lambda: self._set_entry_text(display_text))

    def _finish_tk_recording(self):
        keys = set(self._tk_all_pressed_keys)
        self._stop_tk_recording()

        if not keys:
            self._on_recording_finish(None, t("hotkey.recorder.error.no_key_detected"))
            return

        hotkey_preview = " + ".join(k.title() for k in ["ctrl", "shift", "alt", "cmd"] if k in keys)
        error = HotkeyChecker.validate_hotkey_keys(keys, hotkey_repr=hotkey_preview.replace(" + ", "+"), detailed=True)
        hotkey_str = None
        if not error:
            modifier_order = ["ctrl", "shift", "alt", "cmd"]
            modifiers = [f"<{m}>" for m in modifier_order if m in keys]
            normal_keys = sorted(k for k in keys if k not in modifier_order)
            wrapped = [f"<{k}>" if len(k) > 1 else k for k in normal_keys]
            hotkey_str = "+".join(modifiers + wrapped)

        self._on_recording_finish(hotkey_str, error)

    def _stop_tk_recording(self):
        self._tk_recording = False
        if self._tk_press_binding is not None:
            try:
                self.root.unbind("<KeyPress>", self._tk_press_binding)
            except Exception:
                pass
            self._tk_press_binding = None
        if self._tk_release_binding is not None:
            try:
                self.root.unbind("<KeyRelease>", self._tk_release_binding)
            except Exception:
                pass
            self._tk_release_binding = None
        self._tk_pressed_keys.clear()
        self._tk_released_keys.clear()
        self._tk_all_pressed_keys.clear()

    def is_alive(self) -> bool:
                        
        try:
            return bool(self.root.winfo_exists())
        except Exception:
            return False
    
    def restore_and_focus(self):
                         
        if not self.is_alive():
            return
        
        try:
            self.root.deiconify()
            original_topmost = bool(self.root.attributes("-topmost"))
            self.root.lift()

            self.root.attributes("-topmost", True)
            self.root.after(50, lambda: self.root.attributes("-topmost", original_topmost))
            self.root.focus_force()
        except Exception as e:
            log(f"Failed to restore hotkey dialog: {e}")
    
    def _center_window(self):
                     
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_widgets(self):
                    

        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)
        
        title_label = ttk.Label(
            title_frame,
            text=t("hotkey.dialog.heading"),
            font=("Microsoft YaHei UI", 12, "bold")
        )
        title_label.pack()
        

        current_frame = ttk.Frame(self.root, padding="10")
        current_frame.pack(fill=tk.X)
        
        ttk.Label(current_frame, text=t("hotkey.dialog.current_hotkey")).pack(side=tk.LEFT)
        ttk.Label(
            current_frame,
            text=self._format_hotkey(self.current_hotkey),
            font=("Consolas", 10, "bold")
        ).pack(side=tk.LEFT, padx=5)
        

        input_frame = ttk.Frame(self.root, padding="10")
        input_frame.pack(fill=tk.X)
        
        ttk.Label(input_frame, text=t("hotkey.dialog.new_hotkey")).pack(side=tk.LEFT)
        
        self.hotkey_entry = ttk.Entry(
            input_frame,
            font=("Consolas", 10),
            state="readonly",
            width=25
        )
        self.hotkey_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        

        record_frame = ttk.Frame(self.root, padding="10")
        record_frame.pack(fill=tk.X)
        
        self.record_btn = ttk.Button(
            record_frame,
            text=t("hotkey.dialog.record_button"),
            command=self._start_recording
        )
        self.record_btn.pack()
        

        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        cancel_btn = ttk.Button(
            button_frame,
            text=t("hotkey.dialog.cancel_button"),
            command=self._on_cancel,
            width=12
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        self.save_btn = ttk.Button(
            button_frame,
            text=t("hotkey.dialog.save_button"),
            command=self._on_save,
            state=tk.DISABLED,
            width=12
        )
        self.save_btn.pack(side=tk.RIGHT, padx=5)
    
    def _format_hotkey(self, hotkey: str) -> str:
                     
        return hotkey.replace("<", "").replace(">", "").replace("+", " + ").title()
    
    def _start_recording(self):
                    
        self.new_hotkey = None
        
        self.record_btn.config(text=t("hotkey.dialog.recording_button"), state=tk.DISABLED)
        self.hotkey_entry.config(state=tk.NORMAL)
        self.hotkey_entry.delete(0, tk.END)
        self.hotkey_entry.insert(0, t("hotkey.dialog.waiting_input"))
        self.hotkey_entry.config(state="readonly")
        
        if is_macos():
            self._stop_tk_recording()
            self._tk_recording = True
            self.root.focus_force()
            self._tk_press_binding = self.root.bind("<KeyPress>", self._tk_on_key_press, add="+")
            self._tk_release_binding = self.root.bind("<KeyRelease>", self._tk_on_key_release, add="+")
        else:

            assert self.recorder is not None
            self.recorder.start_recording(
                on_update=self._on_recording_update,
                on_finish=self._on_recording_finish
            )
    
    def _on_recording_update(self, display_text: str):
                          
        self.root.after(0, lambda: self._set_entry_text(display_text))
    
    def _on_recording_finish(self, hotkey_str: Optional[str], error: Optional[str]):
                    
        if error:

            self.root.after(0, lambda: messagebox.showwarning(t("hotkey.dialog.invalid_title"), error))
            self.root.after(0, self._reset_recording)
        elif hotkey_str:

            self.new_hotkey = hotkey_str
            self.root.after(0, self._enable_save_button)
        else:

            self.root.after(0, self._reset_recording)
    
    def _set_entry_text(self, text: str):
                           
        self.hotkey_entry.config(state=tk.NORMAL)
        self.hotkey_entry.delete(0, tk.END)
        self.hotkey_entry.insert(0, text)
        self.hotkey_entry.config(state="readonly")
    
    def _enable_save_button(self):
                    
        self.save_btn.config(state=tk.NORMAL)
        self.record_btn.config(text=t("hotkey.dialog.record_again"), state=tk.NORMAL)
    
    def _reset_recording(self):
                    
        self.record_btn.config(text=t("hotkey.dialog.record_button"), state=tk.NORMAL)
        self.hotkey_entry.config(state=tk.NORMAL)
        self.hotkey_entry.delete(0, tk.END)
        self.hotkey_entry.config(state="readonly")
    
    def _on_save(self):
                  
        if not self.new_hotkey:
            messagebox.showwarning(t("hotkey.dialog.notice_title"), t("hotkey.dialog.record_first"))
            return
        

        confirm_msg = t(
            "hotkey.dialog.confirm_message",
            old_hotkey=self._format_hotkey(self.current_hotkey),
            new_hotkey=self._format_hotkey(self.new_hotkey)
        )
        
        if not messagebox.askyesno(t("hotkey.dialog.confirm_title"), confirm_msg):
            return
        

        if not HotkeyChecker.is_hotkey_available(self.new_hotkey):
            conflict_msg = t(
                "hotkey.dialog.conflict_message",
                hotkey=self._format_hotkey(self.new_hotkey)
            )
            if not messagebox.askyesno(t("hotkey.dialog.conflict_title"), conflict_msg, icon='warning'):
                return

        try:
            self._cleanup()

            self.on_save(self.new_hotkey)
            if not is_macos():
                messagebox.showinfo("成功", f"热键已更新为：{self._format_hotkey(self.new_hotkey)}\n\n请使用新热键测试功能�?)
            self._safe_destroy()
            self._schedule_on_close_callback()
        except Exception as e:
            log(f"Failed to save hotkey: {e}")
            messagebox.showerror("错误", f"保存热键失败：{str(e)}")
    
    def _cleanup(self):
                  
        try:
            if is_macos():
                self._stop_tk_recording()
            elif self.recorder is not None:
                self.recorder.stop_recording()
        except Exception as e:
            log(f"Error stopping recorder: {e}")
    
    def _safe_destroy(self):
                            
        try:
            self.root.destroy()
        except Exception as e:

            if "Tcl_AsyncDelete" not in str(e):
                log(f"Error destroying window: {e}")
    
    def _on_close(self):
                    
        self._cleanup()
        self._safe_destroy()
        self._schedule_on_close_callback()
    
    def _on_cancel(self):
                  
        self._cleanup()
        self._safe_destroy()
        self._schedule_on_close_callback()
    
    def show(self):
                   
        try:
            if app_state.root and app_state.root.winfo_exists():
                self.root.transient(app_state.root)
            else:
                self.root.transient(None)
            self.root.deiconify()
            self.restore_and_focus()
        except Exception as e:
            log(f"Error showing hotkey dialog: {e}")
