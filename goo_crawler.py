import requests
from bs4 import BeautifulSoup

def crawl_goo_entries(word):
    url = f"https://dictionary.goo.ne.jp/srch/all/{word}/m0u/"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    ul = soup.find('ul', class_='content_list idiom lsize')
    if not ul:
        return []

    entries = []
    for li in ul.find_all('li'):
        a = li.find('a')
        if not a:
            continue
        title_p = a.find('p', class_='title')
        text_p = a.find('p', class_='text')

        title = title_p.get_text(strip=True) if title_p else ""
        definition = text_p.get_text(strip=True) if text_p else ""

        entries.append({'title': title, 'definition': definition})

    return entries