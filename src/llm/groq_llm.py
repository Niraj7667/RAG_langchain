from langchain_groq import ChatGroq
from src.config.settings import GROQ_API_KEY


def get_groq_llm(model_name="qwen/qwen3-32b",temp=0.1):
    """Returns a instance of chatgroq"""

    return ChatGroq(
        api_key=GROQ_API_KEY,
        model = model_name,
        temperature=temp,
        timeout=30,
        max_retries=2
    )

if __name__ == "__main__":
    llm = get_groq_llm()
    response = llm.invoke("Translate I love Programming in telugu")
    print(response.content)