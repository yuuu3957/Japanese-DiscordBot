import requests
from bs4 import BeautifulSoup

url = "https://www.gavo.t.u-tokyo.ac.jp/ojad/search/index/textbook:13/section:8/page:2"
headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)
if response.status_code != 200:
    print("無法取得網頁")
    exit()

soup = BeautifulSoup(response.text, "html.parser")

# 找到 id="word_table" 的 table
table = soup.find("table", id="word_table")
if not table:
    print("找不到word_table表格")
    exit()

# 取得所有表格列(tr)，第一列通常是表頭
rows = table.find_all("tr")

# 解析表格內容
for row in rows:
    # 取得該列所有欄(td)
    cells = row.find_all(["td", "th"])
    # 把欄位文字取出並合成列表
    data = [cell.get_text(strip=True) for cell in cells]
    print(data)