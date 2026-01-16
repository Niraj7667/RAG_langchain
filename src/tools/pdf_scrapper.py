from langchain_community.document_loaders import PyPDFLoader , DirectoryLoader

def scrape_pdf(file_path: str):
    """
    Uses LangChain's PyPDFLoader to extract text and metadata.
    Returns a list of Document objects.
    """

    try:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        return documents
    except Exception as e:
        print(f"Error loading PDF: {e}")
        return []
    
def bulk_pdf_scrap(directory_path):
    try:
        loader = DirectoryLoader(
            directory_path,
            glob="./*.pdf",
            loader_cls=PyPDFLoader,
            show_progress=True
        )
        docs = loader.load()
        return docs
    except Exception as e:
        print(f"Error loading PDF: {e}")
        return []
    
if __name__ == "__main__":
    docs = bulk_pdf_scrap("data/raw/pdfs")
    if docs:
        print(f"Page 1 Metadata: {docs[0].metadata}")
        print(f"Page 1 Content: {docs[0].page_content[:200]}")