from collections import defaultdict

chat_histories = defaultdict(list)

def add_turn(session_id: str,role: str,content:str):
    chat_histories[session_id].append({"role" : role , "content":content})

def get_history(session_id: str):
    return chat_histories[session_id]

def clear_history(session_id: str):
    chat_histories[session_id] = []