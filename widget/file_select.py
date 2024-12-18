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
        self.setIcon(QMessageBox.Icon.Warning)
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
    # (filepath, category1, category2, category3, blender_version, render_engine, image_list)
    file_selected = pyqtSignal(str, str, str, str, str, str, list)
    
    def __init__(self):
        super().__init__()
        self.image_dict.clear()
        self.setMinimumWidth(500)
        self.setWindowTitle("Select 3D Model File")
        buttonBoxFlag = (QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.accepted.connect(self.handle_file_selected)
        self.buttonBox = QDialogButtonBox(buttonBoxFlag)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        mainLayout = QVBoxLayout()
        
        file_input_layout = QHBoxLayout()
        
        self.file_path_line_edit = QLineEdit()
        self.file_path_line_edit.setReadOnly(True)
        self.file_path_line_edit.setPlaceholderText("Click the 'Select File' button to select a file")
        select_file_button = QPushButton("Select a 3D Model File")
        select_file_button.setFixedWidth(150)
        select_file_button.clicked.connect(self.select_file)
        
        file_input_layout.addWidget(self.file_path_line_edit)
        file_input_layout.addWidget(select_file_button)
        
        mainLayout.addLayout(file_input_layout)
        
        self.file_name = QLineEdit()
        self.file_name.setPlaceholderText("File Name")
        mainLayout.addWidget(self.file_name)

        categoryLayout = QHBoxLayout()
        
        category_1_layout = QVBoxLayout()
        self.category_1_line_edit = QLineEdit()
        self.category_1_line_edit.setPlaceholderText("Category 1")
        category_1_layout.addWidget(QLabel("Category 1"))
        category_1_layout.addWidget(self.category_1_line_edit)
        
        category_2_layout = QVBoxLayout()
        self.category_2_line_edit = QLineEdit()
        self.category_2_line_edit.setPlaceholderText("Category 2")
        category_2_layout.addWidget(QLabel("Category 2"))
        category_2_layout.addWidget(self.category_2_line_edit)
        
        category_3_layout = QVBoxLayout()
        self.category_3_line_edit = QLineEdit()
        category_3_layout.addWidget(QLabel("Category 3"))
        self.category_3_line_edit.setPlaceholderText("Category 3")
        category_3_layout.addWidget(self.category_3_line_edit)
        
        categoryLayout.addLayout(category_1_layout)
        categoryLayout.addLayout(category_2_layout)
        categoryLayout.addLayout(category_3_layout)

        mainLayout.addLayout(categoryLayout)
        
        renderInfoLayout = QHBoxLayout()
        
        blenderVersionLayout = QVBoxLayout()
        
        self.blender_version_drop_down = QComboBox()
        self.blender_version_drop_down.addItems(BLENDER_VERSION_LIST)
        blenderVersionLayout.addWidget(QLabel("Blender Version"))
        blenderVersionLayout.addWidget(self.blender_version_drop_down)

        renderEngineLayout = QVBoxLayout()
        
        self.render_engine_drop_down = QComboBox()
        self.render_engine_drop_down.addItems(RENDER_ENGINE_LIST)
        renderEngineLayout.addWidget(QLabel("Render Engine"))
        renderEngineLayout.addWidget(self.render_engine_drop_down)
        
        renderInfoLayout.addLayout(blenderVersionLayout)
        renderInfoLayout.addLayout(renderEngineLayout)
        
        imageInputLayout = QVBoxLayout()
        imageLabelAndAddImageButtonLayout = QHBoxLayout()
        
        addImageButton = QPushButton("Add Preview Images")
        addImageButton.clicked.connect(self.add_images)
        addImageButton.setFixedWidth(150)
        imageLabelAndAddImageButtonLayout.addWidget(QLabel("Images"))
        imageLabelAndAddImageButtonLayout.addWidget(addImageButton)
        imageInputLayout.addLayout(imageLabelAndAddImageButtonLayout)
        
        self.imageListLayout = QHBoxLayout()

        imageScrollWidget = QWidget()
        imageScrollWidget.setLayout(self.imageListLayout)
        imageScrollArea = QScrollArea()
        imageScrollArea.setMinimumHeight(300)
        imageScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        imageScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        imageScrollArea.setWidgetResizable(True)
        imageScrollArea.setWidget(imageScrollWidget)
        
        imageInputLayout.addWidget(imageScrollArea)
        
        mainLayout.addLayout(renderInfoLayout)
        mainLayout.addLayout(imageInputLayout)
        mainLayout.addWidget(self.buttonBox)
        
        self.setLayout(mainLayout)
    
    @pyqtSlot()
    def handle_file_selected(self):
        self.file_selected.emit(
            self.file_path_line_edit.text(),
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
        file_path, _ = QFileDialog.getOpenFileName(self, "Select 3D Model File", __file__, "3D Model Files (*.stl *.obj *.blend *.fbx);;Any Files (*)")
        
        if file_path:
            self.file_path_line_edit.setText(file_path)
            *category_list, file_name = file_path.split(os.sep)
            self.file_name.setText(file_name)

            category_line_edit_list = [
                self.category_1_line_edit,
                self.category_2_line_edit,
                self.category_3_line_edit
            ]
            
            for i, category_line_edit in enumerate(category_line_edit_list):
                try:
                    category_line_edit.setText(category_list.pop())
                except IndexError:
                    for i in range(len(category_list)):
                        category_list[i].setText("N/A")
                    break
            
    @pyqtSlot()
    def add_images(self):
        file_list, _ = QFileDialog.getOpenFileNames(self, "Select Image Files", __file__, "Image Files (*.png *.jpg *.jpeg *.bmp *.webp);;Any Files (*)")
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

        