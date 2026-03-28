from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import requests

# 1. 連 Qdrant
client = QdrantClient(url="http://localhost:6333")

# 2. 建 collection
client.recreate_collection(
    collection_name="test_collection",
    vectors_config=VectorParams(size=4096, distance=Distance.COSINE),
)

# 3. 取得 embedding
data = {
    "texts": ["人工智慧很有趣"],
    "normalize": True,
    "batch_size": 32
}

response = requests.post("https://ws-04.wade0426.me/embed", json=data)
result = response.json()

vector = result["embeddings"][0]

# 4. 存入 Qdrant
client.upsert(
    collection_name="test_collection",
    points=[
        PointStruct(
            id=1,
            vector=vector,
            payload={"text": "人工智慧很有趣"}
        )
    ]
)

# 5. 查詢 embedding
query_data = {
    "texts": ["AI有什麼好處？"],
    "normalize": True
}

query_res = requests.post("https://ws-04.wade0426.me/embed", json=query_data)
query_vector = query_res.json()["embeddings"][0]

# 6. 搜尋
search_result = client.search(
    collection_name="test_collection",
    query_vector=query_vector,
    limit=3
)

# 7. 印結果
for point in search_result:
    print(point.payload["text"], point.score)
