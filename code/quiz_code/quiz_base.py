import random
from notebook_code.notebook_base import load_user_notebook, save_user_notebook


def check_num(user_id, num):
    notebook = load_user_notebook(user_id)
    if len(notebook) < num:
        return len(notebook)
    else:
        return num

def get_quiz_words(user_id, num_questions):
    notebook = load_user_notebook(str(user_id))

    # 篩出未學詞彙
    unlearned = [w for w in notebook if w.get("status") == "未學"]
    learned = [w for w in notebook if w.get("status") == "已學"]

    if len(unlearned) >= num_questions:
        # 從未學詞彙中隨機抽題
        return random.sample(unlearned, num_questions)
    else:
        # 未學不夠，先全拿未學，再從已學補足
        needed = num_questions - len(unlearned)
        sampled_learned = random.sample(learned, min(needed, len(learned)))
        return unlearned + sampled_learned

def update_quiz_result(word_data, direction, correct):
    """
    word_data: 詞彙 dict
    direction: 'jp_to_ch' 或 'ch_to_jp'
    correct: True or False
    """
    if "quiz_results" not in word_data:
        word_data["quiz_results"] = {"jp_to_ch": {"correct":0, "wrong":0}, "ch_to_jp": {"correct":0, "wrong":0}}

    if correct:
        word_data["quiz_results"][direction]["correct"] += 1
    else:
        word_data["quiz_results"][direction]["wrong"] += 1

    # 簡單判斷學習狀態
    corrects = word_data["quiz_results"]["jp_to_ch"]["correct"] and word_data["quiz_results"]["ch_to_jp"]["correct"]
    if corrects:
        word_data["status"] = "已學"
    else:
        word_data["status"] = "未學"

def update_user_word_result(user_id, japanese_word, direction, correct):
    notebook = load_user_notebook(user_id)
    for word in notebook:
        if word.get("japanese") == japanese_word:
            update_quiz_result(word, direction, correct)
            save_user_notebook(user_id, notebook)
            return True
    return False  # 找不到該詞彙