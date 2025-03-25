import sys
import os
import ffmpeg
import whisper
from dotenv import load_dotenv
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QLineEdit, QTextEdit, QProgressBar,
    QMessageBox, QCheckBox, QFileDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import yt_dlp

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

load_dotenv()
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.7)
informe_prompt = PromptTemplate.from_template("""
Eres un asistente profesional experto en análisis de contenido hablado.

Tu tarea es elaborar un informe detallado, claro y completo a partir del texto transcrito de un video. El informe debe estar dividido en las siguientes secciones:

1. 📝 Introducción: Describe brevemente de qué trata el contenido y cuál es su propósito general.
2. 📄 Desarrollo: Analiza en profundidad los temas tratados, explicando los conceptos clave, datos mencionados, argumentos importantes y ejemplos relevantes.
3. 💡 Puntos clave: Lista las ideas principales y cualquier conclusión o reflexión importante.
4. 📊 Valoraciones o implicaciones (si aplica): Añade una interpretación del impacto, utilidad o contexto del contenido.
5. ✅ Conclusión: Resume lo aprendido o transmitido en el contenido.
6. 📌 Observaciones adicionales: Incluye cualquier comentario adicional relevante, advertencias, lenguaje técnico, tono utilizado o estructura discursiva.

Utiliza un lenguaje natural y técnico cuando sea necesario, incluye emojis para mayor claridad visual, y asegúrate de que el informe sea comprensible y útil incluso si alguien no vio el video original.

Contenido transcrito:
{texto}
""")

def generar_informe_desde_txt(path_txt):
    informe_path = path_txt.replace(".txt", "_informe.md")

    if os.path.exists(informe_path):
        print(f"🟡 Informe ya existe: {informe_path}")
        return

    with open(path_txt, "r", encoding="utf-8") as f:
        texto = f.read()

    if not texto.strip():
        print(f"⚠️ El archivo {path_txt} está vacío. Se omite informe.")
        return

    prompt = informe_prompt.format(texto=texto)
    try:
        respuesta = llm.invoke(prompt).content
        with open(informe_path, "w", encoding="utf-8") as f:
            f.write(respuesta)
        print(f"✅ Informe generado en: {informe_path}")
        return informe_path
    except Exception as e:
        print(f"❌ Error generando informe: {e}")
        return None

class DescargadorThread(QThread):
    progreso = pyqtSignal(str)
    error = pyqtSignal(str)
    completado = pyqtSignal()
    progreso_porcentaje = pyqtSignal(int)

    def __init__(self, urls, carpeta_destino, transcribir_audio, solo_informe, usar_openai):
        super().__init__()
        self.urls = urls
        self.carpeta_destino = carpeta_destino
        self.transcribir_audio = transcribir_audio
        self.solo_informe = solo_informe
        self.usar_openai = usar_openai

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
        for archivo in archivos_videos:
            archivo_video = os.path.join(self.carpeta_destino, archivo)
            archivo_audio = archivo_video.replace(".mp4", ".wav")
            self.progreso.emit(f"Convirtiendo {archivo_video} a WAV...")
            ffmpeg.input(archivo_video).output(archivo_audio, format="wav", acodec="pcm_s16le").run()

    def procesar_transcripciones(self):
        archivos_audio = [f for f in os.listdir(self.carpeta_destino) if f.endswith(".wav")]
        for archivo in archivos_audio:
            archivo_audio = os.path.join(self.carpeta_destino, archivo)
            archivo_txt = archivo_audio.replace(".wav", ".txt")

            if not os.path.exists(archivo_txt) and os.path.getsize(archivo_audio) > 1024:
                self.progreso.emit(f"Procesando transcripción de {archivo_audio}...")
                texto_transcrito = self.transcribir_audio_func(archivo_audio)
                self.guardar_transcripcion(archivo_audio, texto_transcrito)

    def transcribir_audio_func(self, archivo_audio):
        try:
            self.progreso.emit(f"Cargando modelo Whisper...")
            modelo = whisper.load_model("base")
            resultado = modelo.transcribe(archivo_audio)
            return resultado["text"].strip() if resultado and "text" in resultado else ""
        except Exception as e:
            self.error.emit(f"Error en transcripción: {str(e)}")
            return ""

    def guardar_transcripcion(self, archivo_audio, texto):
        nombre_txt = archivo_audio.replace(".wav", ".txt")
        if texto.strip():
            with open(nombre_txt, "w", encoding="utf-8") as f:
                f.write(texto)
            self.progreso.emit(f"Transcripción guardada en: {nombre_txt}")

            informe_path = None
            if self.usar_openai:
                informe_path = generar_informe_desde_txt(nombre_txt)
                if informe_path:
                    self.progreso.emit("✅ Informe generado con éxito usando OpenAI.")

            if self.solo_informe:
                try:
                    if os.path.exists(archivo_audio):
                        os.remove(archivo_audio)
                    video_path = archivo_audio.replace(".wav", ".mp4")
                    if os.path.exists(video_path):
                        os.remove(video_path)
                    if self.usar_openai and os.path.exists(nombre_txt):
                        os.remove(nombre_txt)
                    mensaje_final = "✅ Archivos eliminados."
                    if self.usar_openai:
                        mensaje_final += " Solo se ha conservado el informe generado."
                    else:
                        mensaje_final += " Se ha conservado la transcripción."
                    self.progreso.emit(mensaje_final)
                except Exception as e:
                    self.error.emit(f"Error al borrar archivos: {e}")

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Descargador de Videos de YouTube")
        self.setMinimumSize(600, 400)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #202124;
            }
            QPushButton {
                background-color: #4285F4;
                color: white;
                font-weight: bold;
                padding: 5px;
                border-radius: 5px;
            }
            QCheckBox, QLabel {
                color: white;
            }
            QLineEdit, QTextEdit {
                color: black;
                background-color: white;
            }
            QProgressBar {
                background-color: #3c4043;
                color: white;
                border: 1px solid #4285F4;
                border-radius: 5px;
                text-align: center;
            }
        """)

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

        self.usar_openai_checkbox = QCheckBox("Generar informe con OpenAI")
        layout.addWidget(self.usar_openai_checkbox)

        self.solo_informe_checkbox = QCheckBox("¡Solo generar informe y borrar archivos!")
        layout.addWidget(self.solo_informe_checkbox)

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
        self.thread_descarga = DescargadorThread(
            urls, self.carpeta_destino,
            self.transcrib_checkbox.isChecked(),
            self.solo_informe_checkbox.isChecked(),
            self.usar_openai_checkbox.isChecked()
        )
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