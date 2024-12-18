import praw
from fpdf import FPDF
import unicodedata
import os

# API de Reddit
reddit = praw.Reddit(
    client_id="QzV4lgBjl1o6hnqAMHyTBw",
    client_secret="U_o9QzvngxvpwRdbZZNxPGFo0aMjmg",
    user_agent="script:TareaIa:v1.0 (by /u/Time_Revolution_3610)",
)

# Ruta para los archivos
OUTPUT_DIR = r"C:/Users/rodri/Downloads/Ollama/informacion/Reddit"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# Función para limpiar texto
def clean_text(text):
    return (
        unicodedata.normalize("NFKD", text)
        .encode("latin-1", "ignore")
        .decode("latin-1")
    )


# Función para obtener los comentarios de una publicación
def get_comments(submission):
    submission.comments.replace_more(limit=0)  # Elimina los "More Comments"
    comments = []
    for comment in submission.comments.list():
        comments.append(comment.body)
    return comments


# Función para buscar y guardar información
def scrape_reddit(topic):
    txt_filename = os.path.join(OUTPUT_DIR, f"{topic.replace(' ', '_')}_reddit.txt")
    pdf_filename = os.path.join(OUTPUT_DIR, f"{topic.replace(' ', '_')}_reddit.pdf")

    # Guardar en archivo de texto
    with open(txt_filename, "w", encoding="utf-8") as txt_file:
        txt_file.write(f"Resultados de la búsqueda en Reddit para: {topic}\n\n")

        # Buscar en Reddit
        for submission in reddit.subreddit("all").search(topic, limit=20):
            title = submission.title
            url = submission.url
            score = submission.score
            comments = submission.num_comments

            txt_file.write(f"Título: {title}\n")
            txt_file.write(f"URL: {url}\n")
            txt_file.write(f"Puntuación: {score}\n")
            txt_file.write(f"Número de comentarios: {comments}\n")

            # Obtener los comentarios de la publicación
            comment_list = get_comments(submission)
            for idx, comment in enumerate(comment_list, start=1):
                txt_file.write(f"Comentario {idx}: {comment}\n")

            txt_file.write("\n" + "-" * 50 + "\n\n")

    # Crear archivo PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(
        200,
        10,
        txt=clean_text(f"Resultados de la búsqueda en Reddit para: {topic}"),
        ln=True,
        align="C",
    )

    with open(txt_filename, "r", encoding="utf-8") as txt_file:
        for line in txt_file:
            pdf.multi_cell(0, 10, txt=clean_text(line.strip()))

    pdf.output(pdf_filename)
    print(f"Archivos creados:\n - {txt_filename}\n - {pdf_filename}")


# Ejecución del script
if __name__ == "__main__":
    tema = input("Introduce el tema a buscar en Reddit: ")
    scrape_reddit(tema)
