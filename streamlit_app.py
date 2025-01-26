import os
import pandas as pd
import streamlit as st
from data_handler import append_data, get_sorted_df
from number_detection import load_model, process_images_with_yolo, extract_unique_crops
from pdf_jpg_processor import pdf_to_images, write_sorted_pdf


UPLOAD_FOLDER = "uploads"
PAGES_FOLDER = "pages"
CROPS_FOLDER = "crops"
SORTED_PDF = "data/sorted_acts.pdf"
DATA_FILE = "data/all_data.csv"
SORTED_DF = "data/sorted_data.csv"

if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["uploaded_file", "page", "object_number"]).to_csv(DATA_FILE, index=False)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PAGES_FOLDER, exist_ok=True)
os.makedirs(CROPS_FOLDER, exist_ok=True)

# Интерфейс Streamlit
st.title("Поиск номеров объектов и сортировка актов")

# Загрузка PDF
uploaded_pdf = st.file_uploader("Загрузите PDF с актами", type="pdf")

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
    st.write("Ищем номера объектов...")
    model = load_model()
    results = process_images_with_yolo(page_files, model)

    all_numbers_entered = True

    for i, result in enumerate(results, start=1):

        crop_files = extract_unique_crops(result, i, CROPS_FOLDER, uploaded_pdf.name)

        if crop_files:
            st.write(f"Страница {i}: Номера объектов")
            for crop_file in crop_files:
                st.image(crop_file, caption=f"Страница {i}: Вырезанный номер")

            # Ждем ввода числа пользователем
            obj_number = st.text_input(f"Введите номер объекта для страницы {i}", key=f"input_page_{i}")

            if obj_number:
                append_data(uploaded_pdf.name, page_files[i - 1], obj_number, DATA_FILE)
            else:
                all_numbers_entered = False

    if all_numbers_entered:
        st.success("""Все номера объектов введены! 
        Теперь можно загрузить следующий PDF или отсортировать и выгрузить финальный документ.
        Не забудьте закрыть файл перед загрузкой нового PDF - для этого нажмите на x рядом с названием файла.""",
                   icon="✅")

    else:
        st.info("Введите номера объектов для всех страниц перед загрузкой нового PDF.")

if st.button("Отсортировать и собрать в PDF"):
    df_sorted = get_sorted_df(DATA_FILE, SORTED_DF)
    write_sorted_pdf(df_sorted, SORTED_PDF)
    st.success("Готовый PDF собран и отсортирован!")

    with open(SORTED_PDF, "rb") as f:
        st.download_button("Скачать PDF", f, file_name="sorted_acts.pdf")