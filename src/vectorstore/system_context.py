import os
from src.tools.web_crawler import scrape_from_file
from src.tools.pdf_scrapper import scrape_pdf
from src.vectorstore.file_hash import add_to_vector_store

# --- FUNCTION 1: PERMANENT PDF INGESTION ---
def ingest_permanent_pdfs(directory_path="data/raw/pdfs"):
    print(f"Starting Permanent PDF Ingestion from {directory_path} ---")
    if not os.path.exists(directory_path):
        print(f" Error: Directory {directory_path} not found.")
        return

    files = [f for f in os.listdir(directory_path) if f.endswith(".pdf")]
    
    for filename in files:
        file_path = os.path.join(directory_path, filename)
        print(f"Processing: {filename}")
        
        # We use scrape_pdf function to get Document objects
        docs = scrape_pdf(file_path)
        
        if docs:
            # is_permanent=True means context is available for all users 
            status = add_to_vector_store(
                documents=docs, 
                source_identifier=file_path, 
                is_file=True, 
                is_permanent=True
            )
            print(f"   Result: {status}")

# --- FUNCTION 2: PERMANENT URL INGESTION ---
def ingest_permanent_urls(file_path="data/raw/web/urls.txt"):
    print(f"--- Starting Permanent URL Ingestion from {file_path} ---")
    

    # scrape_from_file returns a list of lists [[Doc1], [Doc2]]
    web_docs_list = scrape_from_file(file_path)
    
    for doc_list in web_docs_list:
        if doc_list:
            url = doc_list[0].metadata['source']
            print(f" Processing URL: {url}")
            
            # is_permanent=True means context is available for all users
            status = add_to_vector_store(
                documents=doc_list, 
                source_identifier=url, 
                is_file=False, 
                is_permanent=True
            )
            print(f"   Result: {status}")


if __name__ == "__main__":
    # Run both functions to populate your "Permanent" knowledge base
    ingest_permanent_pdfs()
    print("\n" + "="*50 + "\n")
    ingest_permanent_urls()