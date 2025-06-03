from .notebook_base import load_user_notebook, save_user_notebook

def add_word_to_notebook(user_id, word_data):
    notebook = load_user_notebook(user_id)
    if any(w.get("japanese") == word_data.get("japanese") for w in notebook):
        return False
    notebook.append(word_data)
    save_user_notebook(user_id, notebook)
    return True