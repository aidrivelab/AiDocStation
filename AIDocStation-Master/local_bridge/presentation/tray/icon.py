# -*- coding: utf-8 -*-
"""
@File    : local_bridge/presentation/tray/icon.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:42
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import os
from PIL import Image, ImageDraw

from ...config.paths import get_tray_icon_path
from ...utils.dpi import get_dpi_scale
from ...utils.system_detect import is_macos


def create_fallback_icon(ok: bool = True, flash: bool = False) -> Image.Image:
    








       

    scale = get_dpi_scale()
    base_size = 64

    target_size = int(base_size * max(1.0, scale))
    target_size = min(256, max(64, target_size))
    
    size = (target_size, target_size)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    

    bg_color = (30, 30, 30, 255)
    draw.rectangle([0, 0, size[0], size[1]], fill=bg_color)
    

    color = (60, 200, 80, 255) if ok else (220, 70, 70, 255)
    if flash:
        color = tuple(min(255, int(c * 1.3)) if i < 3 else c for i, c in enumerate(color))
    


    ratio = target_size / 64.0
    padding = 10 * ratio
    draw.ellipse(
        [padding, padding, target_size - padding, target_size - padding],
        fill=color
    )
    
    return img


def load_base_icon() -> Image.Image:
    




       
    try:
        icon_path = get_tray_icon_path()
        if os.path.exists(icon_path):
            return Image.open(icon_path).convert("RGBA")
    except Exception:
        pass
    

    return create_fallback_icon(ok=True)


def create_status_icon(ok: bool) -> Image.Image:
    







       
    base = load_base_icon().copy()


    if is_macos():
        return base

    width, height = base.size
    draw = ImageDraw.Draw(base)


    radius = int(min(width, height) * 0.28)
    padding = int(radius * 0.25)


    x1 = width - radius - padding
    y1 = height - radius - padding
    x2 = width - padding
    y2 = height - padding


    draw.ellipse([x1 - 2, y1 - 2, x2 + 2, y2 + 2], fill=(255, 255, 255, 255))


    status_color = (60, 200, 80, 255) if ok else (220, 70, 70, 255)
    draw.ellipse([x1, y1, x2, y2], fill=status_color)

    return base
