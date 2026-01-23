from langchain_core.prompts import ChatPromptTemplate


def get_prompt_template():
    """Defines the nature of AI Response"""

    template = """
    You are a helpful assistant. 
    
    1. Use the provided context below to answer the user's question.
    2. If the context is not relevant or is empty, use your own internal knowledge to provide a general answer, but clarify to the user that you are not using the uploaded documents for that part.
    3. If you truly do not know the answer at all, then say you don't know.
    4. Use three sentences maximum and keep the answer concise.

    HISTORY:{history}
    
    CONTEXT:{context}

    QUESTION:{question}

    ANSWER:
    """

    return ChatPromptTemplate.from_template(template)