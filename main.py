import os
import shutil
import time
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import your custom modules
from src.llm.groq_llm import get_groq_llm
from src.rag.prompt import get_prompt_template
from src.vectorstore.file_hash import (
    get_vector_db, 
    add_to_vector_store
)
from src.rag.rag_chain import gen_answer_with_scope
from src.tools.pdf_scrapper import scrape_pdf
from src.tools.web_crawler import scrape_web_page

app = FastAPI()

# Enable CORS for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELS ---
class ChatRequest(BaseModel):
    message: str
    session_id: str
    search_mode: str = "both" # options: "permanent", "temporary", "both"

# --- BACKGROUND TASKS ---
def cleanup_temporary_data(session_id: str):
    """Deletes temporary session data after a delay or on command."""
    # In a real app, you might run this after 24 hours
    # For now, this can be called manually or scheduled
    vector_db = get_vector_db()
    vector_db.delete(where={"scope": f"user_{session_id}"})
    print(f"🗑️ Cleaned up data for session: {session_id}")

# --- ENDPOINTS ---

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), session_id: str = Form(...)):
    print(f"--- Incoming Upload ---")
    print(f"Filename: {file.filename}")
    print(f"Session ID: {session_id}")

    try:
        temp_dir = "data/temp"
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        docs = scrape_pdf(file_path)
        print(f"Scraped {len(docs)} documents from PDF")

        status = add_to_vector_store(
            documents=docs, 
            source_identifier=file_path, 
            is_file=True, 
            is_permanent=False, 
            session_id=session_id
        )
        
        print(f"Vector Store Status: {status}") # This is the crucial log
        os.remove(file_path)
        return {"status": status, "filename": file.filename}

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        return {"status": f"Error: {str(e)}", "filename": file.filename}
    

@app.post("/add-url")
async def add_url(url: str = Form(...), session_id: str = Form(...)):
    docs = scrape_web_page(url)

    # NEW DEBUG CHECK:
    # if not docs or len(docs[0].page_content) < 100:
    #     print(f" SCRAPE FAILED: Only found {len(docs[0].page_content) if docs else 0} chars.")
    #     return {"status": "Scraping failed: No readable text found", "url": url}
    # print(f"DEBUG the scrapped docs: {docs}")
    # print("\n\n")
    print(f"Scraped {len(docs)} documents from PDF")
    
    status = add_to_vector_store(
        documents=docs, 
        source_identifier=url, 
        is_file=False, 
        is_permanent=False, 
        session_id=session_id
    )
    return {"status": status, "url": url}

# --- main.py ---

@app.post("/chat")
async def chat(request: ChatRequest):
    vector_db = get_vector_db()
    
    # 1. Determine the scope filter
    if request.search_mode == "permanent":
        scope_filter = "permanent"
    elif request.search_mode == "temporary":
        scope_filter = f"user_{request.session_id}"
    else:
        scope_filter = {"$in": ["permanent", f"user_{request.session_id}"]}
    
    try:
        response_data = gen_answer_with_scope(request.message,scope_filter,session_id=request.session_id)
        return response_data
    except Exception as e:
        print(f"Error in chat {str(e)}")
        return {"answer" : "An error occured during the process of your request" , "sources":[]}

@app.post("/clear-chat")
async def clear_chat(session_id: str, background_tasks: BackgroundTasks):
    # Delete temporary data in the background
    background_tasks.add_task(cleanup_temporary_data, session_id)
    return {"message": "Cleanup scheduled"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)