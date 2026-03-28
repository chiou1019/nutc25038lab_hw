from semantic_text_splitter import TextSplitter

text = "日本利用壓電磁磚將腳步轉化為電能。這些瓷磚捕捉來自你腳步的動能。當你行走時,你的重量和動作會對瓷磚產生壓力。磁磚會輕微彎曲,從而產生機械應力。磁磚內部的壓電材料將這種應力轉化為電能。每一步都會產生少量電荷,而數百萬步結合在一起就能產生足夠的電力來驅動 LED燈、數位顯示器和感測器。在像澀谷車站這樣繁忙的地方,每天大約有240萬個腳步為此系統作出貢獻。這些電能可以被儲存或立即使用,從而減少對傳統電賴,並支持永續的城市基礎設施。這種方法將日常運動轉化為實用的再生能源#日本 #科技 #迷因 #複製文"

max_characters = 500
splitter = TextSplitter((50,max_characters))

chunks = splitter.chunks(text)

for i, chunk in enumerate(chunks, 1):
    print(f"=== Chunk {i} ===")
    print(chunk)
    print()
