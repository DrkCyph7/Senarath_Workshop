from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
import os
from ui.theme import ColorPalette, Typography, Spacing, Styles


class LoginPage(QWidget):
    # PIN credentials
    CORRECT_PIN = "2345"
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # === UI Colors - Professional Theme ===
        bg_color = "#ffffff"
        card_color = "#ffffff"
        accent_color = "#1e5f4a"
        text_color = "#212529"
        border_color = "#dee2e6"
        success_color = "#28a745"

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                color: {text_color};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QLabel {{
                background-color: transparent;
            }}
            QLabel#title {{
                font-size: 28px;
                font-weight: bold;
                color: {text_color};
                background-color: transparent;
                padding: 15px 0px 5px 0px;
            }}
            QLabel#subtitle {{
                font-size: 13px;
                color: #6c757d;
                background-color: transparent;
                padding-bottom: 30px;
                font-weight: 400;
            }}
            QLabel#field_label {{
                font-size: 13px;
                font-weight: 600;
                color: {text_color};
                background-color: transparent;
                padding: 8px 0px 5px 0px;
            }}
            QLabel#footer_text {{
                font-size: 11px;
                color: #6c757d;
                background-color: transparent;
                padding: 0px;
                margin: 0px;
            }}
            QLabel#footer_link {{
                font-size: 11px;
                color: {accent_color};
                background-color: transparent;
                text-decoration: underline;
                padding: 0px;
                margin: 0px;
            }}
            QFrame#login_card {{
                background-color: {card_color};
                border-radius: 12px;
                padding: 48px;
                border: 1px solid {border_color};
            }}
            QLineEdit {{
                background-color: #ffffff;
                border: 1px solid {border_color};
                border-radius: 6px;
                padding: 12px 14px;
                font-size: 16px;
                color: {text_color};
                min-height: 18px;
                letter-spacing: 2px;
            }}
            QLineEdit:focus {{
                border: 2px solid {accent_color};
                background-color: #ffffff;
            }}
            QPushButton#login_btn {{
                background-color: {accent_color};
                color: white;
                font-size: 15px;
                font-weight: 600;
                padding: 14px;
                border-radius: 6px;
                min-height: 45px;
                border: none;
            }}
            QPushButton#login_btn:hover {{
                background-color: #184d3e;
            }}
            QPushButton#login_btn:pressed {{
                background-color: #0f3829;
            }}
        """)

        # Main layout with center alignment
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignCenter)

        # Login card
        login_card = QFrame()
        login_card.setObjectName("login_card")
        login_card.setFixedWidth(420)
        card_layout = QVBoxLayout(login_card)
        card_layout.setSpacing(18)

        # Logo section
        logo_layout = QVBoxLayout()
        logo_layout.setAlignment(Qt.AlignCenter)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        
        # Load and display logo
        logo_path = os.path.join(os.path.dirname(__file__), "../../assets/logo.png")
        if os.path.exists(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path)
            # Scale logo to 120x120 pixels
            pixmap = pixmap.scaledToWidth(120, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            logo_layout.addWidget(logo_label)
            logo_layout.addSpacing(15)
        
        card_layout.addLayout(logo_layout)

        # Title section
        title = QLabel("Senarath WMS")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)

        subtitle = QLabel("System Access")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(subtitle)

        # PIN field
        pin_label = QLabel("Enter PIN")
        pin_label.setObjectName("field_label")
        card_layout.addWidget(pin_label)

        self.pin_input = QLineEdit()
        self.pin_input.setPlaceholderText("••••")
        self.pin_input.setEchoMode(QLineEdit.Password)
        self.pin_input.setAlignment(Qt.AlignCenter)
        self.pin_input.setMaxLength(4)
        self.pin_input.returnPressed.connect(self.login)
        card_layout.addWidget(self.pin_input)

        # Add spacing
        card_layout.addSpacing(10)

        # Login button
        login_btn = QPushButton("Login")
        login_btn.setObjectName("login_btn")
        login_btn.clicked.connect(self.login)
        card_layout.addWidget(login_btn)

        main_layout.addWidget(login_card)

        # Footer with developer info
        footer_layout = QVBoxLayout()
        footer_layout.setContentsMargins(0, 25, 0, 15)
        footer_layout.setAlignment(Qt.AlignCenter)
        footer_layout.setSpacing(3)

        # System name with developer and company credits
        dev_label = QLabel("Senarath WMS • Developed by <a href='https://www.google.com/search?q=DrkCyph7' style='color: #1e5f4a; text-decoration: none;'>DrkCyph7</a> • <a href='https://nexcy.lk' style='color: #1e5f4a; text-decoration: none;'>NexCy Technologies</a>")
        dev_label.setObjectName("footer_text")
        dev_label.setAlignment(Qt.AlignCenter)
        dev_label.setOpenExternalLinks(True)
        footer_layout.addWidget(dev_label)

        main_layout.addLayout(footer_layout)
        self.setLayout(main_layout)
        
        # Set focus to PIN input
        self.pin_input.setFocus()

    def login(self):
        pin = self.pin_input.text().strip()

        # Simple PIN authentication
        if pin == self.CORRECT_PIN:
            self.main_window.go_to_home()
        else:
            QMessageBox.warning(
                self,
                "Invalid PIN",
                "The PIN you entered is incorrect.\n\nPlease try again."
            )
            self.pin_input.clear()
            self.pin_input.setFocus()