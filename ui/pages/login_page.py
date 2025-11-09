from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class LoginPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # === UI Colors (No Blue) ===
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
            QLabel#title {{
                font-size: 36px;
                font-weight: bold;
                color: {accent_color};
                padding: 20px;
            }}
            QLabel#subtitle {{
                font-size: 16px;
                color: #666;
                padding-bottom: 40px;
            }}
            QLabel#field_label {{
                font-size: 14px;
                font-weight: 600;
                color: {text_color};
                padding: 5px 0px;
            }}
            QFrame#login_card {{
                background-color: {card_color};
                border-radius: 16px;
                padding: 50px;
                border: 1px solid {border_color};
            }}
            QLineEdit {{
                background-color: #fafafa;
                border: 1px solid {border_color};
                border-radius: 8px;
                padding: 14px 16px;
                font-size: 14px;
                color: {text_color};
                min-height: 20px;
            }}
            QLineEdit:focus {{
                border: 2px solid {accent_color};
                background-color: #ffffff;
            }}
            QPushButton#login_btn {{
                background-color: {accent_color};
                color: white;
                font-size: 16px;
                font-weight: 600;
                padding: 16px;
                border-radius: 8px;
                min-height: 50px;
            }}
            QPushButton#login_btn:hover {{
                background-color: #246651;
            }}
            QPushButton#login_btn:pressed {{
                background-color: #1d5240;
            }}
        """)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        # Login card
        login_card = QFrame()
        login_card.setObjectName("login_card")
        login_card.setFixedWidth(450)
        card_layout = QVBoxLayout(login_card)
        card_layout.setSpacing(20)

        # Logo/Title section
        title_layout = QVBoxLayout()
        title_layout.setAlignment(Qt.AlignCenter)
        
        logo_label = QLabel("🏭")
        logo_label.setStyleSheet("font-size: 64px; padding: 10px;")
        logo_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(logo_label)

        title = QLabel("Senarath Workshop")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title)

        subtitle = QLabel("Workshop Management System")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(subtitle)

        card_layout.addLayout(title_layout)

        # Username field
        username_label = QLabel("Username")
        username_label.setObjectName("field_label")
        card_layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.returnPressed.connect(self.login)
        card_layout.addWidget(self.username_input)

        # Password field
        password_label = QLabel("Password")
        password_label.setObjectName("field_label")
        card_layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self.login)
        card_layout.addWidget(self.password_input)

        # Login button
        login_btn = QPushButton("Login")
        login_btn.setObjectName("login_btn")
        login_btn.clicked.connect(self.login)
        card_layout.addWidget(login_btn)

        # Info text
        info_label = QLabel("Default: admin / admin")
        info_label.setStyleSheet("color: #888; font-size: 12px; padding-top: 10px;")
        info_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(info_label)

        main_layout.addWidget(login_card)
        self.setLayout(main_layout)

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        # Simple authentication (in production, use proper authentication)
        if username == "admin" and password == "admin":
            self.main_window.go_to_home()
        else:
            QMessageBox.warning(
                self,
                "Login Failed",
                "Invalid username or password.\n\nPlease try again."
            )
            self.password_input.clear()
            self.password_input.setFocus()