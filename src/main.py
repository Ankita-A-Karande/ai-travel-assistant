# main.py

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from src.file_loader import read_file_content
from src.rag import create_vector_store, retrieve_chunks
from dotenv import load_dotenv
import os
import openai

# -- OPENAI API KEY ---
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

app = FastAPI(title="AI Travel Assistant API")

ALLOWED_EXTENSIONS = (".pdf", ".docx", ".txt")

@app.get("/")
async def home():
    return {"message": "Travel API is running"}

@app.post("/generate-itinerary")
async def generate_itinerary(
    query: str = Form(...),
    file: UploadFile = File(None)
):
    context_text = ""

    # Extract file text if uploaded
    if file:
        if not file.filename.lower().endswith(ALLOWED_EXTENSIONS):
            raise HTTPException(status_code=400, detail="Only pdf, docx, txt allowed")
        context_text = read_file_content(file)

    # RAG pipeline
    if context_text:
        index, chunks = create_vector_store(context_text)
        relevant_chunks = retrieve_chunks(query, index, chunks)
        context_summary = "\n".join(relevant_chunks)
    else:
        context_summary = "No additional context provided."

# ---- Call OpenAI GPT ----
    prompt = f"""
You are a travel planner assistant. 

User request:
{query}

Context:
{context_summary}

Create a detailed itinerary with:
- Day-wise breakdown
- Activities + timing
- Food recommendations
- Travel tips
- Budget suggestions

Make it engaging and practical.
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        itinerary_text = response['choices'][0]['message']['content'].strip()
        usage = response.get("usage", {})

    except Exception as e:
        itinerary_text = f"Error generating itinerary: {str(e)}"

    return {"itinerary": itinerary_text , "usage": usage}

@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail="Only pdf, docx, txt allowed")
    content = await file.read()
    return {
        "filename": file.filename,
        "size": len(content),
        "message": "File uploaded successfully"
    }