from src.vectorstore.file_hash import get_vector_db
CHROMA_PATH = "data/processed/embeddings"

def get_docs_with_similarity(query: str, scope_filter, k=3, threshold=0.35):
   
    vector_db = get_vector_db()
    
    chroma_filter = {"scope": scope_filter}
    
    results = vector_db.similarity_search_with_score(
        query, 
        k=k, 
        filter=chroma_filter
    )
    
    return [(doc, score) for doc, score in results if score <= threshold]