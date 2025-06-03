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
    拼音:
    例句1️⃣：
        日文句子
        日文拼音
    中文翻譯1️⃣：
        中文句子
    例句2️⃣：
        日文句子
        日文拼音
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