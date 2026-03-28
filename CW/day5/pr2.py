from langchain_text_splitters import RecursiveCharacterTextSplitter
import tiktoken

# 原始文字（你要自己放）
text = "日本利用壓電磁磚將腳步轉化為電能。這些瓷磚捕捉來自你腳步的動能。當你行走時，你的重量和動作會對瓷磚產生壓力。磁磚會輕微彎曲，從而產生機械應力。磁磚內部的壓電材料將這種應力轉化為電能。每一步都會產生少量電荷，而數百萬步結合在一起就能產生足夠的電力來驅動LED燈、數位顯示器和感測器。"

# 建立 splitter（用 token 切）
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    model_name="gpt-4",
    chunk_size=80,
    chunk_overlap=10,
    separators=[""]  # 最後手段：直接硬切
)

# tiktoken 編碼器（算 token 用）
encoding = tiktoken.encoding_for_model("gpt-4")

# 切割
chunks = text_splitter.split_text(text)

# 原始 token 數
print(f"Source text length: {len(encoding.encode(text))} tokens")

# chunk 數量
print(f"共有 {len(chunks)} 段\n")

# 每段內容
for i, chunk in enumerate(chunks, 1):
    token_count = len(encoding.encode(chunk))
    print(f"=== 第{i}段 ===")
    print(f"長度: {token_count} tokens")
    print(f"內容: {chunk}")
    print()
