from concurrent.futures import ThreadPoolExecutor
from bing_image_downloader import downloader
from serpapi import GoogleSearch
import requests
import os
from PIL import Image
import imagehash

# === CONFIGURACIÓN ===
SEARCH_QUERIES = [
    'tesla model s',
    'tesla model s side view',
    'tesla model s front view',
    'tesla model s rear view',
    'tesla model s modified',
    'tesla model s parked',
    'tesla model s at car show',
    'tesla model s in urban setting',
    'tesla model s on highway',
    'tesla model s on race track',
    'tesla model s top view',
    'tesla model s aerial view',
    'tesla model s side profile',
    'tesla model s front angle low shot',
    'tesla model s sunset drive',
    'tesla model s in mountain road',
    'tesla model s at night'
]





BING_LIMIT = 400  # Número de imágenes por búsqueda en Bing
GOOGLE_LIMIT = 400  # Número de imágenes por búsqueda en Google
OUTPUT_DIR = 'C:/Users/rodri/Downloads/model_s'  # Carpeta donde se guardarán las imágenes
GOOGLE_API_KEY = "8ef489ad071133e5c93448d902c0e5078911f682f258c57642ad6803adc86513"

# === FUNCIONES ===
def download_images_from_bing(query):
    """Descarga imágenes desde Bing."""
    print(f"Descargando imágenes desde Bing para: {query}")
    downloader.download(query, limit=BING_LIMIT, output_dir=OUTPUT_DIR, adult_filter_off=True, force_replace=False, timeout=60, verbose=False)

def download_images_from_google(query):
    """Descarga imágenes desde Google usando SerpAPI."""
    print(f"Descargando imágenes desde Google para: {query}")
    search = GoogleSearch({
        "q": query,
        "tbm": "isch",
        "ijn": "0",
        "api_key": GOOGLE_API_KEY
    })
    results = search.get_dict()
    image_urls = [result['original'] for result in results.get('images_results', [])[:GOOGLE_LIMIT]]

    query_dir = os.path.join(OUTPUT_DIR, query.replace(' ', '_'))
    os.makedirs(query_dir, exist_ok=True)

    for i, url in enumerate(image_urls):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                with open(os.path.join(query_dir, f"google_{i}.jpg"), 'wb') as f:
                    f.write(response.content)
        except Exception as e:
            print(f"Error descargando {url}: {e}")

def remove_duplicates(folder):
    """Elimina imágenes duplicadas en una carpeta usando hashes."""
    print("Eliminando imágenes duplicadas...")
    seen_hashes = set()
    for root, _, files in os.walk(folder):
        for filename in files:
            filepath = os.path.join(root, filename)
            try:
                img_hash = imagehash.average_hash(Image.open(filepath))
                if img_hash in seen_hashes:
                    os.remove(filepath)
                else:
                    seen_hashes.add(img_hash)
            except Exception as e:
                print(f"Error con {filename}: {e}")

# === MAIN ===
if __name__ == "__main__":
    # Paralelizar descargas desde Bing y Google
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Bing descargas
        executor.map(download_images_from_bing, SEARCH_QUERIES)

        # Google descargas
        executor.map(download_images_from_google, SEARCH_QUERIES)

    # Eliminar duplicados
    remove_duplicates(OUTPUT_DIR)

    print("Descarga completa y dataset limpio.")