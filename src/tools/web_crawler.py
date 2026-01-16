import requests
import os
from bs4 import BeautifulSoup
from langchain_core.documents import Document 

def scrape_web_page(url: str) -> str:
    try:
        headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/115.0 Safari/537.36"
}
        response = requests.get(url,headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text,'lxml')

        for elements in soup(["script","style","nav","footer","header"]):
            elements.decompose()
        
        text = soup.get_text(separator=' ')

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = ' '.join(lines)

        # Wrapping the text as Document object
        doc = [Document(page_content=clean_text, metadata={"source": url})]
        return doc

    except Exception as e:
        print(f"Scraping failed for {url}: {e}")
        return []
    


def scrape_from_file(file_path):
    
    if not os.path.exists(file_path):
        print(f"File {file_path} not found")
        return []
    
    with open(file_path, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    if not urls:
        print(" No URLs found in the file.")
        return []

    print(f"Starting bulk scrape for {len(urls)} URLs...")

    all_docs = []
    for url in urls:
        print(f"Scraping: {url}")
        doc = scrape_web_page(url)
        if doc:
            all_docs.append(doc)

    print(f"\n Total web documents successfully loaded: {len(all_docs)}")
    return all_docs

if __name__ == "__main__":
    print(scrape_web_page("https://en.wikipedia.org/wiki/LangChain"))
    URL_FILE = "data/raw/web/urls.txt"
    
    # Run the bulk scraper
    web_documents = scrape_from_file(URL_FILE)
    
    # Displaying results
    if web_documents:
        print(f"\nSample Source: {web_documents[0].metadata['source']}")
        print(f"Sample Preview: {web_documents[0].page_content[:150]}...")


