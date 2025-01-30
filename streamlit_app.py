import os
from config import config
import streamlit as st
from data_handler import append_acts_data, get_sorted_df
from number_detection import load_model, process_images_with_yolo, extract_unique_crops
from pdf_jpg_processor import pdf_to_images, write_sorted_pdf


def run_app():
    st.title("Поиск номеров объектов и сортировка актов")

    uploaded_pdf = st.file_uploader("Загрузите PDF с актами", type="pdf")

    if uploaded_pdf:
        pdf_path = os.path.join(config.UPLOAD_FOLDER, uploaded_pdf.name)
        with open(pdf_path, "wb") as f:
            f.write(uploaded_pdf.read())

        st.write("Разбиваем PDF на страницы...")
        pdf_to_images(pdf_path, config.PAGES_FOLDER, uploaded_pdf.name)

        page_files = [os.path.join(config.PAGES_FOLDER, f) for f in os.listdir(config.PAGES_FOLDER)
                      if f.startswith(uploaded_pdf.name) and f.endswith('.jpg')]
        st.write(f"Найдено страниц: {len(page_files)}")

        # Применяем YOLO для каждого изображения
        st.write("Ищем номера объектов...")
        model = load_model()
        results = process_images_with_yolo(page_files, model)

        all_numbers_entered = True

        for i, result in enumerate(results, start=1):
            crop_files = extract_unique_crops(result, i, config.CROPS_FOLDER, uploaded_pdf.name)

            if crop_files:
                st.write(f"Страница {i}: Номера объектов")
                for crop_file in crop_files:
                    st.image(crop_file, caption=f"Страница {i}: Вырезанный номер")

                obj_number = st.text_input(f"Введите номер объекта для страницы {i}", key=f"input_page_{i}")

                if obj_number:
                    append_acts_data(uploaded_pdf.name, page_files[i - 1], obj_number, config.DATA_FILE)
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
        df_sorted = get_sorted_df(config.DATA_FILE, config.SORTED_DF)
        write_sorted_pdf(df_sorted, config.SORTED_PDF)
        st.success("Готовый PDF собран и отсортирован!")

        with open(config.SORTED_PDF, "rb") as f:
            st.download_button("Скачать PDF", f, file_name="sorted_acts.pdf")