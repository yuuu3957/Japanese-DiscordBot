import requests

def lookup_word(word):
    url = f"https://jisho.org/api/v1/search/words?keyword={word}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None, None
        data = response.json()
        if not data['data']:
            return None, None

        # 找完全匹配的詞條
        for entry in data['data']:
            japanese_word = entry['japanese'][0].get('word') or entry['japanese'][0].get('reading')
            if japanese_word == word:
                english = ', '.join(entry['senses'][0]['english_definitions'])
                return japanese_word, english

        # 找不到完全相符，回傳第一筆
        return None, None

    except Exception as e:
        print(f"查詢錯誤: {e}")
        return None, None