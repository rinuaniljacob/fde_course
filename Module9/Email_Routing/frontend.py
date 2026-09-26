import streamlit as st
import requests
import json

st.set_page_config(page_title="Email Router")

st.title("📧 AI Email Routing System")

st.write("Paste email content below and classify it automatically.")

email_content = st.text_area(
    "Enter Email Content",
    height=250
)

if st.button("Route Email"):
    if email_content.strip() == "":
        st.warning("Please enter email content.")
    else:
        try:
            response = requests.post(
                "http://127.0.0.1:8000/route-email",
                json={
                    "email_content": email_content
                }
            )

            result = response.json()

            st.subheader("Routing Result")
            st.json(result)

        except Exception as e:
            st.error(f"Error: {e}")