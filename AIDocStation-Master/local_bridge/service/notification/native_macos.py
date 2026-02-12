# -*- coding: utf-8 -*-
"""
@File    : local_bridge/service/notification/native_macos.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import subprocess
from typing import Optional

from ...utils.logging import log


class NativeMacOSNotifier:
                                          

    @staticmethod
    def is_available() -> bool:
                                               
        return True

    @staticmethod
    def notify(title: str, message: str, app_icon: Optional[str] = None,
               timeout: int = 5, group: Optional[str] = None) -> bool:
        











           
        try:

            safe_title = title.replace('"', '\\"').replace('\\', '\\\\')
            safe_message = message.replace('"', '\\"').replace('\\', '\\\\')
            

            script = f'display notification "{safe_message}" with title "{safe_title}"'
            
            subprocess.run(
                ["osascript", "-e", script],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=2,
            )
            
            log(f"macOS notification sent: {title}")
            return True

        except subprocess.TimeoutExpired:
            log("macOS notification timeout")
            return False
        except subprocess.CalledProcessError as e:
            log(f"macOS notification error: {e.stderr.strip() if e.stderr else str(e)}")
            return False
        except Exception as e:
            log(f"macOS notification error: {e}")
            return False


def test_notification():
                
    if NativeMacOSNotifier.is_available():
        print("�?Native macOS notifier available")
        result = NativeMacOSNotifier.notify(
            "测试通知",
            "这是一条原�?macOS 通知",
            group="com.richqaq.local_bridge"
        )
        print(f"Notification sent: {result}")
    else:
        print("�?Native macOS notifier not available")


if __name__ == "__main__":
    test_notification()
