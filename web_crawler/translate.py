import os
import csv
from googletrans import Translator

translator = Translator()

def translate_text(text):
    try:
        result = translator.translate(text, dest='zh-tw')
        return result.text
    except Exception as e:
        print(f"翻譯失敗: {text}，原因: {e}")
        return ""

def translate_csv(input_file, output_file, translate_col_indices):
    with open(input_file, newline='', encoding='utf-8') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        headers = next(reader)
        new_headers = []
        for i, h in enumerate(headers):
            new_headers.append(h)
            if i in translate_col_indices:
                new_headers.append("chinese")
        writer.writerow(new_headers)

        for row in reader:
            new_row = []
            for i, val in enumerate(row):
                new_row.append(val)
                if i in translate_col_indices:
                    zh = translate_text(val) if val else ""
                    new_row.append(zh)
            writer.writerow(new_row)

def batch_translate_folder(input_folder, output_folder, translate_col_indices):
    os.makedirs(output_folder, exist_ok=True)  # 確保輸出資料夾存在

    for filename in os.listdir(input_folder):
        if filename.endswith(".csv"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename.replace(".csv", "_translated.csv"))
            print(f"翻譯檔案：{filename}")
            translate_csv(input_path, output_path, translate_col_indices)
    print("所有檔案翻譯完成！")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_folder = os.path.join(base_dir, "ojad_data")
    output_folder = os.path.join(base_dir, "ojad_data_translated")
    translate_cols = [0]
    batch_translate_folder(input_folder, output_folder, translate_cols)