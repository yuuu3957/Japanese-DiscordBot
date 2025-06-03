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