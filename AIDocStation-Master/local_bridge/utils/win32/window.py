# -*- coding: utf-8 -*-
"""
@File    : local_bridge/utils/win32/window.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:43
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import os
from time import sleep
import psutil
import win32gui
import win32process
from ..logging import log


def get_foreground_window() -> int:
    




       
    try:
        return win32gui.GetForegroundWindow()
    except Exception as e:
        log(f"Failed to get foreground window: {e}")
        return 0


def get_foreground_process_name() -> str:
    




       
    try:
        hwnd = get_foreground_window()
        if not hwnd:
            return ""
        
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)
        return os.path.basename(process.exe()).lower()
        
    except Exception as e:
        log(f"Failed to get foreground process: {e}")
        return ""


def get_foreground_process_path() -> str:
    




       
    try:
        hwnd = get_foreground_window()
        if not hwnd:
            return ""
        
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)
        return process.exe().lower()
        
    except Exception as e:
        log(f"Failed to get foreground process path: {e}")
        return ""


def get_foreground_window_title() -> str:
    




       
    try:
        hwnd = get_foreground_window()
        if not hwnd:
            return ""
        return win32gui.GetWindowText(hwnd)
    except Exception as e:
        log(f"Failed to get window title: {e}")
        return ""


def get_running_apps() -> list[dict]:
    




       
    apps = {}
    
    def enum_handler(hwnd, _):
        try:
            if not win32gui.IsWindowVisible(hwnd):
                return True
            

            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            

            proc = psutil.Process(pid)
            exe_path = proc.exe()
            name = proc.name().replace(".exe", "")
            

            if name not in apps:
                apps[name] = {
                    "name": name,
                    "exe_path": exe_path,
                }
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
        except Exception as e:
            log(f"Error enumerating app: {e}")
        return True
    
    try:
        win32gui.EnumWindows(enum_handler, None)
    except Exception as e:
        log(f"Failed to enumerate windows: {e}")
    
    return list(apps.values())


def cleanup_background_wps_processes(ep: int = 0) -> int:
    









       
    try:
        cleaned_count = 0
        

        wps_process_names = ['wps.exe', 'kwps.exe', 'et.exe', 'ket.exe']
        

        all_wps_processes = []
        target_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'ppid']):
            try:
                proc_name = proc.info['name'].lower()

                if proc_name in wps_process_names or proc_name == 'wpscloudsvr.exe':
                    all_wps_processes.append(proc)

                    if proc_name in wps_process_names:
                        target_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        if not target_processes:
            log("No WPS target processes found")
            return 0
        
        log(f"Found {len(target_processes)} WPS target process(es), {len(all_wps_processes)} total WPS-related")
        




        protected_pids = set()
        
        for proc in all_wps_processes:
            try:
                pid = proc.pid


                cmdline = proc.info.get('cmdline', [])
                cmdline_str = ' '.join(cmdline) if cmdline else ''
                has_automation = '/automation' in cmdline_str.lower()


                if not has_automation and _has_main_user_window(pid):
                    protected_pids.add(pid)
                    log(f"Protected: user application {pid} (no /Automation)")
                else:
                    log(f"Skipped: automation process {pid} (has /Automation)")
            except:
                pass


        def add_children(parent_pid):
            for proc in all_wps_processes:
                try:
                    if proc.info.get('ppid') == parent_pid and proc.pid not in protected_pids:
                        protected_pids.add(proc.pid)
                        log(f"Protected: child {proc.pid} (parent: {parent_pid})")
                        add_children(proc.pid)
                except:
                    pass

        for pid in list(protected_pids):
            add_children(pid)


        for proc in target_processes:
            if proc.info['name'].lower() == 'wpscloudsvr.exe':
                continue
            try:
                pid = proc.pid
                proc_name = proc.info['name'].lower()
                
                if pid in protected_pids:
                    continue
                
                log(f"Cleaning up background process: {pid} ({proc_name})")
                try:
                    proc.terminate()
                    try:
                        proc.wait(timeout=2)
                    except psutil.TimeoutExpired:
                        proc.kill()
                    cleaned_count += 1
                except Exception as e:
                    log(f"Failed to terminate {pid}: {e}")
            except:
                pass
        
        if cleaned_count > 0:
            if ep < 3:
                sleep(0.15)
                cleanup_background_wps_processes(ep+1)
            log(f"Cleaned up {cleaned_count} background process(es)")
        
        return cleaned_count
    
    except Exception as e:
        log(f"Error during cleanup: {e}")
        return 0


def _has_taskbar_window(pid: int) -> bool:
    













       
    try:
        import win32con
        
        has_taskbar = False
        
        def window_callback(hwnd, extra):
            nonlocal has_taskbar
            try:

                _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                if window_pid != pid:
                    return True
                

                is_visible = win32gui.IsWindowVisible(hwnd)
                is_minimized = win32gui.IsIconic(hwnd)
                
                if not is_visible and not is_minimized:

                    return True
                

                ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                

                if ex_style & win32con.WS_EX_TOOLWINDOW:
                    return True
                

                has_app_window = ex_style & win32con.WS_EX_APPWINDOW
                
                if has_app_window:

                    title = win32gui.GetWindowText(hwnd)
                    log(f"Found taskbar window (APPWINDOW) for PID {pid}: '{title}'")
                    has_taskbar = True
                    return False
                

                owner = win32gui.GetWindow(hwnd, win32con.GW_OWNER)
                

                if not owner and is_visible:
                    title = win32gui.GetWindowText(hwnd)

                    if title:
                        log(f"Found taskbar window (no owner, visible) for PID {pid}: '{title}'")
                        has_taskbar = True
                        return False
                
            except Exception as e:
                log(f"Error checking taskbar window for PID {pid}: {e}")
                pass
            return True
        
        win32gui.EnumWindows(window_callback, None)
        return has_taskbar
    
    except Exception as e:
        log(f"Error checking taskbar window for PID {pid}: {e}")

        return True


def _has_document_window(pid: int) -> bool:
    












       
    try:
        import win32con
        
        has_doc_window = False
        
        def window_callback(hwnd, extra):
            nonlocal has_doc_window
            try:

                _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                if window_pid != pid:
                    return True
                

                is_minimized = win32gui.IsIconic(hwnd)
                

                is_visible = win32gui.IsWindowVisible(hwnd)
                

                if is_minimized:
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        log(f"Found minimized document window for PID {pid}: '{title}'")
                        has_doc_window = True
                        return False
                

                if not is_visible:
                    return True
                

                title = win32gui.GetWindowText(hwnd)
                if not title:

                    return True
                

                ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                

                if ex_style & win32con.WS_EX_TOOLWINDOW:
                    return True
                

                try:
                    rect = win32gui.GetWindowRect(hwnd)
                    width = rect[2] - rect[0]
                    height = rect[3] - rect[1]
                    

                    if width < 200 or height < 200:
                        return True
                except Exception:

                    return True
                

                log(f"Found document window for PID {pid}: '{title}' ({width}x{height})")
                has_doc_window = True
                return False
                
            except Exception as e:
                log(f"Error checking window for PID {pid}: {e}")
                pass
            return True
        
        win32gui.EnumWindows(window_callback, None)
        return has_doc_window
    
    except Exception as e:
        log(f"Error checking document window for PID {pid}: {e}")

        return True


def _has_main_user_window(pid: int) -> bool:
    














       
    try:
        import win32con
        
        has_user_window = False
        
        def window_callback(hwnd, extra):
            nonlocal has_user_window
            try:

                _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                if window_pid != pid:
                    return True
                

                is_minimized = win32gui.IsIconic(hwnd)
                if is_minimized:
                    title = win32gui.GetWindowText(hwnd)
                    log(f"Found minimized window for PID {pid}: '{title}'")
                    has_user_window = True
                    return False
                

                is_visible = win32gui.IsWindowVisible(hwnd)
                if not is_visible:

                    return True
                

                title = win32gui.GetWindowText(hwnd)
                

                style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
                ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                

                is_tool_window = ex_style & win32con.WS_EX_TOOLWINDOW
                

                has_caption = style & win32con.WS_CAPTION
                

                if title or is_tool_window or has_caption:
                    window_type = "tool window" if is_tool_window else "main window"
                    log(f"Found visible {window_type} for PID {pid}: '{title}'")
                    has_user_window = True
                    return False
                
            except Exception as e:
                log(f"Error checking window for PID {pid}: {e}")
                pass
            return True
        
        win32gui.EnumWindows(window_callback, None)
        return has_user_window
    
    except Exception as e:
        log(f"Error checking main window for PID {pid}: {e}")

        return True
