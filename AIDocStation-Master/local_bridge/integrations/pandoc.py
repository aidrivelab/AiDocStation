# -*- coding: utf-8 -*-
"""
@File    : local_bridge/integrations/pandoc.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import os
import re
import subprocess
from typing import Optional, List

from ..utils.html_formatter import protect_brackets

from ..config.paths import resource_path

from ..core.errors import PandocError
from ..utils.logging import log

LUA_KEEP_ORIGINAL_FORMULA = resource_path("lua/keep-latex-math.lua")
LUA_LATEX_REPLACEMENTS = resource_path("lua/latex-replacements.lua")
LUA_DOCX_BODY_MAP = resource_path("lua/docx-body-map.lua")
LUA_LIST_TO_TEXT = resource_path("lua/list-to-text.lua")


def _log_pandoc_stderr_as_warning(stderr: Optional[bytes], *, context: str) -> None:
    if not stderr:
        return

    msg = stderr.decode("utf-8", "ignore").strip()
    if not msg:
        return

    max_len = 4000
    if len(msg) > max_len:
        msg = msg[:max_len] + "...(truncated)"

    log(f"{context} (stderr): {msg}")


def _add_request_headers(cmd: List[str], request_headers: Optional[List[str]]) -> List[str]:
    if not request_headers:
        return cmd
    for header in request_headers:
        if not isinstance(header, str):
            continue
        header = header.strip()
        if not header:
            continue
        cmd += ["--request-header", header]
    return cmd


class PandocIntegration:
                     
    
    def __init__(self, pandoc_path: str = "pandoc"):

        cmd = [pandoc_path, "--version"]
        try:
            startupinfo = None
            creationflags = 0
            if os.name == "nt":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                creationflags = subprocess.CREATE_NO_WINDOW
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                shell=False,
                startupinfo=startupinfo,
                creationflags=creationflags,
            )
            if result.returncode != 0:
                raise PandocError(f"Pandoc not found or not working: {result.stderr.strip()}")
        except FileNotFoundError:
            raise PandocError(f"Pandoc executable not found: {pandoc_path}")
        except Exception as e:
            raise PandocError(f"Pandoc Error: {e}")
        self.pandoc_path = pandoc_path

    def _build_metadata_args(self, metadata: Optional[dict] = None) -> List[str]:
                                     
        args = []
        if not metadata:
            return args
        for k, v in metadata.items():
            if v is not None:
                args.extend(["-M", f"{k}={v}"])
        return args

    def _build_filter_args(self, custom_filters: Optional[List[str]] = None) -> List[str]:
        







           
        filter_args = []
        
        if not custom_filters:
            return filter_args
        
        import shutil
        
        for filter_path in custom_filters:

            expanded_path = os.path.expandvars(filter_path)
            

            if expanded_path.lower().endswith('.lua'):
                if not os.path.isabs(expanded_path):
                    expanded_path = os.path.abspath(expanded_path)
                if os.path.exists(expanded_path):
                    filter_args.extend(["--lua-filter", expanded_path])
                else:
                    log(f"Warning: Lua filter file not found, skipping: {expanded_path}")
                continue
            


            which_result = shutil.which(expanded_path)
            if which_result:
                filter_args.extend(["--filter", which_result])
                log(f"Using global filter from PATH: {which_result}")
                continue
            

            if not os.path.isabs(expanded_path):
                expanded_path = os.path.abspath(expanded_path)
            
            if os.path.exists(expanded_path):
                filter_args.extend(["--filter", expanded_path])
            else:
                log(f"Warning: Filter file not found, skipping: {expanded_path}")
        
        return filter_args


    def _convert_html_to_md(
        self,
        html_text: str,
        custom_filters: Optional[List[str]] = None,
    ) -> str:
        

           
        html_text = protect_brackets(html_text)
        cmd = [
            self.pandoc_path,
            "-f", "html+tex_math_dollars+raw_tex+tex_math_double_backslash+tex_math_single_backslash",
            "-t", "gfm-raw_html+tex_math_dollars",
            "-o", "-",
            "--wrap", "none",
        ]
        cmd += self._build_filter_args(custom_filters)

        startupinfo = None
        creationflags = 0
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            creationflags = subprocess.CREATE_NO_WINDOW

        result = subprocess.run(
            cmd,
            input=html_text.encode("utf-8"),
            capture_output=True,
            text=False,
            shell=False,
            startupinfo=startupinfo,
            creationflags=creationflags,
        )
        if result.returncode != 0:
            err = (result.stderr or b"").decode("utf-8", "ignore")
            log(f"Pandoc HTML to MD error: {err}")
            raise PandocError(err or "Pandoc HTML to Markdown conversion failed")


        md = result.stdout.decode("utf-8", "ignore")
        md = md.replace('\r\n', '\n').replace('\r', '\n')
        md = re.sub(r'```\s*math\s*\n(.*?)\n\s*```', r'$$\n\1\n$$', md, flags=re.DOTALL)
        md = re.sub(r'\$\s*`([^`]+)`\s*\$', r'$\1$', md)
        md = re.sub(r'(```\s*\w+)\s+[^\n]+', r'\1', md)

        md = re.sub(r'\\~~(.*?)\\~~', r'~~\1~~', md)

        md = md.replace("{{TASK_CHECKED}}", "[x]").replace("{{TASK_UNCHECKED}}", "[ ]")
        return md

    def convert_html_to_markdown_text(
        self,
        html_text: str,
        *,
        custom_filters: Optional[List[str]] = None,
    ) -> str:
        

           
        return self._convert_html_to_md(html_text, custom_filters)

    def convert_markdown_to_html_text(
        self,
        md_text: str,
        *,
        Keep_original_formula: bool = False,
        enable_latex_replacements: bool = True,
        custom_filters: Optional[List[str]] = None,
        cwd: Optional[str] = None,
    ) -> str:
        





           
        cmd = [
            self.pandoc_path,
            "-f", "markdown+tex_math_dollars+raw_tex+tex_math_double_backslash+tex_math_single_backslash",
            "-t", "html",
            "-o", "-",
            "--wrap", "none",
            "--standalone",
        ]
        if enable_latex_replacements:
            cmd += ["--lua-filter", LUA_LATEX_REPLACEMENTS]
        if Keep_original_formula:
            cmd += ["--lua-filter", LUA_KEEP_ORIGINAL_FORMULA]
        cmd += self._build_filter_args(custom_filters)


        if cwd:
            cwd = os.path.expandvars(cwd)
            os.makedirs(cwd, exist_ok=True)

        startupinfo = None
        creationflags = 0
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            creationflags = subprocess.CREATE_NO_WINDOW

        result = subprocess.run(
            cmd,
            input=md_text.encode("utf-8"),
            capture_output=True,
            text=False,
            shell=False,
            startupinfo=startupinfo,
            creationflags=creationflags,
            cwd=cwd,
        )
        if result.returncode != 0:
            err = (result.stderr or b"").decode("utf-8", "ignore")
            log(f"Pandoc Markdown to HTML error: {err}")
            raise PandocError(err or "Pandoc Markdown to HTML conversion failed")

        return result.stdout.decode("utf-8", "ignore")

    def convert_markdown_to_rtf_bytes(
        self,
        md_text: str,
        *,
        Keep_original_formula: bool = False,
        enable_latex_replacements: bool = True,
        custom_filters: Optional[List[str]] = None,
        request_headers: Optional[List[str]] = None,
        cwd: Optional[str] = None,
    ) -> bytes:
        

           
        cmd = [
            self.pandoc_path,
            "-f", "markdown+tex_math_dollars+raw_tex+tex_math_double_backslash+tex_math_single_backslash",
            "-t", "rtf",
            "-o", "-",
            "--standalone",
        ]
        if enable_latex_replacements:
            cmd += ["--lua-filter", LUA_LATEX_REPLACEMENTS]
        if Keep_original_formula:
            cmd += ["--lua-filter", LUA_KEEP_ORIGINAL_FORMULA]
        cmd += self._build_filter_args(custom_filters)
        cmd = _add_request_headers(cmd, request_headers)


        if cwd:
            cwd = os.path.expandvars(cwd)
            os.makedirs(cwd, exist_ok=True)

        startupinfo = None
        creationflags = 0
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            creationflags = subprocess.CREATE_NO_WINDOW

        result = subprocess.run(
            cmd,
            input=md_text.encode("utf-8"),
            capture_output=True,
            text=False,
            shell=False,
            startupinfo=startupinfo,
            creationflags=creationflags,
            cwd=cwd,
        )
        if result.returncode != 0:
            err = (result.stderr or b"").decode("utf-8", "ignore")
            log(f"Pandoc Markdown to RTF error: {err}")
            raise PandocError(err or "Pandoc Markdown to RTF conversion failed")

        return result.stdout

    def convert_to_docx_bytes(self, md_text: str, reference_docx: Optional[str] = None, Keep_original_formula: bool = False, enable_latex_replacements: bool = True, custom_filters: Optional[List[str]] = None, request_headers: Optional[List[str]] = None, cwd: Optional[str] = None, metadata: Optional[dict] = None) -> bytes:
        












           
        cmd = [
            self.pandoc_path,
            "-f", "markdown+tex_math_dollars+raw_tex+tex_math_double_backslash+tex_math_single_backslash",
            "-t", "docx",
            "-o", "-",
            "--highlight-style", "tango",
        ]
        if enable_latex_replacements:
            cmd += ["--lua-filter", LUA_LATEX_REPLACEMENTS]
        if Keep_original_formula:
            cmd += ["--lua-filter", LUA_KEEP_ORIGINAL_FORMULA]

        cmd += self._build_filter_args(custom_filters)
        if reference_docx:
            cmd += ["--reference-doc", reference_docx]
        cmd += self._build_metadata_args(metadata)
        cmd = _add_request_headers(cmd, request_headers)

        startupinfo = None
        creationflags = 0
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            creationflags = subprocess.CREATE_NO_WINDOW


        if cwd:
            cwd = os.path.expandvars(cwd)
            os.makedirs(cwd, exist_ok=True)


        env = os.environ.copy()
        env["MERMAID_FILTER_SCALE"] = "2"
        env["MERMAID_FILTER_WIDTH"] = "1600"


        result = subprocess.run(
            cmd,
            input=md_text.encode("utf-8"),
            capture_output=True,
            text=False,
            shell=False,
            startupinfo=startupinfo,
            creationflags=creationflags,
            cwd=cwd,
            env=env,
        )
        if result.returncode != 0:

            err = (result.stderr or b"").decode("utf-8", "ignore")
            log(f"Pandoc error: {err}")
            raise PandocError(err or "Pandoc conversion failed")

        _log_pandoc_stderr_as_warning(result.stderr, context="Pandoc warning (MD->DOCX)")
        return result.stdout

    def convert_html_to_docx_bytes(
        self,
        html_text: str,
        reference_docx: Optional[str] = None,
        Keep_original_formula: bool = False,
        enable_latex_replacements: bool = True,
        custom_filters: Optional[List[str]] = None,
        request_headers: Optional[List[str]] = None,
        cwd: Optional[str] = None,
        custom_filters_html_to_md: Optional[List[str]] = None,
        custom_filters_md_to_docx: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
    ) -> bytes:
        















           
        if Keep_original_formula:
            md = self._convert_html_to_md(html_text, custom_filters_html_to_md)
            return self.convert_to_docx_bytes(
                    md_text=md,
                    reference_docx=reference_docx,
                    Keep_original_formula=Keep_original_formula,
                    enable_latex_replacements=enable_latex_replacements,
                    custom_filters=custom_filters_md_to_docx or custom_filters,
                    request_headers=request_headers,
                    cwd=cwd,
                    metadata=metadata,
                )
        
        cmd = [
            self.pandoc_path,
            "-f", "html+tex_math_dollars+raw_tex+tex_math_double_backslash+tex_math_single_backslash",
            "-t", "docx",
            "-o", "-",
            "--highlight-style", "tango",
        ]
        if enable_latex_replacements:
            cmd += ["--lua-filter", LUA_LATEX_REPLACEMENTS]

        cmd += self._build_filter_args(custom_filters)
        if reference_docx:
            cmd += ["--reference-doc", reference_docx]
        cmd += self._build_metadata_args(metadata)
        cmd = _add_request_headers(cmd, request_headers)

        startupinfo = None
        creationflags = 0
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            creationflags = subprocess.CREATE_NO_WINDOW


        if cwd:
            cwd = os.path.expandvars(cwd)
            os.makedirs(cwd, exist_ok=True)


        result = subprocess.run(
            cmd,
            input=html_text.encode("utf-8"),
            capture_output=True,
            text=False,
            shell=False,
            startupinfo=startupinfo,
            creationflags=creationflags,
            cwd=cwd,
        )
        if result.returncode != 0:

            err = (result.stderr or b"").decode("utf-8", "ignore")
            log(f"Pandoc HTML conversion error: {err}")
            raise PandocError(err or "Pandoc HTML conversion failed")

        _log_pandoc_stderr_as_warning(result.stderr, context="Pandoc warning (HTML->DOCX)")
        return result.stdout

    def _strip_latex_preamble(self, latex: str) -> str:
        






           
        lines = latex.split('\n')
        result_lines = []
        in_document = False
        skip_patterns = [
            r'^\s*\\documentclass',
            r'^\s*\\usepackage',
            r'^\s*\\begin\{document\}',
            r'^\s*\\end\{document\}',
            r'^\s*\\maketitle',
            r'^\s*\\date\{',
            r'^\s*\\author\{',
            r'^\s*\\providecommand',
            r'^\s*\\setlength',
            r'^\s*\\def\\tightlist',
            r'^\s*\\tightlist',
            r'^\s*\\newcommand',
        ]
        
        for line in lines:

            should_skip = False
            for pattern in skip_patterns:
                if re.match(pattern, line):
                    should_skip = True
                    break
            
            if should_skip:
                if '\\begin{document}' in line:
                    in_document = True
                continue
            

            if in_document or not any(re.match(r'^\s*\\documentclass', l) for l in lines[:20]):
                result_lines.append(line)
        

        result = '\n'.join(result_lines)

        result = result.strip()
        return result

    def convert_html_to_latex_text(
        self,
        html_text: str,
        *,
        strip_preamble: bool = True,
        custom_filters_html_to_md: Optional[List[str]] = None,
        custom_filters_md_to_latex: Optional[List[str]] = None,
    ) -> str:
        








           

        md_text = self._convert_html_to_md(html_text, custom_filters_html_to_md)

        return self.convert_markdown_to_latex_text(
            md_text,
            strip_preamble=strip_preamble,
            custom_filters=custom_filters_md_to_latex,
        )

    def convert_markdown_to_latex_text(
        self,
        md_text: str,
        *,
        strip_preamble: bool = True,
        enable_latex_replacements: bool = True,
        custom_filters: Optional[List[str]] = None,
    ) -> str:
        










           
        cmd = [
            self.pandoc_path,
            "-f", "markdown+tex_math_dollars+raw_tex+tex_math_double_backslash+tex_math_single_backslash",
            "-t", "latex",
            "-o", "-",
            "--wrap", "none",
        ]
        if enable_latex_replacements:
            cmd += ["--lua-filter", LUA_LATEX_REPLACEMENTS]
        cmd += self._build_filter_args(custom_filters)

        startupinfo = None
        creationflags = 0
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            creationflags = subprocess.CREATE_NO_WINDOW

        result = subprocess.run(
            cmd,
            input=md_text.encode("utf-8"),
            capture_output=True,
            text=False,
            shell=False,
            startupinfo=startupinfo,
            creationflags=creationflags,
        )
        if result.returncode != 0:
            err = (result.stderr or b"").decode("utf-8", "ignore")
            log(f"Pandoc Markdown to LaTeX error: {err}")
            raise PandocError(err or "Pandoc Markdown to LaTeX conversion failed")

        latex = result.stdout.decode("utf-8", "ignore")
        
        if strip_preamble:
            latex = self._strip_latex_preamble(latex)
        
        return latex

    def convert_docx_to_html_text(self, docx_path: str) -> str:
        

           
        if not os.path.exists(docx_path):
            raise FileNotFoundError(f"DOCX file not found: {docx_path}")

        cmd = [
            self.pandoc_path,
            "-f", "docx",
            "-t", "html",
            "-o", "-",
            "--standalone",
            "--wrap", "none",
        ]

        startupinfo = None
        creationflags = 0
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            creationflags = subprocess.CREATE_NO_WINDOW

        result = subprocess.run(
            cmd,


            cwd=os.path.dirname(docx_path),
            capture_output=True,
            text=False,
            shell=False,
            startupinfo=startupinfo,
            creationflags=creationflags,
        )
        

        cmd = [
            self.pandoc_path,
            docx_path,
            "-f", "docx",
            "-t", "html",
            "-o", "-",
            "--standalone",
            "--wrap", "none",
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=False,
            shell=False,
            startupinfo=startupinfo,
            creationflags=creationflags,
        )

        if result.returncode != 0:
            err = (result.stderr or b"").decode("utf-8", "ignore")
            log(f"Pandoc DOCX to HTML error: {err}")
            raise PandocError(err or "Pandoc DOCX to HTML conversion failed")

        return result.stdout.decode("utf-8", "ignore")
