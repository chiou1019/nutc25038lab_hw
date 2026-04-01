import csv
from ques_rewrite import rewrite_query
from serfill_ans import retrieve, answer

QUESTIONS_CSV = "questions.csv"
OUTPUT_CSV = "questions_with_answer.csv"

def main():
    rows = []

    # 讀原 CSV
    with open(QUESTIONS_CSV, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames + ["Rewrite_Question", "答案"]  # 新增欄位

        for i, r in enumerate(reader, start=1):
            question = r["題目"]  # 注意要對應你的 CSV 欄位名稱

            print(f"\nQ{i}: {question}")

            # 改寫問題
            rq = rewrite_query(question)
            print(f" Rewrite: {rq}")

            # 檢索相關內容
            contexts = retrieve(rq)
            print(f" Retrieved {len(contexts)} chunks")

            # 得到最終答案
            final_answer = answer(question, contexts)
            print("💡 Answer:")
            print(final_answer)

            # 將結果寫回資料列
            r["Rewrite_Question"] = rq
            r["答案"] = final_answer

            rows.append(r)

    # 寫入新的 CSV
    with open(OUTPUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n✅ 完成！所有結果已寫入 {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
