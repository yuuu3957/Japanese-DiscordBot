import json
import os
import shlex

def load_user_notebook(user_id):
    folder = "notebooks"
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{user_id}.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_user_notebook(user_id, notebook):
    folder = "notebooks"
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{user_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(notebook, f, ensure_ascii=False, indent=2)

def add_word_to_notebook(user_id, word_data):
    notebook = load_user_notebook(user_id)
    if any(w.get("japanese") == word_data.get("japanese") for w in notebook):
        return False
    notebook.append(word_data)
    save_user_notebook(user_id, notebook)
    return True