# -*- coding: utf-8 -*-
"""
@File    : local_bridge/service/hotkey/manager.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import threading
import ctypes
import time
from typing import Optional, Callable, Dict, Tuple
from ctypes import windll, byref, Structure, c_int, c_uint, c_void_p, POINTER
from pynput import keyboard

from ...utils.logging import log
from ...utils.system_detect import is_macos
from ...core.state import app_state


user32 = windll.user32


WM_HOTKEY = 0x0312
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000


VK_MAP: Dict[str, int] = {
    'backspace': 0x08, 'tab': 0x09, 'enter': 0x0D, 'pause': 0x13, 'caps_lock': 0x14, 'esc': 0x1B,
    'space': 0x20, 'page_up': 0x21, 'page_down': 0x22, 'end': 0x23, 'home': 0x24,
    'left': 0x25, 'up': 0x26, 'right': 0x27, 'down': 0x28,
    'print_screen': 0x2C, 'insert': 0x2D, 'delete': 0x2E,
    '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
    '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39,
    'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45,
    'f': 0x46, 'g': 0x47, 'h': 0x48, 'i': 0x49, 'j': 0x4A,
    'k': 0x4B, 'l': 0x4C, 'm': 0x4D, 'n': 0x4E, 'o': 0x4F,
    'p': 0x50, 'q': 0x51, 'r': 0x52, 's': 0x53, 't': 0x54,
    'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58, 'y': 0x59, 'z': 0x5A,
    'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73, 'f5': 0x74,
    'f6': 0x75, 'f7': 0x76, 'f8': 0x77, 'f9': 0x78, 'f10': 0x79,
    'f11': 0x7A, 'f12': 0x7B,
    'num0': 0x60, 'num1': 0x61, 'num2': 0x62, 'num3': 0x63, 'num4': 0x64,
    'num5': 0x65, 'num6': 0x66, 'num7': 0x67, 'num8': 0x68, 'num9': 0x69,
    'multiply': 0x6A, 'add': 0x6B, 'separator': 0x6C, 'subtract': 0x6D, 'decimal': 0x6E, 'divide': 0x6F,
    ';': 0xBA, '=': 0xBB, ',': 0xBC, '-': 0xBD, '.': 0xBE, '/': 0xBF, '`': 0xC0,
    '[': 0xDB, '\\': 0xDC, ']': 0xDD, "'": 0xDE,
}

class POINT(Structure):
    _fields_ = [("x", c_int), ("y", c_int)]

class MSG(Structure):
    _fields_ = [
        ('hwnd', c_void_p),
        ('message', c_uint),
        ('wParam', c_void_p),
        ('lParam', c_void_p),
        ('time', c_uint),
        ('pt', POINT),
    ]

class HotkeyManager:
                                             
    
    def _print_debug(self, msg):
        import sys
        try:
            sys.stdout.write(f"[HotkeyManager] {msg}\n")
            sys.stdout.flush()
        except: pass
    
    def __init__(self):
        self._print_debug("HotkeyManager Initializing (v7.03 - RELEASE focused)")
        self.current_hotkey: Optional[str] = None
        self._mac_listener: Optional[keyboard.Listener] = None
        self._mac_hotkey: Optional[keyboard.HotKey] = None
        self._mac_lock = threading.Lock()
        

        self._win32_thread: Optional[threading.Thread] = None
        self._win32_stop_event = threading.Event()
        self._win32_hotkey_id = 9001
        self._win32_callback: Optional[Callable[[], None]] = None
        

        self._dc_listener = None
        self._last_key_time = 0
        self._last_key_vk = None
        self._target_key_vk = None
        self._dc_callback: Optional[Callable[[], None]] = None
        




    def _should_ignore_key(self, key) -> bool:

         return False

    def _mac_ensure_listener(self) -> None:

        pass
        
    def _mac_set_hotkey(self, hotkey, callback):

        pass




    

    _active_hotkeys: Dict[str, Tuple[threading.Event, threading.Thread]] = {}

    def _parse_hotkey_win32(self, hotkey_str: str) -> Optional[Tuple[int, int]]:
                                                                       
        try:
            parts = hotkey_str.lower().replace("<", "").replace(">", "").split("+")
            modifiers = 0
            vk_code = 0
            for part in parts:
                part = part.strip()
                if not part: continue
                if part == 'ctrl': modifiers |= MOD_CONTROL
                elif part == 'alt': modifiers |= MOD_ALT
                elif part == 'shift': modifiers |= MOD_SHIFT
                elif part in ('cmd', 'win'): modifiers |= MOD_WIN
                else:
                    if part in VK_MAP:
                        vk_code = VK_MAP[part]
                    elif len(part) == 1:
                        res = user32.VkKeyScanW(ord(part))
                        if res != -1:
                            vk_code = res & 0xFF
            
            if vk_code == 0: return None

            modifiers |= MOD_NOREPEAT
            return modifiers, vk_code
        except Exception as e:
            log(f"Error parsing hotkey {hotkey_str}: {e}")
            return None

    def _win32_msg_loop(self, modifiers, vk, hotkey_id, callback, stop_event):
                                           
        self._print_debug(f"Starting Win32 hotkey loop for ID {hotkey_id} (Mods={modifiers}, VK={vk})")
        

        if not user32.RegisterHotKey(None, hotkey_id, modifiers, vk):
            err = ctypes.get_last_error()
            self._print_debug(f"FATAL: Failed to register hotkey ID {hotkey_id}. Error Code: {err}")
            return
        else:
            self._print_debug(f"SUCCESS: Hotkey ID {hotkey_id} registered.")

        msg = MSG()
        try:
            while not stop_event.is_set():
                if user32.PeekMessageW(byref(msg), None, 0, 0, 1):
                    if msg.message == WM_HOTKEY:
                        if msg.wParam == hotkey_id:
                            self._print_debug(f"TRIGGER: Global Hotkey ID {hotkey_id}")
                            try:
                                callback()
                            except Exception as e:
                                self._print_debug(f"Callback error: {e}")
                                    
                    user32.TranslateMessage(byref(msg))
                    user32.DispatchMessageW(byref(msg))
                
                time.sleep(0.01)
        finally:
            user32.UnregisterHotKey(None, hotkey_id)
            self._print_debug(f"Win32 hotkey loop stopped for ID {hotkey_id}")

    def bind(self, hotkey: str, callback: Callable[[], None]) -> None:
                           
        if is_macos():

            return


        if hotkey in self._active_hotkeys:
            log(f"Hotkey {hotkey} already bound, ignoring re-bind.")
            return

        parsed = self._parse_hotkey_win32(hotkey)
        if not parsed:
            log(f"Invalid hotkey format for Win32: {hotkey}")
            return
            
        mods, vk = parsed
        


        hotkey_id = abs(hash(hotkey)) % 20000 + 1000
        
        stop_event = threading.Event()
        t = threading.Thread(
            target=self._win32_msg_loop,
            args=(mods, vk, hotkey_id, callback, stop_event),
            daemon=True,
            name=f"Hotkey-{hotkey}"
        )
        t.start()
        
        self._active_hotkeys[hotkey] = (stop_event, t)
        log(f"Win32 Hotkey bound: {hotkey} (ID: {hotkey_id})")

    def unbind(self, hotkey: str = None) -> None:
                              
        if is_macos():
            return

        targets = list(self._active_hotkeys.keys()) if hotkey is None else [hotkey]
        
        for key in targets:
            if key in self._active_hotkeys:
                stop_event, t = self._active_hotkeys.pop(key)
                stop_event.set()


                log(f"Hotkey unbound triggered for: {key}")

    def is_bound(self, hotkey: str) -> bool:
        return hotkey in self._active_hotkeys

    def resume(self, callback: Callable[[], None]) -> None:
        pass


    def start_double_click_listener(self, callback: Optional[Callable[[], None]] = None):
                     

        if callback:
            self._dc_callback = callback
            
        if not app_state.config.get("enable_double_click_paste", False):
            self._print_debug("Double-click paste disabled in config, not starting.")
            return


        if self._mac_listener:
             self._print_debug("Stopping existing double-click listener...")
             try:
                 self._mac_listener.stop()
                 self._mac_listener = None
             except Exception as e:
                 self._print_debug(f"Error stopping existing listener: {e}")
        

        self._last_key_time = 0
        self._last_key_vk = None
        

        target_str = app_state.config.get("double_click_paste_key", "ctrl_l")
        self._target_key_vk = self._parse_pynput_key(target_str)
        
        log(f"[HotkeyManager v7.04] Starting Double-Click listener for {target_str}")

        from pynput import keyboard
        self._mac_listener = keyboard.Listener(
            on_release=self._on_dc_release,


        )
        self._mac_listener.start()

    def stop_double_click_listener(self):
                     
        if self._mac_listener:
            try:
                self._mac_listener.stop()
                self._mac_listener = None
                log("[HotkeyManager] Double-Click listener stopped.")
            except Exception as e:
                log(f"[HotkeyManager] Error stopping listener: {e}")

    def _parse_pynput_key(self, key_str):
        from pynput.keyboard import Key, KeyCode
        key_map = {
            "ctrl_l": Key.ctrl_l,
            "ctrl_r": Key.ctrl_r,
            "ctrl": Key.ctrl,
            "alt_l": Key.alt_l,
            "alt_r": Key.alt_r,
            "alt": Key.alt,
            "shift_l": Key.shift_l,
            "shift_r": Key.shift_r,
            "shift": Key.shift,
            "cmd": Key.cmd,
            "cmd_l": Key.cmd_l,
            "cmd_r": Key.cmd_r,
            "caps_lock": Key.caps_lock,
            "space": Key.space,
            "enter": Key.enter,
            "tab": Key.tab,
            "esc": Key.esc
        }
        if key_str in key_map:
            return key_map[key_str]

        if hasattr(Key, key_str):
            return getattr(Key, key_str)

        if len(key_str) == 1:
            return KeyCode.from_char(key_str.lower())
        return None

    def _normalize_key(self, key):
                                                           
        from pynput.keyboard import Key

        if key in (Key.ctrl_l, Key.ctrl_r): return Key.ctrl
        if key in (Key.shift_l, Key.shift_r): return Key.shift
        if key in (Key.alt_l, Key.alt_r): return Key.alt
        if key in (Key.cmd_l, Key.cmd_r): return Key.cmd
        return key

    def _on_dc_press(self, key):

        pass

    def _on_dc_release(self, key):

        n_key = self._normalize_key(key)
        n_target = self._normalize_key(self._target_key_vk)
        

        if n_key == n_target:
            import time
            current_time = time.time()
            

            if self._last_key_vk == n_key:
                dt = current_time - self._last_key_time
                self._print_debug(f"Target key RELEASE repeat! dt={dt:.3f}s")
                
                if 0.05 < dt < 0.50:
                    self._on_double_click_triggered()
                    self._last_key_time = 0
                    self._last_key_vk = None
                    return
            
            self._last_key_time = current_time
            self._last_key_vk = n_key
        else:


            from pynput.keyboard import Key
            is_mod = n_key in (Key.ctrl, Key.shift, Key.alt, Key.cmd, Key.alt_gr, Key.caps_lock)
            
            if not is_mod:
                if self._last_key_vk is not None:
                    self._print_debug(f"DC Reset by non-mod release: {key}")
                self._last_key_vk = None
                self._last_key_time = 0

    def _on_double_click_triggered(self):

        log("[HotkeyManager] Double-Click Callback Triggering...")
        
        if self._dc_callback:
            try:
                self._dc_callback()
            except Exception as e:
                log(f"[HotkeyManager] Double-click callback error: {e}")
        else:
            log("[HotkeyManager] WARNING: No callback registered for double-click.")
