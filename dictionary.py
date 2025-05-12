import requests
from googletrans import Translator

translator = Translator()

def lookup_word(word):
    """
    用 Jisho API 查詢日文單字
    回傳 (日文, 英文解釋, 中文解釋) 或 (None, None, None) 表示查無資料
    """
    url = f"https://jisho.org/api/v1/search/words?keyword={word}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None, None, None
        data = response.json()
        if not data['data']:
            return None, None, None

        first = data['data'][0]
        japanese = first['japanese'][0].get('word') or first['japanese'][0].get('reading')
        english = ', '.join(first['senses'][0]['english_definitions'])

        # 翻譯英文解釋成中文
        chinese = translator.translate(english, dest='zh-tw').text

        return japanese, english, chinese
    except Exception as e:
        print(f"查詢錯誤: {e}")
        return None, None, None