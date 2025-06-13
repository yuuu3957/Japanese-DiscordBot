
import asyncio
from lookup_code.goo_crawler import crawl_word_full  # 爬蟲函式
from lookup_code.Jisho import lookup_word  # Jisho API
from lookup_code.lookup_groq import generate_japanese_lookup


async def lookup_word_full(word, model, client):

    # 非同步執行阻塞的爬蟲函式，爬 goo辞書
    goo_result = await asyncio.to_thread(crawl_word_full, word, 3)

    # 非同步執行 Jisho API 查詢
    jp, en = await asyncio.to_thread(lookup_word, word)

    jisho_result = {"jp" : jp, "en": en}

    groq_result = await asyncio.to_thread(generate_japanese_lookup, word, model, client)



    return jisho_result, goo_result, groq_result 
