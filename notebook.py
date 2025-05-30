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

def add_or_update_word(user_id, word_data, note=""):
    notebook = load_user_notebook(user_id)
    for w in notebook:
        if w["japanese"] == word_data["japanese"]:
            w["notes"] = note  # 更新筆記
            save_user_notebook(user_id, notebook)
            return False  # 代表是更新
    # 不存在則新增
    word_data["notes"] = note
    notebook.append(word_data)
    save_user_notebook(user_id, notebook)
    return True  # 代表是新增

def parse_args_to_dict(args_str):
    """
    將類似 'japanese=猫 chinese=貓 reading=ねこ' 的字串轉成字典
    """
    args = shlex.split(args_str)  # 支援引號包含有空白
    data = {}
    for arg in args:
        if "=" in arg:
            key, value = arg.split("=", 1)
            data[key] = value
    return data

def add_word_to_notebook(user_id, word_data):
    notebook = load_user_notebook(user_id)
    if any(w.get("japanese") == word_data.get("japanese") for w in notebook):
        return False
    notebook.append(word_data)
    save_user_notebook(user_id, notebook)
    return True

def save_word(user_id, word_data):
    folder = "notebooks"
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, f"{user_id}.json")

    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            notebook = json.load(f)
    else:
        notebook = []

    # 避免重複加入
    if any(w.get("japanese") == word_data["japanese"] for w in notebook):
        return False

    notebook.append(word_data)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(notebook, f, ensure_ascii=False, indent=2)

    return True

def delete_word(user_id, japanese):
    notebook = load_user_notebook(user_id)

    japanese = str(japanese)
    new_notebook = [data for data in notebook if data['japanese'] != japanese ]

    if len(new_notebook) == len(notebook) :
        return False
    save_user_notebook(user_id, new_notebook)
    return True

        