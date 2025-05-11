import requests
from bs4 import BeautifulSoup
import csv

def crawl_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"無法取得網頁：{url}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", id="word_table")
    if not table:
        print("找不到word_table表格")
        return []

    rows = table.find_all("tr")

    data_list = []
    current_category = None

    for row in rows:
        cells = row.find_all(["td", "th"])
        data = [cell.get_text(strip=True) for cell in cells[:9]]

        if len(data) > 1 and data[0] == '' and data[1]:
            current_category = data[1]
            data_list.append([current_category] + [''] * 8)
            continue

        if current_category:
            data_list.append([current_category] + data)
        else:
            data_list.append(['未知分類'] + data)

    return data_list

def save_to_csv(data, filename):
    with open(filename, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['category', 'col1', 'col2', 'col3', 'col4', 'col5', 'col6', 'col7', 'col8', 'col9'])
        for row in data:
            writer.writerow(row)
    print(f"資料已儲存到 {filename}")

if __name__ == "__main__":
    base_url = "https://www.gavo.t.u-tokyo.ac.jp/ojad/search/index/textbook:13/section:8"
    all_data = []

    # 第一頁網址
    print("爬取第1頁...")
    page_data = crawl_page(base_url)
    if page_data:
        all_data.extend(page_data)

    # 第二頁開始的網址
    for page_num in range(2, 4):  # 假設爬1~3頁
        url = f"{base_url}/page:{page_num}"
        print(f"爬取第{page_num}頁...")
        page_data = crawl_page(url)
        if page_data:
            all_data.extend(page_data)

    save_to_csv(all_data, "ojad_words_pages_1_to_3.csv")