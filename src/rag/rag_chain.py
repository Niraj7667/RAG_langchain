from src.llm.groq_llm import get_groq_llm
from src.rag.retriever import get_docs_with_similarity
from src.rag.prompt import get_prompt_template
import re
from src.history import add_turn , get_history

def gen_answer_with_scope(question: str, scope_filter, session_id: str):
    
    matches = get_docs_with_similarity(question, scope_filter)

    #if there is no match found then we have to query llm based on the llm's knowledge
    if not matches:
        context = "No specific document context found"
        source = []
    else:
        context = "\n".join([d.page_content for d, _ in matches])
        source = [d.metadata.get("source") for d, _ in matches]

    #Build Chat History
    history = get_history(session_id)
    history_text = ""
    for turn in history:
        history_text += f"{turn['role'].capitalize} : {turn['content']}\n"

    # Printing in console for debugging
    print("\n--- Similarity Scores Check ---")
    for doc, score in matches:
        print(f"Distance: {score:.4f} | Source: {doc.metadata.get('source')}")

    prompt = get_prompt_template().format(context=context, question=question , history = history_text)
    
    llm = get_groq_llm()
    response = llm.invoke(prompt)

    answer_including_thinking = response.content

    clean_answer = re.sub(r'<think>.*?</think>','',answer_including_thinking,flags=re.DOTALL).strip()
    
    #updating history
    add_turn(session_id,"user",question)
    add_turn(session_id,"assistant",clean_answer)
    
    return {
        "answer": clean_answer,
        "sources": list(set(source)),
        "history": history + [{"role": "assistant", "content":clean_answer}]
    }