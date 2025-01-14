import streamlit as st
from ultralytics import YOLO

model = YOLO("models/yolo11_best.pt")

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
        img_bytes = uploaded_file.getvalue()
        with open("saved_image.jpg", "wb") as f:
            f.write(img_bytes)
        results = model("saved_image.jpg")
        for result in results:
            result.save(filename="result.jpg")
        st.image("result.jpg", caption="Uploaded Image")


