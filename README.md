# 🎥 Descargador de Videos de YouTube

<div align="center">

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg)

</div>

## 📝 Descripción

Este script en Python permite descargar videos de YouTube de manera eficiente y segura. Utiliza la biblioteca `yt-dlp`, que es un fork mejorado de youtube-dl, para realizar las descargas con las siguientes características:

- ⚡ Descarga en la mejor calidad disponible
- 🔒 Manejo seguro de conexiones
- 🔄 Reintentos automáticos en caso de fallos
- 📊 Barra de progreso en tiempo real
- 🎯 Formato MP4 optimizado

## 🛠️ Requisitos Técnicos

- Python 3.6 o superior
- pip (gestor de paquetes de Python)
- Conexión a Internet estable

## ⚙️ Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/tu-usuario/descargar_videos.git
cd descargar_videos
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## 🚀 Uso

1. Ejecuta el script:
```bash
python descargar_videos.py
```

2. Ingresa la URL del video de YouTube cuando se te solicite
3. El video se descargará automáticamente en la mejor calidad disponible
4. Para salir del programa, ingresa 'q' cuando se te solicite la URL

## 💻 Características Técnicas

- **Manejo de Errores**: Sistema robusto de manejo de excepciones
- **Reintentos Automáticos**: Configuración de reintentos para descargas fallidas
- **Formato de Salida**: Videos en formato MP4 con la mejor calidad disponible
- **Interfaz CLI**: Interfaz de línea de comandos interactiva y amigable
- **Gestión de Directorios**: Descarga automática en el directorio actual

## 🔧 Configuración

El script utiliza las siguientes configuraciones por defecto:
- Timeout de conexión: 30 segundos
- Número de reintentos: 10
- Formato de salida: MP4
- Calidad: Mejor disponible

## ⚠️ Solución de Problemas

Si encuentras algún error, intenta:
1. Actualizar yt-dlp: `pip install --upgrade yt-dlp`
2. Verificar tu conexión a Internet
3. Probar con una URL diferente
4. Esperar unos minutos si el error persiste

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue primero para discutir los cambios que te gustaría hacer.

---
<div align="center">
Hecho con ❤️ para la comunidad
</div> 