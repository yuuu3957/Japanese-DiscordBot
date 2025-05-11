import requests
from bs4 import BeautifulSoup
import csv
import os

def crawl_page(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print(f"無法取得網頁：{url}")
        return None, None

    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.find("table", id="word_table")
    if not table:
        print("找不到word_table表格")
        return None, None

    rows = table.find_all("tr")

    pos_titles = []
    grouped_data = {}
    current_pos = None

    for row in rows:
        cells = row.find_all(["td", "th"])
        data = [cell.get_text(strip=True) for cell in cells]

        # 詞性標題判斷（單欄且非空）
        if len(data) == 1 and data[0] != '':
            current_pos = data[0]
            pos_titles.append(current_pos)
            if current_pos not in grouped_data:
                grouped_data[current_pos] = []
            continue

        # 非詞性標題，加入當前分類
        if current_pos:
            grouped_data[current_pos].append(data)
        else:
            grouped_data.setdefault('未知詞性', []).append(data)

    return pos_titles, grouped_data

def merge_grouped_data(all_grouped, new_grouped):
    for pos, rows in new_grouped.items():
        if pos in all_grouped:
            all_grouped[pos].extend(rows)
        else:
            all_grouped[pos] = rows

def save_grouped_data(grouped_data, output_dir="output_by_pos"):
    os.makedirs(output_dir, exist_ok=True)
    for pos, rows in grouped_data.items():
        safe_pos = pos.replace(' ', '_').replace('/', '_')
        filename = os.path.join(output_dir, f"{safe_pos}.csv")
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            for row in rows:
                writer.writerow(row)
        print(f"已儲存詞性 '{pos}' 的資料到 {filename}")

if __name__ == "__main__":
    base_url = "https://www.gavo.t.u-tokyo.ac.jp/ojad/search/index/textbook:13/section:8"
    all_pos_titles = set()
    all_grouped_data = {}

    # 先爬第1頁
    print("爬取第1頁...")
    pos_titles, grouped_data = crawl_page(base_url)
    if pos_titles is not None:
        all_pos_titles.update(pos_titles)
    if grouped_data is not None:
        merge_grouped_data(all_grouped_data, grouped_data)

    # 爬第2頁以後
    for page_num in range(2, 4):  # 2~3頁
        url = f"{base_url}/page:{page_num}"
        print(f"爬取第{page_num}頁...")
        pos_titles, grouped_data = crawl_page(url)
        if pos_titles is not None:
            all_pos_titles.update(pos_titles)
        if grouped_data is not None:
            merge_grouped_data(all_grouped_data, grouped_data)

    print("所有詞性標題：")
    for pos in sorted(all_pos_titles):
        print(pos)

    save_grouped_data(all_grouped_data)
