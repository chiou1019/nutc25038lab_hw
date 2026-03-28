from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

# 1. 連 Qdrant
client = QdrantClient(url="http://localhost:6333")

# 2. embedding 模型
model = SentenceTransformer("all-MiniLM-L6-v2")

# 3. 建 collection
client.recreate_collection(
    collection_name="test_collection",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)

# 4. 存資料
text = "人工智慧很有趣"
vector = model.encode(text)

client.upsert(
    collection_name="test_collection",
    points=[
        PointStruct(
            id=1,
            vector=vector.tolist(),
            payload={"text": text}
        )
    ]
)

# 5. 查詢
query = "AI有什麼好處？"
query_vector = model.encode(query)

results = client.query_points(
    collection_name="test_collection",
    query=query_vector,
    limit=3
)

for point in results.points:
    print(f"ID: {point.id}")
    print(f"相似度分數: {point.score}")
    print(f"內容: {point.payload['text']}")
    print("---")
