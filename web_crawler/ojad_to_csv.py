import requests
from bs4 import BeautifulSoup
import csv
import os

def crawl_and_clean_auto_pos_skip_first_col(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.find("table", id="word_table")
    if not table:
        print("找不到word_table表格")
        return {}, {}

    rows = table.find_all("tr")

    grouped = {}
    headers_dict = {}
    current_pos = None
    skip_word = "全体を一括再生"
    key_word = "詞"

    for row in rows:
        cells = row.find_all(["td", "th"])
        data_full = [c.get_text(strip=True) for c in cells]

        if not any(data_full):
            continue

        # 判斷詞性標題：第2欄不等於skip_word且包含key_word視為詞性標題
        if len(data_full) > 1 and data_full[1] != skip_word and key_word in data_full[1]:
            current_pos = data_full[1]
            # headers 是從第2欄開始（忽略第1欄）
            headers_dict[current_pos] = data_full[1:]
            if current_pos not in grouped:
                grouped[current_pos] = []
            continue

        if current_pos:
            if data_full[1] != skip_word:
                if "・" in data_full[1]: data_full[1] = data_full[1][0:data_full[1].index("・")]
                data = data_full[1:]
                grouped[current_pos].append(data)
        else:
            data = data_full[1:]
            grouped.setdefault("未知詞性", []).append(data)

    return grouped, headers_dict

def save_grouped_csv(grouped_data, headers_dict, output_dir="ojad_data"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_output_dir = os.path.join(base_dir, output_dir)
    os.makedirs(full_output_dir, exist_ok=True)

    for pos, rows in grouped_data.items():
        safe_pos = pos.replace(' ', '_').replace('/', '_')
        filename = os.path.join(full_output_dir, f"{safe_pos}.csv")
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            # 使用該詞性的 headers，如果沒有就跳過
            headers = headers_dict.get(pos)
            if headers:
                writer.writerow(headers)
            else:
                # 沒有 headers 時寫一個簡單提示
                writer.writerow(['No header found'])
            for row in rows:
                writer.writerow(row)
        print(f"已將詞性 '{pos}' 的資料存到 {filename}")

if __name__ == "__main__":
    base_url = "https://www.gavo.t.u-tokyo.ac.jp/ojad/search/index/textbook:1/section:8"
    total_pages = 3

    all_grouped = {}
    all_headers = {}

    print("爬取第1頁...")
    grouped, headers = crawl_and_clean_auto_pos_skip_first_col(base_url)
    for pos, rows in grouped.items():
        all_grouped.setdefault(pos, []).extend(rows)
    for pos, h in headers.items():
        all_headers[pos] = h

    for page_num in range(2, total_pages + 1):
        url = f"{base_url}/page:{page_num}"
        print(f"爬取第{page_num}頁...")
        grouped, headers = crawl_and_clean_auto_pos_skip_first_col(url)
        for pos, rows in grouped.items():
            all_grouped.setdefault(pos, []).extend(rows)
        for pos, h in headers.items():
            if pos not in all_headers:
                all_headers[pos] = h

    save_grouped_csv(all_grouped, all_headers)