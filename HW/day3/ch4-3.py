import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool

# 1. 初始化 LLM
llm = ChatOpenAI(
    base_url="https://ws-02.wade0426.me/v1",
    api_key="vllm-token", # 記得填入你的 Token
    model="google/gemma-3-27b-it",
    temperature=0
)

# 2. 定義科技摘要工具
@tool
def generate_tech_summary(article_content: str):
    """
    這是一個專業的科技文章摘要工具。
    當使用者的輸入內容看起來像是一篇科技新聞、技術文章或長篇報導時，請使用此工具進行歸納。
    """
    # 工具內部的專屬 Prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一個專業的科技文章編輯，請將提供的文章內容歸納出 3 個重點，並以繁體中文條列式輸出。"),
        ("user", "{text}")
    ])

    # 建立內部的 Chain
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"text": article_content})

# 3. 綁定工具並設定路由 Prompt
llm_with_tools = llm.bind_tools([generate_tech_summary])

router_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一個聰明的助手。如果使用者提供的是科技文章，請呼叫工具進行摘要；如果是普通閒聊，請直接回覆。"),
    ("user", "{input}")
])

# 4. 建立路由 Chain
router_chain = router_prompt | llm_with_tools

# 5. 互動迴圈
print("--- 科技編輯 AI 已啟動 (輸入 exit 離開) ---")
while True:
    try:
        user_input = input("\nUser: ")

        if user_input.lower() in ["exit", "q"]:
            print("再見！")
            break

        # 第一階段：判斷意圖
        ai_msg = router_chain.invoke({"input": user_input})

        # 第二階段：根據 AI 的決策執行不同路徑
        if ai_msg.tool_calls:
            print("✅ [決策] 偵測到科技文章，啟動摘要工具...")
            
            # 提取 AI 整理好的參數
            tool_args = ai_msg.tool_calls[0]['args']
            
            # 執行工具邏輯
            # 注意：這裡直接呼叫函數，並用 ** 將字典參數解包傳入
            final_result = generate_tech_summary.func(**tool_args)
            
            print(f"\n📝 [科技摘要結果]:\n{final_result}")
        else:
            print("💬 [決策] 一般對話：")
            print(f"AI: {ai_msg.content}")

    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
