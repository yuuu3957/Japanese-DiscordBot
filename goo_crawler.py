import requests
from bs4 import BeautifulSoup

def get_entry_links(word):
    url = f"https://dictionary.goo.ne.jp/srch/all/{word}/m0u/"
    base_url = "https://dictionary.goo.ne.jp"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    ul = soup.find('ul', class_='content_list idiom lsize')
    if not ul:
        return []
    
    links = []

    for li in ul.find_all('li'):
        a = li.find('a')
        if a and a.has_attr('href'):
            links.append(base_url+a['href'])
    return links

def crawl_entry_details(link):
    headers = {"User-Agent": "Mozilla/5.0"}
    

    res = requests.get(link, headers=headers)
    if res.status_code != 200:
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    title = soup.find('div', class_='basic_title').find('h1')
    cut = title.find('span',class_='meaning')
    title_name = title.get_text(strip=True)
    title_name = title_name.replace(cut.get_text(strip=True),"")
        
    definition = soup.find('div',class_='contents')
    definition_name = definition.get_text(strip=True)

    
    return {
        'title' : title_name,
        'definition' : definition_name
    }
    

def crawl_word_full(word,max_entries):
    links = get_entry_links(word)
    results= []
    for link in links:
        if max_entries<=0:
            break
        detail = crawl_entry_details(link)
        if detail:
            results.append({
                'url': link,
                'title' : detail['title'],
                'definition' : detail['definition']
            })
        max_entries-=1
    return results