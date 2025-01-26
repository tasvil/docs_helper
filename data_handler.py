import streamlit as st
import pandas as pd

@st.cache_data
def append_data(uploaded_file, page_file, object_number, df):
    data = pd.read_csv(df)
    data = pd.concat([data, pd.DataFrame([{"uploaded_file": uploaded_file, "page": page_file, "object_number": object_number}])], ignore_index=True)
    data.to_csv(df, index=False)

def get_sorted_df(data_file, data_sorted):
    data = pd.read_csv(data_file)
    data = data.drop_duplicates()
    df_sorted = data.sort_values(by="object_number")
    df_sorted.to_csv(data_sorted, index=False)
    return df_sorted