from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json

# 1. 初始化模型
llm = ChatOpenAI(
   base_url="https://ws-02.wade0426.me/v1",
   api_key="vllm-token",
   model="Qwen/Qwen3-VL-8B-Instruct",
   temperature=0  # 提取資料建議將溫度設為 0，比較穩定
)

# 2. 定義 Parser
parser = JsonOutputParser()

# 3. 修正 Prompt 模板 (必須包含 {format_instructions})
# 這是最重要的部分：告訴 AI 嚴格遵守格式且不準廢話
system_prompt = """你是一個專業的資料提取助手。
請從使用者的輸入中提取資訊。
你必須嚴格遵守下方的格式說明，只輸出 JSON 內容，不要包含任何開場白或解釋。

{format_instructions}"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("user", "{text}")
])

# 4. 建立 Chain
chain = prompt | llm | parser

user_input = "你好，我是陳大明，電話是 0912-345-678，我想要訂購 3 台筆記型電腦，下週五送到台中市北區。"

# 5. 執行
# ... 前面初始化 llm, prompt, parser 的部分都一樣 ...

print("--- 開始串流提取資料 ---")
try:
    # 使用 .stream
    for chunk in chain.stream({
        "text": user_input,
        "format_instructions": parser.get_format_instructions() 
    }):
        # chunk 會是目前已經解析出來的 JSON 片段
        # 我們直接印出目前的進度
        print(chunk, flush=True)
        
except Exception as e:
    print(f"❌ 執行錯誤: {e}")
