# -*- coding: utf-8 -*-
"""
@File    : local_bridge/i18n/__init__.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from __future__ import annotations

import json
import locale
import logging
import os
from typing import Dict, Iterator, Optional
from ..config.paths import resource_path


DEFAULT_LANGUAGE = "zh"


LANGUAGE_DISPLAY_NAMES: Dict[str, str] = {
    "auto": "跟随系统 (Follow System)",
    "zh": "简体中�?,
    "en": "English",
}

_LOCALE_PACKAGE = "local_bridge.i18n.locales"
_LOCALE_FILES = {
    "zh": "zh.json",
    "en": "en.json",
}

_loaded_translations: Dict[str, Dict[str, str]] = {}
_current_language = DEFAULT_LANGUAGE
_logger = logging.getLogger(__name__)


def _normalize_language_code(language: Optional[str]) -> Optional[str]:
                                                                   
    if not language:
        return None
    normalized = language.replace("_", "-").split("-")[0].lower()
    return normalized or None


def _load_translations(language: str) -> Dict[str, str]:
                                                                                     
    normalized = _normalize_language_code(language) or DEFAULT_LANGUAGE
    if normalized in _loaded_translations:
        return _loaded_translations[normalized]

    data: Dict[str, str] = {}
    file_name = _LOCALE_FILES.get(normalized)

    if file_name:
        try:
            json_path = resource_path(os.path.join("i18n", "locales", file_name))
            if not os.path.isfile(json_path):
                 _logger.warning("Locale file not found at: %s", json_path)

            with open(json_path, "r", encoding="utf-8") as fp:
                loaded = json.load(fp)

            if isinstance(loaded, dict):
                data = {str(k): str(v) for k, v in loaded.items()}
        
        except FileNotFoundError:
            _logger.warning("Translation file missing for %s at %s", normalized, json_path)
        except Exception as exc:
            _logger.warning("Failed to load translations for %s: %s", normalized, exc)

    _loaded_translations[normalized] = data or {}
    return _loaded_translations[normalized]



_load_translations(DEFAULT_LANGUAGE)


def is_supported_language(language: Optional[str]) -> bool:
                                                              
    normalized = _normalize_language_code(language)
    return bool(normalized and normalized in LANGUAGE_DISPLAY_NAMES)


def set_language(language: str) -> None:
                                                                                   
    global _current_language
    normalized = _normalize_language_code(language)
    
    if normalized == "auto":
        _current_language = "auto"

        sys_lang = detect_system_language() or "en"
        _load_translations(sys_lang)
    elif normalized in LANGUAGE_DISPLAY_NAMES:
        _current_language = normalized
        _load_translations(_current_language)
    else:
        _current_language = DEFAULT_LANGUAGE
        _load_translations(_current_language)


def get_language() -> str:
                                              
    return _current_language


def get_language_label(language: str) -> str:
                                                              
    normalized = _normalize_language_code(language) or language
    return LANGUAGE_DISPLAY_NAMES.get(normalized, language)


def iter_languages() -> Iterator[tuple[str, str]]:
                                                        
    for code, label in LANGUAGE_DISPLAY_NAMES.items():
        yield code, label


def detect_system_language() -> Optional[str]:
    




       
    candidates: list[str | None] = []


    try:
        import ctypes
        from locale import windows_locale

        lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        candidates.append(windows_locale.get(lang_id))
    except Exception:
        pass


    try:
        lang, _encoding = locale.getdefaultlocale()
        candidates.append(lang)
    except (ValueError, TypeError):
        pass

    try:
        lang, _encoding = locale.getlocale()
        candidates.append(lang)
    except (ValueError, TypeError):
        pass

    for candidate in candidates:
        normalized = _normalize_language_code(candidate)
        if normalized and normalized in LANGUAGE_DISPLAY_NAMES:
            return normalized

    return None


def t(key: str, **kwargs) -> str:
    





       
    lookup_lang = _current_language
    if lookup_lang == "auto":
        lookup_lang = detect_system_language() or "en"

    translations = _load_translations(lookup_lang)
    text = translations.get(key)

    if text is None and lookup_lang != DEFAULT_LANGUAGE:
        text = _load_translations(DEFAULT_LANGUAGE).get(key)

    if text is None:

        for data in _loaded_translations.values():
            if key in data:
                text = data[key]
                break

    if text is None:
        text = key

    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            pass

    return text


def get_no_app_action_map() -> Dict[str, str]:
                              



    return {
        "open": t("action.open"),
        "save": t("action.save"),
        "clipboard": t("action.clipboard"),
        "none": t("action.none"),
    }
