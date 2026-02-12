# -*- coding: utf-8 -*-
"""
@File    : local_bridge/service/document/generator_bak.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:42
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import os
from typing import Optional, List

from ...integrations.pandoc import PandocIntegration
from ...utils.docx_processor import DocxProcessor
from ...utils.logging import log
from ...core.state import app_state
from ...core.errors import PandocError
from ...config.defaults import DEFAULT_CONFIG
from ...config.loader import ConfigLoader
from ...config.paths import resource_path
from ...utils.reference_doc import get_or_create_reference_docx


def _get_default_reference_docx() -> Optional[str]:
    


       
    resources_dir = resource_path("resources")
    return get_or_create_reference_docx(resources_dir)


_DEFAULT_PANDOC_REQUEST_HEADERS: List[str] = [
    "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]


def _get_pandoc_request_headers(config: dict) -> List[str]:
    if "pandoc_request_headers" not in config:
        return _DEFAULT_PANDOC_REQUEST_HEADERS

    headers = config.get("pandoc_request_headers")
    if headers is None:
        return []
    if isinstance(headers, str):
        return [headers]
    if isinstance(headers, list):
        return [h.strip() for h in headers if isinstance(h, str) and h.strip()]
    return []


def _mask_pandoc_request_headers(headers: List[str]) -> List[str]:
    masked: List[str] = []
    sensitive_names = {
        "authorization",
        "proxy-authorization",
        "cookie",
        "set-cookie",
        "x-api-key",
        "x-auth-token",
    }

    for raw in headers:
        if not isinstance(raw, str):
            continue
        raw = raw.strip()
        if not raw:
            continue

        name, sep, value = raw.partition(":")
        if not sep:
            masked.append(raw[:300] + "...(truncated)" if len(raw) > 300 else raw)
            continue

        header_name = name.strip()
        header_value = value.strip()
        if header_name.lower() in sensitive_names:
            masked.append(f"{header_name}: <redacted>")
            continue

        if len(header_value) > 300:
            header_value = header_value[:300] + "...(truncated)"
        masked.append(f"{header_name}: {header_value}")

    return masked


def _normalize_filters(value) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, (list, tuple)):
        return [item.strip() for item in value if isinstance(item, str) and item.strip()]
    return []


def _get_pandoc_filters(config: dict, key: str) -> List[str]:
    global_filters = _normalize_filters(config.get("pandoc_filters"))

    per_filters: List[str] = []
    by_conversion = config.get("pandoc_filters_by_conversion")
    if isinstance(by_conversion, dict):
        per_filters.extend(_normalize_filters(by_conversion.get(key)))

    per_filters.extend(_normalize_filters(config.get(f"pandoc_filters_{key}")))

    combined = []
    seen = set()
    for item in global_filters + per_filters:
        if item not in seen:
            combined.append(item)
            seen.add(item)
    return combined


class DocumentGenerator:
    









       
    
    def __init__(self) -> None:
        self._pandoc_integration: Optional[PandocIntegration] = None
    
    def _ensure_pandoc_integration(self) -> None:
        








           
        if self._pandoc_integration is not None:
            return
        
        pandoc_path = app_state.config.get("pandoc_path", "pandoc")
        try:
            self._pandoc_integration = PandocIntegration(pandoc_path)
        except PandocError as e:
            log(f"Failed to initialize PandocIntegration: {e}")

            try:
                default_path = DEFAULT_CONFIG.get("pandoc_path", "pandoc")
                self._pandoc_integration = PandocIntegration(default_path)

                app_state.config["pandoc_path"] = default_path
                config_loader = ConfigLoader()
                config_loader.save(config=app_state.config)
                log(f"Fallback to default pandoc_path: {default_path}")
            except PandocError as e2:
                log(f"Retry to initialize PandocIntegration failed: {e2}")
                self._pandoc_integration = None
                raise PandocError(f"Pandoc initialization failed: {e2}")
    
    def convert_markdown_to_docx_bytes(self, md_text: str, config: dict) -> bytes:
        














           

        self._ensure_pandoc_integration()
        request_headers = _get_pandoc_request_headers(config)
        if "pandoc_request_headers" in config and request_headers != _DEFAULT_PANDOC_REQUEST_HEADERS:
            log(
                f"pandoc_request_headers (effective): {_mask_pandoc_request_headers(request_headers)}"
            )

        filters = _get_pandoc_filters(config, "md_to_docx")
        from ...integrations.pandoc import LUA_DOCX_BODY_MAP
        if LUA_DOCX_BODY_MAP not in filters:
            filters.append(LUA_DOCX_BODY_MAP)
        

        if "```{.mermaid}" in md_text or "```mermaid" in md_text:
            mermaid_filter = "mermaid-filter"
            if mermaid_filter not in filters:
                filters.insert(0, mermaid_filter)
                log(f"[Generator] Added mermaid-filter for Mermaid diagrams")
        
        body_style = config.get("body_style", "正文")
        log(f"[Generator] Applying body style: '{body_style}' via Lua AST")

        metadata = {
            "body_style": body_style,
            "body-style": body_style
        }


        reference_docx = config.get("reference_docx")
        if not reference_docx:
            reference_docx = _get_default_reference_docx()
            if reference_docx:
                log(f"[Generator] Using default reference document for style mapping")

        docx_bytes = self._pandoc_integration.convert_to_docx_bytes(
            md_text=md_text,
            reference_docx=reference_docx,
            Keep_original_formula=config.get("Keep_original_formula", False),
            enable_latex_replacements=config.get("enable_latex_replacements", True),
            custom_filters=filters,
            request_headers=request_headers,
            cwd=config.get("save_dir"),
            metadata=metadata,
        )
        

        image_style = config.get("image_style", "正文")
        image_scale_str = config.get("image_scale_rule", "100%")

        try:
            image_scale = int(image_scale_str.replace("%", ""))
        except:
            image_scale = 100


        docx_bytes = DocxProcessor.apply_custom_processing(
            docx_bytes,
            disable_first_para_indent=config.get("md_disable_first_para_indent", True),
            target_style="Body Text",
            add_table_borders=config.get("table_border_default", True),
            table_autofit=True,
            table_text_style=config.get("table_text_style", "正文"),
            body_style=config.get("body_style", "正文"),
            image_style=image_style,
            image_scale=image_scale
        )
        
        return docx_bytes
    
    def convert_html_to_docx_bytes(self, html_text: str, config: dict) -> bytes:
        











           

        self._ensure_pandoc_integration()
        request_headers = _get_pandoc_request_headers(config)
        if "pandoc_request_headers" in config and request_headers != _DEFAULT_PANDOC_REQUEST_HEADERS:
            log(
                f"pandoc_request_headers (effective): {_mask_pandoc_request_headers(request_headers)}"
            )

        filters = _get_pandoc_filters(config, "html_to_docx")
        from ...integrations.pandoc import LUA_DOCX_BODY_MAP
        if LUA_DOCX_BODY_MAP not in filters:
            filters.append(LUA_DOCX_BODY_MAP)
        
        body_style = config.get("body_style", "正文")
        log(f"[Generator] Applying body style: '{body_style}' via Lua AST (HTML)")
        metadata = {
            "body_style": body_style,
            "body-style": body_style
        }


        reference_docx = config.get("reference_docx")
        if not reference_docx:
            reference_docx = _get_default_reference_docx()
            if reference_docx:
                log(f"[Generator] Using default reference document for style mapping (HTML)")

        docx_bytes = self._pandoc_integration.convert_html_to_docx_bytes(
            html_text=html_text,
            reference_docx=reference_docx,
            Keep_original_formula=config.get("Keep_original_formula", False),
            enable_latex_replacements=config.get("enable_latex_replacements", True),
            custom_filters=filters,
            custom_filters_html_to_md=_get_pandoc_filters(config, "html_to_md"),
            custom_filters_md_to_docx=_get_pandoc_filters(config, "md_to_docx"),
            request_headers=request_headers,
            cwd=config.get("save_dir"),
            metadata=metadata,
        )
        

        docx_bytes = DocxProcessor.apply_custom_processing(
            docx_bytes,
            disable_first_para_indent=config.get("html_disable_first_para_indent", True),
            target_style="Body Text",
            add_table_borders=config.get("table_border_default", True),
            table_autofit=True,
            table_text_style=config.get("table_text_style", "正文"),
            body_style=config.get("body_style", "正文")
        )
        
        return docx_bytes

    def convert_html_to_markdown_text(self, html_text: str, config: dict) -> str:
        




           
        self._ensure_pandoc_integration()
        return self._pandoc_integration.convert_html_to_markdown_text(
            html_text,
            custom_filters=_get_pandoc_filters(config, "html_to_md"),
        )

    def convert_markdown_to_html_text(self, md_text: str, config: dict) -> str:
        




           
        self._ensure_pandoc_integration()
        return self._pandoc_integration.convert_markdown_to_html_text(
            md_text,
            Keep_original_formula=config.get("Keep_original_formula", True),
            enable_latex_replacements=config.get("enable_latex_replacements", True),
            custom_filters=_get_pandoc_filters(config, "md_to_html"),
            cwd=config.get("save_dir"),
        )

    def convert_markdown_to_rtf_bytes(self, md_text: str, config: dict) -> bytes:
        

           
        self._ensure_pandoc_integration()
        request_headers = _get_pandoc_request_headers(config)
        if "pandoc_request_headers" in config and request_headers != _DEFAULT_PANDOC_REQUEST_HEADERS:
            log(
                f"pandoc_request_headers (effective): {_mask_pandoc_request_headers(request_headers)}"
            )
        return self._pandoc_integration.convert_markdown_to_rtf_bytes(
            md_text,
            Keep_original_formula=config.get("Keep_original_formula", True),
            enable_latex_replacements=config.get("enable_latex_replacements", True),
            custom_filters=_get_pandoc_filters(config, "md_to_rtf"),
            request_headers=request_headers,
            cwd=config.get("save_dir"),
        )

    def convert_html_to_latex_text(self, html_text: str, config: dict) -> str:
        




           
        self._ensure_pandoc_integration()
        return self._pandoc_integration.convert_html_to_latex_text(
            html_text,
            strip_preamble=True,
            custom_filters_html_to_md=_get_pandoc_filters(config, "html_to_md"),
            custom_filters_md_to_latex=_get_pandoc_filters(config, "md_to_latex"),
        )

    def convert_markdown_to_latex_text(self, md_text: str, config: dict) -> str:
        




           
        self._ensure_pandoc_integration()
        return self._pandoc_integration.convert_markdown_to_latex_text(
            md_text,
            strip_preamble=True,
            enable_latex_replacements=config.get("enable_latex_replacements", True),
            custom_filters=_get_pandoc_filters(config, "md_to_latex"),
        )
