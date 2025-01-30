import os
import streamlit as st
from ultralytics import YOLO

@st.cache_resource
def load_model():
    model = YOLO("models/yolo11_best.pt")
    return model

@st.cache_data
def process_images_with_yolo(page_files, _model):
    """Функция детекции номеров объектов на изображениях

    :param page_files: Список с актами в формате jpg, на которых необходимо обнаружить номера
    :param _model: Загруженная модель (YOLO)
    :return: Список результатов детекции модели
    """
    results = _model(page_files)
    return results

def extract_unique_crops(result, page_index, crops_folder, uploaded_file):
    """Вырезает отдельные номера актов, распознанные моделью

    :param result: результат детекции модели
    :param page_index: Номер страницы загруженного файла
    :param crops_folder: Путь для сохранения вырезанных номеров
    :param uploaded_file: загруженный файл PDF
    :return: Список вырезанных номеров объектов
    """
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