from pathlib import Path
from rembg import remove, new_session
import requests
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QLineEdit,
    QVBoxLayout, QFileDialog, QMessageBox
)

def transformImage(path,outputPath = None):
    if outputPath is None:
        outputPath = path

    path = Path(path)
    outputPath = Path(outputPath)
    
    if path.is_dir():
        return transformFolder(path)
        
    elif path.is_file():
        return transformFile(path, outputPath)

    return "Error"


def transformFolder(folderPath):

    session = new_session()

    for file in Path(folderPath).glob('*.png'):
        input_path = str(file)
        output_path = str(file.parent / (file.stem + ".out.png"))

        with open(input_path, 'rb') as i:
            with open(output_path, 'wb') as o:
                input = i.read()
                output = remove(input, session=session)
                o.write(output)

def transformFile(inputPath, outputPath):
    input_path = Path(inputPath)

    output_name = Path(outputPath).stem + ".png"
    output_path = str(Path(outputPath).with_name(output_name))

    with open(input_path, 'rb') as i:
        with open(output_path, 'wb') as o:
            raw = i.read()
            output = remove(raw)
            o.write(output)

    return f"File processed → {output_path}"

class ImageConverter(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Convertisseur Image → PNG Transparent")
        self.resize(400, 250)

        self.label = QLabel("Aucun fichier sélectionné")
        self.btn_select = QPushButton("Choisir un fichier")
        self.btn_process = QPushButton("Transformer l'image")

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Entrer une URL d'image...")

        self.btn_curl = QPushButton("Télécharger depuis l'URL")

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.btn_select)
        layout.addWidget(self.url_input)
        layout.addWidget(self.btn_curl)
        layout.addWidget(self.btn_process)
        self.setLayout(layout)

        self.selected_file = None

        self.btn_select.clicked.connect(self.select_file)
        self.btn_curl.clicked.connect(self.curlImg)
        self.btn_process.clicked.connect(self.process_image)

    def select_file(self):
        self.selected_file = None
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir une image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )

        if file_path:
            self.selected_file = file_path
            self.label.setText(f"Fichier sélectionné :\n{file_path}")

    def curlImg(self):
        self.selected_file = None
        url = self.url_input.text().strip()

        if not url:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer une URL.")
            return

        try:
            response = requests.get(url)
            response.raise_for_status()

            tmp_file = Path("./downloaded_image.jpg")

            with open(tmp_file, "wb") as f:
                f.write(response.content)

            self.selected_file = str(tmp_file)
            self.label.setText(f"Image téléchargée :\n{tmp_file}")

        except Exception as e:
            QMessageBox.critical(self, "Erreur téléchargement", str(e))

    def process_image(self):
        if not self.selected_file:
            QMessageBox.warning(self, "Erreur", "Veuillez d'abord sélectionner ou télécharger un fichier.")
            return

        input_path = Path(self.selected_file)
        output_path = input_path.with_suffix(".png")

        try:
            result = transformFile(input_path, output_path)
            QMessageBox.information(self, "Succès", f"Image convertie :\n{result}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageConverter()
    window.show()
    sys.exit(app.exec())

#https://doc.qt.io/qtforpython-6/_images/pyside6-designer_screenshot.webp