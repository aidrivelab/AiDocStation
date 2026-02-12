# -*- coding: utf-8 -*-
"""
@File    : local_bridge/service/hotkey/recorder.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from typing import Optional, Callable, Set
from pynput import keyboard

from ...utils.logging import log
from ...utils.hotkey_checker import HotkeyChecker
from ...i18n import t


class HotkeyRecorder:
                              
    
    def __init__(self):
        self.recording = False
        self.pressed_keys: Set[str] = set()
        self.released_keys: Set[str] = set()
        self.all_pressed_keys: Set[str] = set()
        self.recording_listener: Optional[keyboard.Listener] = None
        self.on_update_callback: Optional[Callable[[str], None]] = None
        self.on_finish_callback: Optional[Callable[[Optional[str], Optional[str]], None]] = None
    
    def start_recording(
        self,
        on_update: Optional[Callable[[str], None]] = None,
        on_finish: Optional[Callable[[Optional[str], Optional[str]], None]] = None
    ) -> None:
        





           
        if self.recording:
            return
        
        self.recording = True
        self.pressed_keys.clear()
        self.released_keys.clear()
        self.all_pressed_keys.clear()
        self.on_update_callback = on_update
        self.on_finish_callback = on_finish
        

        self.recording_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self.recording_listener.start()
        log("Hotkey recording started")
    
    def stop_recording(self) -> None:
                  
        self.recording = False
        if self.recording_listener:
            try:
                self.recording_listener.stop()
            except Exception as e:
                log(f"Error stopping recorder listener: {e}")
            finally:
                self.recording_listener = None
        
        self.pressed_keys.clear()
        self.released_keys.clear()
        self.all_pressed_keys.clear()
        log("Hotkey recording stopped")
    
    def _on_key_press(self, key):
                    
        if not self.recording:
            return
        
        try:
            key_name = self._get_key_name(key)
            if key_name:
                self.pressed_keys.add(key_name)
                self.all_pressed_keys.add(key_name)
                self._notify_update()
        except Exception as e:
            log(f"Error in key press handler: {e}")
    
    def _on_key_release(self, key):
                    
        if not self.recording:
            return False
        
        try:
            key_name = self._get_key_name(key)
            if key_name:
                self.released_keys.add(key_name)
                self.pressed_keys.discard(key_name)
                

                if self.all_pressed_keys and self.all_pressed_keys == self.released_keys:

                    self._finish_recording()
                    return False
        except Exception as e:
            log(f"Error in key release handler: {e}")
        
        return True
    
    def _get_key_name(self, key) -> Optional[str]:
                        
        try:

            if key in [keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r]:
                return "ctrl"

            elif key in [keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r]:
                return "shift"

            elif key in [keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r]:
                return "alt"

            elif key == keyboard.Key.cmd:
                return "cmd"
            elif key in [keyboard.Key.cmd_l, keyboard.Key.cmd_r]:
                return "cmd"
            

            if hasattr(key, 'name'):
                key_name = key.name.lower()

                if key_name in ['alt_l', 'alt_r', 'alt_gr']:
                    return "alt"
                elif key_name in ['ctrl_l', 'ctrl_r']:
                    return "ctrl"
                elif key_name in ['shift_l', 'shift_r']:
                    return "shift"
                elif key_name in ['cmd_l', 'cmd_r', 'cmd']:
                    return "cmd"
                return key_name
            


            if hasattr(key, 'vk') and key.vk is not None:
                vk = key.vk

                if 65 <= vk <= 90:
                    return chr(vk).lower()

                elif 48 <= vk <= 57:
                    return chr(vk)

                elif 96 <= vk <= 105:
                    return f"num{vk - 96}"
            


            if hasattr(key, 'char') and key.char:

                if ord(key.char) >= 32:
                    return key.char.lower()
            
            return None
        except Exception as e:
            log(f"Error getting key name: {e}")
            return None
    
    def _notify_update(self) -> None:
                          
        if self.on_update_callback and self.all_pressed_keys:
            display_text = self._format_keys_for_display()
            try:
                self.on_update_callback(display_text)
            except Exception as e:
                log(f"Error in update callback: {e}")
    
    def _format_keys_for_display(self) -> str:
                       
        if not self.all_pressed_keys:
            return ""
        

        modifiers = []
        keys = []
        
        modifier_order = ['ctrl', 'shift', 'alt', 'cmd']
        for mod in modifier_order:
            if mod in self.all_pressed_keys:
                modifiers.append(mod)
        
        for key in self.all_pressed_keys:
            if key not in modifier_order:
                keys.append(key)
        
        all_keys = modifiers + sorted(keys)
        return " + ".join(k.title() for k in all_keys)
    
    def _finish_recording(self) -> None:
                     
        if not self.all_pressed_keys:
            self.stop_recording()
            if self.on_finish_callback:
                self.on_finish_callback(None, t("hotkey.recorder.error.no_key_detected"))
            return
        

        error = self._validate_hotkey()
        if error:
            hotkey_str = None
        else:
            hotkey_str = self._generate_hotkey_string()
        

        self.stop_recording()
        

        if self.on_finish_callback:
            try:
                self.on_finish_callback(hotkey_str, error)
            except Exception as e:
                log(f"Error in finish callback: {e}")
    
    def _validate_hotkey(self) -> Optional[str]:
        




           
        hotkey_preview = self._format_keys_for_display().replace(" + ", "+")
        return HotkeyChecker.validate_hotkey_keys(
            self.all_pressed_keys,
            hotkey_repr=hotkey_preview,
            detailed=True,
        )
    
    def _generate_hotkey_string(self) -> str:
                               

        modifiers = []
        keys = []
        
        modifier_order = ['ctrl', 'shift', 'alt', 'cmd']
        for mod in modifier_order:
            if mod in self.all_pressed_keys:
                modifiers.append(f"<{mod}>")
        
        for key in self.all_pressed_keys:
            if key not in modifier_order:

                if len(key) > 1:
                    keys.append(f"<{key}>")
                else:
                    keys.append(key)
        
        return "+".join(modifiers + sorted(keys))
