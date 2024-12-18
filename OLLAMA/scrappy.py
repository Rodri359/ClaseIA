import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
import os

# Sustituye estos valores por tu API Key y CSE ID
API_KEY = "AIzaSyDyiQKA8GZXTcMwCOoPJG6wdMMyvkEYX_A"
CSE_ID = "9467937e284cd49b2"

# Ruta específica donde se guardarán los archivos
output_directory = r"C:/Users/rodri/Downloads/Ollama/informacion"
def fetch_google_results(query, num_results=10):
    #Busca en Google y obtiene enlaces relevantes.
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": CSE_ID,
        "q": query,
        "num": num_results
    }
    response = requests.get(url, params=params)
    results = response.json().get("items", [])
    return [(item["title"], item["link"]) for item in results]

def extract_page_content(url):
    # Extrae el contenido de texto
    try:
        response = requests.get(url, timeout=10, verify=False)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Filtrar contenido principal
        main_content = soup.find(["article", "main"])
        if not main_content:
            # Si no hay contenedor claro, extraer todos los párrafos
            main_content = soup
        
        # Eliminar elementos irrelevantes
        for tag in main_content.find_all(["nav", "aside", "footer", "script", "style"]):
            tag.decompose()  # Eliminar del árbol de HTML
        
        paragraphs = main_content.find_all("p")
        content = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        return content or "No se encontró contenido relevante."
    except Exception as e:
        return f"Error al acceder a {url}: {e}"

def save_to_text(content, filename):
    # Guarda el contenido en un archivo de texto.
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)

def save_to_pdf(content, filename):
    # Guarda el contenido en un archivo PDF.
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Convertir caracteres no compatibles con latin-1
    safe_content = content.encode("latin1", "replace").decode("latin1")
    
    for line in safe_content.split("\n"):
        pdf.multi_cell(190, 10, txt=line)
    pdf.output(filename)

def main():
    query = input("Introduce el tema a buscar en Google: ")
    
    print("\nBuscando resultados en Google...")
    results = fetch_google_results(query)
    
    if not results:
        print("No se encontraron resultados.")
        return
    
    combined_content = ""
    for title, link in results:
        print(f"\nExtrayendo contenido de: {title} ({link})")
        content = extract_page_content(link)
        combined_content += f"\n\n{title}\n{'='*len(title)}\n{content}\n"
    
    # Crear la carpeta si no existe
    os.makedirs(output_directory, exist_ok=True)
    
    # Guardar los resultados en la carpeta especificada
    text_filename = os.path.join(output_directory, f"{query.replace(' ', '_')}_google.txt")
    pdf_filename = os.path.join(output_directory, f"{query.replace(' ', '_')}_google.pdf")
    
    save_to_text(combined_content, text_filename)
    save_to_pdf(combined_content, pdf_filename)
    
    print(f"\nInformación guardada en '{text_filename}' y '{pdf_filename}'.")

if __name__ == "__main__":
    main()