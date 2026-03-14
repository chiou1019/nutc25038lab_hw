from openai import OpenAI

# 1. 初始化 Client
client = OpenAI(
    base_url="http://ws-02.wade0426.me/v1",
    api_key="vllm-token"
)

prompt = "請用100字形容『人工智慧』。"
temps = [0.1,0.2,0.3,0.4,0.5, 1.5,5]  # 0.1 很冷靜, 1.5 很發散

for t in temps:
    print(f"\n➡️ 測試 Temperature = {t} ...")
    try:
        # 2. 呼叫 API
        response = client.chat.completions.create(
            model="Qwen/Qwen3-VL-8B-Instruct",
            messages=[{"role": "user", "content": prompt}],
            temperature=t,
            max_tokens=1000
        )
        # 3. 印出結果
        print(f"🤖 回覆: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
