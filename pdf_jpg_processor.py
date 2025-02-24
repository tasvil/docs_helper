import os
import fitz  # PyMuPDF
import streamlit as st
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter

@st.cache_data
def pdf_to_images(pdf_path, output_folder, uploaded_file):
    """Преобразует PDF-файл в изображения и сохраняет их.

    :param pdf_path: Путь к PDF-файлу.
    :param output_folder: Папка для сохранения изображений.
    :param uploaded_file: загруженный файл PDF
    :return: Список путей к сохраненным изображениям.
    """
    doc = fitz.open(pdf_path)
    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        pix = page.get_pixmap(dpi=200)
        image_path = f"{output_folder}/{uploaded_file}_page_{page_number + 1}.jpg"
        pix.save(image_path)
        print(f"Сохранено: {image_path}")
    doc.close()
    return [os.path.join(output_folder, f) for f in os.listdir(output_folder) if f.endswith(".jpg")]


def write_sorted_pdf(df_sorted, sorted_pdf_path):
    """Собирает PDF-файл из JPG страниц в отсортированном порядке

    :param df_sorted: Датасет с актами, отсортированными по порядку номеров объектов
    :param sorted_pdf_path: Путь для сохранения отсортированного файла PDF
    """
    writer = PdfWriter()

    for _, row in df_sorted.iterrows():
        page_image = Image.open(row["page"])
        page_image.save(row["page"].replace(".jpg", ".pdf"))
        writer.add_page(PdfReader(row["page"].replace(".jpg", ".pdf")).pages[0])

    with open(sorted_pdf_path, "wb") as output_pdf:
        writer.write(output_pdf)