# -*- coding: utf-8 -*-
"""
@File    : local_bridge/core/singleton.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

import os
import sys
from abc import ABC, abstractmethod

from .state import app_state
from ..utils.logging import log
from ..utils.system_detect import is_windows, is_macos


class SingleInstanceChecker(ABC):
                  
    
    def __init__(self, app_name: str):
        self.app_name = app_name
    
    @abstractmethod
    def is_already_running(self) -> bool:
                         
        pass
    
    @abstractmethod
    def acquire_lock(self) -> bool:
                   
        pass
    
    @abstractmethod
    def release_lock(self) -> None:
                   
        pass


class WindowsSingleInstanceChecker(SingleInstanceChecker):
                                             
    
    def __init__(self, app_name: str = "Global\\AIDocStation-Mutex"):
        super().__init__(app_name)
        self.mutex_handle = None
        

        import ctypes
        self.kernel32 = ctypes.windll.kernel32
        self.ERROR_ALREADY_EXISTS = 183
    
    def is_already_running(self) -> bool:
                                           
        try:

            self.mutex_handle = self.kernel32.CreateMutexW(
                None,
                True,
                self.app_name
            )
            
            if self.mutex_handle:
                last_error = self.kernel32.GetLastError()
                if last_error == self.ERROR_ALREADY_EXISTS:
                    log("Mutex already exists, another instance is running")
                    return True
                else:
                    log("Mutex created successfully")
                    return False
            else:
                log("Failed to create mutex")
                return False
                
        except Exception as e:
            log(f"Error checking single instance: {e}")
            return False
    
    def acquire_lock(self) -> bool:
                   
        if self.mutex_handle:
            log("Mutex lock acquired")
            return True
        return False
    
    def release_lock(self) -> None:
                   
        try:
            if self.mutex_handle:
                self.kernel32.ReleaseMutex(self.mutex_handle)
                self.kernel32.CloseHandle(self.mutex_handle)
                self.mutex_handle = None
                log("Mutex released")
        except Exception as e:
            log(f"Error releasing mutex: {e}")


class MacOSSingleInstanceChecker(SingleInstanceChecker):
                                
    
    def __init__(self, app_name: str = "AIDocStation"):
        super().__init__(app_name)
        self.lock_file = None
        self.lock_fd = None
        

        import tempfile
        self.lock_path = os.path.join(tempfile.gettempdir(), f"{app_name}.lock")
    
    def is_already_running(self) -> bool:
                                
        try:
            import fcntl
            

            self.lock_fd = os.open(self.lock_path, os.O_CREAT | os.O_RDWR)
            
            try:

                fcntl.flock(self.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                

                os.ftruncate(self.lock_fd, 0)
                os.write(self.lock_fd, str(os.getpid()).encode())
                
                log(f"Lock file created: {self.lock_path}")
                return False
                
            except BlockingIOError:

                log(f"Lock file already locked, another instance is running")
                os.close(self.lock_fd)
                self.lock_fd = None
                return True
                
        except Exception as e:
            log(f"Error checking single instance: {e}")
            if self.lock_fd is not None:
                try:
                    os.close(self.lock_fd)
                except Exception:
                    pass
                self.lock_fd = None
            return False
    
    def acquire_lock(self) -> bool:
                   
        if self.lock_fd is not None:
            log("File lock acquired")
            return True
        return False
    
    def release_lock(self) -> None:
                   
        try:
            if self.lock_fd is not None:
                import fcntl
                fcntl.flock(self.lock_fd, fcntl.LOCK_UN)
                os.close(self.lock_fd)
                self.lock_fd = None
                

                try:
                    if os.path.exists(self.lock_path):
                        os.remove(self.lock_path)
                except Exception:
                    pass
                
                log("File lock released")
        except Exception as e:
            log(f"Error releasing file lock: {e}")


def check_single_instance() -> bool:
    




       

    if is_windows():
        checker = WindowsSingleInstanceChecker()
    elif is_macos():
        checker = MacOSSingleInstanceChecker()
    else:

        checker = MacOSSingleInstanceChecker()
    

    if checker.is_already_running():
        log("Another instance of the application is already running")
        return False
    

    if not checker.acquire_lock():
        log("Failed to acquire application lock")
        return False
    

    app_state.instance_checker = checker
    
    return True
