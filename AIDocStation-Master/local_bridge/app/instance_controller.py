# -*- coding: utf-8 -*-
"""
@File    : local_bridge/app/instance_controller.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:41
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtCore import QObject, Signal, QDataStream, QIODevice
from local_bridge.utils.logging import log

class SingleInstanceController(QObject):
    

       
    message_received = Signal(str)

    def __init__(self, server_name="AIDOC_Station_Local_Server", parent=None):
        super().__init__(parent)
        self.server_name = server_name
        self._server = None

    def is_already_running(self, message="") -> bool:
        

           
        socket = QLocalSocket(self)
        socket.connectToServer(self.server_name)
        
        if socket.waitForConnected(500):
            if message:
                log(f"[Instance] Sending message to existing instance: {message}")
                stream = QDataStream(socket)
                stream.writeString(message)
                socket.waitForBytesWritten(500)
            socket.disconnectFromServer()
            return True
        
        return False

    def start_server(self) -> bool:
        

           

        QLocalServer.removeServer(self.server_name)
        
        self._server = QLocalServer(self)
        if not self._server.listen(self.server_name):
            log(f"[Instance] Failed to start local server: {self._server.errorString()}")
            return False
        
        self._server.newConnection.connect(self._on_new_connection)
        log(f"[Instance] Local server listening on: {self.server_name}")
        return True

    def _on_new_connection(self):
        socket = self._server.nextPendingConnection()
        if socket:
            socket.readyRead.connect(lambda: self._read_message(socket))

    def _read_message(self, socket: QLocalSocket):
        stream = QDataStream(socket)
        if socket.bytesAvailable() > 0:
            message = stream.readString()
            if "aidoc://auth" in message:
                log(f"[Instance] Received auth message from another instance (Token hidden for security)")
            else:
                log(f"[Instance] Received message from another instance: {message}")
            self.message_received.emit(message)
        socket.disconnectFromServer()
