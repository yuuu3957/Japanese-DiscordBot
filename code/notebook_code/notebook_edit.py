from .notebook_base import load_user_notebook, save_user_notebook

def edit_word(user_id, word ,field, value):
    notebook = load_user_notebook(user_id)

    # 尋找詞彙並修改欄位
    modified = False
    if field == "status":
        if value == "未學":
            for w in notebook:
                if w["japanese"] == word:
                    w[field] = value
                    modified = True
                    w["quiz_results"] = {"jp_to_ch": {"correct":0, "wrong":0}, "ch_to_jp": {"correct":0, "wrong":0}}
                    break


    elif "example" not in field:
        for w in notebook:
            if w["japanese"] == word:
                w[field] = value
                modified = True
                break
    elif "example1" in field:
        field = field[len("example1 "):]
        for w in notebook:
            if w["japanese"] == word:
                w["examples"][0][field] = value
                modified = True
                break
    else:
        field = field[len("example2 "):]  
        for w in notebook:
            if w["japanese"] == word:
                w["examples"][1][field] = value
                modified = True
                break

    if modified:
        save_user_notebook(user_id, notebook)
    
    return modified