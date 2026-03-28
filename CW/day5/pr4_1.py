import pandas as pd
import re

def markdown_to_csv(md_file, csv_file):
    # 讀取 Markdown 檔案
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 以每行分割
    lines = content.strip().split('\n')

    data = []

    for line in lines:
        # 跳過分隔線，例如 |---|---|---|
        if re.match(r'^\|?[\s\-:|]+\|?$', line):
            continue

        # 解析每行的欄位
        if '|' in line:
            # 用 | 分割欄位，並去除前後空白
            cells = [cell.strip() for cell in line.split('|')]
            # 移除空字串元素（可能是行首或行尾的空欄位）
            cells = [c for c in cells if c]
            data.append(cells)

    # 將資料轉成 DataFrame
    if len(data) > 1:
        df = pd.DataFrame(data[1:], columns=data[0])
    else:
        df = pd.DataFrame(data)

    # 存成 CSV
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')  # utf-8-sig 方便 Excel 打開

# 使用範例
markdown_to_csv('table_txt.md', 'output.csv')
