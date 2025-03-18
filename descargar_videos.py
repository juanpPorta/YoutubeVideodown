import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLineEdit, QLabel, 
                            QFileDialog, QProgressBar, QTextEdit, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import yt_dlp

class DescargadorThread(QThread):
    progreso = pyqtSignal(str)
    error = pyqtSignal(str)
    completado = pyqtSignal()

    def __init__(self, urls, carpeta_destino):
        super().__init__()
        self.urls = urls
        self.carpeta_destino = carpeta_destino

    def run(self):
        try:
            for url in self.urls:
                self.progreso.emit(f"Procesando: {url}")
                self.descargar_video(url)
            self.completado.emit()
        except Exception as e:
            self.error.emit(str(e))

    def descargar_video(self, url):
        try:
            # Limpiar la URL
            url = url.strip('"').strip("'").strip()
            
            ydl_opts = {
                'format': 'best[ext=mp4]',
                'outtmpl': os.path.join(self.carpeta_destino, '%(title)s.%(ext)s'),
                'quiet': False,
                'no_warnings': False,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                },
                'extract_flat': False,
                'force_generic_extractor': False,
                'socket_timeout': 30,
                'retries': 10,
                'fragment_retries': 10,
                'file_access_retries': 10,
                'extractor_retries': 10,
                'ignoreerrors': True,
                'no_check_certificate': True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    # Obtener información del video
                    info = ydl.extract_info(url, download=False)
                    if info is None:
                        raise Exception("No se pudo obtener información del video")
                    
                    self.progreso.emit(f"Descargando: {info.get('title', 'Video sin título')}")
                    ydl.download([url])
                    
                except yt_dlp.utils.DownloadError as e:
                    # Si falla, intentar con configuración alternativa
                    self.progreso.emit("Primer intento fallido, probando configuración alternativa...")
                    ydl_opts.update({
                        'format': 'best',
                        'force_generic_extractor': True
                    })
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl2:
                        ydl2.download([url])
                        
        except Exception as e:
            self.error.emit(f"Error al descargar el video: {str(e)}")

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Descargador de Videos de YouTube")
        self.setMinimumSize(600, 400)
        
        # Widget principal
        widget_principal = QWidget()
        self.setCentralWidget(widget_principal)
        layout = QVBoxLayout(widget_principal)
        
        # Estilo
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QLineEdit, QTextEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 4px;
                text-align: center;
                background-color: white;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
            QLabel {
                font-size: 14px;
            }
        """)
        
        # Sección de archivo
        layout_archivo = QHBoxLayout()
        self.label_archivo = QLabel("Archivo de enlaces:")
        self.line_edit_archivo = QLineEdit()
        self.line_edit_archivo.setReadOnly(True)
        self.boton_buscar = QPushButton("Buscar")
        self.boton_buscar.clicked.connect(self.buscar_archivo)
        layout_archivo.addWidget(self.label_archivo)
        layout_archivo.addWidget(self.line_edit_archivo)
        layout_archivo.addWidget(self.boton_buscar)
        layout.addLayout(layout_archivo)
        
        # Sección de URL individual
        layout_url = QHBoxLayout()
        self.label_url = QLabel("URL individual:")
        self.line_edit_url = QLineEdit()
        self.line_edit_url.setPlaceholderText("Ingresa la URL del video de YouTube")
        layout_url.addWidget(self.label_url)
        layout_url.addWidget(self.line_edit_url)
        layout.addLayout(layout_url)
        
        # Área de log
        self.texto_log = QTextEdit()
        self.texto_log.setReadOnly(True)
        layout.addWidget(self.texto_log)
        
        # Barra de progreso
        self.barra_progreso = QProgressBar()
        self.barra_progreso.setTextVisible(True)
        self.barra_progreso.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.barra_progreso)
        
        # Botón de descarga
        self.boton_descargar = QPushButton("Descargar")
        self.boton_descargar.clicked.connect(self.iniciar_descarga)
        layout.addWidget(self.boton_descargar)
        
        # Crear carpeta de destino
        self.carpeta_destino = self.crear_carpeta_destino()
        
        # Inicializar variables
        self.thread_descarga = None
        self.urls = []

    def crear_carpeta_destino(self):
        carpeta_destino = os.path.join(os.getcwd(), 'video_outs')
        if not os.path.exists(carpeta_destino):
            os.makedirs(carpeta_destino)
            self.agregar_log(f"Carpeta de destino creada: {carpeta_destino}")
        return carpeta_destino

    def buscar_archivo(self):
        archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo de enlaces",
            "",
            "Archivos de texto (*.txt);;Todos los archivos (*.*)"
        )
        if archivo:
            self.line_edit_archivo.setText(archivo)
            self.leer_archivo_enlaces(archivo)

    def leer_archivo_enlaces(self, ruta_archivo):
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                self.urls = [linea.strip() for linea in archivo if linea.strip()]
                self.agregar_log(f"Se encontraron {len(self.urls)} enlaces en el archivo")
        except Exception as e:
            self.agregar_log(f"Error al leer el archivo: {str(e)}")
            QMessageBox.warning(self, "Error", f"Error al leer el archivo: {str(e)}")

    def agregar_log(self, mensaje):
        self.texto_log.append(mensaje)
        self.texto_log.verticalScrollBar().setValue(
            self.texto_log.verticalScrollBar().maximum()
        )

    def iniciar_descarga(self):
        # Obtener URLs
        urls = []
        if self.line_edit_archivo.text():
            urls.extend(self.urls)
        if self.line_edit_url.text():
            urls.append(self.line_edit_url.text())
            
        if not urls:
            QMessageBox.warning(self, "Error", "Por favor, ingresa una URL o selecciona un archivo de enlaces")
            return
            
        # Deshabilitar controles
        self.boton_descargar.setEnabled(False)
        self.boton_buscar.setEnabled(False)
        self.line_edit_url.setEnabled(False)
        self.barra_progreso.setValue(0)
        
        # Iniciar descarga en un hilo separado
        self.thread_descarga = DescargadorThread(urls, self.carpeta_destino)
        self.thread_descarga.progreso.connect(self.actualizar_progreso)
        self.thread_descarga.error.connect(self.mostrar_error)
        self.thread_descarga.completado.connect(self.descarga_completada)
        self.thread_descarga.start()

    def actualizar_progreso(self, mensaje):
        self.agregar_log(mensaje)
        self.barra_progreso.setValue(self.barra_progreso.value() + 1)

    def mostrar_error(self, mensaje):
        self.agregar_log(f"ERROR: {mensaje}")
        QMessageBox.critical(self, "Error", mensaje)

    def descarga_completada(self):
        self.boton_descargar.setEnabled(True)
        self.boton_buscar.setEnabled(True)
        self.line_edit_url.setEnabled(True)
        self.agregar_log("¡Descarga completada!")
        QMessageBox.information(self, "Éxito", "Todos los videos han sido descargados")

def main():
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 