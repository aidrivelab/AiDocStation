# -*- coding: utf-8 -*-
"""
@File    : local_bridge/presentation/components/qt_widgets.py
@Desc    : AiDoc Station Lite 核心模块 - 赋能高效文档协作与智能排版处�?
@Author  : AIDriveLab Team
@Create  : 2026-02-09 21:12:42
@Version : V0.2.6
@Copyright: ©AIDriveLab Inc. All Rights Reserved.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
    QPushButton, QFrame, QGraphicsDropShadowEffect,
    QAbstractButton, QStyledItemDelegate, QMenu, QLineEdit
)
from PySide6.QtCore import Qt, QSize, Property, QRect, QPoint, QPropertyAnimation, Signal, QEasingCurve, QEvent, QTimer
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QIcon, QPixmap, QAction, QPainterPath, QKeySequence
import os

class ModernComboBox(QPushButton):
    


       
    currentIndexChanged = Signal(int)
    currentTextChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ModernComboBox")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(32)
        

        self.menu = QMenu(self)
        self.menu.setObjectName("ModernComboBoxMenu")
        self.setMenu(self.menu)
        

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(20, 0, 35, 0)
        self.main_layout.setSpacing(0)
        
        self.lbl_display = QLabel()
        self.lbl_display.setStyleSheet("border: none; background: transparent; font-size: 13px; color: #000000;")
        self.lbl_display.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.main_layout.addWidget(self.lbl_display)
        

        self._items = []
        self._current_index = -1
        
        self.setStyleSheet("""
            /* 按钮主体样式（模拟下拉框�?*/
            QPushButton#ModernComboBox {
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding-left: 0px;    /* 内部由布局控制 */
                padding-right: 0px;
                padding-top: 0px;
                padding-bottom: 0px;
                background-color: #FFFFFF;
                font-size: 13px;
                color: #000000;
                min-width: 165px;
            }
            QPushButton#ModernComboBox:hover {
                border: 1px solid #335DFF;
            }
            /* 下拉三角指示�?(模拟�?2) */
            QPushButton#ModernComboBox::menu-indicator {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                right: 12px;
                width: 10px;
                height: 10px;
                image: none;
            }
            
            /* 弹出菜单样式（Strategy F + �?3 优化�?*/
            QMenu#ModernComboBoxMenu {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 4px 0px;
            }
            QMenu#ModernComboBoxMenu::item {
                height: 36px;
                padding: 0px 16px; /* 4px(margin) + 16px = 20px, 与按钮内部布局 20px 完美对齐 */
                background-color: transparent;
                color: #000000;
                font-size: 13px;
                margin: 0px 4px;
                border-radius: 4px;
            }
            QMenu#ModernComboBoxMenu::item:selected {
                background-color: #F2F3F5;
                color: #335DFF;
                border-left: 3px solid #335DFF;
                padding-left: 13px; /* 4px(margin) + 3px(border) + 13px = 20px */
            }
        """)

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor("#666666")))
        

        x = self.width() - 25
        y = (self.height() - 6) // 2
        path = QPainterPath()
        path.moveTo(x, y)
        path.lineTo(x + 10, y)
        path.lineTo(x + 5, y + 6)
        path.closeSubpath()
        painter.drawPath(path)

    def mousePressEvent(self, event):

        self.menu.setFixedWidth(self.width())

        pos = self.mapToGlobal(QPoint(0, self.height() + 2))
        self.menu.exec(pos)

    def addItem(self, text, data=None):
        action = QAction(text, self.menu)
        action.setData(len(self._items))
        self.menu.addAction(action)
        self._items.append(text)
        

        action.triggered.connect(lambda: self.setCurrentIndex(action.data()))
        

        if self._current_index == -1:
            self.setCurrentIndex(0)

    def addItems(self, texts):
        for t in texts:
            self.addItem(t)

    def setCurrentIndex(self, index):
        if 0 <= index < len(self._items):
            self._current_index = index

            original_text = self._items[index]
            self.lbl_display.setText(original_text)
            self.setText("")
            
            self.currentIndexChanged.emit(index)
            self.currentTextChanged.emit(original_text)

    def currentIndex(self):
        return self._current_index

    def currentText(self):
        if 0 <= self._current_index < len(self._items):
            return self._items[self._current_index]
        return ""

    def clear(self):
        self.menu.clear()
        self._items = []
        self._current_index = -1
        self.setText("")


COLOR_PRIMARY = "#335DFF"
COLOR_BG = "#F3F3F3"
COLOR_CARD_BG = "#FFFFFF"
COLOR_TEXT = "#000000"
COLOR_SUBTEXT = "#666666"
COLOR_DIVIDER = "#E5E5E5"
COLOR_HOVER = "#EAEAEA"
COLOR_SELECTED = "#FFFFFF"


SCROLLBAR_STYLE = """
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 6px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical {
    background: #CCCCCC;
    min-height: 20px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background: #AAAAAA;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

class ModernSwitch(QAbstractButton):
                                  
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(44, 24)
        
        self._thumb_pos = 3
        self._bg_color = QColor("#E0E0E0")
        self._thumb_color = QColor("#FFFFFF")
        
        self.animation = QPropertyAnimation(self, b"thumb_pos")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

    @Property(int)
    def thumb_pos(self):
        return self._thumb_pos

    @thumb_pos.setter
    def thumb_pos(self, pos):
        self._thumb_pos = pos
        self.update()

    def setChecked(self, checked):
                                          
        super().setChecked(checked)

        self._thumb_pos = 23 if checked else 3
        self.update()

    def nextCheckState(self):
        super().nextCheckState()
        start = self._thumb_pos
        end = 23 if self.isChecked() else 3
        self.animation.setStartValue(start)
        self.animation.setEndValue(end)
        self.animation.start()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        

        bg_rect = QRect(0, 0, self.width(), self.height())
        p.setPen(Qt.NoPen)

        color = QColor(COLOR_PRIMARY) if self.isChecked() else QColor("#E9E9E9")
        p.setBrush(color)
        p.drawRoundedRect(bg_rect, 12, 12)
        

        p.setBrush(QColor("#FFFFFF"))


        p.drawEllipse(QPoint(self._thumb_pos + 9, 12), 9, 9)

class PathSelector(QWidget):
    

       
    pathChanged = Signal(str)

    def __init__(self, current_path, placeholder="", browse_callback=None, reset_callback=None, reset_text="Reset", 
                 browse_icon=None, reset_icon=None, input_width=160, parent=None, show_browse=True):
        super().__init__(parent)
        self.setStyleSheet("background-color: #FFFFFF; border: none;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)


        self.line_edit = QLineEdit(current_path)
        self.line_edit.setPlaceholderText(placeholder)
        self.line_edit.setFixedHeight(30)
        self.line_edit.setFixedWidth(input_width)
        self.line_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 0 8px;
                background-color: #FFFFFF;
                font-size: 13px;
                color: #000000;
            }
            QLineEdit:focus { border: 1px solid #335DFF; }
        """)
        self.line_edit.editingFinished.connect(lambda: self.pathChanged.emit(self.line_edit.text()))
        layout.addWidget(self.line_edit)


        def get_btn_style(is_icon=False):
            if is_icon:
                return """
                    QPushButton {
                        border: none;
                        background-color: transparent;
                        min-width: 25px;
                        max-width: 25px;
                        height: 25px;
                        padding: 0;
                    }
                    QPushButton:hover { background-color: #EAEAEA; border-radius: 4px; }
                    QPushButton:pressed { background-color: #D0D0D0; }
                """
            else:
                return """
                    QPushButton {
                        border: 1px solid #CCCCCC;
                        border-radius: 4px;
                        background-color: #FFFFFF;
                        color: #333333;
                        font-size: 12px;
                        min-width: 60px;
                        height: 28px;
                    }
                    QPushButton:hover { background-color: #F5F5F5; border-color: #BBBBBB; }
                    QPushButton:pressed { background-color: #E0E0E0; }
                """

        from local_bridge.i18n import t
        

        self.btn_browse = QPushButton(t("settings.general.browse"))
        if browse_icon:
            self.btn_browse.setFixedSize(25, 25)
            self.btn_browse.setIcon(QIcon(browse_icon))
            self.btn_browse.setIconSize(QSize(20, 20))
            self.btn_browse.setText("") 
            self.btn_browse.setToolTip(t("settings.general.browse"))
            self.btn_browse.setStyleSheet(get_btn_style(True))
        else:
            self.btn_browse.setStyleSheet(get_btn_style(False))

        if browse_callback:
            self.btn_browse.clicked.connect(browse_callback)
        
        self.btn_browse.setVisible(show_browse)
        if show_browse:
            layout.addWidget(self.btn_browse)


        if reset_callback:
            self.btn_reset = QPushButton(reset_text)
            if reset_icon:
                self.btn_reset.setFixedSize(25, 25)
                self.btn_reset.setIcon(QIcon(reset_icon))
                self.btn_reset.setIconSize(QSize(20, 20))
                self.btn_reset.setText("")
                self.btn_reset.setToolTip(reset_text)
                self.btn_reset.setStyleSheet(get_btn_style(True))
            else:
                self.btn_reset.setStyleSheet(get_btn_style(False))
                
            self.btn_reset.clicked.connect(reset_callback)
            layout.addWidget(self.btn_reset)
        



class SidebarTile(QPushButton):
                                                              
    def __init__(self, icon_path: str, title: str, selected=False, parent=None):
        super().__init__(parent)
        self.setText(f"{title}") 
        self.icon_path = icon_path
        self.setFixedHeight(40)
        self.setCheckable(True)
        self.setChecked(selected)
        self.setCursor(Qt.PointingHandCursor)
        self._selected = selected
        self._show_dot = False
        self.update_style()

    def set_show_dot(self, show: bool):
        self._show_dot = show
        self.update()

    def set_selected(self, selected: bool):
        self._selected = selected
        self.setChecked(selected)
        self.update_style()

    def update_style(self):
        color = "#000000" if self._selected else COLOR_SUBTEXT
        bg = COLOR_SELECTED if self._selected else "transparent"
        weight = "500" if self._selected else "normal"
        
        style = f"""
        QPushButton {{
            text-align: left;
            padding-left: 45px;
            font-size: 14px;
            border-radius: 6px;
            background-color: {bg};
            color: {color};
            font-weight: {weight};
            border: none;
        }}
        QPushButton:hover {{
            background-color: {COLOR_HOVER if not self._selected else COLOR_SELECTED};
        }}
        """
        self.setStyleSheet(style)
        if self._selected:
            self.setGraphicsEffect(None)
        
    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        

        if self._selected:
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(COLOR_PRIMARY))
            p.drawRoundedRect(6, 10, 4, 20, 2, 2)
            

        if self.icon_path and os.path.exists(self.icon_path):
            pix = QPixmap(self.icon_path)
            dpr = self.devicePixelRatio()
            target_size = QSize(20, 20)
            


            pix = pix.scaled(target_size * dpr, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            pix.setDevicePixelRatio(dpr)
            

            y_pos = (self.height() - target_size.height()) // 2

            target_rect = QRect(20, y_pos, target_size.width(), target_size.height())
            
            p.drawPixmap(target_rect, pix)
        else:

            p.setPen(QColor(COLOR_PRIMARY if self._selected else COLOR_SUBTEXT))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(22, 13, 14, 14)
            

        if self._show_dot:
            p.setPen(Qt.NoPen)
            p.setBrush(QColor("#FF4D4F"))

            p.drawEllipse(34, 8, 8, 8)

class SettingRow(QWidget):
                                                                           
    def __init__(self, title: str, subtitle: str = "", control: QWidget = None, icon: str = None, extend=False, sub_width=270, raw_icon=False, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingRow")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("#SettingRow { background-color: transparent; border: none; }") 
        
        self.content_layout = QHBoxLayout(self)
        self.content_layout.setContentsMargins(10, 15, 10, 15) 
        self.content_layout.setSpacing(15)
        

        if icon:
            self.icon_label = QLabel()
            self.icon_label.setFixedSize(24, 24)
            self.icon_label.setAlignment(Qt.AlignCenter)
            if raw_icon:
                self.icon_label.setStyleSheet("background: transparent; border: none; font-size: 16px;")
                self.icon_label.setText(icon)
            else:
                self.icon_label.setStyleSheet(f"background-color: #F0F0F0; border-radius: 4px; color: {COLOR_PRIMARY}; font-weight: bold; font-size: 10px;")
                self.icon_label.setText(icon[0].upper() if icon else "")
            self.content_layout.insertWidget(0, self.icon_label)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(1)
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"font-size: 15px; font-weight: 500; color: {COLOR_TEXT}; background: transparent; border: none;")
        text_layout.addWidget(self.title_label)
        
        self.sub_label = QLabel(subtitle if subtitle else "")
        self.sub_label.setStyleSheet(f"font-size: 13px; color: {COLOR_SUBTEXT}; background: transparent; border: none;")
        self.sub_label.setWordWrap(True)
        self.sub_label.setTextFormat(Qt.RichText)
        if sub_width is not None:
            self.sub_label.setFixedWidth(sub_width)
        
        if not subtitle:
            self.sub_label.hide()
            
        text_layout.addWidget(self.sub_label)
            
        self.content_layout.addLayout(text_layout)
        
        if control:
            if extend:
                self.content_layout.addWidget(control, 1)
            else:
                self.content_layout.addStretch()
                self.content_layout.addWidget(control)
        else:
            self.content_layout.addStretch()

    def set_title(self, text: str):
                       
        if hasattr(self, 'title_label') and self.title_label:
            self.title_label.setText(text)

    def set_subtitle(self, text: str):
                        
        if hasattr(self, 'sub_label') and self.sub_label:
            self.sub_label.setText(text)
            if text:
                self.sub_label.show()
            else:
                self.sub_label.hide()

    def get_subtitle(self):
        return self.sub_label.text() if self.sub_label else ""

class SectionCard(QFrame):
                                             
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_CARD_BG};
                border-radius: 10px;
                border: 1px solid {COLOR_DIVIDER};
            }}
        """)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 10, 20, 10)
        self.layout.setSpacing(0)
        








    def add_row(self, row: SettingRow, show_divider=True):
        self.layout.addWidget(row)
        if show_divider:
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Plain)
            line.setStyleSheet(f"background-color: {COLOR_DIVIDER}; max-height: 1px; border: none;")
            self.layout.addWidget(line)
        
    def finish_layout(self):

        if self.layout.count() > 0:
            last_item = self.layout.itemAt(self.layout.count() - 1).widget()
            if isinstance(last_item, QFrame) and last_item.styleSheet().find("max-height: 1px") != -1:
                last_item.deleteLater()

class CustomTooltipWrapper(QLabel):
    

       
    def __init__(self, text, parent=None):
        super().__init__(text, parent)

        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        

        self.setStyleSheet("""
            QLabel {
                background-color: #FFFFFF;
                color: #333333;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 6px 8px;
                font-family: 'Microsoft YaHei';
                font-size: 12px;
            }
        """)
        self.adjustSize()

    def showAt(self, global_pos):

        self.move(global_pos + QPoint(10, 10))
        self.show()


_active_custom_tooltip = None

def show_custom_tooltip(global_pos, text):
    global _active_custom_tooltip
    if _active_custom_tooltip:
        try:
            _active_custom_tooltip.close()
            _active_custom_tooltip.deleteLater()
        except: pass
        _active_custom_tooltip = None
    
    if not text:
        return

    _active_custom_tooltip = CustomTooltipWrapper(text)
    _active_custom_tooltip.showAt(global_pos)
    

    from PySide6.QtCore import QTimer
    QTimer.singleShot(3000, _active_custom_tooltip.close)


class ModernResetButton(QPushButton):
                                                                      
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(22, 22)
        self._custom_tooltip_text = ""
        

        current_dir = os.path.dirname(os.path.abspath(__file__))
        local_bridge_dir = os.path.dirname(os.path.dirname(current_dir))
        icon_path = os.path.join(local_bridge_dir, "assets", "images", "icon_Active", "icon-udo.png")
        
        if os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(16, 16))
        
        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
        """)
        
    def setToolTip(self, text):
        self._custom_tooltip_text = text
    
    def event(self, event):
        if event.type() == QEvent.ToolTip:
            if self._custom_tooltip_text:
                show_custom_tooltip(event.globalPos(), self._custom_tooltip_text)
            return True
        return super().event(event)

class ConflictIcon(QLabel):
                                                                               
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("!")
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(16, 16)
        
        self._custom_tooltip_text = ""
        self._scale = 1.0
        self._hover = False
        

        self.anim = QPropertyAnimation(self, b"scale_factor")
        self.anim.setDuration(150)
        self.anim.setEasingCurve(QEasingCurve.OutQuad)

    @Property(float)
    def scale_factor(self):
        return self._scale

    @scale_factor.setter
    def scale_factor(self, value):
        self._scale = value
        self.update()

    def enterEvent(self, event):
        self._hover = True
        self.anim.stop()
        self.anim.setEndValue(1.15)
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover = False
        self.anim.stop()
        self.anim.setEndValue(1.0)
        self.anim.start()
        super().leaveEvent(event)

    def setToolTip(self, text):
        self._custom_tooltip_text = text

    def event(self, event):
        if event.type() == QEvent.ToolTip:
            if self._custom_tooltip_text:
                clean_text = self._custom_tooltip_text.replace("<font color='black'>", "").replace("</font>", "")
                show_custom_tooltip(event.globalPos(), clean_text)
            return True
        return super().event(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        

        cx, cy = self.width() / 2, self.height() / 2
        p.translate(cx, cy)
        p.scale(self._scale, self._scale)
        p.translate(-cx, -cy)
        


        bg_color = QColor("#FF7070") if self._hover else QColor("#FF5252")
        p.setBrush(QBrush(bg_color))
        p.setPen(Qt.NoPen)
        p.drawEllipse(0, 0, self.width(), self.height())
        

        p.setPen(QColor("#FFFFFF"))
        font = self.font()
        font.setPointSize(10)
        font.setBold(True)
        p.setFont(font)
        p.drawText(self.rect(), Qt.AlignCenter, "!")


class HotkeyEdit(QWidget):
    




       
    hotkeyChanged = Signal(str)
    toggled = Signal(bool)
    
    _current_recorder = None

    def __init__(self, current_hotkey="", default_val="", validate_callback=None, single_key_mode=False, width=None, reset_icon=None, parent=None):
        super().__init__(parent)
        self._hotkey = current_hotkey
        self._default_val = default_val 
        self._validate_callback = validate_callback
        self._single_key_mode = single_key_mode
        self._is_recording = False
        self._checked = False 

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(4) 


        self.icon_label = ConflictIcon(self)
        self.icon_label.hide()
        self.layout.addWidget(self.icon_label)


        from local_bridge.i18n import t
        self.reset_btn = ModernResetButton()

        self.reset_btn.setToolTip(t("settings.general.restore_default"))
        
        self.reset_btn.clicked.connect(self.restore_default)
        self.reset_btn.hide()
        self.layout.addWidget(self.reset_btn)


        self.input_frame = QFrame(self)
        self.input_frame.setCursor(Qt.PointingHandCursor)
        if width:
            self.input_frame.setFixedSize(width, 36)
        else:
            self.input_frame.setMinimumWidth(200)
            self.input_frame.setFixedHeight(36)
            
        self.input_frame.setMouseTracking(True)
        

        self.input_layout = QHBoxLayout(self.input_frame)
        self.input_layout.setContentsMargins(10, 0, 5, 0)
        self.input_layout.setSpacing(0)


        self.text_label = QLabel(self.input_frame)
        self.text_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.text_label.setStyleSheet("border: none; background: transparent; color: #333333; font-size: 13px;")
        self.text_label.setAttribute(Qt.WA_TransparentForMouseEvents) 
        self.input_layout.addWidget(self.text_label, 1)


        self.clear_btn = QPushButton(self.input_frame)
        self.clear_btn.setText("×")
        self.clear_btn.setFixedSize(24, 24)
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                color: #999999;
                font-size: 18px;
                background: transparent;
                border: none;
                padding: 0;
                margin: 0;
                line-height: 20px;
                border-radius: 12px;
            }
            QPushButton:hover {
                color: #FF5252;
                background-color: rgba(0, 0, 0, 0.05);
            }
        """)
        self.clear_btn.clicked.connect(self.clear_hotkey)
        self.clear_btn.hide()
        self.input_layout.addWidget(self.clear_btn)

        self.layout.addWidget(self.input_frame)


        self.input_frame.installEventFilter(self)

        self._update_style()
        self.update_display()

    def eventFilter(self, obj, event):
        if obj == self.input_frame:
            if event.type() == QEvent.Enter:
                if self._hotkey and not self._is_recording:
                    self.clear_btn.show()
            elif event.type() == QEvent.Leave:
                self.clear_btn.hide()
            elif event.type() == QEvent.MouseButtonPress:
                if event.button() == Qt.LeftButton:

                    self.setFocus() 
                    self.setChecked(not self.isChecked())
                    return True
        return super().eventFilter(obj, event)

    def setChecked(self, checked):
        if self._checked != checked:

            if checked:
                if HotkeyEdit._current_recorder and HotkeyEdit._current_recorder != self:
                    HotkeyEdit._current_recorder.setChecked(False)
                HotkeyEdit._current_recorder = self
            else:
                if HotkeyEdit._current_recorder == self:
                    HotkeyEdit._current_recorder = None

            self._checked = checked
            self.toggled.emit(checked)
            self._on_toggled(checked)
            self._update_style()

    def isChecked(self):
        return self._checked
        
    def _update_style(self):

        border_color = "#335DFF" if self._checked else "#CCCCCC"
        bg_color = "#FFFFFF"
        

        if self.icon_label.isVisible() and not self._checked:
             border_color = "#FF5252"

        if self._checked:
             bg_color = "#F0F4FF"

        self.input_frame.setStyleSheet(f"""
            QFrame {{
                border: {("2px" if self._checked else "1px")} solid {border_color};
                border-radius: 6px;
                background-color: {bg_color};
            }}
        """)
        
        text_color = "#335DFF" if self._checked else "#333333"
        self.text_label.setStyleSheet(f"""
            border: none; 
            background: transparent; 
            color: {text_color}; 
            font-size: 13px;
        """)

    def update_display(self):

        if not self._hotkey:
            from local_bridge.i18n import t
            self.text_label.setText(t("settings.hotkey.click_to_set"))
            self.clear_btn.hide()
            self.icon_label.hide()
        else:
            from local_bridge.i18n import t
            display = self._hotkey
            

            if self._single_key_mode:
                if display == "ctrl_l": display = t("settings.hotkey.left_ctrl")
                elif display == "ctrl_r": display = t("settings.hotkey.right_ctrl")
                elif display == "alt_l": display = "Alt (L)"
                elif display == "shift_l": display = "Shift (L)"
                else:
                     display = display.replace("<", "").replace(">", "").title()
                

                display = t("settings.hotkey.double_click_prefix").format(key=display)
            else:
                 display = display.replace("<", "").replace(">", "").title()
                 display = display.replace("+", " + ")
                 display = display.replace("Cmd", "Win").replace("Meta", "Win")
            
            self.text_label.setText(display)
            

        if self._default_val and self._hotkey != self._default_val:
            self.reset_btn.show()
        else:
            self.reset_btn.hide()

        self._update_style()

    def restore_default(self):
        if self._default_val:
            self._hotkey = self._default_val
            self.update_display()
            self.hotkeyChanged.emit(self._hotkey)
            if self._is_recording:
                self.setChecked(False)

    def clear_hotkey(self):
        self._hotkey = ""
        self.icon_label.hide()
        self.update_display()
        self.hotkeyChanged.emit("")
        if self._is_recording:
            self.setChecked(False)

    def set_conflict(self, is_conflict, message=""):
        if is_conflict and self._hotkey:
            self.icon_label.show()


            rich_msg = f"<font color='black'>{message}</font>"
            self.icon_label.setToolTip(rich_msg)
        else:
            self.icon_label.hide()
            self.icon_label.setToolTip("")
        self._update_style()

    def _on_toggled(self, checked):
        if checked:
            self._is_recording = True
            from local_bridge.i18n import t
            self.text_label.setText(t("settings.hotkey.recording"))
            self.clear_btn.hide()
            self.icon_label.hide()
        else:
            self._is_recording = False
            self.update_display()

    def keyPressEvent(self, event):
        if not self._is_recording:
            super().keyPressEvent(event)
            return

        key = event.key()
        modifiers = event.modifiers()
        
        if key == Qt.Key_Escape:
            self.setChecked(False)
            return

        if self._single_key_mode:

            key_map = {
                Qt.Key_Control: "ctrl",
                Qt.Key_Alt: "alt",
                Qt.Key_Shift: "shift",
                Qt.Key_Meta: "cmd"
            }

            if key in key_map:




                





                


                pass


            from PySide6.QtGui import QKeySequence
            text = QKeySequence(key).toString().lower()
            

            if key == Qt.Key_Control: 



                text = "ctrl_l" 
            elif key == Qt.Key_Alt: text = "alt_l"
            elif key == Qt.Key_Shift: text = "shift_l"
            elif key == Qt.Key_Meta: text = "cmd"
            
            self._hotkey = text
            self.update_display()
            self.hotkeyChanged.emit(text)
            self.setChecked(False)
            return


        if key in [Qt.Key_Control, Qt.Key_Alt, Qt.Key_Shift, Qt.Key_Meta]:
            return

        parts = []
        if modifiers & Qt.ControlModifier: parts.append("<ctrl>")
        if modifiers & Qt.AltModifier: parts.append("<alt>")
        if modifiers & Qt.ShiftModifier: parts.append("<shift>")
        if modifiers & Qt.MetaModifier: parts.append("<cmd>")

        from PySide6.QtGui import QKeySequence
        key_name = QKeySequence(key).toString().lower()
        parts.append(key_name)
        new_hotkey = "+".join(parts)
        
        self._hotkey = new_hotkey
        self.update_display()
        self.hotkeyChanged.emit(new_hotkey)
        self.setChecked(False)

    def focusOutEvent(self, event):
        if self._is_recording:
            self.setChecked(False)
        super().focusOutEvent(event)
