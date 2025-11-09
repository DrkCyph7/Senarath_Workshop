from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal
import shutil
import os


class BackupWorker(QThread):
    progress = Signal(int)
    finished = Signal(str)

    def __init__(self, source_path, dest_path):
        super().__init__()
        self.source_path = source_path
        self.dest_path = dest_path

    def run(self):
        try:
            total_size = os.path.getsize(self.source_path)
            copied = 0
            with open(self.source_path, 'rb') as src, open(self.dest_path, 'wb') as dst:
                while chunk := src.read(1024 * 1024):
                    dst.write(chunk)
                    copied += len(chunk)
                    self.progress.emit(int((copied / total_size) * 100))
            self.finished.emit("Backup completed successfully ✅")
        except Exception as e:
            self.finished.emit(f"Error: {e}")


class BackupPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("font-size: 16px;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("📦 Backup & Restore")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)

        self.backup_btn = QPushButton("Create Backup")
        self.restore_btn = QPushButton("Restore Backup")
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setVisible(False)

        self.backup_btn.clicked.connect(self.create_backup)
        self.restore_btn.clicked.connect(self.restore_backup)

        layout.addWidget(self.backup_btn)
        layout.addWidget(self.restore_btn)
        layout.addWidget(self.progress)

    def create_backup(self):
        source_path = "database.db"  # Example: your local SQLite or Firestore export
        if not os.path.exists(source_path):
            QMessageBox.warning(self, "Error", "Database file not found!")
            return

        dest_path, _ = QFileDialog.getSaveFileName(
            self, "Save Backup As", "", "Database Backup (*.db)"
        )
        if dest_path:
            self.progress.setVisible(True)
            self.worker = BackupWorker(source_path, dest_path)
            self.worker.progress.connect(self.progress.setValue)
            self.worker.finished.connect(self.on_backup_finished)
            self.worker.start()

    def on_backup_finished(self, message):
        self.progress.setVisible(False)
        QMessageBox.information(self, "Backup", message)

    def restore_backup(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Backup File", "", "Database Backup (*.db)"
        )
        if file_path:
            try:
                shutil.copy(file_path, "database.db")
                QMessageBox.information(self, "Restore", "Database restored successfully ✅")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Restore failed: {e}")