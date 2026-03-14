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
try:
    # 使用 .invoke() 確保拿到完整的 JSON 再解析
    result = chain.invoke({
       "text": user_input,
       "format_instructions": parser.get_format_instructions() 
    })
    
    print("--- 提取結果 ---")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
except Exception as e:
    print(f"❌ Chain 執行錯誤: {e}")
