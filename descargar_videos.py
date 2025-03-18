import sys
import os
import ffmpeg
import whisper
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLineEdit, QLabel, 
                            QFileDialog, QProgressBar, QTextEdit, QMessageBox, QCheckBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import yt_dlp

class DescargadorThread(QThread):
    progreso = pyqtSignal(str)
    error = pyqtSignal(str)
    completado = pyqtSignal()
    progreso_porcentaje = pyqtSignal(int)
    
    def __init__(self, urls, carpeta_destino, transcribir_audio):
        super().__init__()
        self.urls = urls
        self.carpeta_destino = carpeta_destino
        self.transcribir_audio = transcribir_audio

    def run(self):
        try:
            total_videos = len(self.urls)
            for index, url in enumerate(self.urls, start=1):
                self.progreso.emit(f"Procesando: {url}")
                self.descargar_video(url)
                self.progreso_porcentaje.emit(int((index / total_videos) * 100))
            
            if self.transcribir_audio:
                self.progreso.emit("Extrayendo audio de todos los videos descargados...")
                self.convertir_videos_a_audio()
                
                self.progreso.emit("Eliminando archivos de video MP4...")
                self.eliminar_videos_mp4()
                
                self.progreso.emit("Iniciando transcripción de archivos de audio...")
                self.procesar_transcripciones()
            
            self.completado.emit()
        except Exception as e:
            self.error.emit(str(e))

    def descargar_video(self, url):
        try:
            url = url.strip()
            ydl_opts = {
                'format': 'best[ext=mp4]',
                'outtmpl': os.path.join(self.carpeta_destino, '%(title)s.%(ext)s'),
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(url, download=True)
        except Exception as e:
            self.error.emit(f"Error al descargar el video: {str(e)}")

    def convertir_videos_a_audio(self):
        archivos_videos = [f for f in os.listdir(self.carpeta_destino) if f.endswith(".mp4")]
        total_videos = len(archivos_videos)
        for index, archivo in enumerate(archivos_videos, start=1):
            archivo_video = os.path.join(self.carpeta_destino, archivo)
            archivo_audio = archivo_video.replace(".mp4", ".wav")
            self.progreso.emit(f"Convirtiendo {archivo_video} a WAV...")
            ffmpeg.input(archivo_video).output(archivo_audio, format="wav", acodec="pcm_s16le").run()
            self.progreso_porcentaje.emit(int((index / total_videos) * 100))

    def eliminar_videos_mp4(self):
        for archivo in os.listdir(self.carpeta_destino):
            if archivo.endswith(".mp4"):
                os.remove(os.path.join(self.carpeta_destino, archivo))
                self.progreso.emit(f"Eliminado {archivo}")
    
    def procesar_transcripciones(self):
        archivos_audio = [f for f in os.listdir(self.carpeta_destino) if f.endswith(".wav")]
        total_audios = len(archivos_audio)
        for index, archivo in enumerate(archivos_audio, start=1):
            archivo_audio = os.path.join(self.carpeta_destino, archivo)
            archivo_txt = archivo_audio.replace(".wav", ".txt")
            
            if not os.path.exists(archivo_txt) and os.path.getsize(archivo_audio) > 1024:
                self.progreso.emit(f"Procesando transcripción de {archivo_audio}, esto puede tardar varios minutos...")
                texto_transcrito = self.transcribir_audio_func(archivo_audio)
                self.guardar_transcripcion(archivo_audio, texto_transcrito)
            else:
                self.progreso.emit(f"Error: El archivo de audio {archivo_audio} está vacío o no existe.")
            self.progreso_porcentaje.emit(int((index / total_audios) * 100))

    def transcribir_audio_func(self, archivo_audio):
        try:
            self.progreso.emit(f"Cargando modelo Whisper...")
            modelo = whisper.load_model("base")  # Puedes cambiar a "small" o "large" según tu hardware
            self.progreso.emit(f"Procesando transcripción de {archivo_audio}...")
            resultado = modelo.transcribe(archivo_audio)
            
            if resultado and "text" in resultado:
                transcripcion = resultado["text"].strip()
                self.progreso.emit(f"Transcripción recibida: {transcripcion[:100]}...")
                return transcripcion
            else:
                self.progreso.emit(f"Error en la transcripción: Whisper no devolvió texto para {archivo_audio}")
                return ""
        except Exception as e:
            self.error.emit(f"Excepción en la transcripción: {str(e)}")
            return ""
    
    def guardar_transcripcion(self, archivo_audio, texto):
        try:
            nombre_txt = archivo_audio.replace(".wav", ".txt")
            if texto.strip():
                with open(nombre_txt, "w", encoding="utf-8") as f:
                    f.write(texto)
                self.progreso.emit(f"Transcripción guardada en: {nombre_txt}")
            else:
                self.error.emit(f"Error: La transcripción para {archivo_audio} está vacía.")
        except Exception as e:
            self.error.emit(f"Error al guardar transcripción: {str(e)}")

    def actualizar_log(self, mensaje):
        self.texto_log.append(mensaje)

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Descargador de Videos de YouTube")
        self.setMinimumSize(600, 400)

        widget_principal = QWidget()
        self.setCentralWidget(widget_principal)
        layout = QVBoxLayout(widget_principal)

        self.boton_buscar = QPushButton("Buscar Archivo")
        self.boton_buscar.clicked.connect(self.buscar_archivo)
        layout.addWidget(self.boton_buscar)

        self.line_edit_archivo = QLineEdit()
        self.line_edit_archivo.setReadOnly(True)
        layout.addWidget(self.line_edit_archivo)

        self.texto_log = QTextEdit()
        self.texto_log.setReadOnly(True)
        layout.addWidget(self.texto_log)

        self.barra_progreso = QProgressBar()
        layout.addWidget(self.barra_progreso)

        self.transcrib_checkbox = QCheckBox("Transcribir audio después de la descarga")
        layout.addWidget(self.transcrib_checkbox)

        self.boton_descargar = QPushButton("Descargar")
        self.boton_descargar.clicked.connect(self.iniciar_descarga)
        layout.addWidget(self.boton_descargar)

        self.carpeta_destino = os.path.join(os.getcwd(), 'video_outs')
        if not os.path.exists(self.carpeta_destino):
            os.makedirs(self.carpeta_destino)

        self.thread_descarga = None
    
    def buscar_archivo(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo de enlaces", "", "Archivos de texto (*.txt)")
        if archivo:
            self.line_edit_archivo.setText(archivo)
            with open(archivo, 'r', encoding='utf-8') as f:
                self.urls = [line.strip() for line in f.readlines()]
    
    def iniciar_descarga(self):
        urls = getattr(self, 'urls', [])
        if not urls:
            QMessageBox.warning(self, "Error", "Ingrese una URL o seleccione un archivo de enlaces")
            return
        self.thread_descarga = DescargadorThread(urls, self.carpeta_destino, self.transcrib_checkbox.isChecked())
        self.thread_descarga.progreso.connect(self.actualizar_log)
        self.thread_descarga.progreso_porcentaje.connect(self.barra_progreso.setValue)
        self.thread_descarga.start()
    
    def actualizar_log(self, mensaje):
        self.texto_log.append(mensaje)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())