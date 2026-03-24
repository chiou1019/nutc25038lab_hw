import os #取得電腦環境系統
import json #讀取、搜尋、快娶json檔用
import base64 #把網頁節圖轉成文字編碼,給ai看
import uuid   #產生獨一無二的id,讓ai區分不同人的對話
import requests #發送網路請求
import time  #計數
import operator      # 實作「知識累加」的神奇小工具
from typing import Annotated,TypedDict,Optional,List  #規定有哪些欄位、代表這個欄位可以是空的

# 眼睛：模擬瀏覽器行為
from playwright.sync_api import sync_playwright
# 大腦：與 LLM 溝通
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
# 工廠：串連所有流程
from langgraph.graph import StateGraph, END
# 記憶卡：儲存對話紀錄
from langgraph.checkpoint.memory import MemorySaver

#先設定大腦（規則）
llm = ChatOpenAI(
	base_url="https://ws-02.wade0426.me/v1",
    	api_key="chiou", 
    	model="google/gemma-3-27b-it",
    	temperature=0         #0代表最理智、1代表較為創意
)


#搜尋引擎的地址
SEARXNG_URL="https://puli-8080.huannago.com/search"


"""學長的搜索工具"""
def search_searxng(query: str, time_range: str = None, limit: int = 3):
    print(f"🔍 正在搜尋: {query} (範圍: {time_range if time_range else '全部'})")
    # 建構請求參數
    params = {
        "q": query,
        "format": "json",
        "language": "zh-TW" # 設定預設語言為繁體中文
    }
    if time_range and time_range != "all":
        params["time_range"] = time_range

    try:
        # 發送請求
        response = requests.get(SEARXNG_URL, params=params, timeout=10)
        response.raise_for_status() # 檢查 HTTP 狀態碼

        data = response.json()
        results = data.get('results', [])

        # 簡單過濾：排除沒有 URL 的結果
        valid_results = [r for r in results if 'url' in r]

        return valid_results[:limit]

    except requests.exceptions.RequestException as e:
        print(f"❌ 連線錯誤: {e}")
        return []
    except json.JSONDecodeError:
        print("❌ 解析 JSON 失敗，可能是回傳格式錯誤")
        return []
    except Exception as e:
        print(f"❌ 發生未預期錯誤: {e}")
        return []








"""學長的視覺化工具"""

def vlm_read_website(url: str, title: str = "網頁內容") -> str:
    """使用 Playwright 滾動截圖，並使用多模態 LLM 讀取網頁內容。"""
    print(f"📸 [VLM] 啟動視覺閱讀: {url}")
    
    def capture_rolling_screenshots(url, output_dir="scans_temp"):
        if not os.path.exists(output_dir): os.makedirs(output_dir)
        screenshots_b64 = []
        
        try:
            with sync_playwright() as p:
                # 啟動瀏覽器 (Headless 模式)
                browser = p.chromium.launch(
                    headless=True, 
                    args=["--disable-blink-features=AutomationControlled"] # 規避部分反爬蟲
                )
                
                # 設定 viewport (模擬桌面瀏覽)
                context = browser.new_context(viewport={'width': 1280, 'height': 1200})
                page = context.new_page()
                
                # 前往網頁
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(3000) # 等待渲染
                
                # --- CSS Injection (去廣告/彈窗) ---
                page.add_style_tag(content="""
                    iframe { opacity: 0 !important; pointer-events: none !important; }
                    div[id*='cookie'], div[class*='cookie'], div[id*='ads'], div[class*='ads'] { display: none !important; }
                    div[class*='overlay'], div[id*='overlay'], div[class*='popup'] { opacity: 0 !important; pointer-events: none !important; }
                    header, nav { position: absolute !important; } /* 防止 sticky header 遮擋截圖 */
                """)

                total_height = page.evaluate("document.body.scrollHeight")
                viewport_height = 1200
                current_scroll = 0
                
                for i in range(3):
                    # 滾動
                    page.evaluate(f"window.scrollTo(0, {current_scroll})")
                    page.wait_for_timeout(1000) # 等待滾動後渲染
                    
                    # 截圖並轉 Base64
                    b64 = base64.b64encode(page.screenshot()).decode('utf-8')
                    screenshots_b64.append(b64)
                    print(f"   - 截圖 {i+1} 完成 (Scroll: {current_scroll})")
                    
                    current_scroll += (viewport_height - 200) # 重疊 200px 避免割裂文字
                    if current_scroll >= total_height: break
                    
                browser.close()
        except Exception as e:
            print(f"❌ 截圖失敗: {e}")
            
        return screenshots_b64

    # 執行截圖
    images = capture_rolling_screenshots(url)
    
    if not images: 
        return "錯誤：無法讀取網頁內容或截圖失敗。"

    print(f"🤖 [LLM] 正在分析 {len(images)} 張圖片...")

    # --- 組裝多模態訊息 ---
    msg_content = [
        {
            "type": "text", 
            "text": f"這是一個網頁的滾動截圖，標題為：{title}。\n請忽略廣告與導航欄，摘要此網頁的核心內容，並特別關注任何數據、日期或具體事實。"
        }
    ]
    
    # 加入所有圖片
    for img in images:
        msg_content.append({
            "type": "image_url", 
            "image_url": {"url": f"data:image/png;base64,{img}"}
        })
    
    # 呼叫 LLM
    try:
        response = llm.invoke([HumanMessage(content=msg_content)])
        return response.content
    except Exception as e:
        return f"LLM 分析失敗: {e}"







#機器人查證過程,所需要紀錄的所有資訊欄位
class AgentState(TypedDict):
	question: str #使用者最初問題
	current_query: str #目前正在使用的關鍵字
	search_results: List[dict] #儲存找回來的網頁列表
	target_url: Optional[str] #目前正在閱讀的目標網址
	knowledge_base: Annotated[List[str],operator.add] #把每次的摘要都貼在清單後,並非刪除
	decision: str  #決策紀錄
	answer:	str #最終答案

"""建立node員========================================================================================="""
#引用學長的serch_searxng程式
def search_node(state: AgentState):
    print(f"📡 [Node] 正在為問題搜尋資料: {state['question']}")
    # 修正函數拼字 search_searxng 與參數 limit
    raw_results = search_searxng(state['question'], limit=3)  
    if not raw_results:
        return {"decision": "FINISH", "answer": "抱歉，找不到相關搜尋結果。"}
    
    first_url = raw_results[0].get('url')
    return {
        "search_results": raw_results,
        "target_url": first_url,
        "current_query": state['question'],
        "decision": "CONTINUE" # 給予初始決策值
    }


def vlm_node(state: AgentState):
    # 呼叫學長的視覺閱讀工具
    summary = vlm_read_website(state["target_url"])
    return {"knowledge_base": [summary]}

def planner_node(state: AgentState):
    print("🧠 [Node] Planner 評估中...")
    # 讓 AI 判斷目前的 knowledge_base 是否足以回答 question
    prompt = f"問題：{state['question']}\n資料：{state['knowledge_base']}\n夠回答嗎？請回傳 FINISH 或 MORE。"
    resp = llm.invoke([HumanMessage(content=prompt)]).content.upper()
    decision = "FINISH" if "FINISH" in resp else "MORE"
    return {"decision": decision}

def final_answer_node(state:AgentState):
	print("📝 [Node] 正在整理最終答案...")
	prompt = f"""
	請根據以下查證到的資訊，回答用戶的問題："{state['question']}"
	查證資訊：
	{state['knowledge_base']}

	請用繁體中文回答，確保事實準確。
	"""
	response = llm.invoke([HumanMessage(content=prompt)])
	return {"answer": response.content}




"""建造圖形藍圖"""
def router(state: AgentState):
    if state["decision"] == "FINISH":
        return "final_answer"
    return "search"

workflow = StateGraph(AgentState)  #藍圖

#註冊個名字
workflow.add_node("search",search_node)
workflow.add_node("vlm_read",vlm_node)
workflow.add_node("planner",planner_node)
workflow.add_node("final_answer", final_answer_node)

workflow.set_entry_point("search")    # 從搜尋開始
workflow.add_edge("search", "vlm_read") # 搜完去讀
workflow.add_edge("vlm_read", "planner") # 讀完去評估

workflow.add_conditional_edges(
    "planner", 
    router, 
    {
        "search": "search",             # 如果 router 說 search，就回頭重搜 (Loop)
        "final_answer": "final_answer"  # 如果 router 說 finish，就去寫答案
    }
)
# 最後寫完答案就收工
workflow.add_edge("final_answer", END)
checkpointer = MemorySaver()   #讓其能夠長期記憶

app = workflow.compile(
    checkpointer=checkpointer
)

print(app.get_graph().draw_ascii())  #顯示最終結果圖




if __name__ == "__main__":
    while True:
        try:
            question_input = input("\n請輸入要詢問的問題(q離開):").strip()
            if not question_input:
                continue 
            if question_input.lower() == 'q':
                break
            
            thread_id = str(uuid.uuid4())

            # 這裡就是機器人的「啟動開關」
            result = app.invoke(
                {
                    "question": question_input,   # 使用者問的問題
                    "current_query": "",          # 初始搜尋關鍵字
                    "search_results": [],         # 初始搜尋結果
                    "target_url": None,           # 初始網址
                    "knowledge_base": [],         # 重要！初始知識庫
                    "decision": "MORE",           # 初始決策狀態
                    "answer": ""                  # 初始答案
                },
                config={
                    "configurable": {
                        "thread_id": thread_id
                    },
                    "recursion_limit": 20         # 防止 AI 陷入無限迴圈
                }
            )

            print("\n" + "=" * 40)
            print("📌 最終回答：")
            print(result.get("answer"))
            print("=" * 40)

        except KeyboardInterrupt:
            print("\n👋 中斷結束")
            break
        except Exception as e:
            print(f"❌ 執行時發生錯誤: {e}")
