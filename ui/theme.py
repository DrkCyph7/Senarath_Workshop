"""
Senarath WMS - Unified Theme Configuration
Provides consistent colors, fonts, and styling across all application pages
"""

# ==========================================
# Color Palette
# ==========================================
class ColorPalette:
    """Modern, professional color palette for Senarath WMS"""
    
    # Base colors
    BG_PRIMARY = "#ffffff"
    BG_SECONDARY = "#f0f2f5"
    
    # Text colors
    TEXT_PRIMARY = "#111827"
    TEXT_SECONDARY = "#4b5563"
    TEXT_MUTED = "#6c757d"
    
    # Accent colors
    ACCENT_PRIMARY = "#2e7d6e"      # Teal (main primary)
    ACCENT_SECONDARY = "#a0754f"    # Brown
    ACCENT_BLUE = "#2563eb"         # Blue
    ACCENT_GREEN = "#059669"        # Green
    ACCENT_ORANGE = "#d97706"       # Orange
    ACCENT_RED = "#dc2626"          # Red
    ACCENT_YELLOW = "#fef3c7"       # Light yellow
    
    # UI elements
    BORDER_COLOR = "#d1d5db"
    BORDER_LIGHT = "#dee2e6"
    CARD_BG = "#ffffff"
    HOVER_BG = "#f9f9f9"


# ==========================================
# Typography
# ==========================================
class Typography:
    """Font sizes and styles for consistent typography"""
    
    FONT_FAMILY_PRIMARY = "'Segoe UI', 'Inter', Arial, sans-serif"
    FONT_FAMILY_MONO = "'Monaco', 'Courier New', monospace"
    
    # Font sizes
    SIZE_HEADER_LG = 36
    SIZE_HEADER_MD = 28
    SIZE_HEADER_SM = 20
    SIZE_TITLE = 18
    SIZE_SUBTITLE = 15
    SIZE_BODY = 14
    SIZE_SMALL = 13
    SIZE_TINY = 12
    
    # Font weights
    WEIGHT_NORMAL = 400
    WEIGHT_MEDIUM = 500
    WEIGHT_SEMIBOLD = 600
    WEIGHT_BOLD = 700
    WEIGHT_EXTRABOLD = 800
    
    # Page header title
    PAGE_TITLE_SIZE = 24
    PAGE_TITLE_WEIGHT = 700
    PAGE_TITLE_POINT_SIZE = 18  # Point size for QFont (approximately 24px)


# ==========================================
# Spacing
# ==========================================
class Spacing:
    """Consistent spacing throughout the application"""
    
    PADDING_SMALL = 8
    PADDING_MEDIUM = 12
    PADDING_LARGE = 16
    PADDING_XL = 24
    PADDING_XXL = 32
    
    MARGIN_SMALL = 4
    MARGIN_MEDIUM = 8
    MARGIN_LARGE = 12
    MARGIN_XL = 16
    MARGIN_XXL = 24
    
    BORDER_RADIUS_SMALL = 6
    BORDER_RADIUS_MEDIUM = 10
    BORDER_RADIUS_LARGE = 12
    
    # Back button dimensions
    BACK_BUTTON_HEIGHT = 36
    BACK_BUTTON_WIDTH = 100


# ==========================================
# Component Styles
# ==========================================
class Styles:
    """Reusable component stylesheets"""
    
    @staticmethod
    def get_button_primary(color=ColorPalette.ACCENT_PRIMARY):
        """Primary button stylesheet"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                font-size: 14px;
                font-weight: 600;
                padding: 10px 20px;
                border-radius: {Spacing.BORDER_RADIUS_MEDIUM}px;
                border: none;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {ColorPalette.ACCENT_PRIMARY};
                opacity: 0.9;
            }}
            QPushButton:pressed {{
                background-color: {color};
            }}
        """
    
    @staticmethod
    def get_button_secondary():
        """Secondary button stylesheet"""
        return f"""
            QPushButton {{
                background-color: #e5e7eb;
                color: {ColorPalette.TEXT_PRIMARY};
                font-size: 14px;
                font-weight: 600;
                padding: 10px 20px;
                border-radius: {Spacing.BORDER_RADIUS_MEDIUM}px;
                border: none;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: #d1d5db;
            }}
            QPushButton:pressed {{
                background-color: #d1d5db;
            }}
        """

    @staticmethod
    def get_button_danger(color=ColorPalette.ACCENT_RED):
        """Danger / destructive button stylesheet"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                font-size: 14px;
                font-weight: 600;
                padding: 10px 20px;
                border-radius: {Spacing.BORDER_RADIUS_MEDIUM}px;
                border: none;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {ColorPalette.ACCENT_RED};
                opacity: 0.9;
            }}
            QPushButton:pressed {{
                background-color: {color};
            }}
        """
    
    @staticmethod
    def get_back_button():
        """Back button stylesheet - consistent across all pages"""
        return f"""
            QPushButton {{
                background-color: #e5e7eb;
                color: {ColorPalette.TEXT_PRIMARY};
                font-size: 13px;
                font-weight: 600;
                padding: 8px 16px;
                border-radius: {Spacing.BORDER_RADIUS_MEDIUM}px;
                border: none;
                min-height: {Spacing.BACK_BUTTON_HEIGHT}px;
                min-width: {Spacing.BACK_BUTTON_WIDTH}px;
            }}
            QPushButton:hover {{
                background-color: #d1d5db;
            }}
            QPushButton:pressed {{
                background-color: #bfdbfe;
            }}
        """
    
    @staticmethod
    def get_page_title():
        """Page title stylesheet - consistent across all pages"""
        return f"""
            QLabel {{
                font-size: {Typography.PAGE_TITLE_SIZE}px;
                font-weight: {Typography.PAGE_TITLE_WEIGHT};
                color: {ColorPalette.TEXT_PRIMARY};
                background-color: transparent;
            }}
        """
    
    @staticmethod
    def get_input_field():
        """Input field stylesheet"""
        return f"""
            QLineEdit, QTextEdit, QComboBox {{
                background-color: #fafafa;
                border: 1px solid {ColorPalette.BORDER_LIGHT};
                border-radius: {Spacing.BORDER_RADIUS_SMALL}px;
                padding: 10px 12px;
                font-size: {Typography.SIZE_SMALL}px;
                color: {ColorPalette.TEXT_PRIMARY};
            }}
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
                border: 2px solid {ColorPalette.ACCENT_PRIMARY};
                background-color: white;
            }}
        """
    
    @staticmethod
    def get_card_frame():
        """Card frame stylesheet"""
        return f"""
            QFrame {{
                background-color: {ColorPalette.CARD_BG};
                border-radius: {Spacing.BORDER_RADIUS_LARGE}px;
                padding: {Spacing.PADDING_LARGE}px;
                border: none;
            }}
            QFrame:hover {{
                background-color: {ColorPalette.HOVER_BG};
            }}
        """
    
    @staticmethod
    def get_header():
        """Header stylesheet"""
        return f"""
            QLabel#header_title {{
                font-size: {Typography.SIZE_HEADER_LG}px;
                font-weight: {Typography.WEIGHT_EXTRABOLD};
                color: {ColorPalette.TEXT_PRIMARY};
                letter-spacing: -0.5px;
            }}
            QLabel#header_subtitle {{
                font-size: {Typography.SIZE_SUBTITLE}px;
                color: {ColorPalette.TEXT_SECONDARY};
                font-weight: {Typography.WEIGHT_NORMAL};
            }}
        """
    
    @staticmethod
    def get_section_title():
        """Section title stylesheet"""
        return f"""
            QLabel#section_title {{
                font-size: {Typography.SIZE_HEADER_SM}px;
                font-weight: {Typography.WEIGHT_BOLD};
                color: {ColorPalette.TEXT_PRIMARY};
                padding-bottom: 2px;
            }}
            QLabel#section_subtitle {{
                font-size: {Typography.SIZE_SMALL}px;
                color: {ColorPalette.TEXT_SECONDARY};
                font-weight: {Typography.WEIGHT_NORMAL};
            }}
        """


# ==========================================
# Helper Functions for Common UI Elements
# ==========================================
def create_page_header(title_text, parent=None):
    """
    Create a consistent page header with title and back button.
    
    Returns: (header_layout, title_label, back_button)
    """
    from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QFont
    
    header_layout = QHBoxLayout()
    header_layout.setSpacing(12)
    header_layout.setContentsMargins(0, 0, 0, 0)
    
    # Title label
    title_label = QLabel(title_text)
    title_label.setObjectName("page_title")
    title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    title_label.setStyleSheet(f"""
        color: {ColorPalette.TEXT_PRIMARY};
        background-color: transparent;
        font-size: 24px;
        font-weight: 700;
    """)
    header_layout.addWidget(title_label)
    
    header_layout.addStretch()
    
    # Back button
    back_button = QPushButton("⬅ Back")
    back_button.setObjectName("back_button")
    back_button.setFixedHeight(Spacing.BACK_BUTTON_HEIGHT)
    back_button.setFixedWidth(Spacing.BACK_BUTTON_WIDTH)
    back_button.setCursor(Qt.PointingHandCursor)
    back_button.setStyleSheet(Styles.get_back_button())
    header_layout.addWidget(back_button)
    
    return header_layout, title_label, back_button


# ==========================================
# Global Theme Stylesheet
# ==========================================
def get_global_stylesheet():
    """Get global application stylesheet"""
    return f"""
        QWidget {{
            background-color: {ColorPalette.BG_PRIMARY};
            color: {ColorPalette.TEXT_PRIMARY};
            font-family: {Typography.FONT_FAMILY_PRIMARY};
        }}
        
        QLabel {{
            background-color: transparent;
        }}
        
        QLabel#header_title {{
            font-size: {Typography.SIZE_HEADER_LG}px;
            font-weight: {Typography.WEIGHT_EXTRABOLD};
            color: {ColorPalette.TEXT_PRIMARY};
            letter-spacing: -0.5px;
        }}
        
        QLabel#header_subtitle {{
            font-size: {Typography.SIZE_SUBTITLE}px;
            color: {ColorPalette.TEXT_SECONDARY};
            font-weight: {Typography.WEIGHT_NORMAL};
        }}
        
        QLabel#section_title {{
            font-size: {Typography.SIZE_HEADER_SM}px;
            font-weight: {Typography.WEIGHT_BOLD};
            color: {ColorPalette.TEXT_PRIMARY};
            padding-bottom: 2px;
        }}
        
        QLabel#section_subtitle {{
            font-size: {Typography.SIZE_SMALL}px;
            color: {ColorPalette.TEXT_SECONDARY};
            font-weight: {Typography.WEIGHT_NORMAL};
        }}
        
        QPushButton {{
            background-color: {ColorPalette.ACCENT_PRIMARY};
            color: white;
            font-weight: {Typography.WEIGHT_SEMIBOLD};
            border-radius: {Spacing.BORDER_RADIUS_MEDIUM}px;
            border: none;
            min-height: 40px;
        }}
        
        QPushButton:hover {{
            opacity: 0.9;
        }}
        
        QPushButton:pressed {{
            opacity: 0.8;
        }}
        
        QLineEdit, QTextEdit, QComboBox {{
            background-color: #fafafa;
            border: 1px solid {ColorPalette.BORDER_LIGHT};
            border-radius: {Spacing.BORDER_RADIUS_SMALL}px;
            padding: 10px 12px;
            font-size: {Typography.SIZE_SMALL}px;
        }}
        
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
            border: 2px solid {ColorPalette.ACCENT_PRIMARY};
            background-color: white;
        }}
        
        QFrame {{
            background-color: transparent;
            border: none;
        }}
    """
