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

def save_crops(result, crops_folder):
    result.save_crop(save_dir=crops_folder)
    crop_folder = os.path.join(crops_folder, "number")
    crop_files = [os.path.join(crop_folder, f) for f in os.listdir(crop_folder) if f.endswith(".jpg")]
    return list(set(crop_files))

def extract_unique_crops(result, page_index, crops_folder):
    page_folder = os.path.join(crops_folder, f"page_{page_index + 1}")
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

# Папки для временных файлов
UPLOAD_FOLDER = "uploads"
PAGES_FOLDER = "pages"
CROPS_FOLDER = "crops"
SORTED_PDF = "data/sorted_acts.pdf"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PAGES_FOLDER, exist_ok=True)
os.makedirs(CROPS_FOLDER, exist_ok=True)

# Интерфейс Streamlit
st.title("Обработка актов с YOLO")

# Загрузка PDF
uploaded_pdf = st.file_uploader("Загрузите PDF с актами", type="pdf")

@st.cache_data
def pdf_to_images(pdf_path, output_folder):
    doc = fitz.open(pdf_path)
    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        pix = page.get_pixmap(dpi=200)
        image_path = f"{output_folder}/page_{page_number + 1}.jpg"
        pix.save(image_path)
        print(f"Сохранено: {image_path}")
    doc.close()
    return [os.path.join(output_folder, f) for f in os.listdir(output_folder) if f.endswith(".jpg")]

# Проверка и загрузка данных из all_data.csv при старте
if "all_data" not in st.session_state:
    if os.path.exists("data/all_data.csv"):
        st.session_state.all_data = pd.read_csv("data/all_data.csv").to_dict(orient="records")
    else:
        st.session_state.all_data = []


if uploaded_pdf:
    # Сохраняем PDF
    pdf_path = os.path.join(UPLOAD_FOLDER, uploaded_pdf.name)
    with open(pdf_path, "wb") as f:
        f.write(uploaded_pdf.read())

    # Разбиваем PDF на страницы
    st.write("Разбиваем PDF на страницы...")
    pdf_to_images(pdf_path, PAGES_FOLDER)

    page_files = [os.path.join(PAGES_FOLDER, f) for f in os.listdir(PAGES_FOLDER) if f.endswith(".jpg")]
    st.write(f"Найдено страниц: {len(page_files)}")

    # Применяем YOLO для каждого изображения
    st.write("Обрабатываем страницы через YOLO...")
    model = load_model()
    results = process_images_with_yolo(page_files)

    # Выводим результаты
    data = []
    processed_pages = set()  # Для отслеживания обработанных страниц

    for i, result in enumerate(results):
        if i in processed_pages:
            continue
        processed_pages.add(i)
        crop_files = extract_unique_crops(result, i, CROPS_FOLDER)

        if crop_files:
            st.write(f"Страница {i + 1}: Вырезанные номера")
            for crop_file in crop_files:
                st.image(crop_file, caption=f"Страница {i + 1}: Вырезанный номер")

            # Ждем ввода числа пользователем
            obj_number = st.text_input(f"Введите номер объекта для страницы {i + 1}", key=f"input_page_{i}")

            if obj_number:
                data.append({"page_file": page_files[i], "object_number": obj_number})

    # Сохраняем разметку в DataFrame
    if data:
        df = pd.DataFrame(data)
        st.write("Собранные данные:", df)

        # Сохранение отсортированного PDF
        if st.button("Отсортировать и собрать в PDF"):
            df_sorted = df.sort_values(by="object_number")
            writer = PdfWriter()

            for _, row in df_sorted.iterrows():
                page_image = Image.open(row["page_file"])
                page_image.save(row["page_file"].replace(".jpg", ".pdf"))

                writer.add_page(PdfReader(row["page_file"].replace(".jpg", ".pdf")).pages[0])

            with open(SORTED_PDF, "wb") as output_pdf:
                writer.write(output_pdf)

            st.success("Готовый PDF собран и отсортирован!")
            with open(SORTED_PDF, "rb") as f:
                st.download_button("Скачать PDF", f, file_name="sorted_acts.pdf")
