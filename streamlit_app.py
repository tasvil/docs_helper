import numpy as np
import pandas as pd
import streamlit as st

st.title('Docs Helper')

uploaded_file = st.file_uploader("Choose a PDF or JPG file", type=["pdf", "jpg"])

if uploaded_file is not None:
    # Display file details
    st.write("Filename:", uploaded_file.name)
    st.write("File type:", uploaded_file.type)
    st.write("File size:", uploaded_file.size)

    # Handle the uploaded file
    if uploaded_file.type == "application/pdf":
        st.write("You uploaded a PDF file.")
        # Add your PDF processing logic here
    elif uploaded_file.type == "image/jpeg":
        st.image(uploaded_file, caption="Uploaded Image")