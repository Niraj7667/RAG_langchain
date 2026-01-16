import os
import hashlib
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.embeddings.embedding_model import get_embedding

CHROMA_PATH = "data/processed/embeddings"

def get_vector_db():
    """Returns the Chroma instance."""
    embeddings = get_embedding()
    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_metadata={"hnsw:space": "cosine"}
    )

def get_content_hash(content: str):
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def get_file_hash(file_path: str):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def add_to_vector_store(documents, source_identifier, is_file=True, is_permanent=False, session_id=None):
    """
    documents: List of LangChain Documents
    is_permanent: Set to True for our local 'data/raw' folder data
    session_id: Pass a unique ID (like user_id) for dynamic uploads of user
    """
    if not documents:
        return "No documents provided."
    
    #scoping the queries
    scope = "permanent" if is_permanent else f"user_{session_id}"

    if is_file:
        unique_hash = get_file_hash(source_identifier)
    else:
        # Combine all text from all document objects to get a full content hash
        full_text = "".join([doc.page_content for doc in documents])
        unique_hash = get_content_hash(full_text)
    

    vector_db = get_vector_db()
    
    #checks if a file or url content are already exist in database or not
    existing = vector_db.get(
        where={
            "$and": [
                {"scope": scope},
                {"$or": [
                    {"content_hash": unique_hash},
                    {"source": source_identifier}
                ]}
            ]
        }
    )

    if existing and len(existing['ids']) > 0:
        print(f"DEBUG: Duplicate found for {source_identifier} in scope {scope}")
        return "Duplicate detected."

    # 4. Chunking
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)

    

    for chunk in chunks:
        chunk.metadata["content_hash"] = unique_hash
        chunk.metadata["source"] = source_identifier
        chunk.metadata["scope"] = scope 

    # 6. Add in database
    vector_db.add_documents(chunks)
    return f"Success: Added to {scope}"