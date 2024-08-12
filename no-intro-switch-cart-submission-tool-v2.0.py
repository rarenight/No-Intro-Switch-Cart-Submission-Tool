import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QComboBox, QPlainTextEdit, QGroupBox, QDialog, QTabWidget, QCheckBox, QDateEdit, QSizePolicy, QMessageBox, QTextEdit
)
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QRegExpValidator, QPalette
from PyQt5.QtCore import Qt, QDate, QRegExp, QSettings
import hashlib
import zlib
import rarfile
import glob
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import subprocess
import platform
import time

class XMLGeneratorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("No-Intro Switch Cart Submission Tool by rarenight v2.0")
        self.setGeometry(100, 100, 470, 400)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.scene_dir = ""
        self.gameid2 = ""
        self.default_xci_path = None
        self.initial_area_path = None

        self.tool_options = ["nxdt_rw_poc v2.0.0 (rewrite-dirty)", "DBI", "nxdumptool v1.1.15", "MigDumpTool (nxdumptool-rewrite)"]
        
        self.region_options = [
            "Nintendo published cart (World)", "-USA cart (USA)", "-EUR cart (Europe)", "-JPN cart (Japan)", "-ASI cart (Asia)", "-AUS cart (Australia)", "-CHN cart (China)", "-CHT cart (Taiwan, Hong Kong)", "-KOR cart (Korea)", "-MSE cart (Middle East)", "-RUS cart (Russia)", "-UKV cart (United Kingdom)"
        ]
        self.region_values = {
            "Nintendo published cart (World)": "World",
            "-ASI cart (Asia)": "Asia",
            "-AUS cart (Australia)": "Australia",
            "-CHN cart (China)": "China",
            "-CHT cart (Taiwan, Hong Kong)": "Taiwan, Hong Kong",
            "-EUR cart (Europe)": "Europe",
            "-JPN cart (Japan)": "Japan",
            "-KOR cart (Korea)": "Korea",
            "-MSE cart (Middle East)": "Middle East",
            "-RUS cart (Russia)": "Russia",
            "-UKV cart (United Kingdom)": "United Kingdom",
            "-USA cart (USA)": "USA"
        }
        
        self.settings = QSettings("MyCompany", "XMLGeneratorApp")
        self.default_dumper = self.settings.value("defaultDumper", "")
        self.default_tool = self.settings.value("defaultTool", "nxdt_rw_poc v2.0.0 (rewrite-dirty)")

        self.initUI()
    
    def initUI(self):
        self.tabs = QTabWidget()
        
        self.basic_info_tab = QWidget()
        self.basic_info_layout = QVBoxLayout()
        
        self.basic_info_form_layout = QFormLayout()
        self.import_button = QPushButton("Automatically Import Metadata")
        self.import_button.clicked.connect(self.open_import_nx_game_info_dialog)
        self.basic_info_form_layout.addRow(self.import_button)
        self.basic_info_labels = [
            ("Game Name", "All nouns, verbs, and adjectives are uppercase, move initial articles to the end of the name, intermediary link words are lowercase, colons are replaced with dashes, no \\ / : * ? \" < > | , e.g. 'Legend of Zelda, The - A Link to the Past'"), 
            ("Languages", "Comma-separated in ISO 639-1 format, e.g. English, Japanese, Korean, Simplified Chinese, Traditional Chinese is 'en,ja,ko,Zh-Hans,Zh-Hant'"), 
            ("GameID1", "All base application Title IDs (ending in 000) comma-separated, no patches, no add-ons, e.g. '0100182014022000, 010065A014024000'")]
        self.basic_info_inputs = self.create_form_group(self.basic_info_labels, self.basic_info_form_layout)
        
        self.region_combo_box = QComboBox()
        self.region_combo_box.addItems(self.region_options)
        self.basic_info_form_layout.addRow(QLabel("Region"), self.region_combo_box)

        self.custom_region_checkbox = QCheckBox("Custom Region")
        self.custom_region_checkbox.stateChanged.connect(self.toggle_custom_region)
        self.custom_region_input = QLineEdit()
        self.custom_region_input.setEnabled(False)
        self.basic_info_form_layout.addRow(self.custom_region_checkbox, self.custom_region_input)
    

        self.scene_release_checkbox = QCheckBox("Scene Release")
        self.scene_release_checkbox.stateChanged.connect(self.toggle_scene_release)
        self.basic_info_layout.addWidget(self.scene_release_checkbox)

        self.basic_info_layout.addLayout(self.basic_info_form_layout)
        self.basic_info_tab.setLayout(self.basic_info_layout)
        
        self.source_details_tab = QWidget()
        self.source_details_layout = QFormLayout()
        self.source_details_labels = [
            ("Dumper", "Individual who dumped the game"),
            ("Tool", "Tool used to dump the cart, ideally you should embed the commit code like this: 'nxdt_rw_poc v2.0.0 (rewrite-3c519cd-dirty)'"),
        ]
        self.source_details_inputs = self.create_form_group(self.source_details_labels, self.source_details_layout)

        self.set_preferred_button = QPushButton("Set Default Dumper and Tool")
        self.set_preferred_button.clicked.connect(self.set_preferred)
        self.source_details_layout.addRow(self.set_preferred_button)

        self.generate_card_id_button = QPushButton("Generate Card ID Values")
        self.generate_card_id_button.clicked.connect(self.open_generate_card_id_dialog)
        self.source_details_layout.addRow(self.generate_card_id_button)

        self.source_details_inputs['Comment1'] = QPlainTextEdit()
        self.source_details_inputs['Comment1'].textChanged.connect(self.update_display)
        self.source_details_layout.addRow(QLabel("Card IDs"), self.source_details_inputs['Comment1'])
        self.source_details_layout.addRow(QLabel("In this format:\nCard ID 1: <first four bytes>\nCard ID 2: <second four bytes>\nCard ID 3: <remaining four bytes>\nCRC32: <hash of Card ID BIN>"))

        self.custom_dump_date_checkbox = QCheckBox("Custom Dump Date (if different from today)")
        self.custom_dump_date_checkbox.stateChanged.connect(self.toggle_custom_dump_date)
        self.source_details_layout.addRow(self.custom_dump_date_checkbox)

        self.custom_dump_date_input = QDateEdit()
        self.custom_dump_date_input.setDisplayFormat("yyyy-MM-dd")
        self.custom_dump_date_input.setCalendarPopup(True)
        self.custom_dump_date_input.setDate(QDate.currentDate())
        self.custom_dump_date_input.setEnabled(False)
        self.source_details_layout.addRow(self.custom_dump_date_input)

        self.source_details_tab.setLayout(self.source_details_layout)
        
        self.serial_details_tab = QWidget()
        self.serial_details_layout = QFormLayout()
        self.serial_details_labels = [
            ("Media Serial 1", "Cart front serial, e.g. 'LA-H-AQBEB-USA'"), 
            ("Media Serial 2", "Cart back serial, e.g. 'AQBEB20A000'"), 
            ("PCB Serial", "Visible numbers and symbols on the PCB, if any, e.g. '▼ 10'"), 
            ("Box Serial", "Serials listed in the bottom right corner of the box, e.g. 'HAC P AQBEB, 81928'"), 
            ("Box Barcode", "Barcode listed in the bottom right corner of the box, spaces preserved, e.g. '8 59716 00628 4'")
        ]
        self.serial_details_inputs = self.create_form_group(self.serial_details_labels, self.serial_details_layout)
        self.serial_details_tab.setLayout(self.serial_details_layout)

        self.loose_cart_checkbox = QCheckBox("Loose Cart")
        self.loose_cart_checkbox.stateChanged.connect(self.toggle_loose_cart)
        self.serial_details_layout.addRow(self.loose_cart_checkbox)

        self.serial_details_inputs['Media Serial 1'].textChanged.connect(self.update_game_id2)
        self.serial_details_inputs['Media Serial 2'].textChanged.connect(self.update_mediastamp)
        
        self.file_info_tab = QWidget()
        self.file_info_layout = QVBoxLayout()

        button_layout = QHBoxLayout()

        self.calculate_hashes_button = QPushButton("Calculate Hashes")
        self.calculate_hashes_button.clicked.connect(self.prompt_for_initial_area)
        button_layout.addWidget(self.calculate_hashes_button)

        self.generate_full_xci_button = QPushButton("Generate FullXCI File")
        self.generate_full_xci_button.clicked.connect(self.open_generate_full_xci_dialog)
        button_layout.addWidget(self.generate_full_xci_button)

        self.truncate_full_xci_button = QPushButton("Truncate FullXCI File")
        self.truncate_full_xci_button.clicked.connect(self.open_truncate_full_xci_dialog)
        button_layout.addWidget(self.truncate_full_xci_button)

        self.file_info_layout.addLayout(button_layout)

        self.create_file_info_section(self.file_info_layout)

        self.file_info_tab.setLayout(self.file_info_layout)

        self.scene_cart_tab = QWidget()
        self.scene_cart_layout = QVBoxLayout()

        self.scene_cart_form_layout = QFormLayout()

        self.select_directory_button = QPushButton("Select Scene Directory")
        self.select_directory_button.clicked.connect(self.select_directory)
        self.scene_cart_form_layout.addRow(self.select_directory_button)

        self.scene_directory_label = QLabel("No directory selected")
        self.scene_directory_label.setWordWrap(True)
        self.scene_cart_form_layout.addRow(QLabel("Selected Directory:"), self.scene_directory_label)

        self.nfo_viewer_button = QPushButton("Open NFO")
        self.nfo_viewer_button.setEnabled(False)
        self.nfo_viewer_button.clicked.connect(self.open_nfo_viewer)
        self.scene_cart_form_layout.addRow(self.nfo_viewer_button)

        self.verify_rars_button = QPushButton("Verify Scene RARs")
        self.verify_rars_button.setEnabled(False)
        self.verify_rars_button.clicked.connect(self.verify_scene_rars)
        self.scene_cart_form_layout.addRow(self.verify_rars_button)

        self.extract_rars_button = QPushButton("Extract Scene RARs")
        self.extract_rars_button.setEnabled(False)
        self.extract_rars_button.clicked.connect(self.extract_scene_rars)
        self.scene_cart_form_layout.addRow(self.extract_rars_button)

        self.auto_delete_checkbox = QCheckBox("Delete RARs after extraction")
        self.auto_delete_checkbox.setChecked(True)
        self.auto_delete_checkbox.setEnabled(False)
        self.scene_cart_form_layout.addRow(self.auto_delete_checkbox)

        self.scene_group_dropdown = QComboBox()
        self.scene_group_dropdown.addItems([
            "2K", "AUGETY", "BANDAI", "BigBlueBox", "BLASTCiTY", "Console", "DarKmooN", "DELiGHT",
            "GANT", "High-Road", "HR", "iNCiDENT", "JRP", "Lakitu", "Lightforce", "Lube", "LUMA", "NiiNTENDO",
            "NrZ", "NXFLY", "PEACH", "Pussycat", "Suxxors", "Venom", "WiiERD"
        ])
        self.scene_group_dropdown.setEnabled(False)
        self.scene_cart_form_layout.addRow(QLabel("Scene Group"), self.scene_group_dropdown)

        self.custom_scene_group_input = QLineEdit()
        self.custom_scene_group_input.setPlaceholderText("Custom Scene Group")
        self.custom_scene_group_input.setEnabled(False)
        self.custom_scene_group_input.textChanged.connect(self.toggle_custom_scene_group)
        self.scene_cart_form_layout.addRow(QLabel("Custom Scene Group"), self.custom_scene_group_input)

        self.scene_cart_layout.addLayout(self.scene_cart_form_layout)
        self.scene_cart_tab.setLayout(self.scene_cart_layout)

        self.tabs.addTab(self.basic_info_tab, "Game Info")
        self.tabs.addTab(self.source_details_tab, "Dump Info")
        self.tabs.addTab(self.serial_details_tab, "Media Info")
        self.tabs.addTab(self.scene_cart_tab, "Scene Cart")
        self.tabs.addTab(self.file_info_tab, "File Info")

        self.layout.addWidget(self.tabs)
        
        button_layout = QHBoxLayout()
        
        self.generate_button = QPushButton("Generate Submission (X fields left)")
        self.generate_button.setEnabled(False)
        self.generate_button.clicked.connect(self.generate_xml)
        button_layout.addWidget(self.generate_button)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_all_fields)
        button_layout.addWidget(self.reset_button)

        self.layout.addLayout(button_layout)
        
        self.setAcceptDrops(True)
        self.update_generate_button_text()
        self.load_preferences()

        self.tabs.setTabEnabled(self.tabs.indexOf(self.scene_cart_tab), False)
    
    def create_form_group(self, labels, layout):
        inputs = {}
        for label, explanation in labels:
            if label == "Game Name":
                line_edit = QLineEdit()
                validator = QRegExpValidator(QRegExp("[^\\\\/:*?\"<>|]+"))
                line_edit.setValidator(validator)
                line_edit.setMaximumHeight(30)
                line_edit.setMaximumWidth(400)
                line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                line_edit.textChanged.connect(self.update_display)
                label_widget = QLabel(label)
                label_widget.setMaximumWidth(400)
                layout.addRow(label_widget, line_edit)
                explanation_label = QLabel(explanation)
                explanation_label.setWordWrap(True)
                explanation_label.setMaximumWidth(400)
                layout.addRow(explanation_label)
                inputs[label] = line_edit
            elif label == "PCB Serial":
                combo_box = QComboBox()
                combo_box.addItems(["", "▼", "▼ 10"])
                combo_box.setEditable(True)
                combo_box.setMaximumHeight(30)
                combo_box.setMaximumWidth(400)
                combo_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                combo_box.currentTextChanged.connect(self.update_display)
                label_widget = QLabel(label)
                label_widget.setMaximumWidth(400)
                layout.addRow(label_widget, combo_box)
                explanation_label = QLabel(explanation)
                explanation_label.setWordWrap(True)
                explanation_label.setMaximumWidth(400)
                layout.addRow(explanation_label)
                inputs[label] = combo_box
            elif label == "Tool":
                combo_box = QComboBox()
                combo_box.addItems(self.tool_options)
                combo_box.setEditable(True)
                combo_box.setCurrentText(self.default_tool)
                combo_box.setMaximumHeight(30)
                combo_box.setMaximumWidth(400)
                combo_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                combo_box.currentTextChanged.connect(self.update_display)
                label_widget = QLabel(label)
                label_widget.setMaximumWidth(400)
                layout.addRow(label_widget, combo_box)
                explanation_label = QLabel(explanation)
                explanation_label.setWordWrap(True)
                explanation_label.setMaximumWidth(400)
                layout.addRow(explanation_label)
                inputs[label] = combo_box
            else:
                line_edit = QLineEdit()
                line_edit.setMaximumHeight(30)
                line_edit.setMaximumWidth(400)
                line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                line_edit.textChanged.connect(self.update_display)
                label_widget = QLabel(label)
                label_widget.setMaximumWidth(400)
                layout.addRow(label_widget, line_edit)
                explanation_label = QLabel(explanation)
                explanation_label.setWordWrap(True)
                explanation_label.setMaximumWidth(400)
                layout.addRow(explanation_label)
                inputs[label] = line_edit
        return inputs
    
    def create_file_info_section(self, layout):
        self.file_inputs = {}
        
        self.include_initial_area_checkbox = QCheckBox("Include Initial Area")
        self.include_initial_area_checkbox.setChecked(True)
        layout.addWidget(self.include_initial_area_checkbox)

        group_titles = ["Default XCI", "Initial Area", "FullXCI"]
        file_labels = [
            ["File Size", "CRC32", "MD5", "SHA1", "SHA256", "Version", "Update"],
            ["File Size", "CRC32", "MD5", "SHA1", "SHA256"],
            ["File Size", "CRC32", "MD5", "SHA1", "SHA256"]
        ]
                    
        for i, group_title in enumerate(group_titles):
            group_box = QGroupBox(group_title)
            form_layout = QFormLayout()
            inputs = {}
            for label in file_labels[i]:
                full_label = f"{label} {i+1}"
                line_edit = QLineEdit()
                line_edit.setMaximumWidth(250)
                line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                line_edit.textChanged.connect(self.update_display)
                form_layout.addRow(QLabel(label), line_edit)
                inputs[full_label] = line_edit
            group_box.setLayout(form_layout)
            layout.addWidget(group_box)
            self.file_inputs.update(inputs)

        self.update_display()

    def toggle_custom_dump_date(self, state):
        self.custom_dump_date_input.setEnabled(state == Qt.Checked)
        self.update_display()
    
    def toggle_custom_region(self, state):
        if state == Qt.Checked:
            self.region_combo_box.setEnabled(False)
            self.custom_region_input.setEnabled(True)
        else:
            self.region_combo_box.setEnabled(True)
            self.custom_region_input.setEnabled(False)
        self.update_display()

    def toggle_scene_release(self, state):
        is_scene_release = state == Qt.Checked

        self.tabs.setTabEnabled(self.tabs.indexOf(self.scene_cart_tab), is_scene_release)
            
        self.source_details_inputs["Dumper"].setEnabled(not is_scene_release)
        self.source_details_inputs["Comment1"].setEnabled(not is_scene_release)
        self.source_details_inputs["Tool"].setEnabled(not is_scene_release)
        self.custom_dump_date_checkbox.setEnabled(not is_scene_release)
        self.set_preferred_button.setEnabled(not is_scene_release)
        self.generate_card_id_button.setEnabled(not is_scene_release)

        self.include_initial_area_checkbox.setEnabled(not is_scene_release)
        
        initial_area_keys = ["File Size 2", "CRC32 2", "MD5 2", "SHA1 2", "SHA256 2"]
        for key in initial_area_keys:
            if key in self.file_inputs:
                self.file_inputs[key].setEnabled(not is_scene_release)

        full_xci_keys = ["File Size 3", "CRC32 3", "MD5 3", "SHA1 3", "SHA256 3"]
        for key in full_xci_keys:
            if key in self.file_inputs:
                self.file_inputs[key].setEnabled(not is_scene_release)

        self.update_display()

    def toggle_loose_cart(self, state):
        is_enabled = state != Qt.Checked
        box_serial_input = self.serial_details_inputs['Box Serial']
        box_barcode_input = self.serial_details_inputs['Box Barcode']
        
        box_serial_input.setEnabled(is_enabled)
        box_barcode_input.setEnabled(is_enabled)
        
        palette = box_serial_input.palette()
        palette.setColor(QPalette.Base, Qt.lightGray if not is_enabled else Qt.white)
        box_serial_input.setPalette(palette)
        box_barcode_input.setPalette(palette)
        
        if not is_enabled:
            box_serial_input.clear()
            box_barcode_input.clear()
        
        self.update_display()

    def toggle_custom_scene_group(self, text):
        if text.strip():
            self.scene_group_dropdown.setEnabled(False)
        else:
            self.scene_group_dropdown.setEnabled(True)

    def update_display(self):
        if not hasattr(self, 'generate_button'):
            return
        
        include_initial_area = self.include_initial_area_checkbox.isChecked()
        is_scene_release = self.scene_release_checkbox.isChecked()

        if is_scene_release:
            all_filled = all([
                self.basic_info_inputs["Game Name"].text().strip(),
                self.basic_info_inputs["Languages"].text().strip(),
                self.basic_info_inputs["GameID1"].text().strip(),
                self.region_combo_box.currentText().strip(),
                self.file_inputs["File Size 1"].text().strip(),
                self.file_inputs["CRC32 1"].text().strip(),
                self.file_inputs["MD5 1"].text().strip(),
                self.file_inputs["SHA1 1"].text().strip(),
                self.file_inputs["SHA256 1"].text().strip(),
                self.file_inputs["Version 1"].text().strip(),
                self.file_inputs["Update 1"].text().strip(),
                self.scene_group_dropdown.currentText().strip() or self.custom_scene_group_input.text().strip()
            ])

            if all_filled and hasattr(self, 'scene_dirname') and self.scene_dirname:
                self.generate_button.setEnabled(True)
            else:
                self.generate_button.setEnabled(False)

        else:
            all_filled = all(
                input.text().strip() for input in self.basic_info_inputs.values() if isinstance(input, QLineEdit)
            ) and all(
                input.text().strip() for input in self.source_details_inputs.values() if isinstance(input, QLineEdit)
            ) and all(
                input.text().strip() for label, input in self.serial_details_inputs.items() if isinstance(input, QLineEdit) and label != "PCB Serial" and 
                (label not in ["Box Serial", "Box Barcode"] or input.isEnabled())
            ) and all(
                input.currentText().strip() for label, input in self.serial_details_inputs.items() if isinstance(input, QComboBox) and label != "PCB Serial"
            ) and all(
                self.file_inputs[key].text().strip() for key in self.file_inputs if not key.startswith("FullXCI") and 
                (include_initial_area or not key.startswith("File Size 2"))
            )

            self.generate_button.setEnabled(all_filled)
        
        self.update_generate_button_text()

        self.calculate_hashes_button.setEnabled(True)

    def update_generate_button_text(self):
        include_initial_area = self.include_initial_area_checkbox.isChecked()
        
        if self.scene_release_checkbox.isChecked():
            empty_fields = sum(
                1 for input in [
                    self.basic_info_inputs["Game Name"],
                    self.basic_info_inputs["Languages"],
                    self.basic_info_inputs["GameID1"],
                    self.file_inputs["File Size 1"],
                    self.file_inputs["CRC32 1"],
                    self.file_inputs["MD5 1"],
                    self.file_inputs["SHA1 1"],
                    self.file_inputs["SHA256 1"],
                    self.file_inputs["Version 1"],
                    self.file_inputs["Update 1"]
                ] if not input.text()
            ) + (0 if self.region_combo_box.currentText() else 1) + (
                0 if self.scene_group_dropdown.currentText() or self.custom_scene_group_input.text() else 1
            )
        else:
            empty_fields = sum(
                1 for input in self.basic_info_inputs.values() if isinstance(input, QLineEdit) and not input.text()
            ) + sum(
                1 for input in self.source_details_inputs.values() if isinstance(input, QLineEdit) and not input.text()
            ) + sum(
                1 for label, input in self.serial_details_inputs.items() if isinstance(input, QLineEdit) and label != "PCB Serial" and 
                (label not in ["Box Serial", "Box Barcode"] or input.isEnabled()) and not input.text()
            ) + sum(
                1 for label, input in self.serial_details_inputs.items() if isinstance(input, QComboBox) and label != "PCB Serial" and not input.currentText()
            ) + sum(
                1 for key in self.file_inputs if not key.startswith("FullXCI") and 
                (include_initial_area or not key.startswith("File Size 2")) and not self.file_inputs[key].text()
            )

        self.generate_button.setText(f"Generate Submission ({empty_fields} fields left)")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            self.process_file(file_path)
    
    def process_file(self, file_path):
        self.update_hashes(file_path)

    def update_hashes(self, file_path):
        print(f"Starting hash calculation for: {file_path}")
        total_size = os.path.getsize(file_path)
        processed_size = 0

        size = str(total_size)
        print("Calculated file size.")
        
        crc32 = 0
        hasher_md5 = hashlib.md5()
        hasher_sha1 = hashlib.sha1()
        hasher_sha256 = hashlib.sha256()

        with open(file_path, 'rb') as f:
            while chunk := f.read(4096):
                processed_size += len(chunk)
                crc32 = zlib.crc32(chunk, crc32)
                hasher_md5.update(chunk)
                hasher_sha1.update(chunk)
                hasher_sha256.update(chunk)

                progress = (processed_size / total_size) * 100
                sys.stdout.write(f"\rCalculating hashes... {progress:.0f}% completed")
                sys.stdout.flush()

        print("\nCompleted hash calculation for:", file_path)

        crc32 = format(crc32 & 0xFFFFFFFF, '08x')
        md5 = hasher_md5.hexdigest()
        sha1 = hasher_sha1.hexdigest()
        sha256 = hasher_sha256.hexdigest()

        if file_path.endswith('.xci'):
            self.default_xci_path = file_path
            self.file_inputs['File Size 1'].setText(size)
            self.file_inputs['CRC32 1'].setText(crc32)
            self.file_inputs['MD5 1'].setText(md5)
            self.file_inputs['SHA1 1'].setText(sha1)
            self.file_inputs['SHA256 1'].setText(sha256)
        elif file_path.endswith('.bin') and os.path.getsize(file_path) == 512:
            self.initial_area_path = file_path
            self.file_inputs['File Size 2'].setText(size)
            self.file_inputs['CRC32 2'].setText(crc32)
            self.file_inputs['MD5 2'].setText(md5)
            self.file_inputs['SHA1 2'].setText(sha1)
            self.file_inputs['SHA256 2'].setText(sha256)

        self.update_display()

    def calculate_size(self, file_path):
        return str(os.path.getsize(file_path))
    
    def calculate_hash(self, file_path, hash_type):
        hasher = hashlib.new(hash_type)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def calculate_crc32(self, file_path):
        crc32 = 0
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                crc32 = zlib.crc32(chunk, crc32)
        return format(crc32 & 0xFFFFFFFF, '08x')

    def open_import_nx_game_info_dialog(self):
        required_files = ["nxgameinfo_cli.exe", "LibHac.dll"]
        missing_files = [file for file in required_files if not os.path.exists(file)]

        if missing_files:
            QMessageBox.critical(self, "Missing Files", f"The following required files are missing: {', '.join(missing_files)}\nPlease ensure they are in the same directory as this script")
            return

        dialog = ImportNXGameInfoDialog(self)
        dialog.exec_()
    
    def import_nx_game_info(self, game_info):
        cleaned_title_name = game_info['title_name'].replace(":", " -")
        self.basic_info_inputs['Game Name'].setText(cleaned_title_name)
        self.basic_info_inputs['GameID1'].setText(game_info['title_id'])
        self.basic_info_inputs['Languages'].setText(game_info['languages'])
        self.file_inputs['Version 1'].setText("v" + game_info['display_version'])
        self.file_inputs['Update 1'].setText("v" + game_info['version'])
        self.update_display()

    def open_generate_full_xci_dialog(self):
        dialog = GenerateFullXCIDialog(self)
        dialog.exec_()

    def open_truncate_full_xci_dialog(self):
        dialog = TruncateFullXCIDialog(self)
        dialog.exec_()

    def prompt_for_initial_area(self):
        if self.scene_release_checkbox.isChecked():
            self.prompt_for_default_xci()
            return

        self.calculate_hashes_dialog = QDialog(self)
        self.calculate_hashes_dialog.setWindowTitle("Calculate Hashes")
        self.calculate_hashes_dialog.setGeometry(100, 100, 400, 200)
        layout = QVBoxLayout()
        self.calculate_hashes_dialog.setLayout(layout)
        
        label = QLabel("Drag and Drop Initial Area Here")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        self.calculate_hashes_dialog.show()
        
        self.calculate_hashes_dialog.setAcceptDrops(True)
        self.calculate_hashes_dialog.dragEnterEvent = self.dragEnterEvent
        self.calculate_hashes_dialog.dropEvent = self.drop_initial_area

    def drop_initial_area(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith('.bin') and os.path.getsize(file_path) == 512:
                self.initial_area_path = file_path
                self.process_file(file_path)
                self.calculate_hashes_dialog.close()
                self.prompt_for_default_xci()
                break

    def prompt_for_default_xci(self):
        self.calculate_hashes_dialog = QDialog(self)
        self.calculate_hashes_dialog.setWindowTitle("Calculate Hashes")
        self.calculate_hashes_dialog.setGeometry(100, 100, 400, 200)
        layout = QVBoxLayout()
        self.calculate_hashes_dialog.setLayout(layout)
        
        label = QLabel("Drag and Drop Default XCI here to calculate the hashes\n\nThe program will appear to freeze, it's just calculating all the hashes which can take a while\n\nCheck the terminal for the current status\n\nPlease be patient")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        self.calculate_hashes_dialog.show()
        
        self.calculate_hashes_dialog.setAcceptDrops(True)
        self.calculate_hashes_dialog.dragEnterEvent = self.dragEnterEvent
        self.calculate_hashes_dialog.dropEvent = self.drop_default_xci

    def drop_default_xci(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith('.xci'):
                if self.is_full_xci(file_path):
                    QMessageBox.critical(self, "Invalid XCI", "This is a FullXCI, please drag and drop a Default XCI")
                    return
                else:
                    self.default_xci_path = file_path
                    self.process_file(file_path)
                    self.calculate_hashes_dialog.close()
                    self.calculate_full_xci_hashes()
                    break

    def is_full_xci(self, file_path):
        with open(file_path, 'rb') as file:
            file.seek(0x1A0)
            data_segment = file.read(96)

        is_full_xci = all(b == 0 for b in data_segment)

        return is_full_xci
    
    def calculate_full_xci_hashes(self):
        if self.scene_release_checkbox.isChecked():
            if self.default_xci_path:
                with open(self.default_xci_path, 'rb') as default_xci_file:
                    default_xci_data = default_xci_file.read()

                size = str(len(default_xci_data))
                crc32 = format(zlib.crc32(default_xci_data) & 0xFFFFFFFF, '08x')
                md5 = hashlib.md5(default_xci_data).hexdigest()
                sha1 = hashlib.sha1(default_xci_data).hexdigest()
                sha256 = hashlib.sha256(default_xci_data).hexdigest()

                self.file_inputs["File Size 1"].setText(size)
                self.file_inputs["CRC32 1"].setText(crc32)
                self.file_inputs["MD5 1"].setText(md5)
                self.file_inputs["SHA1 1"].setText(sha1)
                self.file_inputs["SHA256 1"].setText(sha256)

            return

        if self.initial_area_path and self.default_xci_path:
            with open(self.initial_area_path, 'rb') as initial_area_file:
                initial_area_data = initial_area_file.read()

            zeroes_data = b'\x00' * 3584

            with open(self.default_xci_path, 'rb') as default_xci_file:
                default_xci_data = default_xci_file.read()

            full_xci_data = initial_area_data + zeroes_data + default_xci_data

            size = str(len(full_xci_data))
            crc32 = format(zlib.crc32(full_xci_data) & 0xFFFFFFFF, '08x')
            md5 = hashlib.md5(full_xci_data).hexdigest()
            sha1 = hashlib.sha1(full_xci_data).hexdigest()
            sha256 = hashlib.sha256(full_xci_data).hexdigest()

            self.file_inputs["File Size 3"].setText(size)
            self.file_inputs["CRC32 3"].setText(crc32)
            self.file_inputs["MD5 3"].setText(md5)
            self.file_inputs["SHA1 3"].setText(sha1)
            self.file_inputs["SHA256 3"].setText(sha256)

        self.update_display()

    def update_mediastamp(self):
        media_serial2 = self.serial_details_inputs['Media Serial 2'].text()
        mediastamp = media_serial2[-3:] if len(media_serial2) >= 3 else ""
        self.serial_details_inputs['Mediastamp'] = mediastamp
        self.update_display()

    def update_game_id2(self):
        media_serial1 = self.serial_details_inputs['Media Serial 1'].text()
        if media_serial1.endswith('1'):
            self.gameid2 = media_serial1[:-5] if len(media_serial1) > 5 else media_serial1
        else:
            self.gameid2 = media_serial1[:-4] if len(media_serial1) > 4 else media_serial1
        self.update_display()

    def generate_xml(self):
        datafile = ET.Element('datafile')
        game = ET.SubElement(datafile, 'game', name=self.basic_info_inputs['Game Name'].text() or "")

        region = self.custom_region_input.text() if self.custom_region_checkbox.isChecked() else self.region_values.get(self.region_combo_box.currentText(), "")

        archive_attrs = {
            "clone": "P",
            "name": self.basic_info_inputs['Game Name'].text() or "",
            "region": region or "",
            "languages": self.basic_info_inputs['Languages'].text() or "",
            "langchecked": "unk",
            "gameid1": self.basic_info_inputs['GameID1'].text() or "",
            "gameid2": self.gameid2 or "",
            "categories": "Games"
        }

        media_serial2 = self.serial_details_inputs['Media Serial 2'].text().strip()

        if media_serial2 and media_serial2[-1].isdigit() and media_serial2[-1] != "0":
            archive_attrs["version1"] = f"Rev {media_serial2[-1]}"

        archive = ET.SubElement(game, 'archive', **archive_attrs)

        if self.scene_release_checkbox.isChecked():
            release = ET.SubElement(game, 'release')

            nfoname_base = os.path.splitext(self.scene_nfoname or "")[0]
            archivename_base = os.path.splitext(self.scene_archivename or nfoname_base)[0]

            date = self.scene_date or time.strftime('%Y-%m-%d', time.gmtime(os.path.getmtime(os.path.join(self.scene_dirname, self.scene_nfoname))))

            dirname_base = os.path.basename(self.scene_dirname or "")

            details = ET.SubElement(release, 'details')
            details.set("dirname", dirname_base or "")
            details.set("nfoname", nfoname_base or "")
            details.set("archivename", archivename_base or "")
            details.set("region", region or "")
            details.set("nfosize", self.scene_nfosize or "")
            details.set("nfocrc", self.scene_nfocrc or "")
            details.set("date", date or "")
            details.set("group", self.custom_scene_group_input.text() if self.custom_scene_group_input.text() else self.scene_group_dropdown.currentText() or "")

            serials_attrs = {
                "media_serial1": self.serial_details_inputs['Media Serial 1'].text() or "",
                "media_serial2": media_serial2 or "",
                "mediastamp": self.serial_details_inputs.get('Mediastamp', '') or "",
                "pcb_serial": self.serial_details_inputs['PCB Serial'].currentText() or ""
            }

            if self.serial_details_inputs['Box Serial'].isEnabled():
                serials_attrs["box_serial"] = self.serial_details_inputs['Box Serial'].text() or ""

            if self.serial_details_inputs['Box Barcode'].isEnabled():
                serials_attrs["box_barcode"] = self.serial_details_inputs['Box Barcode'].text() or ""

            serials = ET.SubElement(release, 'serials', **serials_attrs)
        else:
            source = ET.SubElement(game, 'source')

            dump_date = self.custom_dump_date_input.date().toString("yyyy-MM-dd") if self.custom_dump_date_checkbox.isChecked() else QDate.currentDate().toString("yyyy-MM-dd")

            comment1_lines = self.source_details_inputs['Comment1'].toPlainText().strip().split('\n')
            comment1 = "&#10;".join(comment1_lines[:4])

            details = ET.SubElement(source, 'details',
                section="Trusted Dump",
                d_date=dump_date or "",
                r_date="",
                r_date_info="0",
                region=region or "",
                dumper=self.source_details_inputs['Dumper'].text() or "",
                project="No-Intro",
                tool=self.source_details_inputs['Tool'].currentText() or "",
                comment1=comment1 or "",
                originalformat="Default",
            )

            serials_attrs = {
                "media_serial1": self.serial_details_inputs['Media Serial 1'].text() or "",
                "media_serial2": media_serial2 or "",
                "mediastamp": self.serial_details_inputs.get('Mediastamp', '') or "",
                "pcb_serial": self.serial_details_inputs['PCB Serial'].currentText() or ""
            }
            
            if self.serial_details_inputs['Box Serial'].isEnabled():
                serials_attrs["box_serial"] = self.serial_details_inputs['Box Serial'].text() or ""
            
            if self.serial_details_inputs['Box Barcode'].isEnabled():
                serials_attrs["box_barcode"] = self.serial_details_inputs['Box Barcode'].text() or ""

            serials = ET.SubElement(source, 'serials', **serials_attrs)

            if self.include_initial_area_checkbox.isChecked():
                file2 = ET.SubElement(source, 'file',
                    forcename="",
                    size=self.file_inputs['File Size 2'].text() or "",
                    crc32=self.file_inputs['CRC32 2'].text().lower() or "",
                    md5=self.file_inputs['MD5 2'].text() or "",
                    sha1=self.file_inputs['SHA1 2'].text() or "",
                    sha256=self.file_inputs['SHA256 2'].text() or "",
                    extension="bin",
                    format="Initial Area"
                )

            if self.file_inputs['File Size 3'].text():
                file3 = ET.SubElement(source, 'file',
                    forcename="",
                    size=self.file_inputs['File Size 3'].text() or "",
                    crc32=self.file_inputs['CRC32 3'].text().lower() or "",
                    md5=self.file_inputs['MD5 3'].text() or "",
                    sha1=self.file_inputs['SHA1 3'].text() or "",
                    sha256=self.file_inputs['SHA256 3'].text() or "",
                    extension="xci",
                    format="FullXCI"
                )

        file1 = ET.SubElement(release if self.scene_release_checkbox.isChecked() else source, 'file',
            forcename="",
            size=self.file_inputs['File Size 1'].text() or "",
            crc32=self.file_inputs['CRC32 1'].text().lower() or "",
            md5=self.file_inputs['MD5 1'].text() or "",
            sha1=self.file_inputs['SHA1 1'].text() or "",
            sha256=self.file_inputs['SHA256 1'].text() or "",
            extension="xci",
            version=self.file_inputs['Version 1'].text() or "",
            update_type=self.file_inputs['Update 1'].text() or "",
            format="Default"
        )

        xml_str = minidom.parseString(ET.tostring(datafile)).toprettyxml(indent="    ")

        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if output_dir:
            game_name = self.basic_info_inputs['Game Name'].text() or ""
            dumper = self.source_details_inputs['Dumper'].text() or ""
            dump_date = self.custom_dump_date_input.date().toString("yyyy-MM-dd") if self.custom_dump_date_checkbox.isChecked() else QDate.currentDate().toString("yyyy-MM-dd")
            file_name = f"{game_name} - {dumper} - {dump_date} Submission.xml"
            file_path = os.path.join(output_dir, file_name)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.transform_xml(xml_str))

            self.open_output_directory(output_dir)


    def transform_xml(self, xml_str):
        return xml_str.replace("&amp;#10;", "&#10;")

    def open_generate_card_id_dialog(self):
        dialog = GenerateCardIDDialog(self)
        dialog.exec_()

    def reset_all_fields(self):
        for input in self.basic_info_inputs.values():
            if isinstance(input, QLineEdit):
                input.clear()
            elif isinstance(input, QComboBox):
                input.setCurrentIndex(0)

        for input in self.source_details_inputs.values():
            if isinstance(input, QLineEdit):
                if input.objectName() != "Dumper":
                    input.clear()
            elif isinstance(input, QPlainTextEdit):
                input.clear()

        self.custom_dump_date_checkbox.setChecked(False)
        self.custom_dump_date_input.setDate(QDate.currentDate())

        for input in self.serial_details_inputs.values():
            if isinstance(input, QLineEdit):
                input.clear()
            elif isinstance(input, QComboBox):
                input.setCurrentIndex(0)

        for input in self.file_inputs.values():
            input.clear()

        self.default_dumper = self.settings.value("defaultDumper", "")
        self.default_tool = self.settings.value("defaultTool", "nxdt_rw_poc v2.0.0 (rewrite-dirty)")

        self.source_details_inputs["Dumper"].setText(self.default_dumper)
        self.source_details_inputs["Tool"].setCurrentText(self.default_tool)

        self.update_display()


    def set_preferred(self):
        dumper = self.source_details_inputs["Dumper"].text()
        tool = self.source_details_inputs["Tool"].currentText()
        self.settings.setValue("defaultDumper", dumper)
        self.settings.setValue("defaultTool", tool)

    def load_preferences(self):
        self.source_details_inputs["Dumper"].setText(self.default_dumper)
        self.source_details_inputs["Tool"].setCurrentText(self.default_tool)

    def open_output_directory(self, path):
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Scene Directory")
        if directory:
            self.scene_dir = directory
            self.scene_directory_label.setWordWrap(True)
            self.scene_directory_label.setText(directory)

            self.extract_scene_info(directory)
        
            self.nfo_viewer_button.setEnabled(True)
            self.verify_rars_button.setEnabled(True)
            self.extract_rars_button.setEnabled(True)
            self.auto_delete_checkbox.setEnabled(True)
            self.scene_group_dropdown.setEnabled(True)
            self.custom_scene_group_input.setEnabled(True)

        else:
            if self.scene_release_checkbox.isChecked():
                self.generate_button.setEnabled(False)
    
    def extract_scene_info(self, directory):
        self.scene_dirname = directory
        self.scene_archivename = None
        self.scene_nfoname = None
        self.scene_nfosize = None
        self.scene_nfocrc = None
        self.scene_date = None

        for file in os.listdir(directory):
            if file.endswith(".rar"):
                self.scene_archivename = file
                self.scene_date = time.strftime('%Y-%m-%d', time.gmtime(os.path.getmtime(os.path.join(directory, file))))
                self.scene_sfvname = file.replace(".rar", ".sfv")
            elif file.endswith(".nfo"):
                self.scene_nfoname = file
                self.scene_nfosize = str(os.path.getsize(os.path.join(directory, file)))
                self.scene_nfocrc = self.calculate_crc32(os.path.join(directory, file))
        self.update_display()

    def open_nfo_viewer(self):
        if not self.scene_nfoname:
            QMessageBox.warning(self, "Missing NFO File", "No NFO file detected in the directory")
            return
        nfo_path = os.path.join(self.scene_dir, self.scene_nfoname)
        dialog = QDialog(self)
        dialog.setWindowTitle("NFO Viewer")
        dialog.resize(800, 800)
        layout = QVBoxLayout(dialog)
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        with open(nfo_path, 'r') as f:
            text_edit.setPlainText(f.read())
        layout.addWidget(text_edit)
        dialog.setLayout(layout)
        dialog.exec_()

    def verify_scene_rars(self):
        if not self.scene_archivename:
            QMessageBox.warning(self, "Missing RAR File", "No RAR file detected in the directory")
            return
        sfv_path = os.path.join(self.scene_dirname, self.scene_sfvname)
        if not os.path.exists(sfv_path):
            QMessageBox.warning(self, "Missing SFV File", "No SFV file detected in the directory")
            return
        
        log = []
        mismatches = []
        all_matched = True
        
        try:
            with open(sfv_path, 'r') as sfv_file:
                sfv_lines = sfv_file.readlines()

                for line in sfv_lines:
                    if line.strip() and not line.startswith(';'):
                        file_name, expected_crc32 = line.rsplit(' ', 1)
                        file_path = os.path.join(self.scene_dirname, file_name)
                        if not os.path.exists(file_path):
                            log.append(f"File {file_name} not found.")
                            all_matched = False
                            continue

                        actual_crc32 = self.calculate_crc32(file_path).strip().upper()
                        expected_crc32 = expected_crc32.strip().upper()

                        log.append(f"Checking {file_name}: Expected [{expected_crc32}] vs Actual [{actual_crc32}]")

                        if actual_crc32 != expected_crc32:
                            log.append(f"CRC mismatch for {file_name}")
                            mismatches.append(file_name)
                            all_matched = False
                        else:
                            log.append(f"{file_name}: CRC matches")
            
            if all_matched:
                log.append("\nAll CRCs matched successfully")
            else:
                log.append("\nMismatched CRCs were found:")
                for mismatch in mismatches:
                    log.append(f"- {mismatch}")

            log_text = "\n".join(log)

            dialog = QDialog(self)
            dialog.setWindowTitle("Verification Result")
            dialog.resize(400, 600)
            layout = QVBoxLayout(dialog)
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setPlainText(log_text)
            layout.addWidget(text_edit)
            dialog.setLayout(layout)
            dialog.exec_()
      
        except Exception as e:
            QMessageBox.critical(self, "Verification Failed", f"Verification failed with error: {str(e)}")

    def extract_scene_rars(self):
        if not self.scene_archivename:
            QMessageBox.warning(self, "No RAR File", "No RAR file available to extract")
            return

        try:
            rar_path = os.path.join(self.scene_dirname, self.scene_archivename)
            with rarfile.RarFile(rar_path) as rar:
                rar.extractall(self.scene_dirname)
                QMessageBox.information(self, "Extraction Result", f"Files extracted to {self.scene_dirname}")

            if self.auto_delete_checkbox.isChecked():
                self.delete_rar_and_split_files(rar_path)
                
        except rarfile.Error as e:
            QMessageBox.critical(self, "Extraction Failed", f"Extraction failed with error: {str(e)}")

    def delete_rar_and_split_files(self, rar_path):
        try:
            os.remove(rar_path)

            base_name = os.path.splitext(rar_path)[0]
            split_files = glob.glob(f"{base_name}.r[0-9][0-9]")

            for split_file in split_files:
                os.remove(split_file)

            QMessageBox.information(self, "Files Deleted", "The RAR files have been deleted")
        
        except OSError as e:
            QMessageBox.critical(self, "Deletion Failed", f"Failed to delete files: {str(e)}")


class ImportNXGameInfoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Metadata")
        self.setGeometry(100, 100, 400, 200)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.drag_drop_label = QLabel("Drag and drop Default XCI here to automatically import metadata from the Control NACP inside the XCI\n\nNote: FullXCIs and multi-title carts aren't supported\n\n nxgameinfo_cli.exe (with associated libraries) must be in the same directory as the script\n\nUp-to-date prod.keys must also be in the same directory")
        self.drag_drop_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.drag_drop_label)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith('.xci'):
                self.process_file(file_path)

    def process_file(self, file_path):
        if self.is_full_xci(file_path):
            QMessageBox.critical(self, "FullXCI Detected", "FullXCIs cannot be auto-imported, please drag and drop a Default XCI")
            return

        command = self.get_command(file_path)
        cli_output = subprocess.check_output(command, universal_newlines=True)
        game_info = self.parse_nx_game_info_output(cli_output)
        self.parent().import_nx_game_info(game_info)
        self.accept()

    def is_full_xci(self, file_path):
        with open(file_path, 'rb') as file:
            file.seek(0x1A0)
            data_segment = file.read(96)

        is_full_xci = all(b == 0 for b in data_segment)

        return is_full_xci

    def get_command(self, file_path):
        system = platform.system()
        if system == "Linux" or system == "Darwin":
            command = ["mono", "nxgameinfo_cli.exe", file_path]
        else:
            command = ["nxgameinfo_cli.exe", file_path]
        return command

    def parse_nx_game_info_output(self, output):
        lines = output.splitlines()
        game_info = {}
        
        lang_map = {
            "en-US": "en", "en-GB": "en", "fr-CA": "fr", "es-419": "es",
            "zh-CN": "Zh-Hans", "zh-TW": "Zh-Hant"
        }
        
        if output.startswith("NX Game Info"):
            for line in lines:
                if "Base Title ID:" in line:
                    game_info['title_id'] = line.split(":")[1].strip()
                elif "Title Name:" in line:
                    game_info['title_name'] = line.split(":", 1)[1].strip()
                elif "Display Version:" in line:
                    game_info['display_version'] = line.split(":")[1].strip()
                elif "Version:" in line:
                    version = line.split(":")[1].strip()
                    if "(" in version:
                        version = version.split(" ")[0]
                    if 'version' not in game_info:
                        game_info['version'] = version if version else "0"
                elif "Languages:" in line:
                    languages = line.split(":")[1].strip().replace("\"", "").split(',')
                    transformed_langs = set(lang_map.get(lang.strip(), lang.strip()) for lang in languages)
                    game_info['languages'] = ','.join(sorted(transformed_langs))

        return game_info

class GenerateFullXCIDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate FullXCI File")
        self.setGeometry(100, 100, 400, 200)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.state = 0
        
        self.drag_drop_label = QLabel("Drag and Drop Initial Area Here")
        self.drag_drop_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.drag_drop_label)
        
        self.initial_area_path = None
        self.default_xci_path = None
        
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if self.state == 0:
                if file_path.endswith('.bin') and os.path.getsize(file_path) == 512:
                    self.initial_area_path = file_path
                    self.state = 1
                    self.drag_drop_label.setText("Drag and Drop Default XCI here to convert it to a FullXCI\n\nThe program will appear to freeze, it's just generating the FullXCI which can take a while\n\nCheck the terminal for the current status\n\nPlease be patient")
                else:
                    self.drag_drop_label.setText("Please drop an Initial Area .bin file that has a size of 512 bytes")
            elif self.state == 1:
                if file_path.endswith('.xci'):
                    if self.is_full_xci(file_path):
                        QMessageBox.critical(self, "Invalid XCI", "This is a FullXCI, please drag and drop a Default XCI")
                        return
                    else:
                        self.default_xci_path = file_path
                        new_full_xci_path = self.generate_full_xci()
                        QMessageBox.information(self, "Success", f"A FullXCI file has been created:\n\n{new_full_xci_path}")
                        self.accept()
                else:
                    self.drag_drop_label.setText("Please drop a .xci file")
    
    def is_full_xci(self, file_path):
        with open(file_path, 'rb') as file:
            file.seek(0x1A0)
            data_segment = file.read(96)

        is_full_xci = all(b == 0 for b in data_segment)

        return is_full_xci
    
    def generate_full_xci(self):
        default_xci_filename = os.path.basename(self.default_xci_path)
        full_xci_filename = os.path.splitext(default_xci_filename)[0] + " (Full XCI)" + os.path.splitext(default_xci_filename)[1]
        full_xci_path = os.path.join(os.path.dirname(self.default_xci_path), full_xci_filename)

        print("Generating FullXCI file...")
        total_size = os.path.getsize(self.initial_area_path) + 3584 + os.path.getsize(self.default_xci_path)
        processed_size = 0

        with open(full_xci_path, 'wb') as full_xci:
            with open(self.initial_area_path, 'rb') as initial_area:
                while chunk := initial_area.read(4096):
                    full_xci.write(chunk)
                    processed_size += len(chunk)
                    progress = (processed_size / total_size) * 100
                    sys.stdout.write(f"\rWriting Initial Area... {progress:.0f}% completed")
                    sys.stdout.flush()

            full_xci.write(b'\x00' * 3584)
            processed_size += 3584
            progress = (processed_size / total_size) * 100
            sys.stdout.write(f"\rWriting zeroes... {progress:.0f}% completed")
            sys.stdout.flush()

            with open(self.default_xci_path, 'rb') as default_xci:
                while chunk := default_xci.read(4096):
                    full_xci.write(chunk)
                    processed_size += len(chunk)
                    progress = (processed_size / total_size) * 100
                    sys.stdout.write(f"\rWriting Default XCI... {progress:.0f}% completed")
                    sys.stdout.flush()

        print(f"\nFullXCI file generated: {full_xci_path}")
        os.startfile(os.path.dirname(full_xci_path))
        return full_xci_path

class TruncateFullXCIDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Truncate FullXCI File")
        self.setGeometry(100, 100, 400, 200)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.drag_drop_label = QLabel("Drag and drop FullXCI here to convert it back to a Default XCI and an Initial Area\n\nThe program will appear to freeze, it's just truncating the FullXCI which can take a while\n\nCheck the terminal for the current status\n\nPlease be patient")
        self.drag_drop_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.drag_drop_label)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith('.xci'):
                if self.is_full_xci(file_path):
                    self.process_file(file_path)
                else:
                    QMessageBox.critical(self, "Invalid XCI", "This is a Default XCI, please drag and drop a FullXCI")
            else:
                self.drag_drop_label.setText("Please drop a .xci file")

    def is_full_xci(self, file_path):
        with open(file_path, 'rb') as file:
            file.seek(0x1A0)
            data_segment = file.read(96)

        is_full_xci = all(b == 0 for b in data_segment)

        return is_full_xci
    
    def process_file(self, file_path):
        print(f"Starting FullXCI truncation for: {file_path}")
        total_size = os.path.getsize(file_path)
        processed_size = 0

        with open(file_path, 'rb') as file:
            initial_area = file.read(512)
            processed_size += 512
            progress = (processed_size / total_size) * 100
            sys.stdout.write(f"\rRead Initial Area... {progress:.0f}% completed")
            sys.stdout.flush()

            file.seek(3584, os.SEEK_CUR)
            processed_size += 3584
            progress = (processed_size / total_size) * 100
            sys.stdout.write(f"\rSkipped zero padding... {progress:.0f}% completed")
            sys.stdout.flush()

            base_name = os.path.splitext(os.path.basename(file_path))[0]
            if base_name.endswith(" (Full XCI)"):
                base_name = base_name[:-11]

            initial_area_path = os.path.join(os.path.dirname(file_path), f"{base_name} (Initial Area).bin")
            with open(initial_area_path, 'wb') as initial_area_file:
                initial_area_file.write(initial_area)
                print(f"\nInitial Area written to: {initial_area_path}")

            default_xci_path = os.path.join(os.path.dirname(file_path), f"{base_name} (Default XCI).xci")

            with open(default_xci_path, 'wb') as default_xci_file:
                while True:
                    chunk = file.read(4096)
                    if not chunk:
                        break
                    default_xci_file.write(chunk)
                    processed_size += len(chunk)
                    progress = (processed_size / total_size) * 100
                    sys.stdout.write(f"\rWriting Default XCI... {progress:.0f}% completed")
                    sys.stdout.flush()

            print(f"\nDefault XCI written to: {default_xci_path}")
            QMessageBox.information(self, "Success", f"Default XCI file has been created:\n\n{default_xci_path}")
            self.accept()

class GenerateCardIDDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate Card ID Values")
        self.setGeometry(100, 100, 400, 200)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.drag_drop_label = QLabel("Drag and Drop Card ID .bin File Here:")
        self.drag_drop_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.drag_drop_label)
        
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            self.process_file(file_path)

    def process_file(self, file_path):
        with open(file_path, 'rb') as file:
            card_id_hex = file.read().hex().upper()
        card_id1 = card_id_hex[:8].upper()
        card_id2 = card_id_hex[8:16].upper()
        card_id3 = card_id_hex[16:24].upper()
        crc32 = self.calculate_crc32(file_path).upper()
        comment1 = f"Card ID 1: {card_id1}\nCard ID 2: {card_id2}\nCard ID 3: {card_id3}\nCRC32: {crc32}"
        self.parent().source_details_inputs['Comment1'].setPlainText(comment1)
        self.accept()

    def calculate_crc32(self, file_path):
        crc32 = 0
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                crc32 = zlib.crc32(chunk, crc32)
        return format(crc32 & 0xFFFFFFFF, '08x')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = XMLGeneratorApp()
    window.show()
    sys.exit(app.exec_())
