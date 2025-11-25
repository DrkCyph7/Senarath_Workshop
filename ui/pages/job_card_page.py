import sqlite3
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QTextEdit, QPushButton,
    QDateEdit, QComboBox, QFrame, QScrollArea, QHBoxLayout, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QDialogButtonBox,
    QCompleter, QListWidget, QListWidgetItem, QDoubleSpinBox
)
from PySide6.QtCore import QDate, Qt, QStringListModel, QSortFilterProxyModel
from PySide6.QtGui import QFont
from ui.theme import ColorPalette, Typography, Spacing, Styles, create_page_header

DB_PATH = "ui/db/senarath.db"

GRADES = ["Grade1", "Grade2", "Grade3", "Grade4", "Helper"]


class SparePartDialog(QDialog):
    def __init__(self, parent=None, edit_data=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Spare Part")
        self.setMinimumWidth(650)
        self.setMinimumHeight(550)
        
        # Load spare parts from database
        self.spare_parts_db = {}
        self.load_spare_parts_db()
        
        # Modern dialog styling using theme
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {ColorPalette.CARD_BG};
            }}
            QLabel {{
                color: {ColorPalette.TEXT_PRIMARY};
                font-weight: {Typography.WEIGHT_SEMIBOLD};
                font-size: 11px;
                background: transparent;
            }}
            QLineEdit, QTextEdit, QComboBox {{
                background-color: #fafafa;
                border: 1px solid {ColorPalette.BORDER_LIGHT};
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 12px;
                min-height: 26px;
            }}
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
                border: 2px solid {ColorPalette.ACCENT_PRIMARY};
                background-color: #ffffff;
            }}
            QLineEdit:read-only {{
                background-color: #f5f5f5;
                border: 1px solid #e8e8e8;
                color: #666;
                padding: 4px 8px;
                min-height: 22px;
                font-size: 11px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QTextEdit {{
                min-height: 60px;
            }}
            QListWidget {{
                background-color: #fafafa;
                border: 1px solid {ColorPalette.BORDER_LIGHT};
                border-radius: 4px;
                font-size: 11px;
                padding: 2px;
            }}
            QListWidget::item {{
                padding: 4px;
                border-radius: 3px;
            }}
            QListWidget::item:hover {{
                background-color: #e8f4f0;
            }}
            QListWidget::item:selected {{
                background-color: {ColorPalette.ACCENT_PRIMARY};
                color: white;
            }}
            QDialogButtonBox QPushButton {{
                background-color: {ColorPalette.ACCENT_PRIMARY};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 18px;
                font-weight: 600;
                min-width: 75px;
                font-size: 12px;
            }}
            QDialogButtonBox QPushButton:hover {{
                opacity: 0.9;
            }}
            QDialogButtonBox QPushButton[text="Cancel"] {{
                background-color: #e8e8e8;
                color: #333;
            }}
            QDialogButtonBox QPushButton[text="Cancel"]:hover {{
                background-color: #d5d5d5;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(18, 16, 18, 16)
        
        # Title
        title = QLabel("🔧 Spare Part Details")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #1a1a1a; padding-bottom: 2px; font-size: 14px;")
        layout.addWidget(title)
        
        # Search section (no label)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Type to search by ID Code, Description, Category...")
        self.search_input.textChanged.connect(self.filter_spare_parts)
        layout.addWidget(self.search_input)
        
        # Search results list
        self.search_results = QListWidget()
        self.search_results.setMaximumHeight(120)
        self.search_results.itemClicked.connect(self.on_part_selected)
        layout.addWidget(self.search_results)
        
        # Separator
        separator = QLabel("─" * 50)
        separator.setStyleSheet("color: #ddd; font-size: 8px; margin: 2px 0px;")
        layout.addWidget(separator)
        
        # Form section
        form_label = QLabel("📋 Part Details:")
        form_label.setStyleSheet("font-size: 11px; color: #666; font-weight: 600; margin-top: 2px;")
        layout.addWidget(form_label)
        
        form_layout = QGridLayout()
        form_layout.setSpacing(8)
        form_layout.setVerticalSpacing(8)
        form_layout.setContentsMargins(0, 0, 0, 0)
        
        # ID Code (read-only from DB)
        self.id_code_input = QLineEdit()
        self.id_code_input.setPlaceholderText("Auto-filled from database")
        self.id_code_input.setReadOnly(True)
        
        # Description (read-only from DB)
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Auto-filled from database")
        self.description_input.setReadOnly(True)
        
        # Category info (read-only from DB)
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Auto-filled from database")
        self.category_input.setReadOnly(True)
        
        # Quantity
        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("e.g., 2")
        self.quantity_input.textChanged.connect(self.calculate_total)
        
        # Unit (read-only from DB)
        self.unit_input = QLineEdit()
        self.unit_input.setPlaceholderText("Auto-filled from database")
        self.unit_input.setReadOnly(True)
        
        # Unit Price
        self.unit_price_input = QLineEdit()
        self.unit_price_input.setPlaceholderText("e.g., 1500.00")
        self.unit_price_input.textChanged.connect(self.calculate_total)
        
        # Total (calculated)
        self.total_input = QLineEdit()
        self.total_input.setReadOnly(True)
        self.total_input.setPlaceholderText("Auto-calculated")
        
        # Remark
        self.remark_input = QLineEdit()
        self.remark_input.setPlaceholderText("e.g., Notes or additional information")
        
        # Create compact labels
        def create_compact_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet("font-size: 11px; color: #555;")
            return lbl
        
        form_layout.addWidget(create_compact_label("ID Code:"), 0, 0)
        form_layout.addWidget(self.id_code_input, 0, 1)
        
        form_layout.addWidget(create_compact_label("Description:"), 1, 0)
        form_layout.addWidget(self.description_input, 1, 1)
        
        form_layout.addWidget(create_compact_label("Category:"), 2, 0)
        form_layout.addWidget(self.category_input, 2, 1)
        
        form_layout.addWidget(create_compact_label("Quantity:"), 3, 0)
        form_layout.addWidget(self.quantity_input, 3, 1)
        
        form_layout.addWidget(create_compact_label("Unit:"), 4, 0)
        form_layout.addWidget(self.unit_input, 4, 1)
        
        form_layout.addWidget(create_compact_label("Unit Price (Rs):"), 5, 0)
        form_layout.addWidget(self.unit_price_input, 5, 1)
        
        form_layout.addWidget(create_compact_label("Total:"), 6, 0)
        form_layout.addWidget(self.total_input, 6, 1)
        
        form_layout.addWidget(create_compact_label("Remark:"), 7, 0)
        form_layout.addWidget(self.remark_input, 7, 1)
        
        layout.addLayout(form_layout)
        layout.addSpacing(4)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # If editing, populate fields
        if edit_data:
            self.id_code_input.setText(edit_data.get('id_code', ''))
            self.description_input.setText(edit_data.get('description', ''))
            self.category_input.setText(edit_data.get('category', ''))
            self.quantity_input.setText(edit_data.get('quantity', ''))
            self.unit_input.setText(edit_data.get('unit', ''))
            self.unit_price_input.setText(edit_data.get('unit_price', ''))
            self.total_input.setText(edit_data.get('total', ''))
            self.remark_input.setText(edit_data.get('remark', ''))
        else:
            # Show all parts initially
            self.filter_spare_parts()
    
    def load_spare_parts_db(self):
        """Load all spare parts from database"""
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT id_code, item_description, main_category, sub_category, uom FROM spare_parts ORDER BY id_code")
            for row in c.fetchall():
                id_code, description, main_cat, sub_cat, uom = row
                category = f"{main_cat} > {sub_cat}" if sub_cat else main_cat
                self.spare_parts_db[id_code] = {
                    'description': description,
                    'category': category,
                    'uom': uom,
                    'main_category': main_cat,
                    'sub_category': sub_cat
                }
            conn.close()
        except Exception as e:
            print(f"Error loading spare parts: {e}")
    
    def filter_spare_parts(self):
        """Filter spare parts based on search input"""
        search_text = self.search_input.text().strip().lower()
        self.search_results.clear()
        
        if not search_text:
            # Show first 50 items when no search
            count = 0
            for id_code, data in sorted(self.spare_parts_db.items()):
                if count >= 50:
                    break
                item_text = f"{id_code} - {data['description']} ({data['category']})"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, id_code)
                self.search_results.addItem(item)
                count += 1
            return
        
        # Search in ID code, description, and category
        count = 0
        for id_code, data in sorted(self.spare_parts_db.items()):
            if count >= 100:  # Limit results
                break
            if (search_text in id_code.lower() or 
                search_text in data['description'].lower() or 
                search_text in data['category'].lower()):
                item_text = f"{id_code} - {data['description']} ({data['category']})"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, id_code)
                self.search_results.addItem(item)
                count += 1
    
    def on_part_selected(self, item):
        """Auto-fill fields when a part is selected from search results"""
        id_code = item.data(Qt.UserRole)
        if id_code in self.spare_parts_db:
            part_data = self.spare_parts_db[id_code]
            self.id_code_input.setText(id_code)
            self.description_input.setText(part_data['description'])
            self.category_input.setText(part_data['category'])
            self.unit_input.setText(part_data['uom'])
            # Focus on quantity for easy data entry
            self.quantity_input.setFocus()
    
    def calculate_total(self):
        try:
            quantity = float(self.quantity_input.text() or 0)
            unit_price = float(self.unit_price_input.text() or 0)
            total = quantity * unit_price
            self.total_input.setText(f"{total:.2f}")
        except ValueError:
            self.total_input.setText("0.00")
    
    def get_data(self):
        return {
            'id_code': self.id_code_input.text().strip(),
            'description': self.description_input.text().strip(),
            'category': self.category_input.text().strip(),
            'quantity': self.quantity_input.text().strip(),
            'unit': self.unit_input.text().strip(),
            'unit_price': self.unit_price_input.text().strip(),
            'total': self.total_input.text().strip(),
            'remark': self.remark_input.text().strip()
        }


class LabourWorkDialog(QDialog):
    def __init__(self, parent=None, edit_data=None, labour_list=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Labour Work")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self.labour_list = labour_list or []
        self.labour_rates = {}
        self.selected_labour = []
        
        # Load labour rates from database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT grade, cost_per_hour FROM labour_rates")
        for row in c.fetchall():
            self.labour_rates[row[0]] = row[1]
        conn.close()
        
        # Modern dialog styling
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {ColorPalette.CARD_BG};
            }}
            QLabel {{
                color: {ColorPalette.TEXT_PRIMARY};
                font-weight: {Typography.WEIGHT_SEMIBOLD};
                font-size: {Typography.SIZE_SMALL}px;
                background: transparent;
            }}
            QLineEdit, QTextEdit, QComboBox, QDoubleSpinBox {{
                background-color: #fafafa;
                border: 1px solid {ColorPalette.BORDER_LIGHT};
                border-radius: {Spacing.BORDER_RADIUS_SMALL}px;
                padding: 8px 11px;
                font-size: {Typography.SIZE_SMALL}px;
            }}
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDoubleSpinBox:focus {{
                border: 2px solid {ColorPalette.ACCENT_PRIMARY};
                background-color: #ffffff;
            }}
            QTextEdit {{
                min-height: 70px;
            }}
            QTableWidget {{
                background-color: {ColorPalette.CARD_BG};
                border: 1px solid {ColorPalette.BORDER_LIGHT};
                border-radius: 6px;
                gridline-color: #f0f0f0;
                font-size: 12px;
            }}
            QHeaderView::section {{
                background-color: {ColorPalette.ACCENT_PRIMARY};
                color: white;
                padding: 8px;
                border: none;
                font-weight: 700;
                font-size: 11px;
            }}
            QTableWidget::item {{
                padding: 6px;
                border: none;
            }}
            QTableWidget::item:selected {{
                background-color: #e8f4f0;
            }}
            QPushButton {{
                border: none;
                border-radius: 6px;
                font-weight: 600;
                font-size: 12px;
                padding: 8px 14px;
            }}
            QPushButton#add {{
                background-color: {ColorPalette.ACCENT_PRIMARY};
                color: white;
            }}
            QPushButton#add:hover {{
                opacity: 0.9;
            }}
            QPushButton#remove {{
                background-color: #c84343;
                color: white;
            }}
            QPushButton#remove:hover {{
                background-color: #b03636;
            }}
            QDialogButtonBox QPushButton {{
                background-color: {ColorPalette.ACCENT_PRIMARY};
                color: white;
                border: none;
                border-radius: {Spacing.BORDER_RADIUS_MEDIUM}px;
                padding: 9px 18px;
                font-weight: {Typography.WEIGHT_SEMIBOLD};
                min-width: 75px;
            }}
            QDialogButtonBox QPushButton:hover {{
                opacity: 0.9;
            }}
            QDialogButtonBox QPushButton[text="Cancel"] {{
                background-color: #e8e8e8;
                color: #333;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("👷 Labour Work Details")
        title.setFont(QFont("Segoe UI", 15, QFont.Bold))
        title.setStyleSheet("color: #1a1a1a; padding-bottom: 6px;")
        layout.addWidget(title)
        
        form_layout = QGridLayout()
        form_layout.setSpacing(10)
        form_layout.setVerticalSpacing(14)
        
        # Work Date
        self.work_date_input = QDateEdit()
        self.work_date_input.setDate(QDate.currentDate())
        self.work_date_input.setCalendarPopup(True)
        self.work_date_input.setDisplayFormat("yyyy-MM-dd")
        
        # Work Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("e.g., Engine oil change and filter replacement")
        
        # Working Hours
        self.hours_input = QDoubleSpinBox()
        self.hours_input.setMinimum(0.0)
        self.hours_input.setMaximum(999.99)
        self.hours_input.setValue(1.0)
        self.hours_input.setSingleStep(0.5)
        self.hours_input.setDecimals(2)
        self.hours_input.setSuffix(" hrs")
        self.hours_input.valueChanged.connect(self.update_cost)
        
        form_layout.addWidget(QLabel("Work Date:"), 0, 0)
        form_layout.addWidget(self.work_date_input, 0, 1)
        
        form_layout.addWidget(QLabel("Work Description:"), 1, 0, 1, 2)
        form_layout.addWidget(self.description_input, 2, 0, 1, 2)
        
        form_layout.addWidget(QLabel("Working Hours:"), 3, 0)
        form_layout.addWidget(self.hours_input, 3, 1)
        
        layout.addLayout(form_layout)
        
        # Labour Selection Section
        labour_label = QLabel("👷 Select Labour (Add multiple if needed)")
        labour_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        labour_label.setStyleSheet(f"color: {ColorPalette.ACCENT_PRIMARY}; padding: 10px 0px 5px 0px;")
        layout.addWidget(labour_label)
        
        # Labour selector with add button
        selector_layout = QHBoxLayout()
        selector_layout.setSpacing(8)
        
        self.labour_selector = QComboBox()
        self.labour_selector.addItems(self.labour_list)
        selector_layout.addWidget(self.labour_selector, 1)
        
        add_labour_btn = QPushButton("➕ Add")
        add_labour_btn.setObjectName("add")
        add_labour_btn.setMaximumWidth(80)
        add_labour_btn.clicked.connect(self.add_labour_to_list)
        selector_layout.addWidget(add_labour_btn)
        
        layout.addLayout(selector_layout)
        
        # Selected labour table
        self.labour_table = QTableWidget()
        self.labour_table.setColumnCount(4)
        self.labour_table.setHorizontalHeaderLabels(["Labour Name", "Grade", "Rate/hr", "Action"])
        self.labour_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.labour_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.labour_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.labour_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.labour_table.setMinimumHeight(150)
        self.labour_table.setMaximumHeight(200)
        layout.addWidget(self.labour_table)
        
        # Work cost summary
        cost_layout = QHBoxLayout()
        cost_layout.addStretch()
        cost_layout.addWidget(QLabel("Total Work Cost: "))
        self.work_cost_label = QLineEdit()
        self.work_cost_label.setReadOnly(True)
        self.work_cost_label.setText("Rs. 0.00")
        self.work_cost_label.setMaximumWidth(150)
        cost_layout.addWidget(self.work_cost_label)
        layout.addLayout(cost_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # If editing, populate fields
        if edit_data:
            # Load work date
            work_date_str = edit_data.get('work_date', QDate.currentDate().toString("yyyy-MM-dd"))
            self.work_date_input.setDate(QDate.fromString(work_date_str, "yyyy-MM-dd"))
            
            self.description_input.setPlainText(edit_data.get('description', ''))
            self.hours_input.setValue(float(edit_data.get('hours', 1.0)))
            
            # Load selected labour list
            labour_list_str = edit_data.get('labour_list', '[]')
            try:
                import json
                self.selected_labour = json.loads(labour_list_str)
                self.refresh_labour_table()
                self.update_cost()  # Update the cost display when editing
            except:
                self.selected_labour = []
    
    def add_labour_to_list(self):
        """Add selected labour to the table"""
        labour_name = self.labour_selector.currentText()
        
        if not labour_name:
            QMessageBox.warning(self, "Error", "Please select a labour")
            return
        
        # Check if already added
        for labour in self.selected_labour:
            if labour['name'] == labour_name:
                QMessageBox.warning(self, "Error", f"{labour_name} is already added")
                return
        
        # Get labour grade and rate
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT grade FROM labour WHERE name = ?", (labour_name,))
        result = c.fetchone()
        conn.close()
        
        if result:
            grade = result[0]
            rate = self.labour_rates.get(grade, 0.0)
            
            self.selected_labour.append({
                'name': labour_name,
                'grade': grade,
                'rate': rate
            })
            
            self.refresh_labour_table()
            self.update_cost()
    
    def remove_labour_from_list(self, index):
        """Remove labour from the table"""
        if 0 <= index < len(self.selected_labour):
            del self.selected_labour[index]
            self.refresh_labour_table()
            self.update_cost()
    
    def refresh_labour_table(self):
        """Refresh the labour selection table"""
        self.labour_table.setRowCount(len(self.selected_labour))
        self.labour_table.setRowHeight(0, 28)  # Set row height for all rows
        
        for row_idx, labour in enumerate(self.selected_labour):
            self.labour_table.setRowHeight(row_idx, 28)  # Set row height
            
            name_item = QTableWidgetItem(labour['name'])
            name_item.setFlags(name_item.flags() ^ Qt.ItemIsEditable)
            self.labour_table.setItem(row_idx, 0, name_item)
            
            grade_item = QTableWidgetItem(labour['grade'])
            grade_item.setFlags(grade_item.flags() ^ Qt.ItemIsEditable)
            self.labour_table.setItem(row_idx, 1, grade_item)
            
            rate_item = QTableWidgetItem(f"Rs. {labour['rate']:.2f}")
            rate_item.setFlags(rate_item.flags() ^ Qt.ItemIsEditable)
            self.labour_table.setItem(row_idx, 2, rate_item)
            
            # Remove button
            remove_btn = QPushButton("Del")
            remove_btn.setObjectName("remove")
            remove_btn.setMaximumWidth(35)
            remove_btn.setMaximumHeight(24)
            remove_btn.setStyleSheet("font-size: 9px; padding: 2px 4px; margin: 0px;")
            remove_btn.clicked.connect(lambda checked, r=row_idx: self.remove_labour_from_list(r))
            self.labour_table.setCellWidget(row_idx, 3, remove_btn)
    
    def update_cost(self):
        """Calculate work cost based on hours and all labour rates"""
        try:
            hours = self.hours_input.value()
            total_cost = 0.0
            
            for labour in self.selected_labour:
                rate = labour.get('rate', 0.0)
                total_cost += hours * rate
            
            self.work_cost_label.setText(f"Rs. {total_cost:.2f}")
        except ValueError:
            self.work_cost_label.setText("Rs. 0.00")
    
    def get_data(self):
        import json
        
        total_cost = 0.0
        try:
            hours = self.hours_input.value()
            for labour in self.selected_labour:
                rate = labour.get('rate', 0.0)
                total_cost += hours * rate
        except ValueError:
            total_cost = 0.0
        
        return {
            'work_date': self.work_date_input.date().toString("yyyy-MM-dd"),
            'description': self.description_input.toPlainText().strip(),
            'hours': str(self.hours_input.value()),
            'labour_list': json.dumps(self.selected_labour),
            'work_cost': f"{total_cost:.2f}"
        }


class OutsourceWorkDialog(QDialog):
    """Dialog for adding/editing outsource work entries"""
    def __init__(self, parent=None, edit_data=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Outsource Work")
        self.setMinimumWidth(550)
        
        # Modern dialog styling
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {ColorPalette.CARD_BG};
            }}
            QLabel {{
                color: {ColorPalette.TEXT_PRIMARY};
                font-weight: {Typography.WEIGHT_SEMIBOLD};
                font-size: {Typography.SIZE_SMALL}px;
                background: transparent;
            }}
            QLineEdit, QTextEdit, QDateEdit, QComboBox {{
                background-color: #fafafa;
                border: 1px solid {ColorPalette.BORDER_LIGHT};
                border-radius: {Spacing.BORDER_RADIUS_SMALL}px;
                padding: 8px 11px;
                font-size: {Typography.SIZE_SMALL}px;
            }}
            QLineEdit:focus, QTextEdit:focus, QDateEdit:focus, QComboBox:focus {{
                border: 2px solid {ColorPalette.ACCENT_PRIMARY};
                background-color: #ffffff;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
            }}
            QTextEdit {{
                min-height: 70px;
            }}
            QDialogButtonBox QPushButton {{
                background-color: {ColorPalette.ACCENT_PRIMARY};
                color: white;
                border: none;
                border-radius: {Spacing.BORDER_RADIUS_MEDIUM}px;
                padding: 9px 18px;
                font-weight: {Typography.WEIGHT_SEMIBOLD};
                min-width: 75px;
            }}
            QDialogButtonBox QPushButton:hover {{
                opacity: 0.9;
            }}
            QDialogButtonBox QPushButton[text="Cancel"] {{
                background-color: #e8e8e8;
                color: #333;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("🔨 Outsource Work Details")
        title.setFont(QFont("Segoe UI", 15, QFont.Bold))
        title.setStyleSheet("color: #1a1a1a; padding-bottom: 6px;")
        layout.addWidget(title)
        
        form_layout = QGridLayout()
        form_layout.setSpacing(10)
        form_layout.setVerticalSpacing(14)
        
        # Work Date
        self.work_date_input = QDateEdit()
        self.work_date_input.setDate(QDate.currentDate())
        self.work_date_input.setCalendarPopup(True)
        self.work_date_input.setDisplayFormat("yyyy-MM-dd")
        
        # Work Type with auto-complete
        self.work_type_input = QComboBox()
        self.work_type_input.setEditable(True)
        self.work_type_input.setInsertPolicy(QComboBox.NoInsert)
        
        # Load work types from database
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT name FROM outsource_types ORDER BY name")
            work_types = [row[0] for row in c.fetchall()]
            conn.close()
            self.work_type_input.addItems(work_types)
        except:
            # Fallback if database not available
            self.work_type_input.addItems(["Welding", "Painting", "Repair", "Alignment", "Testing", "Fabrication"])
        
        # Setup completer for the combo box
        completer = self.work_type_input.completer()
        from PySide6.QtWidgets import QCompleter as QCompleterClass
        completer.setCompletionMode(QCompleterClass.PopupCompletion)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.work_type_input.setPlaceholderText("Select or type work type...")
        
        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("e.g., Details of outsource work performed")
        
        # Cost
        self.cost_input = QLineEdit()
        self.cost_input.setPlaceholderText("e.g., 5000.00")
        self.cost_input.setValidator(None)  # Will be validated on save
        
        # Remark
        self.remark_input = QTextEdit()
        self.remark_input.setPlaceholderText("e.g., Notes, issues, or additional information")
        
        form_layout.addWidget(QLabel("Work Date:"), 0, 0)
        form_layout.addWidget(self.work_date_input, 0, 1)
        
        form_layout.addWidget(QLabel("Work Type:"), 1, 0)
        form_layout.addWidget(self.work_type_input, 1, 1)
        
        form_layout.addWidget(QLabel("Description:"), 2, 0, 1, 2)
        form_layout.addWidget(self.description_input, 3, 0, 1, 2)
        
        form_layout.addWidget(QLabel("Cost (Rs):"), 4, 0)
        form_layout.addWidget(self.cost_input, 4, 1)
        
        form_layout.addWidget(QLabel("Remark:"), 5, 0, 1, 2)
        form_layout.addWidget(self.remark_input, 6, 0, 1, 2)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # If editing, populate fields
        if edit_data:
            self.work_date_input.setDate(QDate.fromString(edit_data.get('work_date', QDate.currentDate().toString("yyyy-MM-dd")), "yyyy-MM-dd"))
            work_type = edit_data.get('work_type', '')
            # Set work type - find in list or add it
            idx = self.work_type_input.findText(work_type)
            if idx >= 0:
                self.work_type_input.setCurrentIndex(idx)
            else:
                self.work_type_input.addItem(work_type)
                self.work_type_input.setCurrentText(work_type)
            self.description_input.setPlainText(edit_data.get('description', ''))
            self.cost_input.setText(edit_data.get('cost', ''))
            self.remark_input.setPlainText(edit_data.get('remark', ''))
    
    def get_data(self):
        cost_text = self.cost_input.text().strip()
        try:
            cost = float(cost_text) if cost_text else 0.0
        except ValueError:
            cost = 0.0
        
        return {
            'work_date': self.work_date_input.date().toString("yyyy-MM-dd"),
            'work_type': self.work_type_input.currentText().strip(),
            'description': self.description_input.toPlainText().strip(),
            'cost': f"{cost:.2f}",
            'remark': self.remark_input.toPlainText().strip()
        }


class JobCardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.conn = sqlite3.connect(DB_PATH)
        self.spare_parts_data = []
        self.labour_works_data = []
        self.outsource_works_data = []

        # === Professional UI Colors ===
        bg_color = "#f5f5f5"
        card_color = "#ffffff"
        accent_color = "#2d7a5f"
        text_color = "#2c2c2c"
        border_color = "#e0e0e0"
        secondary_color = "#8b6f47"
        input_bg = "#fafafa"
        input_focus_bg = "#ffffff"

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                color: {text_color};
                font-family: "Segoe UI", -apple-system, system-ui;
                font-size: 13px;
            }}
            QLabel {{
                background: transparent;
            }}
            QLabel#page_title {{
                font-weight: 700;
                color: #1a1a1a;
                font-size: 24px;
                background: transparent;
            }}
            QLabel#section_title {{
                font-weight: 700;
                color: {accent_color};
                font-size: 14px;
                padding: 0px 0px 12px 0px;
                background: transparent;
            }}
            QLabel#field_label {{
                font-weight: 500;
                color: #666666;
                font-size: 11px;
                background: transparent;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            QLabel#total_label {{
                font-weight: 700;
                color: #1a1a1a;
                font-size: 14px;
                background: transparent;
            }}
            QFrame#card {{
                background-color: {card_color};
                border-radius: 8px;
                padding: 18px;
                border: none;
            }}
            QLineEdit, QDateEdit, QComboBox {{
                background-color: {input_bg};
                border: 1px solid {border_color};
                border-radius: 6px;
                padding: 8px 11px;
                min-height: 32px;
                font-size: 12px;
            }}
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{
                border: 2px solid {accent_color};
                background-color: {input_focus_bg};
                outline: none;
            }}
            QLineEdit:read-only {{
                background-color: #f8f8f8;
                color: #666666;
                font-weight: 500;
                border: 1px solid #efefef;
            }}
            QTextEdit {{
                background-color: {input_bg};
                border: 1px solid {border_color};
                border-radius: 6px;
                padding: 10px;
                min-height: 80px;
                font-size: 12px;
            }}
            QTextEdit:focus {{
                border: 2px solid {accent_color};
                background-color: {input_focus_bg};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 6px;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #999;
                margin-right: 4px;
            }}
            QPushButton {{
                border: none;
                border-radius: 6px;
                font-weight: 600;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.3px;
            }}
            QPushButton#primary {{
                background-color: {accent_color};
                color: white;
                padding: 11px 22px;
            }}
            QPushButton#primary:hover {{
                background-color: #246651;
            }}
            QPushButton#primary:pressed {{
                background-color: #1f5443;
            }}
            QPushButton#secondary {{
                background-color: {secondary_color};
                color: white;
                padding: 9px 16px;
            }}
            QPushButton#secondary:hover {{
                background-color: #735a38;
            }}
            QPushButton#muted {{
                background-color: #e8e8e8;
                color: #333;
                padding: 9px 16px;
            }}
            QPushButton#muted:hover {{
                background-color: #d5d5d5;
            }}
            QPushButton#danger {{
                background-color: #c84343;
                color: white;
                padding: 9px 16px;
            }}
            QPushButton#danger:hover {{
                background-color: #b03636;
            }}
            QPushButton#ghost {{
                background-color: transparent;
                color: #666;
                border: 1px solid #d0d0d0;
                padding: 9px 18px;
                text-transform: none;
                letter-spacing: 0px;
            }}
            QPushButton#ghost:hover {{
                background-color: #fafafa;
                border-color: #bbb;
            }}
            QTableWidget {{
                background-color: {card_color};
                border: 1px solid {border_color};
                border-radius: 6px;
                gridline-color: #f0f0f0;
                font-size: 12px;
            }}
            QTableWidget::item {{
                padding: 8px;
                background: transparent;
                border: none;
            }}
            QTableWidget::item:selected {{
                background-color: #e8f4f0;
                color: #1a1a1a;
            }}
            QHeaderView::section {{
                background-color: {accent_color};
                color: white;
                padding: 10px 8px;
                border: none;
                font-weight: 700;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.3px;
            }}
            QScrollBar:vertical {{
                background: #f5f5f5;
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: #bfbfbf;
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #9f9f9f;
            }}
        """)

        # === Scroll container ===
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        container = QWidget()
        root_layout = QVBoxLayout(container)
        root_layout.setContentsMargins(35, 28, 35, 28)
        root_layout.setSpacing(20)

        # === Page Title with Back Button ===
        header_layout, title_label, back_btn_top = create_page_header("📝 Job Card Entry")
        back_btn_top.clicked.connect(lambda: self.parent.go_to_home() if self.parent else None)
        root_layout.addLayout(header_layout)

        # === Basic Information Card ===
        basic_card = QFrame()
        basic_card.setObjectName("card")
        basic_layout = QVBoxLayout(basic_card)
        basic_layout.setSpacing(14)
        
        basic_title = QLabel("📋 Basic Information")
        basic_title.setObjectName("section_title")
        basic_layout.addWidget(basic_title)
        
        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)

        # === Create labels with consistent styling ===
        def create_label(text):
            lbl = QLabel(text)
            lbl.setObjectName("field_label")
            return lbl

        # === Inputs ===
        self.job_no_input = QLineEdit()
        self.job_no_input.setText(self.generate_job_number())
        self.job_no_input.setPlaceholderText("Auto-generated or enter custom job number")

        self.driver_input = QLineEdit()
        self.driver_input.setPlaceholderText("e.g., John Doe (Type for suggestions)")
        self.driver_input.textChanged.connect(self.on_driver_changed)
        self.driver_completer = QCompleter()
        self.driver_input.setCompleter(self.driver_completer)
        
        self.company_no_input = QLineEdit()
        self.company_no_input.setPlaceholderText("e.g., C-001 (Type for suggestions)")
        self.company_no_input.textChanged.connect(self.on_company_no_changed)
        self.company_no_completer = QCompleter()
        self.company_no_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.company_no_completer.setFilterMode(Qt.MatchContains)
        self.company_no_completer.setCompletionMode(QCompleter.PopupCompletion)
        self.company_no_completer.activated.connect(self.on_company_completer_activated)
        self.company_no_input.setCompleter(self.company_no_completer)

        self.site_input = QComboBox()
        self.vehicle_input = QLineEdit()
        self.vehicle_input.setPlaceholderText("e.g., REG-001 (Type for suggestions)")
        self.vehicle_input.textChanged.connect(self.on_vehicle_no_changed)
        self.vehicle_no_completer = QCompleter()
        self.vehicle_no_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.vehicle_no_completer.setFilterMode(Qt.MatchContains)
        self.vehicle_no_completer.setCompletionMode(QCompleter.PopupCompletion)
        self.vehicle_no_completer.activated.connect(self.on_vehicle_completer_activated)
        self.vehicle_input.setCompleter(self.vehicle_no_completer)

        self.section_input = QComboBox()
        
        self.make_input = QLineEdit()
        self.make_input.setReadOnly(True)
        self.make_input.setPlaceholderText("Auto-filled")

        self.hr_km_input = QLineEdit()
        self.hr_km_input.setPlaceholderText("e.g. 12450 km")

        self.model_input = QLineEdit()
        self.model_input.setReadOnly(True)
        self.model_input.setPlaceholderText("Auto-filled")

        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        self.date_input.dateChanged.connect(self.on_date_changed)  # Update job no when date changes

        self.type_input = QLineEdit()
        self.type_input.setReadOnly(True)
        self.type_input.setPlaceholderText("Auto-filled")
        
        self.engine_no_input = QLineEdit()
        self.engine_no_input.setReadOnly(True)
        self.engine_no_input.setPlaceholderText("Auto-filled")
        
        self.chassis_no_input = QLineEdit()
        self.chassis_no_input.setReadOnly(True)
        self.chassis_no_input.setPlaceholderText("Auto-filled")
        
        self.year_input = QLineEdit()
        self.year_input.setReadOnly(True)
        self.year_input.setPlaceholderText("Auto-filled")
        
        self.status_input = QComboBox()
        self.status_input.addItems(['Completed', 'In Progress'])
        self.status_input.setCurrentText('Completed')

        self.end_date_input = QDateEdit(QDate.currentDate())
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDisplayFormat("yyyy-MM-dd")

        # === Grid layout - Optimized Order ===
        grid.addWidget(create_label("Job No"), 0, 0)
        grid.addWidget(self.job_no_input, 0, 1)
        grid.addWidget(create_label("Driver Name"), 0, 2)
        grid.addWidget(self.driver_input, 0, 3)

        grid.addWidget(create_label("Company No"), 1, 0)
        grid.addWidget(self.company_no_input, 1, 1)
        grid.addWidget(create_label("Site"), 1, 2)
        grid.addWidget(self.site_input, 1, 3)

        grid.addWidget(create_label("Vehicle No"), 2, 0)
        grid.addWidget(self.vehicle_input, 2, 1)
        grid.addWidget(create_label("Section"), 2, 2)
        grid.addWidget(self.section_input, 2, 3)

        grid.addWidget(create_label("Make"), 3, 0)
        grid.addWidget(self.make_input, 3, 1)
        grid.addWidget(create_label("Model"), 3, 2)
        grid.addWidget(self.model_input, 3, 3)

        grid.addWidget(create_label("Type"), 4, 0)
        grid.addWidget(self.type_input, 4, 1)
        grid.addWidget(create_label("Hr/Km Reading"), 4, 2)
        grid.addWidget(self.hr_km_input, 4, 3)

        grid.addWidget(create_label("Engine No"), 5, 0)
        grid.addWidget(self.engine_no_input, 5, 1)
        grid.addWidget(create_label("Chassis No"), 5, 2)
        grid.addWidget(self.chassis_no_input, 5, 3)

        grid.addWidget(create_label("Year"), 6, 0)
        grid.addWidget(self.year_input, 6, 1)
        grid.addWidget(create_label("Status"), 6, 2)
        grid.addWidget(self.status_input, 6, 3)

        grid.addWidget(create_label("Start Date"), 7, 0)
        grid.addWidget(self.date_input, 7, 1)
        grid.addWidget(create_label("End Date"), 7, 2)
        grid.addWidget(self.end_date_input, 7, 3)

        basic_layout.addLayout(grid)
        root_layout.addWidget(basic_card)

        # === Job Description Card ===
        desc_card = QFrame()
        desc_card.setObjectName("card")
        desc_layout = QVBoxLayout(desc_card)
        desc_layout.setSpacing(12)
        
        desc_title = QLabel("📝 Job Description")
        desc_title.setObjectName("section_title")
        desc_layout.addWidget(desc_title)
        
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Describe the work performed, issues found, repairs made, maintenance activities, etc...")
        desc_layout.addWidget(self.desc_input)
        
        root_layout.addWidget(desc_card)

        # === Spare Parts Card ===
        spare_card = QFrame()
        spare_card.setObjectName("card")
        spare_layout = QVBoxLayout(spare_card)
        spare_layout.setSpacing(12)
        
        spare_header = QHBoxLayout()
        spare_header.setSpacing(10)
        spare_title = QLabel("🔧 Spare Parts & Materials")
        spare_title.setObjectName("section_title")
        spare_header.addWidget(spare_title)
        spare_header.addStretch()
        
        add_part_btn = QPushButton("+ Add Part")
        add_part_btn.setObjectName("secondary")
        add_part_btn.setFixedHeight(32)
        add_part_btn.setMaximumWidth(120)
        add_part_btn.setCursor(Qt.PointingHandCursor)
        add_part_btn.clicked.connect(self.add_spare_part)
        spare_header.addWidget(add_part_btn)
        
        spare_layout.addLayout(spare_header)
        
        # Spare parts table
        self.spare_table = QTableWidget()
        self.spare_table.setColumnCount(7)
        self.spare_table.setHorizontalHeaderLabels(["#", "ID Code", "Description", "Quantity", "Unit", "Total", "Remark"])
        self.spare_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.spare_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.spare_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.spare_table.setMinimumHeight(180)
        self.spare_table.setMaximumHeight(260)
        self.spare_table.setSelectionBehavior(QTableWidget.SelectRows)
        spare_layout.addWidget(self.spare_table)
        
        # Spare Parts Total
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        self.spare_parts_total_label = QLabel("Spare Parts: Rs. 0.00")
        self.spare_parts_total_label.setObjectName("total_label")
        self.spare_parts_total_label.setStyleSheet("font-size: 13px; padding: 8px 12px; background-color: #e8f4f0; border-radius: 6px;")
        total_layout.addWidget(self.spare_parts_total_label)
        spare_layout.addLayout(total_layout)
        
        # Spare parts action buttons
        spare_btn_layout = QHBoxLayout()
        spare_btn_layout.setSpacing(8)
        
        edit_part_btn = QPushButton("✏️ Edit")
        edit_part_btn.setObjectName("muted")
        edit_part_btn.setFixedHeight(32)
        edit_part_btn.setMaximumWidth(100)
        edit_part_btn.setCursor(Qt.PointingHandCursor)
        edit_part_btn.clicked.connect(self.edit_spare_part)
        
        delete_part_btn = QPushButton("Del")
        delete_part_btn.setObjectName("danger")
        delete_part_btn.setFixedHeight(32)
        delete_part_btn.setMaximumWidth(70)
        delete_part_btn.setCursor(Qt.PointingHandCursor)
        delete_part_btn.clicked.connect(self.delete_spare_part)
        
        spare_btn_layout.addWidget(edit_part_btn)
        spare_btn_layout.addWidget(delete_part_btn)
        spare_btn_layout.addStretch()
        spare_layout.addLayout(spare_btn_layout)
        
        root_layout.addWidget(spare_card)

        # === Labour Works Card ===
        labour_card = QFrame()
        labour_card.setObjectName("card")
        labour_layout = QVBoxLayout(labour_card)
        labour_layout.setSpacing(12)
        
        labour_header = QHBoxLayout()
        labour_header.setSpacing(10)
        labour_title = QLabel("👷 Labour Works")
        labour_title.setObjectName("section_title")
        labour_header.addWidget(labour_title)
        labour_header.addStretch()
        
        add_work_btn = QPushButton("+ Add Work")
        add_work_btn.setObjectName("secondary")
        add_work_btn.setFixedHeight(32)
        add_work_btn.setMaximumWidth(120)
        add_work_btn.setCursor(Qt.PointingHandCursor)
        add_work_btn.clicked.connect(self.add_labour_work)
        labour_header.addWidget(add_work_btn)
        
        labour_layout.addLayout(labour_header)
        
        # Labour works table
        self.labour_table = QTableWidget()
        self.labour_table.setColumnCount(7)
        self.labour_table.setHorizontalHeaderLabels(["#", "Description", "Hours", "Labour", "Grade", "Rate/hr", "Cost"])
        self.labour_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.labour_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.labour_table.setMinimumHeight(180)
        self.labour_table.setMaximumHeight(260)
        self.labour_table.setSelectionBehavior(QTableWidget.SelectRows)
        labour_layout.addWidget(self.labour_table)
        
        # Labour Cost Total
        labour_total_layout = QHBoxLayout()
        labour_total_layout.addStretch()
        self.labour_cost_total_label = QLabel("Labour Cost: Rs. 0.00")
        self.labour_cost_total_label.setObjectName("total_label")
        self.labour_cost_total_label.setStyleSheet("font-size: 13px; padding: 8px 12px; background-color: #e8f4f0; border-radius: 6px;")
        labour_total_layout.addWidget(self.labour_cost_total_label)
        labour_layout.addLayout(labour_total_layout)
        
        # Labour work action buttons
        labour_btn_layout = QHBoxLayout()
        labour_btn_layout.setSpacing(8)
        
        edit_work_btn = QPushButton("✏️ Edit")
        edit_work_btn.setObjectName("muted")
        edit_work_btn.setFixedHeight(32)
        edit_work_btn.setMaximumWidth(100)
        edit_work_btn.setCursor(Qt.PointingHandCursor)
        edit_work_btn.clicked.connect(self.edit_labour_work)
        
        delete_work_btn = QPushButton("Del")
        delete_work_btn.setObjectName("danger")
        delete_work_btn.setFixedHeight(32)
        delete_work_btn.setMaximumWidth(70)
        delete_work_btn.setCursor(Qt.PointingHandCursor)
        delete_work_btn.clicked.connect(self.delete_labour_work)
        
        labour_btn_layout.addWidget(edit_work_btn)
        labour_btn_layout.addWidget(delete_work_btn)
        labour_btn_layout.addStretch()
        labour_layout.addLayout(labour_btn_layout)
        
        root_layout.addWidget(labour_card)

        # === Outsource Works Card ===
        outsource_card = QFrame()
        outsource_card.setObjectName("card")
        outsource_layout = QVBoxLayout(outsource_card)
        outsource_layout.setSpacing(12)
        
        outsource_header = QHBoxLayout()
        outsource_header.setSpacing(10)
        outsource_title = QLabel("🔨 Outsource Works")
        outsource_title.setObjectName("section_title")
        outsource_header.addWidget(outsource_title)
        outsource_header.addStretch()
        
        add_outsource_btn = QPushButton("+ Add Work")
        add_outsource_btn.setObjectName("secondary")
        add_outsource_btn.setFixedHeight(32)
        add_outsource_btn.setMaximumWidth(120)
        add_outsource_btn.setCursor(Qt.PointingHandCursor)
        add_outsource_btn.clicked.connect(self.add_outsource_work)
        outsource_header.addWidget(add_outsource_btn)
        
        outsource_layout.addLayout(outsource_header)
        
        # Outsource works table
        self.outsource_table = QTableWidget()
        self.outsource_table.setColumnCount(6)
        self.outsource_table.setHorizontalHeaderLabels(["#", "Date", "Work Type", "Description", "Cost", "Remark"])
        self.outsource_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.outsource_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.outsource_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.outsource_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.outsource_table.setMinimumHeight(180)
        self.outsource_table.setMaximumHeight(260)
        self.outsource_table.setSelectionBehavior(QTableWidget.SelectRows)
        outsource_layout.addWidget(self.outsource_table)
        
        # Outsource Total Cost
        outsource_total_layout = QHBoxLayout()
        outsource_total_layout.addStretch()
        self.outsource_total_label = QLabel("Outsource Cost: Rs. 0.00")
        self.outsource_total_label.setObjectName("total_label")
        self.outsource_total_label.setStyleSheet("font-size: 13px; padding: 8px 12px; background-color: #e8f4f0; border-radius: 6px;")
        outsource_total_layout.addWidget(self.outsource_total_label)
        outsource_layout.addLayout(outsource_total_layout)
        
        # Outsource action buttons
        outsource_btn_layout = QHBoxLayout()
        outsource_btn_layout.setSpacing(8)
        
        edit_outsource_btn = QPushButton("✏️ Edit")
        edit_outsource_btn.setObjectName("muted")
        edit_outsource_btn.setFixedHeight(32)
        edit_outsource_btn.setMaximumWidth(100)
        edit_outsource_btn.setCursor(Qt.PointingHandCursor)
        edit_outsource_btn.clicked.connect(self.edit_outsource_work)
        
        delete_outsource_btn = QPushButton("Del")
        delete_outsource_btn.setObjectName("danger")
        delete_outsource_btn.setFixedHeight(32)
        delete_outsource_btn.setMaximumWidth(70)
        delete_outsource_btn.setCursor(Qt.PointingHandCursor)
        delete_outsource_btn.clicked.connect(self.delete_outsource_work)
        
        outsource_btn_layout.addWidget(edit_outsource_btn)
        outsource_btn_layout.addWidget(delete_outsource_btn)
        outsource_btn_layout.addStretch()
        outsource_layout.addLayout(outsource_btn_layout)
        
        root_layout.addWidget(outsource_card)

        # === Grand Total (Spare Parts + Labour + Outsource) ===
        grand_card = QFrame()
        grand_card.setObjectName("card")
        grand_layout = QVBoxLayout(grand_card)
        grand_layout.setContentsMargins(18, 16, 18, 16)
        
        grand_total_inner = QHBoxLayout()
        grand_total_inner.addStretch()
        
        spare_total_lbl = QLabel("Spare Parts: ")
        spare_total_lbl.setObjectName("total_label")
        spare_total_lbl.setStyleSheet("font-size: 12px;")
        self.spare_total_display = QLabel("Rs. 0.00")
        self.spare_total_display.setObjectName("total_label")
        self.spare_total_display.setStyleSheet("font-size: 12px; font-weight: 700;")
        
        labour_cost_lbl = QLabel("Labour Cost: ")
        labour_cost_lbl.setObjectName("total_label")
        labour_cost_lbl.setStyleSheet("font-size: 12px;")
        self.labour_cost_display = QLabel("Rs. 0.00")
        self.labour_cost_display.setObjectName("total_label")
        self.labour_cost_display.setStyleSheet("font-size: 12px; font-weight: 700;")
        
        outsource_cost_lbl = QLabel("Outsource: ")
        outsource_cost_lbl.setObjectName("total_label")
        outsource_cost_lbl.setStyleSheet("font-size: 12px;")
        self.outsource_cost_display = QLabel("Rs. 0.00")
        self.outsource_cost_display.setObjectName("total_label")
        self.outsource_cost_display.setStyleSheet("font-size: 12px; font-weight: 700;")
        
        grand_separator = QLabel("  |  ")
        grand_separator.setStyleSheet("font-size: 12px; color: #ccc;")
        
        grand_lbl = QLabel("GRAND TOTAL: ")
        grand_lbl.setObjectName("total_label")
        grand_lbl.setStyleSheet("font-size: 14px;")
        self.grand_total_display = QLabel("Rs. 0.00")
        self.grand_total_display.setObjectName("total_label")
        self.grand_total_display.setStyleSheet("font-size: 14px; font-weight: 700; color: #c84343;")
        
        grand_total_inner.addWidget(spare_total_lbl)
        grand_total_inner.addWidget(self.spare_total_display)
        grand_total_inner.addSpacing(20)
        grand_total_inner.addWidget(labour_cost_lbl)
        grand_total_inner.addWidget(self.labour_cost_display)
        grand_total_inner.addSpacing(20)
        grand_total_inner.addWidget(outsource_cost_lbl)
        grand_total_inner.addWidget(self.outsource_cost_display)
        grand_total_inner.addWidget(grand_separator)
        grand_total_inner.addWidget(grand_lbl)
        grand_total_inner.addWidget(self.grand_total_display)
        
        grand_layout.addLayout(grand_total_inner)
        root_layout.addWidget(grand_card)

        # === Action Buttons ===
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        
        save_btn = QPushButton("💾 Save Job Card")
        save_btn.setObjectName("primary")
        save_btn.setFixedHeight(38)
        save_btn.setMinimumWidth(180)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self.save_job_card)

        clear_btn = QPushButton("🧹 Clear All")
        clear_btn.setObjectName("muted")
        clear_btn.setFixedHeight(38)
        clear_btn.setMinimumWidth(120)
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.clicked.connect(self.clear_all_fields)

        btn_row.addWidget(save_btn)
        btn_row.addWidget(clear_btn)
        btn_row.addStretch()

        root_layout.addLayout(btn_row)
        root_layout.addStretch()
        
        scroll.setWidget(container)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
        self.setLayout(layout)

        # === Load initial data ===
        self.refresh_dropdowns()

    def refresh_dropdowns(self):
        # Refresh job number in real-time
        self.job_no_input.setText(self.generate_job_number())
        
        cur = self.conn.cursor()

        # Build comprehensive vehicle data for bidirectional lookup
        cur.execute("SELECT company_no, number, make, model, type, engine_no, chassis_no, year FROM vehicles")
        self.vehicles_data = {}  # {vehicle_number: {company_no, make, model, type, engine_no, chassis_no, year}} - for vehicles with numbers
        self.company_vehicles = {}  # {company_no: [{make, model, type, number, engine_no, chassis_no, year}, ...]} - all vehicles per company
        self.vehicle_to_company = {}  # {vehicle_number: company_no} - quick lookup
        self.company_to_vehicles = {}  # {company_no: [vehicle_numbers]} - vehicles per company
        
        vehicle_numbers = set()
        company_nos = set()
        
        for row in cur.fetchall():
            company_no, number, make, model, vtype, engine_no, chassis_no, year = row
            
            # Always store company info
            if company_no:
                company_nos.add(company_no)
                if company_no not in self.company_vehicles:
                    self.company_vehicles[company_no] = []
                
                # Store vehicle info under company
                self.company_vehicles[company_no].append({
                    'number': number if (number and number != "-") else None,
                    'make': make,
                    'model': model,
                    'type': vtype,
                    'engine_no': engine_no,
                    'chassis_no': chassis_no,
                    'year': year
                })
            
            # If vehicle has a number, index it
            if number and number != "-":
                self.vehicles_data[number] = {
                    'company_no': company_no,
                    'make': make,
                    'model': model,
                    'type': vtype,
                    'engine_no': engine_no,
                    'chassis_no': chassis_no,
                    'year': year
                }
                self.vehicle_to_company[number] = company_no
                vehicle_numbers.add(number)
                
                if company_no:
                    if company_no not in self.company_to_vehicles:
                        self.company_to_vehicles[company_no] = []
                    self.company_to_vehicles[company_no].append(number)

        # Setup company_no auto-complete with all companies
        company_model = QStringListModel(sorted(company_nos))
        self.company_no_completer.setModel(company_model)
        self.company_no_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.company_no_completer.setFilterMode(Qt.MatchContains)

        # Setup vehicle_no auto-complete with vehicles that have numbers
        vehicle_model = QStringListModel(sorted(vehicle_numbers))
        self.vehicle_no_completer.setModel(vehicle_model)
        self.vehicle_no_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.vehicle_no_completer.setFilterMode(Qt.MatchContains)

        # Drivers - build lookup
        cur.execute("SELECT name FROM drivers")
        driver_names = [d[0] for d in cur.fetchall()]
        self.driver_names = set(driver_names)
        
        driver_model = QStringListModel(sorted(driver_names))
        self.driver_completer.setModel(driver_model)
        self.driver_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.driver_completer.setFilterMode(Qt.MatchContains)

        # Sites
        cur.execute("SELECT name FROM sites")
        self.site_input.clear()
        [self.site_input.addItem(s[0]) for s in cur.fetchall()]

        # Sections
        cur.execute("SELECT name FROM sections")
        self.section_input.clear()
        [self.section_input.addItem(s[0]) for s in cur.fetchall()]

        # Labour - build lookup (renamed from technicians)
        cur.execute("SELECT name FROM labour ORDER BY name")
        labour_names = [t[0] for t in cur.fetchall()]
        self.labour_names = labour_names
        self.technician_names = labour_names  # Keep for backwards compatibility

    def on_company_completer_activated(self, text):
        """Handle when user selects from company completer"""
        # Trigger the change handler to process the selected company
        self.on_company_no_changed(text)

    def on_company_no_changed(self, company_no):
        """Update vehicle suggestions and details when company_no changes"""
        company_no = company_no.strip()
        
        if not company_no:
            # Clear vehicle and vehicle details
            self.vehicle_input.blockSignals(True)
            self.vehicle_input.clear()
            self.vehicle_input.blockSignals(False)
            self.make_input.clear()
            self.model_input.clear()
            self.type_input.clear()
            # Reset vehicle completer to show all vehicles
            all_vehicles = sorted(self.vehicles_data.keys())
            vehicle_model = QStringListModel(all_vehicles)
            self.vehicle_no_completer.setModel(vehicle_model)
            return
        
        # Check if company_no exists in our data
        if company_no in self.company_vehicles:
            # Get all vehicles for this company (including those without numbers)
            vehicles_for_company = self.company_vehicles[company_no]
            
            # Get vehicle numbers for this company (may be empty)
            vehicle_numbers_for_company = self.company_to_vehicles.get(company_no, [])
            
            # ONLY rebuild model if company was actually selected (exact match)
            # Don't rebuild during partial typing
            matching_companies = [c for c in self.company_vehicles.keys() if c.lower() == company_no.lower()]
            
            if matching_companies:
                # Company exactly matches - update vehicle completer
                vehicle_model = QStringListModel(sorted(vehicle_numbers_for_company))
                self.vehicle_no_completer.setModel(vehicle_model)
                
                # If there's only one vehicle with a number for this company, auto-select it
                if len(vehicle_numbers_for_company) == 1:
                    self.vehicle_input.blockSignals(True)
                    self.vehicle_input.setText(vehicle_numbers_for_company[0])
                    self.vehicle_input.blockSignals(False)
                    self._update_vehicle_details(vehicle_numbers_for_company[0])
                # If there are no vehicles with numbers, show the first vehicle's details anyway
                elif len(vehicle_numbers_for_company) == 0 and vehicles_for_company:
                    self.vehicle_input.blockSignals(True)
                    self.vehicle_input.clear()
                    self.vehicle_input.blockSignals(False)
                    # Use first vehicle data (even if it has no number)
                    first_vehicle = vehicles_for_company[0]
                    self.make_input.setText(first_vehicle.get('make', ''))
                    self.model_input.setText(first_vehicle.get('model', ''))
                    self.type_input.setText(first_vehicle.get('type', ''))
                else:
                    self.make_input.clear()
                    self.model_input.clear()
                    self.type_input.clear()
            # If partial match during typing, don't update completer model
        else:
            # Reset vehicle completer to all vehicles
            vehicle_numbers = sorted(self.vehicles_data.keys())
            vehicle_model = QStringListModel(vehicle_numbers)
            self.vehicle_no_completer.setModel(vehicle_model)
            
            self.make_input.clear()
            self.model_input.clear()
            self.type_input.clear()

    def on_vehicle_completer_activated(self, text):
        """Handle when user selects from vehicle completer"""
        # Trigger the change handler to process the selected vehicle
        self.on_vehicle_no_changed(text)

    def on_vehicle_no_changed(self, vehicle_no):
        """Update company_no and vehicle details when vehicle_no changes"""
        vehicle_no = vehicle_no.strip()
        
        # If empty, clear everything
        if not vehicle_no:
            self.company_no_input.blockSignals(True)
            self.company_no_input.clear()
            self.company_no_input.blockSignals(False)
            self.make_input.clear()
            self.model_input.clear()
            self.type_input.clear()
            return
        
        # Check if this is a COMPLETE match with our database
        # Only update if it's a full match (not partial typing)
        matching_vehicles = [v for v in self.vehicles_data.keys() if v.lower() == vehicle_no.lower()]
        
        if matching_vehicles:
            # Found exact match - do NOT rebuild model to keep popup open
            matched_vehicle = matching_vehicles[0]
            company_no = self.vehicle_to_company[matched_vehicle]
            
            # Update company_no field without triggering its change handler
            self.company_no_input.blockSignals(True)
            self.company_no_input.setText(company_no)
            self.company_no_input.blockSignals(False)
            
            # Update vehicle details
            self._update_vehicle_details(matched_vehicle)
        else:
            # Partial match - user is still typing
            # DO NOT rebuild the model - keep completer popup open for navigation
            pass

    def on_driver_changed(self, driver_name):
        """Validate driver name when it changes"""
        driver_name = driver_name.strip()
        
        # Just validate - driver field doesn't need to trigger other fields
        if driver_name and driver_name not in self.driver_names:
            # Not a valid driver - user is still typing
            pass

    def _update_vehicle_details(self, vehicle_no):
        """Helper method to update make, model, type, engine_no, chassis_no, year from vehicle data"""
        if vehicle_no in self.vehicles_data:
            data = self.vehicles_data[vehicle_no]
            self.make_input.setText(data.get('make', ''))
            self.model_input.setText(data.get('model', ''))
            self.type_input.setText(data.get('type', ''))
            self.engine_no_input.setText(data.get('engine_no', ''))
            self.chassis_no_input.setText(data.get('chassis_no', ''))
            self.year_input.setText(data.get('year', ''))
        else:
            self.make_input.clear()
            self.model_input.clear()
            self.type_input.clear()
            self.engine_no_input.clear()
            self.chassis_no_input.clear()
            self.year_input.clear()

    def on_date_changed(self):
        """Update job number when start date changes"""
        self.job_no_input.setText(self.generate_job_number())

    def generate_job_number(self):
        cur = self.conn.cursor()
        # Use start date if available, otherwise use current date
        if hasattr(self, 'date_input'):
            start_date = self.date_input.date()
        else:
            start_date = QDate.currentDate()
        
        yy = start_date.toString("yy")
        mm = start_date.toString("MM")
        
        # Find the maximum job number for the selected month/year
        cur.execute("SELECT job_no FROM job_cards WHERE job_no LIKE ? ORDER BY job_no DESC LIMIT 1", 
                   (f"SEN/DO/{yy}{mm}%",))
        last_job = cur.fetchone()

        if last_job:
            try:
                next_num = int(last_job[0][-3:]) + 1
            except (ValueError, IndexError):
                next_num = 1
        else:
            next_num = 1

        return f"SEN/DO/{yy}{mm}{next_num:03d}"

    def add_spare_part(self):
        dialog = SparePartDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if data['description']:
                self.spare_parts_data.append(data)
                self.refresh_spare_table()
                self.update_grand_totals()

    def edit_spare_part(self):
        current_row = self.spare_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a spare part to edit.")
            return
        
        current_data = self.spare_parts_data[current_row]
        dialog = SparePartDialog(self, edit_data=current_data)
        if dialog.exec():
            data = dialog.get_data()
            if data['description']:
                self.spare_parts_data[current_row] = data
                self.refresh_spare_table()
                self.update_grand_totals()

    def delete_spare_part(self):
        current_row = self.spare_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a spare part to delete.")
            return
        
        confirm = QMessageBox.question(self, "Confirm Delete", 
                                      "Are you sure you want to delete this spare part?",
                                      QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            del self.spare_parts_data[current_row]
            self.refresh_spare_table()
            self.update_grand_totals()

    def refresh_spare_table(self):
        self.spare_table.setRowCount(len(self.spare_parts_data))
        self.spare_table.setColumnCount(7)
        self.spare_table.setHorizontalHeaderLabels(["#", "ID Code", "Description", "Quantity", "Unit", "Total", "Remark"])
        
        spare_total = 0.0
        
        for row_idx, part in enumerate(self.spare_parts_data):
            self.spare_table.setItem(row_idx, 0, QTableWidgetItem(str(row_idx + 1)))
            self.spare_table.setItem(row_idx, 1, QTableWidgetItem(part.get('id_code', '')))
            self.spare_table.setItem(row_idx, 2, QTableWidgetItem(part.get('description', '')))
            self.spare_table.setItem(row_idx, 3, QTableWidgetItem(part.get('quantity', '')))
            self.spare_table.setItem(row_idx, 4, QTableWidgetItem(part.get('unit', '')))
            self.spare_table.setItem(row_idx, 5, QTableWidgetItem(part.get('total', '')))
            self.spare_table.setItem(row_idx, 6, QTableWidgetItem(part.get('remark', '')))
            
            try:
                total = float(part.get('total', 0))
                spare_total += total
            except ValueError:
                pass
        
        self.spare_parts_total_label.setText(f"Spare Parts: Rs. {spare_total:,.2f}")
        # Auto-update grand totals when spare parts change
        self.update_grand_totals()

    def add_labour_work(self):
        import json
        
        dialog = LabourWorkDialog(self, labour_list=self.labour_names)
        if dialog.exec():
            data = dialog.get_data()
            if data['description']:
                try:
                    labour_list = json.loads(data.get('labour_list', '[]'))
                    if labour_list:
                        self.labour_works_data.append(data)
                        self.refresh_labour_table()
                        self.update_grand_totals()
                    else:
                        QMessageBox.warning(self, "Error", "Please add at least one labour to the work")
                except:
                    QMessageBox.warning(self, "Error", "Invalid labour selection")

    def edit_labour_work(self):
        import json
        
        current_row = self.labour_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a labour work to edit.")
            return
        
        current_data = self.labour_works_data[current_row]
        dialog = LabourWorkDialog(self, edit_data=current_data, labour_list=self.labour_names)
        if dialog.exec():
            data = dialog.get_data()
            if data['description']:
                try:
                    labour_list = json.loads(data.get('labour_list', '[]'))
                    if labour_list:
                        self.labour_works_data[current_row] = data
                        self.refresh_labour_table()
                        self.update_grand_totals()
                    else:
                        QMessageBox.warning(self, "Error", "Please add at least one labour to the work")
                except:
                    QMessageBox.warning(self, "Error", "Invalid labour selection")

    def delete_labour_work(self):
        current_row = self.labour_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a labour work to delete.")
            return
        
        confirm = QMessageBox.question(self, "Confirm Delete", 
                                      "Are you sure you want to delete this labour work?",
                                      QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            del self.labour_works_data[current_row]
            self.refresh_labour_table()
            self.update_grand_totals()

    def refresh_labour_table(self):
        import json
        
        self.labour_table.setRowCount(len(self.labour_works_data))
        self.labour_table.setColumnCount(5)
        self.labour_table.setHorizontalHeaderLabels(["#", "Date", "Description", "Hours", "Cost"])
        
        labour_total = 0.0
        
        for row_idx, work in enumerate(self.labour_works_data):
            self.labour_table.setItem(row_idx, 0, QTableWidgetItem(str(row_idx + 1)))
            self.labour_table.setItem(row_idx, 1, QTableWidgetItem(work.get('work_date', '')))
            self.labour_table.setItem(row_idx, 2, QTableWidgetItem(work.get('description', '')))
            self.labour_table.setItem(row_idx, 3, QTableWidgetItem(f"{work.get('hours', '')} hrs"))
            
            cost_text = work.get('work_cost', '0')
            self.labour_table.setItem(row_idx, 4, QTableWidgetItem(f"Rs. {cost_text}"))
            
            try:
                cost = float(cost_text)
                labour_total += cost
            except ValueError:
                pass
        
        self.labour_cost_total_label.setText(f"Labour Cost: Rs. {labour_total:,.2f}")

    def add_outsource_work(self):
        """Add a new outsource work entry"""
        dialog = OutsourceWorkDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if data['work_type'] or data['description']:
                self.outsource_works_data.append(data)
                self.refresh_outsource_table()
                self.update_grand_totals()

    def edit_outsource_work(self):
        """Edit selected outsource work entry"""
        current_row = self.outsource_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select an outsource work to edit.")
            return
        
        current_data = self.outsource_works_data[current_row]
        dialog = OutsourceWorkDialog(self, edit_data=current_data)
        if dialog.exec():
            data = dialog.get_data()
            if data['work_type'] or data['description']:
                self.outsource_works_data[current_row] = data
                self.refresh_outsource_table()
                self.update_grand_totals()

    def delete_outsource_work(self):
        """Delete selected outsource work entry"""
        current_row = self.outsource_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select an outsource work to delete.")
            return
        
        confirm = QMessageBox.question(self, "Confirm Delete", 
                                      "Are you sure you want to delete this outsource work?",
                                      QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            del self.outsource_works_data[current_row]
            self.refresh_outsource_table()
            self.update_grand_totals()

    def refresh_outsource_table(self):
        """Refresh the outsource works table display"""
        self.outsource_table.setRowCount(len(self.outsource_works_data))
        self.outsource_table.setColumnCount(6)
        self.outsource_table.setHorizontalHeaderLabels(["#", "Date", "Work Type", "Description", "Cost", "Remark"])
        
        outsource_total = 0.0
        
        for row_idx, work in enumerate(self.outsource_works_data):
            self.outsource_table.setItem(row_idx, 0, QTableWidgetItem(str(row_idx + 1)))
            self.outsource_table.setItem(row_idx, 1, QTableWidgetItem(work.get('work_date', '')))
            self.outsource_table.setItem(row_idx, 2, QTableWidgetItem(work.get('work_type', '')))
            self.outsource_table.setItem(row_idx, 3, QTableWidgetItem(work.get('description', '')))
            
            cost_text = work.get('cost', '0')
            self.outsource_table.setItem(row_idx, 4, QTableWidgetItem(f"Rs. {cost_text}"))
            self.outsource_table.setItem(row_idx, 5, QTableWidgetItem(work.get('remark', '')))
            
            try:
                cost = float(cost_text)
                outsource_total += cost
            except ValueError:
                pass
        
        self.outsource_total_label.setText(f"Outsource Cost: Rs. {outsource_total:,.2f}")

    def update_grand_totals(self):
        """Calculate and display spare parts, labour, outsource, and grand totals"""
        # Calculate spare parts total
        spare_total = 0.0
        for part in self.spare_parts_data:
            try:
                total = float(part.get('total', 0))
                spare_total += total
            except ValueError:
                pass
        
        # Calculate labour total
        labour_total = 0.0
        for work in self.labour_works_data:
            try:
                cost = float(work.get('work_cost', 0))
                labour_total += cost
            except ValueError:
                pass
        
        # Calculate outsource total
        outsource_total = 0.0
        for work in self.outsource_works_data:
            try:
                cost = float(work.get('cost', 0))
                outsource_total += cost
            except ValueError:
                pass
        
        # Update displays
        grand_total = spare_total + labour_total + outsource_total
        
        self.spare_total_display.setText(f"Rs. {spare_total:,.2f}")
        self.labour_cost_display.setText(f"Rs. {labour_total:,.2f}")
        self.outsource_cost_display.setText(f"Rs. {outsource_total:,.2f}")
        self.grand_total_display.setText(f"Rs. {grand_total:,.2f}")

    def clear_all_fields(self):
        # Only ask for confirmation when Clear button is clicked
        reply = QMessageBox.question(
            self,
            "Clear All Fields",
            "Are you sure you want to clear all fields?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._perform_clear()

    def _perform_clear(self):
        """Internal method to clear fields without confirmation"""
        self.job_no_input.setText(self.generate_job_number())
        self.company_no_input.clear()
        self.vehicle_input.clear()
        self.driver_input.clear()
        for combo in [self.site_input, self.section_input]:
            combo.setCurrentIndex(-1)
        for line in [self.make_input, self.model_input, self.type_input, self.hr_km_input, self.engine_no_input, self.chassis_no_input, self.year_input]:
            line.clear()
        self.status_input.setCurrentText('Completed')
        self.date_input.setDate(QDate.currentDate())
        self.end_date_input.setDate(QDate.currentDate())
        self.desc_input.clear()
        self.spare_parts_data = []
        self.labour_works_data = []
        self.outsource_works_data = []
        self.refresh_spare_table()
        self.refresh_labour_table()
        self.refresh_outsource_table()
        self.update_grand_totals()

    def save_job_card(self):
        """Save job card with status defaulting to 'Completed'"""
        job_no = self.job_no_input.text().strip()
        company_no = self.company_no_input.text().strip()
        driver_name = self.driver_input.text().strip()

        if not company_no:
            QMessageBox.warning(self, "Missing Field", "Please enter a Company No.")
            return

        if company_no not in self.company_to_vehicles and company_no not in self.company_vehicles:
            QMessageBox.warning(self, "Invalid Company No", f"Company No '{company_no}' not found in database.")
            return

        if driver_name and driver_name not in self.driver_names:
            QMessageBox.warning(self, "Invalid Driver", f"Driver '{driver_name}' not found in database.")
            return

        # Check if job_no already exists
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM job_cards WHERE job_no = ?", (job_no,))
        if cur.fetchone()[0] > 0:
            QMessageBox.warning(self, "Duplicate Entry", f"Job card {job_no} already exists!")
            return

        import json
        spare_parts_json = json.dumps(self.spare_parts_data)
        labour_works_json = json.dumps(self.labour_works_data)
        outsource_works_json = json.dumps(self.outsource_works_data)

        try:
            cur.execute("""
                INSERT INTO job_cards (
                    job_no, company_no, vehicle_no, driver, make, model, type,
                    site, section, hr_km, start_date, end_date, description, spare_parts, labour_works, outsource_works, status, engine_no, chassis_no, year
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_no,
                company_no,
                self.vehicle_input.text().strip() or "-",
                driver_name,
                self.make_input.text(),
                self.model_input.text(),
                self.type_input.text(),
                self.site_input.currentText(),
                self.section_input.currentText(),
                self.hr_km_input.text(),
                self.date_input.date().toString("yyyy-MM-dd"),
                self.end_date_input.date().toString("yyyy-MM-dd"),
                self.desc_input.toPlainText(),
                spare_parts_json,
                labour_works_json,
                outsource_works_json,
                self.status_input.currentText(),  # Get status from dropdown
                self.engine_no_input.text() if hasattr(self, 'engine_no_input') else '',
                self.chassis_no_input.text() if hasattr(self, 'chassis_no_input') else '',
                self.year_input.text() if hasattr(self, 'year_input') else ''
            ))
            self.conn.commit()

            QMessageBox.information(self, "Success ✅", f"Job card {job_no} has been saved successfully!")
            
            # Automatically clear all fields after successful save
            self._perform_clear()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save job card: {str(e)}")