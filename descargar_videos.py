import yt_dlp
import os

def descargar_video(url, ruta_destino=None):
    try:
        # Si no se especifica ruta, usar el directorio actual
        if ruta_destino is None:
            ruta_destino = os.getcwd()
            
        # Configuración de yt-dlp
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': os.path.join(ruta_destino, '%(title)s.%(ext)s'),
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
            'ignoreerrors': True
        }
        
        # Descargar el video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Obtener información del video
            info = ydl.extract_info(url, download=False)
            print(f"Descargando: {info['title']}")
            
            # Descargar el video
            ydl.download([url])
            
        print(f"¡Descarga completada! Video guardado en: {ruta_destino}")
        
    except Exception as e:
        print(f"Error al descargar el video: {str(e)}")
        print("\nSugerencias para solucionar el problema:")
        print("1. Asegúrate de tener una conexión a internet estable")
        print("2. Intenta con una URL diferente")
        print("3. Si el problema persiste, espera unos minutos y vuelve a intentarlo")
        print("4. Intenta actualizar yt-dlp con: pip install --upgrade yt-dlp")

def main():
    print("=== Descargador de Videos de YouTube ===")
    
    while True:
        url = input("\nIngresa la URL del video de YouTube (o 'q' para salir): ")
        
        if url.lower() == 'q':
            break
            
        if not url:
            print("Por favor, ingresa una URL válida.")
            continue
            
        descargar_video(url)

if __name__ == "__main__":
    main() 