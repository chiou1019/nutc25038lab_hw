import json
import time
from typing import TypedDict, Annotated, Literal
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

# 1. 初始化 LLM
llm = ChatOpenAI(
    base_url="https://ws-02.wade0426.me/v1",
    api_key="vllm-token", # 填入你的 Token
    model="google/gemma-3-27b-it",
    temperature=0
)

# 2. 定義狀態 (State)
class MeetingState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    detailed_minutes: str  # 存放 ASR 回傳的 SRT (時間軸)
    summary_text: str     # 存放 ASR 回傳的 TXT (純文字)
    final_report: dict    # 存放最終整合結果

# --- 3. 定義各個節點 (Nodes) ---

def asr_node(state: MeetingState):
    """模擬 ASR 語音轉文字"""
    print("🎬 [Node: ASR] 正在處理語音檔 (離線模式)...")
    
    # 這裡放你截圖中的範例內容
    mock_srt = """00:00:00 - 00:00:03 | 歡迎來到天下文化 podcast
00:00:03 - 00:00:10 | 今天要介紹一本非常棒的書，書名是《努力但不費力》
00:00:10 - 00:00:15 | 我很喜歡這本書的副標題：「只做最重要的人，其實沒有你想像的這麼難」。"""
    
    mock_txt = "歡迎來到天下文化 podcast。今天要介紹一本非常棒的書，書名是《努力但不費力》。我很喜歡這本書的副標題..."
    
    return {
        "detailed_minutes": mock_srt,
        "summary_text": mock_txt,
        "messages": [HumanMessage(content="語音轉錄已完成。")]
    }

def minutes_taker_node(state: MeetingState):
    """將時間軸內容格式化為整齊的逐字稿"""
    print("✍️ [Node: Minutes Taker] 正在整理詳細逐字稿...")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一個專業秘書，請將以下包含時間軸的內容整理成整齊的表格格式輸出。"),
        ("user", "{content}")
    ])
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"content": state["detailed_minutes"]})
    return {"detailed_minutes": result}

def summarizer_node(state: MeetingState):
    """針對純文字內容進行重點摘要"""
    print("📊 [Node: Summarizer] 正在生成重點摘要...")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一個專業的會議分析師。請根據會議內容，整理出：1. 重點摘要 2. 決策結果 3. 待辦事項。"),
        ("user", "{content}")
    ])
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"content": state["summary_text"]})
    return {"summary_text": result}

def writer_node(state: MeetingState):
    """整合摘要與逐字稿，輸出最終結果"""
    print("🏁 [Node: Writer] 正在整合最終報告...")
    # 這裡我們單純把兩者合併
    report = f"""
======= 智慧會議記錄報告 =======
【重點摘要與行動綱領】
{state['summary_text']}

-------------------------------
【詳細會議逐字稿】
{state['detailed_minutes']}
===============================
"""
    return {"messages": [HumanMessage(content=report)]}

# --- 4. 構建 LangGraph 工作流 ---

workflow = StateGraph(MeetingState)

# 加入節點
workflow.add_node("asr", asr_node)
workflow.add_node("minutes_taker", minutes_taker_node)
workflow.add_node("summarizer", summarizer_node)
workflow.add_node("writer", writer_node)

# 設定邊 (Edges)
workflow.set_entry_point("asr")
workflow.add_edge("asr", "minutes_taker")
workflow.add_edge("asr", "summarizer")
workflow.add_edge("minutes_taker", "writer")
workflow.add_edge("summarizer", "writer")
workflow.add_edge("writer", END)

# 編譯
app = workflow.compile()

# --- 5. 執行測試 ---
if __name__ == "__main__":
    print("🚀 啟動智慧會議助手...")
    # 初始化 state
    initial_input = {"messages": [HumanMessage(content="開始處理會議音檔")]}
    
    # 串流執行
    for event in app.stream(initial_input):
        for node_name, output in event.items():
            print(f"--- 節點 {node_name} 執行完畢 ---")
            # 只有 Writer 節點印出最終大報告
            if node_name == "writer":
                print(output["messages"][-1].content)
