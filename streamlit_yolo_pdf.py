import os
import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
from ultralytics import YOLO
import pandas as pd
from PIL import Image

# Настройки YOLO
model = YOLO("models/yolo11_best.pt")

# Папки для временных файлов
UPLOAD_FOLDER = "uploads"
PAGES_FOLDER = "pages"
CROPS_FOLDER = "crops"
SORTED_PDF = "sorted_acts.pdf"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PAGES_FOLDER, exist_ok=True)
os.makedirs(CROPS_FOLDER, exist_ok=True)

# Интерфейс Streamlit
st.title("Обработка актов с YOLO")

# Загрузка PDF
uploaded_pdf = st.file_uploader("Загрузите PDF с актами", type="pdf")

if uploaded_pdf:
    # Сохраняем PDF
    pdf_path = os.path.join(UPLOAD_FOLDER, uploaded_pdf.name)
    with open(pdf_path, "wb") as f:
        f.write(uploaded_pdf.read())

    # Разбиваем PDF на страницы
    st.write("Разбиваем PDF на страницы...")
    pages = convert_from_path(pdf_path, dpi=200, output_folder=PAGES_FOLDER, fmt="jpg")

    st.write(f"Найдено страниц: {len(pages)}")

    # Применяем YOLO для каждого изображения
    st.write("Обрабатываем страницы через YOLO...")
    page_files = [os.path.join(PAGES_FOLDER, f) for f in os.listdir(PAGES_FOLDER) if f.endswith(".jpg")]
    results = model(page_files)

    # Выводим результаты
    data = []
    for i, result in enumerate(results):
        result.save_crop(save_dir=CROPS_FOLDER)
        crop_files = [os.path.join(CROPS_FOLDER, f) for f in os.listdir(CROPS_FOLDER) if f.endswith(".jpg")]

        if crop_files:
            st.image(crop_files[0], caption=f"Страница {i + 1}: Вырезанный номер")

            # Запрашиваем номер у пользователя
            obj_number = st.text_input(f"Введите номер объекта для страницы {i + 1}", key=f"input_{i}")

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
