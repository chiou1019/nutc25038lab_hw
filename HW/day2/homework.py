import time
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableParallel
import json

llm = ChatOpenAI(
   base_url="https://ws-02.wade0426.me/v1",
   api_key="vllm-token",
   model="Qwen/Qwen3-VL-8B-Instruct",
   temperature=0,
   max_tokens=300
)


"""建立ai設定格式 system:給予ai的提示慈、設定人設   human:給ai要回復的內容"""
ig_post=ChatPromptTemplate.from_messages([
	("system" , "你是一個知名ig網紅，用詞要更浮誇一點、多利用一些顏文字或表情符號"),
	("human" , "請針對主題 {topic} 寫一篇貼文")
	])
real_post=ChatPromptTemplate.from_messages([
	("system" , "你是一位各方領域的專家，言詞要用得更專業、客觀，不需要有任何情緒價值"),
	("human" , "請針對主題 {topic} 寫一篇貼文")
	])


chain_ig = ig_post | llm | StrOutputParser()
chain_real = real_post | llm | StrOutputParser()


parallel_chain = RunnableParallel({
	"ig_style" : chain_ig,
	"real_style" : chain_real
	})

user_input = input("輸入一個主題:")
input_post = [{"topic":user_input}]

print(f"--- 準備處裡{len(input_post)}個請求 ---")

start_time = time.time()
results=parallel_chain.batch(input_post)
end_time = time.time()

print(f"\n=== the end , use time: {end_time - start_time : .4f} second ===")
for i ,res in enumerate(results):
	print(f"[IG風格]: {res['ig_style']}")
	print(f"[real風格]: {res['real_style']}")
