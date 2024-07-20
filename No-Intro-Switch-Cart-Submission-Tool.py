import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QComboBox, QPlainTextEdit, QGroupBox, QRadioButton, QDialog, QTabWidget, QButtonGroup, QCheckBox, QDateEdit, QSizePolicy
)
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtCore import Qt, QDate
import hashlib
import zlib
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os

class XMLGeneratorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("No-Intro Switch Cart Submission Tool by rarenight v1.0")
        self.setGeometry(100, 100, 475, 475)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.gameid2 = ""
        
        self.initUI()
    
    def initUI(self):
        self.tabs = QTabWidget()
        
        self.basic_info_tab = QWidget()
        self.basic_info_layout = QVBoxLayout()
        
        self.basic_info_form_layout = QFormLayout()
        self.import_button = QPushButton("Import NX Game Info")
        self.import_button.clicked.connect(self.open_import_nx_game_info_dialog)
        self.basic_info_form_layout.addRow(self.import_button)
        self.basic_info_labels = [
            ("Game Name", "Colons replaced with dashes, move titles to the end of the name, e.g. 'Legend of Zelda, The - Link's Awakening'"), 
            ("Region", "As listed on the cart, e.g., -USA = 'USA', -EUR = 'Europe', -JPN = 'Japan', -ASI = 'Asia', -CHT = 'Taiwan, Hong Kong'"), 
            ("Languages", "Comma-separated in No-Intro terminology, e.g., English, Japanese, Korean, Simplified Chinese, Traditional Chinese is 'en,ja,ko,Zh-Hans,Zh-Hant'"), 
            ("GameID1", "All base application Title IDs (ending in 000) comma-separated, no patches, no add-ons, e.g., '0100182014022000, 010065A014024000'")
        ]
        self.basic_info_inputs = self.create_form_group(self.basic_info_labels, self.basic_info_form_layout)
        
        self.basic_info_layout.addLayout(self.basic_info_form_layout)
        self.basic_info_tab.setLayout(self.basic_info_layout)
        
        self.source_details_tab = QWidget()
        self.source_details_layout = QFormLayout()
        self.source_details_labels = [
            ("Dumper", "Individual who dumped the game"),
            ("Tool", "Tool used to dump the cart, e.g., 'nxdt_rw_poc v2.0.0 (rewrite-3c519cd-dirty)'")
        ]
        self.source_details_inputs = self.create_form_group(self.source_details_labels, self.source_details_layout)

        self.generate_card_id_button = QPushButton("Generate Card ID Values")
        self.generate_card_id_button.clicked.connect(self.open_generate_card_id_dialog)
        self.source_details_layout.addRow(self.generate_card_id_button)

        self.source_details_inputs['Comment1'] = QPlainTextEdit()
        self.source_details_inputs['Comment1'].textChanged.connect(self.update_display)
        self.source_details_layout.addRow(QLabel("Card IDs"), self.source_details_inputs['Comment1'])

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
            ("Media Serial 1", "Cart front serial, e.g., 'LA-H-AQBEB-USA'"), 
            ("Media Serial 2", "Cart back serial, e.g., 'AQBEB20A000'"), 
            ("PCB Serial", "Visible numbers and symbols on the PCB, if any, e.g. '▼ 10'"), 
            ("Box Serial", "Serials listed in the bottom right corner of the box, e.g. 'HAC P AQBEB, 81928'"), 
            ("Box Barcode", "Barcode listed in the bottom right corner of the box, spaces preserved, e.g. '8 59716 00628 4'")
        ]
        self.serial_details_inputs = self.create_form_group(self.serial_details_labels, self.serial_details_layout)
        self.serial_details_tab.setLayout(self.serial_details_layout)

        self.serial_details_inputs['Media Serial 1'].textChanged.connect(self.update_game_id2)
        self.serial_details_inputs['Media Serial 2'].textChanged.connect(self.update_mediastamp)
        
        self.file_info_tab = QWidget()
        self.file_info_layout = QVBoxLayout()

        button_layout = QHBoxLayout()
        self.import_hashes_button = QPushButton("Import Hashes")
        self.import_hashes_button.clicked.connect(self.open_import_hashes_dialog)
        button_layout.addWidget(self.import_hashes_button)
        
        self.generate_full_xci_button = QPushButton("Generate Full XCI")
        self.generate_full_xci_button.clicked.connect(self.open_generate_full_xci_dialog)
        button_layout.addWidget(self.generate_full_xci_button)

        self.file_info_layout.addLayout(button_layout)

        self.create_file_info_section(self.file_info_layout)

        self.file_info_tab.setLayout(self.file_info_layout)
        
        self.tabs.addTab(self.basic_info_tab, "Game Info")
        self.tabs.addTab(self.source_details_tab, "Dump Info")
        self.tabs.addTab(self.serial_details_tab, "Media Info")
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
    
    def create_form_group(self, labels, layout):
        inputs = {}
        for label, explanation in labels:
            if label == "PCB Serial":
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
    
    def create_horizontal_form_group(self, labels, layout):
        inputs = {}
        for label, explanation in labels:
            h_layout = QHBoxLayout()
            label_widget = QLabel(label)
            label_widget.setMaximumWidth(200)
            input_widget = QLineEdit()
            input_widget.setMaximumWidth(200)
            input_widget.textChanged.connect(self.update_display)
            h_layout.addWidget(label_widget)
            h_layout.addWidget(input_widget)
            layout.addLayout(h_layout)
            explanation_label = QLabel(explanation)
            explanation_label.setWordWrap(True)
            explanation_label.setMaximumWidth(400)
            layout.addWidget(explanation_label)
            inputs[label] = input_widget
        return inputs

    def create_file_info_section(self, layout):
        self.file_inputs = {}
        
        group_titles = ["Default XCI", "Initial Area", "FullXCI"]
        file_labels = [
            ["File Size", "CRC32", "MD5", "SHA1", "SHA256", "Version", "Update Type"],
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
    
    def toggle_custom_dump_date(self, state):
        self.custom_dump_date_input.setEnabled(state == Qt.Checked)
        self.update_display()
    
    def update_display(self):
        all_filled = all(input.text() for input in self.basic_info_inputs.values() if isinstance(input, QLineEdit)) and \
                    all(input.text() for input in self.source_details_inputs.values() if isinstance(input, QLineEdit)) and \
                    all(input.text() for label, input in self.serial_details_inputs.items() if isinstance(input, QLineEdit) and label != "PCB Serial") and \
                    all(input.currentText() for label, input in self.serial_details_inputs.items() if isinstance(input, QComboBox) and label != "PCB Serial") and \
                    all(self.file_inputs[key].text() for key in self.file_inputs if not key.startswith("FullXCI"))
        self.generate_button.setEnabled(all_filled)
        self.update_generate_button_text()

    def update_generate_button_text(self):
        empty_fields = sum(1 for input in self.basic_info_inputs.values() if isinstance(input, QLineEdit) and not input.text()) + \
                    sum(1 for input in self.source_details_inputs.values() if isinstance(input, QLineEdit) and not input.text()) + \
                    sum(1 for label, input in self.serial_details_inputs.items() if isinstance(input, QLineEdit) and label != "PCB Serial" and not input.text()) + \
                    sum(1 for label, input in self.serial_details_inputs.items() if isinstance(input, QComboBox) and label != "PCB Serial" and not input.currentText()) + \
                    sum(1 for key in self.file_inputs if not key.startswith("FullXCI") and not self.file_inputs[key].text())
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
        size = self.calculate_size(file_path)
        crc32 = self.calculate_crc32(file_path)
        md5 = self.calculate_hash(file_path, 'md5')
        sha1 = self.calculate_hash(file_path, 'sha1')
        sha256 = self.calculate_hash(file_path, 'sha256')
        
        self.file_inputs['File Size 1'].setText(size)
        self.file_inputs['CRC32 1'].setText(crc32)
        self.file_inputs['MD5 1'].setText(md5)
        self.file_inputs['SHA1 1'].setText(sha1)
        self.file_inputs['SHA256 1'].setText(sha256)
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
        dialog = ImportNXGameInfoDialog(self)
        dialog.exec_()
    
    def import_nx_game_info(self, game_info):
        self.basic_info_inputs['Game Name'].setText(game_info['title_name'])
        self.basic_info_inputs['GameID1'].setText(game_info['title_id'])
        self.basic_info_inputs['Languages'].setText(game_info['languages'])
        self.file_inputs['Version 1'].setText("v" + game_info['display_version'])
        self.file_inputs['Update Type 1'].setText("v" + game_info['version'])
        self.update_display()

    def open_import_hashes_dialog(self):
        dialog = ImportHashesDialog(self)
        dialog.exec_()
    
    def import_hashes(self, hashes, category):
        if category == "Default XCI":
            self.file_inputs["File Size 1"].setText(hashes['size'])
            self.file_inputs["CRC32 1"].setText(hashes['crc32'].lower())
            self.file_inputs["MD5 1"].setText(hashes['md5'])
            self.file_inputs["SHA1 1"].setText(hashes['sha1'])
            self.file_inputs["SHA256 1"].setText(hashes['sha256'])
        elif category == "Initial Area":
            self.file_inputs["File Size 2"].setText(hashes['size'])
            self.file_inputs["CRC32 2"].setText(hashes['crc32'].lower())
            self.file_inputs["MD5 2"].setText(hashes['md5'])
            self.file_inputs["SHA1 2"].setText(hashes['sha1'])
            self.file_inputs["SHA256 2"].setText(hashes['sha256'])
        elif category == "FullXCI":
            self.file_inputs["File Size 3"].setText(hashes['size'])
            self.file_inputs["CRC32 3"].setText(hashes['crc32'].lower())
            self.file_inputs["MD5 3"].setText(hashes['md5'])
            self.file_inputs["SHA1 3"].setText(hashes['sha1'])
            self.file_inputs["SHA256 3"].setText(hashes['sha256'])
        self.update_display()
    
    def open_generate_full_xci_dialog(self):
        dialog = GenerateFullXCIDialog(self)
        dialog.exec_()

    def update_mediastamp(self):
        media_serial2 = self.serial_details_inputs['Media Serial 2'].text()
        mediastamp = media_serial2[-3:] if len(media_serial2) >= 3 else ""
        self.serial_details_inputs['Mediastamp'] = mediastamp
        self.update_display()

    def update_game_id2(self):
        media_serial1 = self.serial_details_inputs['Media Serial 1'].text()
        self.gameid2 = media_serial1[:-4] if len(media_serial1) > 4 else media_serial1
        self.update_display()

    def generate_xml(self):
        datafile = ET.Element('datafile')
        game = ET.SubElement(datafile, 'game', name=self.basic_info_inputs['Game Name'].text())

        archive = ET.SubElement(game, 'archive',
            clone="P",
            name=self.basic_info_inputs['Game Name'].text(),
            region=self.basic_info_inputs['Region'].text(),
            languages=self.basic_info_inputs['Languages'].text(),
            langchecked="unk",
            gameid1=self.basic_info_inputs['GameID1'].text(),
            gameid2=self.gameid2,
            categories="Games"
        )

        source = ET.SubElement(game, 'source')

        dump_date = self.custom_dump_date_input.date().toString("yyyy-MM-dd") if self.custom_dump_date_checkbox.isChecked() else QDate.currentDate().toString("yyyy-MM-dd")

        comment1_lines = self.source_details_inputs['Comment1'].toPlainText().strip().split('\n')
        comment1 = "&#10;".join(comment1_lines[:4])

        details = ET.SubElement(source, 'details',
            section="Trusted Dump",
            d_date=dump_date,
            r_date="",
            r_date_info="0",
            region=self.basic_info_inputs['Region'].text(),
            dumper=self.source_details_inputs['Dumper'].text(),
            project="No-Intro",
            tool=self.source_details_inputs['Tool'].text(),
            comment1=comment1,
            originalformat="Default",
        )

        serials = ET.SubElement(source, 'serials',
            media_serial1=self.serial_details_inputs['Media Serial 1'].text(),
            media_serial2=self.serial_details_inputs['Media Serial 2'].text(),
            mediastamp=self.serial_details_inputs['Mediastamp'],
            pcb_serial=self.serial_details_inputs['PCB Serial'].currentText(),
            box_serial=self.serial_details_inputs['Box Serial'].text(),
            box_barcode=self.serial_details_inputs['Box Barcode'].text()
        )

        file1 = ET.SubElement(source, 'file',
            forcename="",
            size=self.file_inputs['File Size 1'].text(),
            crc32=self.file_inputs['CRC32 1'].text().lower(),
            md5=self.file_inputs['MD5 1'].text(),
            sha1=self.file_inputs['SHA1 1'].text(),
            sha256=self.file_inputs['SHA256 1'].text(),
            extension="xci",
            version=self.file_inputs['Version 1'].text(),
            update_type=self.file_inputs['Update Type 1'].text(),
            format="Default"
        )

        file2 = ET.SubElement(source, 'file',
            forcename="",
            size=self.file_inputs['File Size 2'].text(),
            crc32=self.file_inputs['CRC32 2'].text().lower(),
            md5=self.file_inputs['MD5 2'].text(),
            sha1=self.file_inputs['SHA1 2'].text(),
            sha256=self.file_inputs['SHA256 2'].text(),
            extension="bin",
            item="Initial Area",
            filter="Initial Area",
            format="Default"
        )

        file3 = ET.SubElement(source, 'file',
            forcename="",
            size=self.file_inputs['File Size 3'].text(),
            crc32=self.file_inputs['CRC32 3'].text().lower(),
            md5=self.file_inputs['MD5 3'].text(),
            sha1=self.file_inputs['SHA1 3'].text(),
            sha256=self.file_inputs['SHA256 3'].text(),
            extension="xci",
            format="FullXCI"
        )

        xml_str = minidom.parseString(ET.tostring(datafile)).toprettyxml(indent="    ")

        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if output_dir:
            game_name = self.basic_info_inputs['Game Name'].text()
            dumper = self.source_details_inputs['Dumper'].text()
            dump_date = self.custom_dump_date_input.date().toString("yyyy-MM-dd") if self.custom_dump_date_checkbox.isChecked() else QDate.currentDate().toString("yyyy-MM-dd")
            file_name = f"{game_name} - {dumper} - {dump_date} Submission.xml"
            file_path = os.path.join(output_dir, file_name)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.transform_xml(xml_str))
            os.startfile(output_dir)

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

        self.update_display()

class ImportNXGameInfoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import NX Game Info")
        self.setGeometry(100, 100, 600, 400)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.drag_drop_label = QLabel("Paste the NX Game Info output below:")
        self.drag_drop_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.drag_drop_label)
        
        self.output_text_edit = QPlainTextEdit()
        self.layout.addWidget(self.output_text_edit)
        
        self.import_button = QPushButton("Import")
        self.import_button.clicked.connect(self.import_output)
        self.layout.addWidget(self.import_button)

    def import_output(self):
        output = self.output_text_edit.toPlainText()
        game_info = self.parse_nx_game_info_output(output)
        self.parent().import_nx_game_info(game_info)
        self.accept()

    def parse_nx_game_info_output(self, output):
        lines = output.splitlines()
        game_info = {}
        
        lang_map = {
            "en-US": "en", "en-GB": "en", "fr-CA": "fr", "es-419": "es",
            "zh-CN": "Zh-Hans", "zh-TW": "Zh-Hant"
        }
        
        for line in lines:
            if line.startswith("├ Title ID:"):
                game_info['title_id'] = line.split(":")[1].strip()
            elif line.startswith("├ Title Name:"):
                game_info['title_name'] = line.split(":")[1].strip()
            elif line.startswith("├ Display Version:"):
                game_info['display_version'] = line.split(":")[1].strip()
            elif line.startswith("├ Version:"):
                game_info['version'] = line.split(":")[1].strip()
            elif line.startswith("├ Languages:"):
                languages = line.split(":")[1].strip().split(',')
                transformed_langs = set(lang_map.get(lang.strip(), lang.strip()) for lang in languages)
                game_info['languages'] = ','.join(sorted(transformed_langs))
        
        return game_info

class ImportHashesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Hashes")
        self.setGeometry(100, 100, 400, 200)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.radio_group = QButtonGroup(self)
        
        self.default_xci_radio = QRadioButton("Default XCI")
        self.initial_area_radio = QRadioButton("Initial Area")
        self.full_xci_radio = QRadioButton("FullXCI")
        
        self.radio_group.addButton(self.default_xci_radio)
        self.radio_group.addButton(self.initial_area_radio)
        self.radio_group.addButton(self.full_xci_radio)
        
        self.layout.addWidget(self.default_xci_radio)
        self.layout.addWidget(self.initial_area_radio)
        self.layout.addWidget(self.full_xci_radio)
        
        self.drag_drop_label = QLabel("Drag and Drop File Here")
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
        hashes = {
            'size': self.calculate_size(file_path),
            'sha1': self.calculate_hash(file_path, 'sha1'),
            'sha256': self.calculate_hash(file_path, 'sha256'),
            'crc32': self.calculate_crc32(file_path),
            'md5': self.calculate_hash(file_path, 'md5')
        }
        selected_button = self.radio_group.checkedButton()
        if selected_button:
            category = selected_button.text()
            self.parent().import_hashes(hashes, category)
            self.set_next_radio_button()
    
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
        return format(crc32 & 0xFFFFFFFF, '08x').upper()
    
    def showEvent(self, event):
        super().showEvent(event)
        self.set_default_radio_button()

    def set_default_radio_button(self):
        parent = self.parent()
        if parent:
            if not parent.file_inputs["SHA1 1"].text():
                self.default_xci_radio.setChecked(True)
            elif not parent.file_inputs["SHA1 2"].text():
                self.initial_area_radio.setChecked(True)
            elif not parent.file_inputs["SHA1 3"].text():
                self.full_xci_radio.setChecked(True)
            else:
                self.default_xci_radio.setChecked(True)

    def set_next_radio_button(self):
        parent = self.parent()
        if parent:
            if not parent.file_inputs["SHA1 1"].text():
                self.default_xci_radio.setChecked(True)
            elif not parent.file_inputs["SHA1 2"].text():
                self.initial_area_radio.setChecked(True)
            elif not parent.file_inputs["SHA1 3"].text():
                self.full_xci_radio.setChecked(True)

class GenerateFullXCIDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate Full XCI")
        self.setGeometry(100, 100, 400, 200)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.state = 0
        
        self.drag_drop_label = QLabel("Drag and Drop Initial Area (.bin) Here")
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
                    self.drag_drop_label.setText("Drag and Drop Default XCI (.xci) Here")
                else:
                    self.drag_drop_label.setText("Please drop an Initial Area .bin file that has a size of 512 bytes")
            elif self.state == 1:
                if file_path.endswith('.xci'):
                    self.default_xci_path = file_path
                    self.generate_full_xci()
                    self.accept()
                else:
                    self.drag_drop_label.setText("Please drop a .xci file")
    
    def generate_full_xci(self):
        default_xci_filename = os.path.basename(self.default_xci_path)
        full_xci_filename = os.path.splitext(default_xci_filename)[0] + " (Full XCI)" + os.path.splitext(default_xci_filename)[1]
        full_xci_path = os.path.join(os.path.dirname(self.default_xci_path), full_xci_filename)
        with open(full_xci_path, 'wb') as full_xci:
            with open(self.initial_area_path, 'rb') as initial_area:
                full_xci.write(initial_area.read())
            full_xci.write(b'\x00' * 3584)
            with open(self.default_xci_path, 'rb') as default_xci:
                full_xci.write(default_xci.read())
        os.startfile(os.path.dirname(full_xci_path))

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
