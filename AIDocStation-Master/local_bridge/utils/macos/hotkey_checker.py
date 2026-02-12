# -*- coding: utf-8 -*-
"""
@File    : local_bridge/utils/macos/hotkey_checker.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from typing import Optional, Set, Tuple
import Quartz

from ...i18n import t
from ...utils.logging import log

MODIFIER_KEYS = {"ctrl", "shift", "alt", "cmd", "option", "command"}


SYSTEM_HOTKEY_DESCRIPTIONS = {
    ('cmd', 'c'): "hotkey.recorder.system.cmd_c",
    ('cmd', 'v'): "hotkey.recorder.system.cmd_v",
    ('cmd', 'x'): "hotkey.recorder.system.cmd_x",
    ('cmd', 'z'): "hotkey.recorder.system.cmd_z",
    ('cmd', 'shift', 'z'): "hotkey.recorder.system.cmd_shift_z",
    ('cmd', 'a'): "hotkey.recorder.system.cmd_a",
    ('cmd', 's'): "hotkey.recorder.system.cmd_s",
    ('cmd', 'f'): "hotkey.recorder.system.cmd_f",
    ('cmd', 'p'): "hotkey.recorder.system.cmd_p",
    ('cmd', 'n'): "hotkey.recorder.system.cmd_n",
    ('cmd', 'w'): "hotkey.recorder.system.cmd_w",
    ('cmd', 't'): "hotkey.recorder.system.cmd_t",
    ('cmd', 'q'): "hotkey.recorder.system.cmd_q",
    ('cmd', 'tab'): "hotkey.recorder.system.cmd_tab",
    ('cmd', 'space'): "hotkey.recorder.system.cmd_space",
}


KEY_CODE_MAP = {
    'a': 0x00, 'b': 0x0B, 'c': 0x08, 'd': 0x02, 'e': 0x0E,
    'f': 0x03, 'g': 0x05, 'h': 0x04, 'i': 0x22, 'j': 0x26,
    'k': 0x28, 'l': 0x25, 'm': 0x2E, 'n': 0x2D, 'o': 0x1F,
    'p': 0x23, 'q': 0x0C, 'r': 0x0F, 's': 0x01, 't': 0x11,
    'u': 0x20, 'v': 0x09, 'w': 0x0D, 'x': 0x07, 'y': 0x10, 'z': 0x06,
    '0': 0x1D, '1': 0x12, '2': 0x13, '3': 0x14, '4': 0x15,
    '5': 0x17, '6': 0x16, '7': 0x1A, '8': 0x1C, '9': 0x19,
    'space': 0x31, 'enter': 0x24, 'tab': 0x30, 'delete': 0x33, 'escape': 0x35, 'esc': 0x35,
    'f1': 0x7A, 'f2': 0x78, 'f3': 0x63, 'f4': 0x76, 'f5': 0x60,
    'f6': 0x61, 'f7': 0x62, 'f8': 0x64, 'f9': 0x65, 'f10': 0x6D,
    'f11': 0x67, 'f12': 0x6F, 'f13': 0x69, 'f14': 0x6B, 'f15': 0x71,
    'left': 0x7B, 'right': 0x7C, 'down': 0x7D, 'up': 0x7E,
    'home': 0x73, 'end': 0x77, 'page_up': 0x74, 'page_down': 0x79,
    '-': 0x1B, '=': 0x18, '[': 0x21, ']': 0x1E, '\\': 0x2A,
    ';': 0x29, "'": 0x27, ',': 0x2B, '.': 0x2F, '/': 0x2C, '`': 0x32,
}


class HotkeyChecker:
                                           

    @staticmethod
    def _split_hotkey_keys(hotkey_str: str) -> Set[str]:
                         
        keys = set()
        for part in hotkey_str.lower().replace("<", "").replace(">", "").split("+"):
            part = part.strip()
            if part:

                if part in ('command', 'cmd'):
                    keys.add('cmd')
                elif part in ('option', 'alt'):
                    keys.add('alt')
                else:
                    keys.add(part)
        return keys

    @staticmethod
    def validate_hotkey_keys(
        keys: Set[str],
        *,
        hotkey_repr: str = "",
        detailed: bool = False,
    ) -> Optional[str]:
        


           

        normalized_keys = set()
        for key in keys:
            if key in ('command', 'cmd'):
                normalized_keys.add('cmd')
            elif key in ('option', 'alt'):
                normalized_keys.add('alt')
            else:
                normalized_keys.add(key)
        
        has_modifier = bool(normalized_keys & MODIFIER_KEYS)
        has_normal_key = bool(normalized_keys - MODIFIER_KEYS)

        if not has_modifier:
            return t("hotkey.recorder.error.no_modifier")

        if not has_normal_key:
            return t("hotkey.recorder.error.no_normal_key")

        if normalized_keys & MODIFIER_KEYS == {"shift"}:
            translation_key = "hotkey.recorder.error.shift_only_long" if detailed else "hotkey.recorder.error.shift_only_short"
            return t(translation_key)


        for combo, desc_key in SYSTEM_HOTKEY_DESCRIPTIONS.items():
            if normalized_keys == set(combo):
                if detailed:
                    return t("hotkey.recorder.error.system_reserved_long", combo=t(desc_key))
                combo_text = hotkey_repr.upper() if hotkey_repr else "+".join(combo).upper()
                return t("hotkey.recorder.error.system_reserved_short", combo=combo_text)

        return None

    @staticmethod
    def validate_hotkey_string(hotkey_str: str, *, detailed: bool = False) -> Optional[str]:
        

           
        try:
            keys = HotkeyChecker._split_hotkey_keys(hotkey_str)
            return HotkeyChecker.validate_hotkey_keys(
                keys,
                hotkey_repr=hotkey_str,
                detailed=detailed,
            )
        except Exception as e:
            return t("hotkey.recorder.error.invalid_format", error=str(e))

    @staticmethod
    def parse_hotkey(hotkey_str: str) -> Optional[Tuple[int, int]]:
        







           
        try:
            parts = hotkey_str.lower().replace("<", "").replace(">", "").split("+")
            modifiers = 0
            key_code = None
            
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                    
                if part in ('ctrl', 'control'):
                    modifiers |= Quartz.kCGEventFlagMaskControl
                elif part in ('alt', 'option'):
                    modifiers |= Quartz.kCGEventFlagMaskAlternate
                elif part == 'shift':
                    modifiers |= Quartz.kCGEventFlagMaskShift
                elif part in ('cmd', 'command'):
                    modifiers |= Quartz.kCGEventFlagMaskCommand
                else:

                    if part in KEY_CODE_MAP:
                        key_code = KEY_CODE_MAP[part]
                    
            if key_code is None:
                return None
                
            return modifiers, key_code
        except Exception as e:
            log(f"Error parsing hotkey {hotkey_str}: {e}")
            return None

    @staticmethod
    def is_hotkey_available(hotkey_str: str) -> bool:
        










           

        error = HotkeyChecker.validate_hotkey_string(hotkey_str)
        if error:
            log(f"Hotkey {hotkey_str} validation failed: {error}")
            return False
        

        parsed = HotkeyChecker.parse_hotkey(hotkey_str)
        if not parsed:
            log(f"Could not parse hotkey for checking: {hotkey_str}")
            return False
        




        
        return True
