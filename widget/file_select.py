from PyQt6.QtWidgets import (
    QDialog, QFileDialog, QDialogButtonBox,
    QVBoxLayout, QHBoxLayout, QComboBox,
    QLabel, QPushButton, QLineEdit, QScrollArea, QWidget
)

from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSlot

BLENDER_VERSION_LIST = [
    "2.79", "2.80", "2.81", "2.82", "2.83",
    "2.90", "2.91", "2.92", "2.93",
    "3.0", "3.1", "3.2", "3.3", "3.4", "3.5"
]

RENDER_ENGINE_LIST = [
    "Cycles", "Eevee"
]

class FileSelectDialog(QDialog):
    
    imageList = []
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Select 3D Model File")
        buttonBoxFlag = (QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        
        self.buttonBox = QDialogButtonBox(buttonBoxFlag)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        mainLayout = QVBoxLayout()
        
        fileInputLayout = QHBoxLayout()
        
        self.filePathLabel = QLabel("<i>Click the 'Select File' button to select a file</i>")
        selectFileButton = QPushButton("Select File")
        selectFileButton.setFixedWidth(150)
        selectFileButton.clicked.connect(self.select_file)
        
        fileInputLayout.addWidget(self.filePathLabel)
        fileInputLayout.addWidget(selectFileButton)
        
        mainLayout.addLayout(fileInputLayout)
        
        categoryLayout = QHBoxLayout()
        
        category1Layout = QVBoxLayout()
        self.category1LineEdit = QLineEdit()
        category1Layout.addWidget(QLabel("Category 1"))
        category1Layout.addWidget(self.category1LineEdit)
        
        category2Layout = QVBoxLayout()
        self.category2LineEdit = QLineEdit()
        category2Layout.addWidget(QLabel("Category 2"))
        category2Layout.addWidget(self.category2LineEdit)
        
        category3Layout = QVBoxLayout()
        self.category3LineEdit = QLineEdit()
        category3Layout.addWidget(QLabel("Category 3"))
        category3Layout.addWidget(self.category3LineEdit)
        
        categoryLayout.addLayout(category1Layout)
        categoryLayout.addLayout(category2Layout)
        categoryLayout.addLayout(category3Layout)

        mainLayout.addLayout(categoryLayout)
        
        renderInfoLayout = QHBoxLayout()
        
        blenderVersionLayout = QVBoxLayout()
        
        self.blenderVersionDropDown = QComboBox()
        self.blenderVersionDropDown.addItems(BLENDER_VERSION_LIST)
        blenderVersionLayout.addWidget(QLabel("Blender Version"))
        blenderVersionLayout.addWidget(self.blenderVersionDropDown)

        renderEngineLayout = QVBoxLayout()
        
        self.renderEngineDropDown = QComboBox()
        self.renderEngineDropDown.addItems(RENDER_ENGINE_LIST)
        renderEngineLayout.addWidget(QLabel("Render Engine"))
        renderEngineLayout.addWidget(self.renderEngineDropDown)
        
        renderInfoLayout.addLayout(blenderVersionLayout)
        renderInfoLayout.addLayout(renderEngineLayout)
        
        imageInputLayout = QVBoxLayout()
        imageLabelAndAddImageButtonLayout = QHBoxLayout()
        
        addImageButton = QPushButton("Add Image")
        addImageButton.clicked.connect(self.add_images)
        addImageButton.setFixedWidth(150)
        imageLabelAndAddImageButtonLayout.addWidget(QLabel("Images"))
        imageLabelAndAddImageButtonLayout.addWidget(addImageButton)
        imageInputLayout.addLayout(imageLabelAndAddImageButtonLayout)
        
        imagePixmap = QPixmap('a.jpeg').scaledToHeight(200)
        itemWidth = int(imagePixmap.width()/2)
        
        self.imageListLayout = QHBoxLayout()
        for i in range(1):
            imageItemLayout = QVBoxLayout()
            imageLabel = QLabel()
            imageLabel.setPixmap(imagePixmap)
            imageItemLayout.addWidget(imageLabel)
            
            imageNameAndButtonLayout = QHBoxLayout()
            imageNameAndButtonLayout.setSpacing(0)
            imageName = QLabel("Image Name")
            imageName.setFixedWidth(itemWidth)
            deleteImageButton = QPushButton("Delete")
            deleteImageButton.clicked.connect(self.delete_image)
            deleteImageButton.setStyleSheet("background-color: red")
            deleteImageButton.setFixedWidth(itemWidth)
            
            imageNameAndButtonLayout.addWidget(imageName)
            imageNameAndButtonLayout.addWidget(deleteImageButton)
            
            imageItemLayout.addLayout(imageNameAndButtonLayout)
            
            self.imageListLayout.addLayout(imageItemLayout)
            self.imageList.append(imageItemLayout)
            
        imageScrollWidget = QWidget()
        imageScrollWidget.setLayout(self.imageListLayout)
        imageScrollArea = QScrollArea()
        imageScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        imageScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        imageScrollArea.setWidgetResizable(True)
        imageScrollArea.setWidget(imageScrollWidget)
        
        imageInputLayout.addWidget(imageScrollArea)
        
        mainLayout.addLayout(renderInfoLayout)
        mainLayout.addLayout(imageInputLayout)
        mainLayout.addWidget(self.buttonBox)
        
        self.setLayout(mainLayout)
    
    def select_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select 3D Model File", __file__, "3D Model Files (*.stl *.obj *.blend *.fbx);;Any Files (*)")
        if file_name:
            self.filePathLabel.setText(file_name)
    
    def add_images(self):
        file_list, _ = QFileDialog.getOpenFileNames(self, "Select Image Files", __file__, "Image Files (*.png *.jpg *.jpeg *.bmp *.webp);;Any Files (*)")
        if not file_list:
            return
        for file_path in file_list:
            imagePixmap = QPixmap(file_path).scaledToHeight(200)
            itemWidth = int(imagePixmap.width()/2)
            
            imageItemLayout = QVBoxLayout()
            imageLabel = QLabel()
            imageLabel.setPixmap(imagePixmap)
            imageItemLayout.addWidget(imageLabel)
            
            imageNameAndButtonLayout = QHBoxLayout()
            imageNameAndButtonLayout.setSpacing(0)
            
            imageName = QLabel("Image Name")
            imageName.setFixedWidth(itemWidth)
            deleteImageButton = QPushButton("Delete")
            deleteImageButton.clicked.connect(self.delete_image, file_path)
            deleteImageButton.setStyleSheet("background-color: red")
            deleteImageButton.setFixedWidth(itemWidth)
            imageNameAndButtonLayout.addWidget(imageName)
            imageNameAndButtonLayout.addWidget(deleteImageButton)
            
            imageItemLayout.addLayout(imageNameAndButtonLayout)
            
            self.imageListLayout.addLayout(imageItemLayout)
            self.imageList.append(imageItemLayout)
    
    @pyqtSlot()
    def delete_image(self, file_path):
        print(self)
        