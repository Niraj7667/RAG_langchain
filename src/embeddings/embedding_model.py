from langchain_huggingface import HuggingFaceEmbeddings

def get_embedding():
    """Initializes and returns the Huggingface embedding model.
    Using all-MiniLM"""

    model_name = "sentence-transformers/all-MiniLM-L6-v2"

    return HuggingFaceEmbeddings(model_name=model_name)