# -*- coding: utf-8 -*-
"""
@File    : local_bridge/api/routes/generate.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, BackgroundTasks
import base64
import os
import tempfile
import shutil
import subprocess
from local_bridge.config.defaults import find_pandoc
from local_bridge.utils.logging import log
from local_bridge.service.document import WordPlacer
from local_bridge.core.state import app_state
import threading

router = APIRouter()


doc_lock = threading.Lock()

class GenerateRequest(BaseModel):
    markdown: str
    options: Optional[dict] = {}

class GenerateResponse(BaseModel):
    status: str
    data: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None

@router.post("/generate", response_model=GenerateResponse)
async def generate_docx(request: GenerateRequest):
    


       
    try:
        md_content = request.markdown
        if not md_content:
            return GenerateResponse(status="error", error="Empty markdown content")

        pandoc_path = find_pandoc()
        if not os.path.exists(pandoc_path) and pandoc_path != "pandoc":
             return GenerateResponse(status="error", error=f"Pandoc not found at {pandoc_path}")


        with tempfile.TemporaryDirectory() as temp_dir:
            input_file = os.path.join(temp_dir, "input.md")
            output_file = os.path.join(temp_dir, "output.docx")
            

            with open(input_file, "w", encoding="utf-8") as f:
                f.write(md_content)
                


            cmd = [
                pandoc_path,
                input_file,
                "-o", output_file,
                "--from", "markdown",
                "--to", "docx"
            ]
            

            ref_doc = request.options.get("referenceDocPath")
            if ref_doc and os.path.exists(ref_doc):
                cmd.extend(["--reference-doc", ref_doc])
            

            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                log(f"Pandoc Error: {result.stderr}")
                return GenerateResponse(status="error", error=f"Pandoc failed: {result.stderr}")
            

            if os.path.exists(output_file):
                with open(output_file, "rb") as f:
                    docx_bytes = f.read()
                    b64_data = base64.b64encode(docx_bytes).decode("utf-8")
                    return GenerateResponse(status="success", data=b64_data)
            else:
                return GenerateResponse(status="error", error="Output file not generated")

    except Exception as e:
        log(f"Generate API Error: {str(e)}")
        return GenerateResponse(status="error", error=str(e))

@router.post("/generate-and-insert", response_model=GenerateResponse)
async def generate_and_insert(request: GenerateRequest):
    

       
    try:
        md_content = request.markdown
        if not md_content:
            return GenerateResponse(status="error", error="Empty markdown content")

        pandoc_path = find_pandoc()
        if not os.path.exists(pandoc_path) and pandoc_path != "pandoc":
             return GenerateResponse(status="error", error=f"Pandoc not found at {pandoc_path}")


        from local_bridge.integrations.pandoc import PandocIntegration
        try:
            pandoc = PandocIntegration(pandoc_path)
            

            options = request.options or {}
            ref_doc = options.get("referenceDocPath")
            

            conv_config = app_state.config.copy()
            if ref_doc:
                conv_config["reference_docx"] = ref_doc


            from local_bridge.service.document import DocumentGenerator
            generator = DocumentGenerator()
            docx_bytes = generator.convert_markdown_to_docx_bytes(md_content, conv_config)
            


            with doc_lock:
                log("[API] Starting serialized document insertion...")
                placer = WordPlacer()
                result = placer.place(docx_bytes, conv_config)
                
                if result.success:

                    if app_state.store:
                        app_state.store.increment_stat("word_paste_count")
                        char_count = len(md_content)
                        app_state.store.increment_stat("word_char_count", char_count)
                        
                        import re
                        img_total = len(re.findall(r'!\[.*?\]\(.*?\)', md_content)) + \
                                    len(re.findall(r'```\s*(?:mermaid|\{\s*\.mermaid\s*\})', md_content, re.IGNORECASE))
                        if img_total > 0:
                            app_state.store.increment_stat("image_paste_count", img_total)
                        
                        if "|" in md_content and "---" in md_content:
                            table_count = md_content.count("|---") or 1
                            app_state.store.increment_stat("table_paste_count", table_count)
                        

                        from local_bridge.api.supabase_client import supabase_client
                        if app_state.store:
                            supabase_client.sync_stats(app_state.store.get("stats", {}))

                    return GenerateResponse(status="success", message="Content generated and inserted successfully")
                else:
                    return GenerateResponse(status="error", error=f"Insertion failed: {result.error}")

        except Exception as e:
            log(f"Generate & Insert Error: {str(e)}")
            return GenerateResponse(status="error", error=str(e))

    except Exception as e:
        log(f"Generate & Insert API Error: {str(e)}")
        return GenerateResponse(status="error", error=str(e))
