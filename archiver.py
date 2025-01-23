#!/usr/bin/python

import sys
import os
import zipfile
import py7zr
import rarfile
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton,
                             QFileDialog, QLabel, QMessageBox, QTableWidget,
                             QTableWidgetItem, QHeaderView,
                             QLineEdit, QComboBox, QDialog)
from PyQt5.QtCore import QTranslator, Qt


class ArchiveApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.current_theme = 'light'
        self.current_language = 'ru'
        self.translator = QTranslator()
        self.setStyleSheet(self.light_theme())
        self.setLanguage()

    def initUI(self):
        self.setWindowTitle('Archiver')
        self.setGeometry(100, 100, 500, 600)

        layout = QVBoxLayout()

        self.label = QLabel('Перетащите архив', self)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.pack_btn = QPushButton('Создать архив', self)
        self.pack_btn.clicked.connect(self.pack_files)
        layout.addWidget(self.pack_btn)

        self.unpack_btn = QPushButton('Распаковать архив', self)
        self.unpack_btn.clicked.connect(self.unpack_archive)
        layout.addWidget(self.unpack_btn)

        self.repair_btn = QPushButton('Восстановить архив', self)
        self.repair_btn.clicked.connect(self.repair_archive)
        layout.addWidget(self.repair_btn)

        self.view_btn = QPushButton('Просмотреть содержимое архива', self)
        self.view_btn.clicked.connect(self.view_archive_contents)
        layout.addWidget(self.view_btn)

        self.theme_btn = QPushButton('Тема', self)
        self.theme_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_btn)

        self.language_btn = QPushButton('Язык', self)
        self.language_btn.clicked.connect(self.toggle_language)
        layout.addWidget(self.language_btn)

        self.setLayout(layout)
        self.setAcceptDrops(True)

    def light_theme(self):
        return """
        QWidget {
            background-color: white;
            color: #4056A1;
            border: 2px dashed #4056A1;
            border-radius: 15px;
            font-size: 22px;
            text-transform: uppercase;
        }
        QPushButton {
            background-color: white;
            border: 1px solid #4056A1;
            border-radius: 15px;
            padding: 10px;
            color: #4056A1;
            font-size: 16px;
            text-transform: none;
        }
        QPushButton:active {
            background-color: white;
            border: 1px solid #4056A1;
            border-radius: 15px;
            padding: 10px;
            color: #4056A1;
            font-size: 16px;
            text-transform: none;
        }
        """

    def dark_theme(self):
        return """
        QWidget {
            background-color: #1A1A1D;
            color: #950740;
            border: 2px dashed #C3073F;
            border-radius: 15px;
            font-size: 22px;
            text-transform: uppercase;
        }
        QPushButton {
            background-color: #1A1A1D;
            border: 1px solid #C3073F;
            border-radius: 15px;
            padding: 10px;
            color: #950740;
            font-size: 16px;
            text-transform: none;
        }
        """

    def toggle_theme(self):
        if self.current_theme == 'light':
            self.current_theme = 'dark'
            self.setStyleSheet(self.dark_theme())
        else:
            self.current_theme = 'light'
            self.setStyleSheet(self.light_theme())

    def toggle_language(self):
        if self.current_language == 'en':
            self.current_language = 'ru'
            self.setLanguage()
        else:
            self.current_language = 'en'
            self.setLanguage()

    def setLanguage(self):
        if self.current_language == 'ru':
            self.label.setText('Перетащите архив')
            self.unpack_btn.setText('Распаковать архив')
            self.view_btn.setText('Просмотреть содержимое архива')
            self.pack_btn.setText('Создать архив')
            self.theme_btn.setText('Тема')
            self.language_btn.setText('Язык')
            self.setWindowTitle('Archiver')
        else:
            self.label.setText('Drag and drop')
            self.unpack_btn.setText('Unpack Archive')
            self.view_btn.setText('View Archive Contents')
            self.pack_btn.setText('Create Archive')
            self.theme_btn.setText('Theme')
            self.language_btn.setText('Language')
            self.setWindowTitle('Archiver')

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if os.path.isfile(file_path):
                    self.handle_drop(file_path)

    def handle_drop(self, file_path):
        if file_path.endswith('.zip') or file_path.endswith('.rar') or file_path.endswith('.7z'):
            try:
                if file_path.endswith('.zip'):
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(os.path.dirname(file_path))
                elif file_path.endswith('.rar'):
                    with rarfile.RarFile(file_path) as rar_ref:
                        rar_ref.extractall(os.path.dirname(file_path))
                elif file_path.endswith('.7z'):
                    with py7zr.SevenZipFile(file_path, mode='r') as archive:
                        archive.extractall(path=os.path.dirname(file_path))
                QMessageBox.information(self, "Успех", "Архив успешно распакован!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось распаковать архив: {e}")
        else:
            QMessageBox.warning(self, "Неверный файл", "Пожалуйста, перетащите действительный архив (.zip, .rar, .7z).")

    def view_archive_contents(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Открыть архив", "",
                                                   "Все архивы (*.zip *.rar *.7z);;"
                                                   "ZIP файлы (*.zip);;"
                                                   "RAR файлы (*.rar);;"
                                                   "7z файлы (*.7z)",
                                                   options=options)
        if file_name:
            contents = []
            if file_name.endswith('.zip'):
                with zipfile.ZipFile(file_name, 'r') as zip_ref:
                    contents = zip_ref.namelist()
            elif file_name.endswith('.rar'):
                with rarfile.RarFile(file_name) as rar_ref:
                    contents = rar_ref.namelist()
            elif file_name.endswith('.7z'):
                with py7zr.SevenZipFile(file_name, mode='r') as archive:
                    contents = archive.getnames()

            self.show_contents(contents)

    def show_contents(self, contents):
        dialog = QDialog()
        dialog.setWindowTitle("Содержимое архива")
        layout = QVBoxLayout()

        table = QTableWidget(len(contents), 1)
        table.setHorizontalHeaderLabels(["Имя файла"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for i, item in enumerate(contents):
            table.setItem(i, 0, QTableWidgetItem(item))

        layout.addWidget(table)
        dialog.setLayout(layout)
        dialog.setGeometry(200, 200, 300, 200)
        dialog.exec_()

    def unpack_archive(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Открыть архив", "",
                                                   "Все архивы (*.zip *.rar *.7z);;"
                                                   "ZIP файлы (*.zip);;"
                                                   "RAR файлы (*.rar);;"
                                                   "7z файлы (*.7z)",
                                                   options=options)
        if file_name:
            self.handle_drop(file_name)

    def pack_files(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Выберите файлы для сжатия", "", "Все файлы (*)",
                                                options=options)

        if files:
            save_file, _ = QFileDialog.getSaveFileName(self, "Сохранить архив как", "",
                                                       "ZIP файлы (*.zip);;"
                                                       "RAR файлы (*.rar);;"
                                                       "7z файлы (*.7z)",
                                                       options=options)

            if save_file:
                password = QLineEdit()
                password.setEchoMode(QLineEdit.Password)

                compression_level_combo = QComboBox()
                compression_level_combo.addItems(['Без сжатия', 'Самый быстрый', 'Нормальный', 'Максимальный'])

                dialog = QDialog()
                dialog.setWindowTitle("Настройки архива")
                dialog_layout = QVBoxLayout()

                dialog_layout.addWidget(QLabel("Пароль (необязательно):"))
                dialog_layout.addWidget(password)
                dialog_layout.addWidget(QLabel("Уровень сжатия:"))
                dialog_layout.addWidget(compression_level_combo)

                ok_button = QPushButton("Создать архив")
                ok_button.clicked.connect(lambda: self.create_archive(save_file, files, password.text(),
                                                                      compression_level_combo.currentIndex()))
                dialog_layout.addWidget(ok_button)

                dialog.setLayout(dialog_layout)
                dialog.setGeometry(200, 200, 300, 200)
                dialog.exec_()

    def create_archive(self, save_file, files, password, compression_level):
        try:
            original_size = sum(os.path.getsize(file) for file in files)
            start_time = os.times()[4]

            if save_file.endswith('.zip'):
                compression = zipfile.ZIP_DEFLATED if compression_level > 0 else zipfile.ZIP_STORED
                with zipfile.ZipFile(save_file, 'w', compression=compression) as zipf:
                    for file in files:
                        zipf.write(file, os.path.basename(file))
            elif save_file.endswith('.rar'):
                with rarfile.RarFile(save_file, 'w') as rarf:
                    for file in files:
                        rarf.write(file)
            elif save_file.endswith('.7z'):
                with py7zr.SevenZipFile(save_file, 'w', password=password) as archive:
                    for file in files:
                        archive.write(file, os.path.basename(file))

            compressed_size = os.path.getsize(save_file)
            end_time = os.times()[4]
            elapsed_time = end_time - start_time

            QMessageBox.information(self, "Успех",
                                    f"Файлы успешно сжаты!"
                                    f"\nРазмер до: {original_size} байт"
                                    f"\nРазмер после: {compressed_size} байт"
                                    f"\nВремя сжатия: {elapsed_time:.2f} секунд")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сжать файлы: {e}")

    def repair_archive(self):
        # Открыть диалог для выбора файла
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Выберите поврежденный архив", "", "Архивы (*.zip *.7z *.rar)",
                                                   options=options)

        if file_name:
            try:
                if file_name.endswith('.zip'):
                    self.repair_zip(file_name)
                elif file_name.endswith('.7z'):
                    self.repair_7z(file_name)
                elif file_name.endswith('.rar'):
                    self.repair_rar(file_name)
                else:
                    self.label.setText('Неподдерживаемый формат файла.')
            except Exception as e:
                self.label.setText(f'Произошла ошибка: {str(e)}')

    def repair_zip(self, file_name):
        repaired_file_name = file_name.replace('.zip', '_repaired.zip')
        with zipfile.ZipFile(file_name) as zf:
            zf.testzip()  # Проверка на ошибки
            with zipfile.ZipFile(repaired_file_name, 'w') as repaired_zf:
                for item in zf.infolist():
                    repaired_zf.writestr(item, zf.read(item.filename))

        self.label.setText(f'ZIP-архив восстановлен: {repaired_file_name}')

    def repair_7z(self, file_name):
        repaired_file_name = file_name.replace('.7z', '_repaired.7z')
        with py7zr.SevenZipFile(file_name, mode='r') as zf:
            zf.extractall(path='temp_extracted')  # Временная папка для извлечения
            with py7zr.SevenZipFile(repaired_file_name, mode='w') as repaired_zf:
                for root, dirs, files in os.walk('temp_extracted'):
                    for file in files:
                        file_path = os.path.join(root, file)
                        repaired_zf.write(file_path, arcname=os.path.relpath(file_path, 'temp_extracted'))

        self.label.setText(f'7z-архив восстановлен: {repaired_file_name}')

    def repair_rar(self, file_name):
        repaired_file_name = file_name.replace('.rar', '_repaired.rar')
        with rarfile.RarFile(file_name) as rf:
            rf.test()  # Проверка на ошибки
            with rarfile.RarFile(repaired_file_name, 'w') as repaired_rf:
                for item in rf.infolist():
                    repaired_rf.write(item.filename)

        self.label.setText(f'RAR-архив восстановлен: {repaired_file_name}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ArchiveApp()
    ex.show()
    sys.exit(app.exec_())