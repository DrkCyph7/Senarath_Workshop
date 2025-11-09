from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.theme import ColorPalette, Typography, Spacing, Styles


class RunningChartPage(QWidget):
    """Placeholder for Running Chart module"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        # === UI Colors ===
        bg_color = "#f5f5f0"
        card_color = "#ffffff"
        accent_color = "#2d7a5f"
        text_color = "#2c2c2c"
        border_color = "#d4d4d4"
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                color: {text_color};
                font-family: 'Segoe UI', Arial;
            }}
            QFrame#card {{
                background-color: {card_color};
                border-radius: 12px;
                padding: 40px;
                border: 1px solid {border_color};
            }}
            QLabel#title {{
                font-size: 28px;
                font-weight: bold;
                color: {accent_color};
            }}
            QLabel#subtitle {{
                font-size: 16px;
                color: #666;
                padding: 15px 0px;
            }}
            QPushButton {{
                background-color: {accent_color};
                color: white;
                font-weight: 600;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #246651;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setAlignment(Qt.AlignCenter)
        
        card = QFrame()
        card.setObjectName("card")
        card.setMaximumWidth(600)
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setSpacing(20)
        
        # Icon
        icon_label = QLabel("🚚")
        icon_label.setStyleSheet("font-size: 80px;")
        icon_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(icon_label)
        
        # Title
        title = QLabel("Running Chart")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("This module is under development.\n\nManage vehicle running schedules, track mileage,\nand monitor vehicle utilization.")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        card_layout.addWidget(subtitle)
        
        # Back button
        back_btn = QPushButton("⬅ Back to Home")
        back_btn.clicked.connect(lambda: self.parent.go_to_home() if self.parent else None)
        back_btn.setFixedWidth(200)
        card_layout.addWidget(back_btn, alignment=Qt.AlignCenter)
        
        layout.addWidget(card)
        self.setLayout(layout)