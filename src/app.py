# app.py
import streamlit as st
import base64
import requests
from fpdf import FPDF

FASTAPI_URL = "http://127.0.0.1:8000/generate-itinerary"

# ---- Page Config ----
st.set_page_config(page_title="AI Travel Assistant", layout="wide")

# ---- Background Image ----
def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

image_path = "data/Blue.jpg"
image_base64 = get_base64(image_path)

st.markdown(f"""
<style>
.stApp {{
    background-image: url("data:image/jpg;base64,{image_base64}");
    background-size: cover;
    background-attachment: fixed;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
}}
.center-content {{
    text-align: center;
    color: white;
}}
.footer {{
    position: fixed;
    bottom: 0;
    width: 100%;
    text-align: center;
    color: white;
    background-color: rgba(0,0,0,0.3);
    padding: 5px;
    font-size: 16px;
}}
div.stTextInput > div, div.stFileUploader {{
    max-width: 400px;
    margin: auto;
}}
div.stButton {{
    display: flex;
    justify-content: center;
}}
</style>

<div class="center-content">
    <h1>Your Travel Planner.</h1>
    <p>Plan better. Travel smarter.</p>
</div>

<div class="footer">
    Instagram: <a href="https://instagram.com/your_instagram" target="_blank">@your_instagram</a> |
    Email: <a href="mailto:youremail@example.com">youremail@example.com</a>
</div>
""", unsafe_allow_html=True)

# ---- Input Section ----
user_text = st.text_input("", placeholder="Plan my trip to Bali for 5 days...", key="input_box")
uploaded_file = st.file_uploader("", type=["pdf", "txt", "docx"])
submit = st.button("Submit")

# ---- Handle Submit ----
if submit:
    if not user_text:
        st.warning("Please enter a query")
        st.stop()
    
    data = {"query": user_text}
    files = None
    if uploaded_file:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}

    try:
        response = requests.post(
            FASTAPI_URL,
            data=data,
            files=files
        )
        response.raise_for_status()  # Raise error for status >= 400

        response_json = response.json()
        itinerary_text = response_json.get("itinerary", "")
        
        st.success("Itinerary Generated!")
        st.write(itinerary_text)

        # Get token usage from response
        tokens_used = response_json.get("usage", {}).get("total_tokens", "N/A")
        st.info(f"Tokens used for this request: {tokens_used}")

        #PDF
        # ---- PDF Download ----
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)
        for line in itinerary_text.split("\n"):
            safe_line = line.encode("latin-1", "replace").decode("latin-1")
            pdf.multi_cell(0, 7, line)
        pdf_output = "itinerary.pdf"
        pdf.output(pdf_output)

        with open(pdf_output, "rb") as f:
            st.download_button(
                label="Download Itinerary as PDF",
                data=f,
                file_name="data/itinerary.pdf",
                mime="application/pdf"
            )

    except requests.exceptions.HTTPError as http_err:
        st.error(f"OpenAI API error: {http_err}. You might have exhausted your credits.")
    except requests.exceptions.RequestException as req_err:
        st.error(f"API request failed: {req_err}")
    except Exception as e:
        st.error(f"Something went wrong: {e}")
