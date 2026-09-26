import streamlit as st
import requests

st.title("Image Object Counter")

uploaded_file = st.file_uploader(
    "Upload an image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:

    st.image(uploaded_file)

    if st.button("Analyze"):

        response = requests.post(
            "http://127.0.0.1:8000/analyze-image",
            files={
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type
                )
            }
        )

        result = response.json()

        st.subheader("Result")

        st.write(result["result"])