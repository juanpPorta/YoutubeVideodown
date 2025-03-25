# 🎥📄 YouTube Video to Transcript & Report Generator

Una aplicación de escritorio con PyQt6 para descargar videos de YouTube, transcribir su audio y generar informes detallados utilizando OpenAI (opcional).

---

## 🔧 Instalación

1. 📥 Clona el repositorio:

```bash
git clone https://github.com/juanpPorta/YoutubeVideodown.git
cd YoutubeVideodown
```

2. 🐍 Crea un entorno virtual (opcional pero recomendado):

```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate.bat   # Windows
```

3. 📦 Instala las dependencias:

```bash
pip install -r requirements.txt
```

---

## 🧰 Dependencias principales

- `PyQt6` 🖥️ — Interfaz gráfica
- `yt_dlp` 🎬 — Descarga de videos
- `ffmpeg` 🔊 — Conversión de video a audio
- `openai`, `langchain-openai` 🤖 — Para generar informes con GPT (opcional)
- `whisper` 🧠 — Transcripción del audio

Asegúrate de tener `ffmpeg` instalado y accesible desde la terminal. Puedes descargarlo desde: https://ffmpeg.org/download.html

---

## 🔐 Configura tu clave de OpenAI

Crea un archivo `.env` en la raíz del proyecto:

```env
OPENAI_API_KEY=tu_clave_de_openai
```

> Si no tienes clave, puedes usar el programa sin generar informes con GPT.

---

## 🚀 Ejecución

```bash
python app.py
```

---

## ✨ Funcionalidades

| Opción | Descripción |
|--------|-------------|
| 📁 **Buscar Archivo** | Selecciona un archivo `.txt` con URLs de YouTube, una por línea |
| ✅ **Transcribir audio después de la descarga** | Extrae audio, lo convierte a texto (.txt) |
| 🧠 **Generar informe con OpenAI** | Crea un informe detallado `.md` desde la transcripción |
| 🧹 **¡Solo generar informe y borrar archivos!** | Borra video/audio/transcripción dejando solo el informe o solo el `.txt` |

---

## 📂 Estructura de salida

Los archivos generados se guardan en la carpeta:

```
./video_outs/
├── video.mp4
├── video.wav
├── video.txt       ← transcripción
├── video_informe.md ← informe generado con OpenAI
```

---

## 🧪 Ejemplo de flujo

1. Marca ✅ “Transcribir audio...”
2. Marca 🧠 “Generar informe con OpenAI”
3. Marca 🧹 “¡Solo generar informe y borrar archivos!”

➡️ Se descargará el video, se transcribirá, se generará el informe y se eliminarán los archivos intermedios.

---

## 💬 Créditos

Desarrollado con ❤️ usando Python, Whisper, LangChain y OpenAI.

---

## 📌 Licencia

MIT License
