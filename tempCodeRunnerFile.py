    # 非同步執行阻塞的爬蟲函式
    results = await asyncio.to_thread(crawl_word_full, word, 5)  # 只抓前三筆
    print(results)
