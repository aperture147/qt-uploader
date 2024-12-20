from PyQt6.QtWidgets import (
    QDialog, QFileDialog, QDialogButtonBox,
    QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox,
    QLabel, QPushButton, QLineEdit, QScrollArea, QWidget
)

from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal
import os
from uuid import uuid4
from typing import Dict

BLENDER_VERSION_LIST = [
    "2.79", "2.80", "2.81", "2.82", "2.83",
    "2.90", "2.91", "2.92", "2.93",
    "3.0", "3.1", "3.2", "3.3", "3.4", "3.5"
]

RENDER_ENGINE_LIST = [
    "Cycles", "Eevee", "RenderMan"
]


class TooManyImageMessageBox(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Too Many Images")
        self.setText("You can only add 5 images at a time")
        self.setIcon(QMessageBox.Icon.Critical)
        self.setStandardButtons(QMessageBox.StandardButton.Ok)

class RequireFieldsNotFulfilledMessageBox(QMessageBox):
    def __init__(self, required_field_list: list):
        super().__init__()
        self.setWindowTitle("Required Fields Not Fulfilled")
        self.setText(f"Please fill in all these required fields: {', '.join(required_field_list)}")
        self.setIcon(QMessageBox.Icon.Critical)
        self.setStandardButtons(QMessageBox.StandardButton.Ok)

class ImageItemWidget(QWidget):

    image_deleted = pyqtSignal(str)

    def __init__(self, file_path: str):
        super().__init__()
        
        self.item_layout = QVBoxLayout()
        
        self.item_layout.setSpacing(10)

        self.file_path = file_path
        name = os.path.basename(file_path)
        self.image_id = str(uuid4())

        imagePixmap = QPixmap(file_path).scaledToHeight(200, Qt.TransformationMode.SmoothTransformation)
        imageWidth = imagePixmap.width()
        
        self.setFixedHeight(250)
        self.setFixedWidth(imageWidth + 40)
        self.image = QLabel()
        self.image.setPixmap(imagePixmap)

        self.item_layout.addWidget(self.image)

        self.image_name_and_btn_layout = QHBoxLayout()
        self.image_name_and_btn_layout.setSpacing(10)
        self.image_name = QLabel(name)
        self.image_name.setFixedWidth(imageWidth - 60)
        
        self.delete_image_button = QPushButton("Delete")
        self.delete_image_button.clicked.connect(self.delete_image)
        self.delete_image_button.setStyleSheet("background-color: red")
        self.delete_image_button.setFixedWidth(50)
        
        self.image_name_and_btn_layout.addWidget(self.image_name)
        self.image_name_and_btn_layout.addWidget(self.delete_image_button)
        
        self.item_layout.addLayout(self.image_name_and_btn_layout)
        self.setLayout(self.item_layout)

    @pyqtSlot()
    def delete_image(self):
        self.image.deleteLater()
        self.image_name_and_btn_layout.deleteLater()
        self.image_name.deleteLater()
        self.delete_image_button.deleteLater()
        self.item_layout.deleteLater()

        self.image_deleted.emit(self.image_id)

class FileSelectDialog(QDialog):
    
    image_dict: Dict[str, ImageItemWidget] = {}
    # (filepath, file_name, category1, category2, category3, blender_version, render_engine, image_list)
    file_selected = pyqtSignal(str, str, str, str, str, str, str, list)
    
    def __init__(self):
        super().__init__()
        self.image_dict.clear()
        self.setMinimumWidth(500)
        self.setWindowTitle("Select 3D Model File")
        buttonBoxFlag = (QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.accepted.connect(self.handle_file_selected)
        
        self.button_box_widget = QDialogButtonBox(buttonBoxFlag)
        self.button_box_widget.accepted.connect(self.check_and_accept)
        self.button_box_widget.rejected.connect(self.reject)
        
        main_layout = QVBoxLayout()
        
        file_input_layout = QHBoxLayout()
        file_input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.file_path_line_edit = QLineEdit()
        self.file_path_line_edit.setReadOnly(True)
        self.file_path_line_edit.setPlaceholderText("Click the 'Select File' button to select a file")
        select_file_button = QPushButton("Select a 3D Model File")
        select_file_button.setFixedWidth(150)
        select_file_button.clicked.connect(self.select_file)
        
        file_input_layout.addWidget(self.file_path_line_edit)
        file_input_layout.addWidget(select_file_button)
        file_input_widget = QWidget()
        file_input_widget.setLayout(file_input_layout)
        main_layout.addWidget(file_input_widget)
        
        file_name_input_layout = QVBoxLayout()
        file_name_input_layout.setContentsMargins(0, 0, 0, 0)
        
        file_name_input_layout.addWidget(QLabel('File Name <span style="color:red">*</span>'))
        self.file_name_line_edit = QLineEdit()
        self.file_name_line_edit.setPlaceholderText("File Name")
        file_name_input_layout.addWidget(self.file_name_line_edit)
        file_name_input_widget = QWidget()
        file_name_input_widget.setLayout(file_name_input_layout)
        
        main_layout.addWidget(file_name_input_widget)

        category_layout = QHBoxLayout()
        category_layout.setContentsMargins(0, 0, 0, 0)
        
        category_1_layout = QVBoxLayout()
        category_1_layout.setContentsMargins(0, 0, 0, 0)
        self.category_1_line_edit = QLineEdit()
        self.category_1_line_edit.setPlaceholderText("Category 1")
        category_1_layout.addWidget(QLabel('Category 1 <span style="color:red">*</span>'))
        category_1_layout.addWidget(self.category_1_line_edit)
        category_1_widget = QWidget()
        
        category_1_widget.setLayout(category_1_layout)
        category_layout.addWidget(category_1_widget)
        
        category_2_layout = QVBoxLayout()
        category_2_layout.setContentsMargins(0, 0, 0, 0)
        self.category_2_line_edit = QLineEdit()
        self.category_2_line_edit.setPlaceholderText("Category 2")
        category_2_layout.addWidget(QLabel('Category 2 <span style="color:red">*</span>'))
        category_2_layout.addWidget(self.category_2_line_edit)
        category_2_widget = QWidget()
        category_2_widget.setLayout(category_2_layout)
        category_layout.addWidget(category_2_widget)
        
        category_3_layout = QVBoxLayout()
        category_3_layout.setContentsMargins(0, 0, 0, 0)
        self.category_3_line_edit = QLineEdit()
        category_3_layout.addWidget(QLabel('Category 3 <span style="color:red">*</span>'))
        self.category_3_line_edit.setPlaceholderText("Category 3")
        category_3_layout.addWidget(self.category_3_line_edit)
        category_3_widget = QWidget()
        category_3_widget.setLayout(category_3_layout)
        category_layout.addWidget(category_3_widget)
        
        category_widget = QWidget()
        category_widget.setLayout(category_layout)

        main_layout.addWidget(category_widget)
        
        render_info_layout = QHBoxLayout()
        render_info_layout.setContentsMargins(0, 0, 0, 0)

        blender_version_layout = QVBoxLayout() 
        blender_version_layout.setContentsMargins(0, 0, 0, 0)       
        self.blender_version_drop_down = QComboBox()
        self.blender_version_drop_down.addItems(BLENDER_VERSION_LIST)
        blender_version_layout.addWidget(QLabel("Blender Version"))
        blender_version_layout.addWidget(self.blender_version_drop_down)
        blender_version_widget = QWidget()
        blender_version_widget.setLayout(blender_version_layout)
        render_info_layout.addWidget(blender_version_widget)

        render_engine_layout = QVBoxLayout()
        render_engine_layout.setContentsMargins(0, 0, 0, 0)
        
        self.render_engine_drop_down = QComboBox()
        
        self.render_engine_drop_down.addItems(RENDER_ENGINE_LIST)
        render_engine_layout.addWidget(QLabel("Render Engine"))
        render_engine_layout.addWidget(self.render_engine_drop_down)
        render_engine_widget = QWidget()
        render_engine_widget.setLayout(render_engine_layout)
        render_info_layout.addWidget(render_engine_widget)
        
        image_input_layout = QVBoxLayout()
        image_input_layout.setContentsMargins(0, 0, 0, 0)
        
        img_label_and_add_image_btn_layout = QHBoxLayout()
        img_label_and_add_image_btn_layout.setContentsMargins(0, 0, 0, 0)
        add_image_button = QPushButton("Add Preview Images")
        add_image_button.clicked.connect(self.add_images)
        add_image_button.setFixedWidth(150)
        img_label_and_add_image_btn_layout.addWidget(QLabel('Images <i>(max 5 images, at lest 3 images)</i> <span style="color:red">*</span>'))
        img_label_and_add_image_btn_layout.addWidget(add_image_button)
        img_label_and_add_image_btn_widget = QWidget()
        img_label_and_add_image_btn_widget.setLayout(img_label_and_add_image_btn_layout)
        image_input_layout.addWidget(img_label_and_add_image_btn_widget)
        
        self.imageListLayout = QHBoxLayout()
        self.imageListLayout.setContentsMargins(0, 0, 0, 0)

        imageScrollWidget = QWidget()
        imageScrollWidget.setLayout(self.imageListLayout)
        imageScrollArea = QScrollArea()
        imageScrollArea.setMinimumHeight(300)
        imageScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        imageScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        imageScrollArea.setWidgetResizable(True)
        imageScrollArea.setWidget(imageScrollWidget)
        
        image_input_layout.addWidget(imageScrollArea)
        
        render_info_widget = QWidget()
        render_info_widget.setLayout(render_info_layout)
        main_layout.addWidget(render_info_widget)
        
        image_input_widget = QWidget()
        image_input_widget.setLayout(image_input_layout)
        main_layout.addWidget(image_input_widget)
        
        main_layout.addWidget(self.button_box_widget)
        
        self.setLayout(main_layout)
    
    @pyqtSlot()
    def check_and_accept(self):
        missed_input = []
        
        if not self.file_path_line_edit.text():
            missed_input.append("File Path")
        
        if not self.file_name_line_edit.text():
            missed_input.append("File Name")
            
        if not self.category_1_line_edit.text():
            missed_input.append("Category 1")
        
        if not self.category_2_line_edit.text():
            missed_input.append("Category 2")
            
        if not self.category_3_line_edit.text():
            missed_input.append("Category 3")
            
        if not self.blender_version_drop_down.currentText():
            missed_input.append("Blender Version")
            
        if not self.render_engine_drop_down.currentText():
            missed_input.append("Render Engine")
            
        if len(self.image_dict) < 3:
            missed_input.append("Image Files (need at least 3)")
        
        if missed_input:
            msg_box = RequireFieldsNotFulfilledMessageBox(missed_input)
            msg_box.exec()
            return
        
        self.accept()
        
    @pyqtSlot()
    def handle_file_selected(self):
        self.file_selected.emit(
            self.file_path_line_edit.text(),
            self.file_name_line_edit.text(),
            self.category_1_line_edit.text(),
            self.category_2_line_edit.text(),
            self.category_3_line_edit.text(),
            self.blender_version_drop_down.currentText(),
            self.render_engine_drop_down.currentText(),
            [
                x.file_path
                for x in self.image_dict.values()
            ]
        )
    
    
    @pyqtSlot()
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select 3D Model File", __file__, "Archive File (*.zip *.rar);;Any File (*)")
        
        if file_path:
            self.file_path_line_edit.setText(file_path)
            *category_list, file_name = file_path.split(os.sep)
            self.file_name_line_edit.setText(os.path.splitext(file_name)[0])
            
            category_line_edit_list = [
                self.category_1_line_edit,
                self.category_2_line_edit,
                self.category_3_line_edit
            ]

            for i, category_line_edit in enumerate(category_line_edit_list):
                try:
                    category_line_edit.setText(category_list.pop())
                except IndexError:
                    for i in range(len(category_line_edit)):
                        category_line_edit_list[i].setText("N/A")
                    break
            
    @pyqtSlot()
    def add_images(self):
        file_list, _ = QFileDialog.getOpenFileNames(self, "Select Image Files", __file__, "Image Files (*.png *.jpg *.jpeg *.webp);;Any Files (*)")
        if not file_list:
            return
        
        if (len(file_list) + len(self.image_dict)) > 5:
            too_many_image_message_box = TooManyImageMessageBox()
            too_many_image_message_box.exec()
            return
            
        for file_path in file_list:
            image_item_widget = ImageItemWidget(file_path)
            
            self.imageListLayout.addWidget(image_item_widget)
            self.image_dict[image_item_widget.image_id] = image_item_widget
            image_item_widget.image_deleted.connect(self.delete_image)

    @pyqtSlot(str)
    def delete_image(self, image_id):
        image_item_widget: QWidget = self.image_dict.pop(image_id, None)
        if image_item_widget:
            self.imageListLayout.removeWidget(image_item_widget)
            image_item_widget.deleteLater()
