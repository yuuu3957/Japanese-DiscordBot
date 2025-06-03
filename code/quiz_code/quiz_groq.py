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