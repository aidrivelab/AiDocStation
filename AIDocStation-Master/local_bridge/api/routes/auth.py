# -*- coding: utf-8 -*-
"""
@File    : local_bridge/api/routes/auth.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from local_bridge.api.supabase_client import supabase_client
from local_bridge.utils.logging import log

router = APIRouter()

@router.get("/auth/callback")
async def auth_callback(
    request: Request,
    access_token: str = Query(None),
    refresh_token: str = Query(None),
    error: str = Query(None)
):
    




       
    if error:
        log(f"[Auth] Callback error: {error}")
        return HTMLResponse(content=f"<h1>认证失败</h1><p>{error}</p>", status_code=400)


    if access_token:
        log(f"[Auth] Received access token (length: {len(access_token)})")
        success = supabase_client.set_session(access_token, refresh_token)
        if success:
            return HTMLResponse(content="""
                <html>
                <head>
                    <title>认证成功</title>
                    <meta charset="utf-8">
                </head>
                <body style="font-family: sans-serif; text-align: center; padding-top: 50px;">
                    <h1 style="color: #4CAF50;">�?认证成功</h1>
                    <p>您已成功登录 AIDOC Station，现在可以关闭此窗口返回软件�?/p>
                    <script>
                        // 尝试自动关闭窗口
                        setTimeout(() => {
                            window.close();
                            // 如果 window.close() 被浏览器拦截，显示提�?
                            document.body.innerHTML += '<p style="color: grey;">(如果窗口未自动关闭，请手动关�?</p>';
                        }, 2500);
                    </script>
                </body>
                </html>
            """)



    return HTMLResponse(content="""
        <html>
        <head>
            <title>正在完成认证...</title>
            <script src="https://appsforoffice.microsoft.com/lib/1/hosted/office.js"></script>
        </head>
        <body>
            <p style="text-align: center; padding-top: 50px;">请稍�? 正在为您连接 AIDOC Station...</p>
            <script>
                // �?Office.js 准备就绪�?
                let officeReady = false;
                if (window.Office) {
                    Office.onReady(() => { officeReady = true; processToken(); });
                } else {
                    processToken();
                }

                function processToken() {
                    const hash = window.location.hash;
                    if (hash && hash.includes('access_token=')) {
                        const params = new URLSearchParams(hash.substring(1));
                        const tokenData = {
                            type: 'AUTH_SUCCESS',
                            access_token: params.get('access_token'),
                            refresh_token: params.get('refresh_token')
                        };

                        // 1. 如果�?Office 对话框中，尝试通知父窗�?
                        if (window.Office && Office.context && Office.context.ui && Office.context.ui.messageParent) {
                            try {
                                Office.context.ui.messageParent(JSON.stringify(tokenData));
                            } catch (e) {
                                console.error("messageParent failed:", e);
                            }
                        }

                        // 2. 也是最重要的，转换并本地设置并同步（Scenario A 核心逻辑�?
                        const query = hash.replace('#', '?');
                        window.location.href = window.location.pathname + query;
                    }
                }
            </script>
        </body>
        </html>
    """)



from pydantic import BaseModel

class SessionSyncRequest(BaseModel):
    access_token: str
    refresh_token: str = None

@router.get("/auth/session")
async def get_current_session():
    

       
    user_profile = supabase_client.get_profile()
    session = supabase_client.get_session()
    
    if user_profile and session:
        return {
            "logged_in": True,
            "user": user_profile,
            "session": session
        }
    return {
        "logged_in": False,
        "user": None,
        "session": None
    }

@router.post("/auth/sync")
async def sync_session_from_plugin(payload: SessionSyncRequest):
    

       
    log(f"[Auth] Received session sync from plugin")
    success = supabase_client.set_session(payload.access_token, payload.refresh_token)
    
    if success:

        user_profile = supabase_client.get_profile()
        return {
            "status": "success", 
            "synced": True,
            "user": user_profile
        }
    else:
        return {
            "status": "error", 
            "message": "Failed to set session"
        }
