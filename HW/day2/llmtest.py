from openai import OpenAI

client = OpenAI(
	base_url="http://ws-02.wade0426.me/v1",
 	api_key="vllm-token"
)
while True:
	user_input = input("User: ")
	if user_input.lower() in ["exit" , "q"]:
		print("bye")
		break
	response = client.chat.completions.create(
		model='google/gemma-3-27b-it',
		messages=[
			{"role": "system", "content" : "你是一個繁體中文聊天機器人"},
			{"role": "user", "content" : user_input}
		],
		temperature=0.7,
		max_tokens=256
	)
	print(f"AI : {response.choices[0].message.content}")

