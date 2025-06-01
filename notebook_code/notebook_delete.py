from .notebook_base import load_user_notebook, save_user_notebook


def delete_word(user_id, japanese):
    notebook = load_user_notebook(user_id)

    japanese = str(japanese)
    new_notebook = [data for data in notebook if data['japanese'] != japanese ]

    if len(new_notebook) == len(notebook) :
        return False
    save_user_notebook(user_id, new_notebook)
    return True
