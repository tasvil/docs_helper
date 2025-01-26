import os
import csv
import streamlit as st
import fitz  # PyMuPDF
from PyPDF2 import PdfReader, PdfWriter
from ultralytics import YOLO
import pandas as pd
from PIL import Image

@st.cache_resource
def load_model():
    model = YOLO("models/yolo11_best.pt")
    return model

@st.cache_data
def process_images_with_yolo(page_files):
    results = model(page_files)
    return results

def extract_unique_crops(result, page_index, crops_folder, uploaded_file):
    page_folder = os.path.join(crops_folder, f"{uploaded_file}_page_{page_index}")
    os.makedirs(page_folder, exist_ok=True)
    # Проверяем, что в page_N еще не создана папка number
    if not os.path.exists(os.path.join(page_folder, "number")):
        result.save_crop(save_dir=page_folder)
    number_folder = os.path.join(page_folder, "number")
    if os.path.exists(number_folder):
        crop_files = [os.path.join(number_folder, f) for f in os.listdir(number_folder) if f.endswith(".jpg")]
    else:
        crop_files = []
    return crop_files


def append_data(uploaded_file, page_file, object_number):
    data = pd.read_csv(DATA_FILE)
    data = pd.concat([data, pd.DataFrame([{"uploaded_file": uploaded_file, "page": page_file, "object_number": object_number}])], ignore_index=True)
    data.to_csv(DATA_FILE, index=False)

UPLOAD_FOLDER = "uploads"
PAGES_FOLDER = "pages"
CROPS_FOLDER = "crops"
SORTED_PDF = "data/sorted_acts.pdf"
DATA_FILE = "data/all_data.csv"

if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["uploaded_file", "page", "object_number"]).to_csv(DATA_FILE, index=False)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PAGES_FOLDER, exist_ok=True)
os.makedirs(CROPS_FOLDER, exist_ok=True)

# Интерфейс Streamlit
st.title("Обработка актов с YOLO")

# Загрузка PDF
uploaded_pdf = st.file_uploader("Загрузите PDF с актами", type="pdf")

@st.cache_data
def pdf_to_images(pdf_path, output_folder, uploaded_file):
    doc = fitz.open(pdf_path)
    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        pix = page.get_pixmap(dpi=200)
        image_path = f"{output_folder}/{uploaded_file}_page_{page_number + 1}.jpg"
        pix.save(image_path)
        print(f"Сохранено: {image_path}")
    doc.close()
    return [os.path.join(output_folder, f) for f in os.listdir(output_folder) if f.endswith(".jpg")]


if uploaded_pdf:
    # Сохраняем PDF
    pdf_path = os.path.join(UPLOAD_FOLDER, uploaded_pdf.name)
    with open(pdf_path, "wb") as f:
        f.write(uploaded_pdf.read())

    # Разбиваем PDF на страницы
    st.write("Разбиваем PDF на страницы...")
    pdf_to_images(pdf_path, PAGES_FOLDER, uploaded_pdf.name)

    page_files = [os.path.join(PAGES_FOLDER, f) for f in os.listdir(PAGES_FOLDER) if f.startswith(uploaded_pdf.name) and f.endswith('.jpg')]
    st.write(f"Найдено страниц: {len(page_files)}")

    # Применяем YOLO для каждого изображения
    st.write("Обрабатываем страницы через YOLO...")
    model = load_model()
    results = process_images_with_yolo(page_files)


    processed_pages = set()  # Для отслеживания обработанных страниц

    for i, result in enumerate(results, start=1):
        if i in processed_pages:
            continue
        processed_pages.add(i)
        crop_files = extract_unique_crops(result, i, CROPS_FOLDER, uploaded_pdf.name)

        if crop_files:
            st.write(f"Страница {i}: Вырезанные номера")
            for crop_file in crop_files:
                st.image(crop_file, caption=f"Страница {i}: Вырезанный номер")

            # Ждем ввода числа пользователем
            obj_number = st.text_input(f"Введите номер объекта для страницы {i}", key=f"input_page_{i}")

            if obj_number:
                append_data(uploaded_pdf.name, page_files[i - 1], obj_number)


if st.button("Отсортировать и собрать в PDF"):
    data = pd.read_csv(DATA_FILE)
    data = data.drop_duplicates()
    df_sorted = data.sort_values(by="object_number")
    data.to_csv("data/sorted_data.csv", index=False)
    writer = PdfWriter()

    for _, row in df_sorted.iterrows():
        page_image = Image.open(row["page"])
        page_image.save(row["page"].replace(".jpg", ".pdf"))
        writer.add_page(PdfReader(row["page"].replace(".jpg", ".pdf")).pages[0])

    with open(SORTED_PDF, "wb") as output_pdf:
        writer.write(output_pdf)

    st.success("Готовый PDF собран и отсортирован!")
    with open(SORTED_PDF, "rb") as f:
        st.download_button("Скачать PDF", f, file_name="sorted_acts.pdf")