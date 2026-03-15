import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

# 1. 初始化 LLM
llm = ChatOpenAI(
    base_url="https://ws-02.wade0426.me/v1",
    api_key="vllm-token", # 記得填入你的 token
    model="google/gemma-3-27b-it",
    temperature=0
)

# 2. 定義 Tool (利用 Python 的 Type Hint 告訴 AI 格式)
@tool
def extract_order_data(name: str, phone: str, product: str, quantity: int, address: str):
    """
    專門提取訂單資料的工具。
    包含姓名、電話、產品名稱、數量、以及送貨地址。
    """
    return {
        "name": name,
        "phone": phone,
        "product": product,
        "quantity": quantity,
        "address": address
    }

# 3. 將工具綁定到 LLM
llm_with_tools = llm.bind_tools([extract_order_data])

# 4. 設定 Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一名專業的訂單管理員，請從用戶提供的對話中提取訂單資訊。"),
    ("user", "{user_input}")
])

# 5. 定義解析器：從 AI 的 Tool Calls 中把參數 (args) 抓出來
def extract_tool_args(ai_message):
    if ai_message.tool_calls:
        # 抓取第一個工具調用的參數
        return ai_message.tool_calls[0]['args']
    return None

# 6. 建立 Chain
# 注意：這裡的順序是 Prompt -> 帶有工具的LLM -> 參數提取器
chain = prompt | llm_with_tools | extract_tool_args

# 7. 執行測試
user_text = input("輸入訂單內容，其中需要包括 姓名、電話、訂購內容、需要訂購數量、和地址:") #你好，我是陳大明，電話是 0912-345-678，我想要訂購 3 台筆記型電腦，下週五送到台中市北區。"

try:
    result = chain.invoke({"user_input": user_text})

    if result:
        print("✅ 提取成功:")
        # 這裡 result 已經是一個 dict 了
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("❌ 提取失敗：AI 沒有呼叫工具。")
except Exception as e:
    print(f"❌ 發生錯誤: {e}")
