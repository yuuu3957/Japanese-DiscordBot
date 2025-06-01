import os
from groq import Groq
import getpass

def set_groq_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}:")

def start_groq() :
    set_groq_env ("Groq_API_KEY")
    client = Groq()
    model = "llama-3.3-70b-versatile"
    return model, client

def generate_japanese_lookup(word,model,client):
    system_prompt = """
    你是一個精通日文語言和文化的專業語言助手，請用繁體中文回答所有問題。  
    當用戶提供一個日文單字時，請詳細解釋該單字的意思，並提供兩個常見的例句。 
    解釋意思的部分請不要提到日文單字是甚麼，解釋就好 
    例句要包含日文原文及其對應的繁體中文翻譯。  
    請保持回答清晰、準確且具教育意義。
    請注意拼音內容要是平假名或片假名
    """

    prompt = f"""
    請用繁體中文解釋日文單字「{word}」的意思，並提供兩個常見例句（包含中文翻譯）。
    格式：
    日文單字:{word}
    解釋：
    拼音(要是平假名或片假名):
    例句1️⃣：
        日文句子
        日文拼音(要是平假名或片假名)
    中文翻譯1️⃣：
        中文句子
    例句2️⃣：
        日文句子
        日文拼音(要是平假名或片假名)
    中文翻譯2️⃣：
        中文句子

    請注意拼音內容要是平假名或片假名
    """

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=500
    )
    thoughts = response.choices[0].message.content
    return thoughts

def generate_japanese_addnote(s, model, client):
    system_prompt = """
    你是一個善於分析文字格式且將純文字轉換為 JSON 格式的專業助手。 
    請根據傳入的字串s，分析其內容，並將其轉換為 JSON格式請根據傳入的字串s，分析其內容，並將其轉換為 JSON格式
    請只回傳純 JSON 字串，無任何額外說明或文字。  
    確保 JSON 格式正確且完整。
    """

    prompt = f"""請分析{s}之文字內容，並
    請嚴格回傳以下格式的 JSON 字串，並填入對應的內容：

    {{
    "japanese" :日文單字
    "chinese": "中文解釋",
    "reading": "假名拼音",
    "examples": [
        {{
        "jp_sentence": "日文句子1",
        "jp_reading": "拼音1",
        "chinese_translation": "中文翻譯1"
        }},
        {{
        "jp_sentence": "日文句子2",
        "jp_reading": "拼音2",
        "chinese_translation": "中文翻譯2"
        }}
    ]
    }}

    不要多餘的文字，只回傳純 JSON。
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
        max_tokens=500
    )
    json_str = response.choices[0].message.content.strip()
    #print("原始回應：", json_str)

    try:
        import json
        data = json.loads(json_str)
        #print(data)
        return data
    except json.JSONDecodeError as e:
        #print("JSON 解析失敗:", e)
        return None
    

def generate_japanese_quiz(ch, jp,model,client):
    system_prompt = """
    你是一個精通日文語言和文化的專業語言助手，請僅回答True 或是 False。
    當用戶提供一中文解釋和日文單字時，
    請判斷該中文解釋是否匹配日文單字，
    若是，請僅回答True。
    若非，請僅回答False。
    答案僅可有此兩種結果。
    """

    prompt = f"""
    請判斷中文解釋{ch}，是否匹配日文單字{jp}。
    若是，請僅回答True。
    若非，請僅回答False。
    答案僅可有此兩種結果。
    """

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=500
    )

    thoughts = response.choices[0].message.content
    if(str(thoughts) == "True"): 
        return True
    else: 
        return False