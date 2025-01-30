import streamlit as st
import pandas as pd

@st.cache_data
def append_acts_data(uploaded_file, page_file, object_number, df):
    """Сохраняет данные о номерах объектов в CSV-файл.

    :param uploaded_file: Имя загруженного файла
    :param page_file: Номер страницы загруженного файла
    :param object_number: Номер объекта, который ввёл пользователь в интерфейсе
    :param df: Датасет, в который записываются данные
    """
    data = pd.read_csv(df)
    data = pd.concat([data,
                      pd.DataFrame([{"uploaded_file": uploaded_file, "page": page_file, "object_number": object_number}])],
                     ignore_index=True)
    data.to_csv(df, index=False)


def get_sorted_df(data_file, data_sorted):
    """Сортирует акты по номерам объектов и сохраняет в CSV-файл.

    :param data_file: Путь к исходному датасету
    :param data_sorted: Путь, куда необходимо сохранить отсортированный датасет
    :return: Отсортированный датасет в формате CSV
    """
    data = pd.read_csv(data_file)
    data = data.drop_duplicates()
    df_sorted = data.sort_values(by="object_number")
    df_sorted.to_csv(data_sorted, index=False)
    return df_sorted